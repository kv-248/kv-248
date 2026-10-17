"""PoC: SEC Reg AB II Form ABS-EE auto-loan tapes (World Omni Auto Receivables trusts, 2017-2024).

Real source: monthly loan-level XML exhibits (EX-102) filed on EDGAR with each ABS-EE.
Reachable mirror: Kaggle `denytran/10-year-automotive-loans-abs-ee` (Parquet, 35.7M loan-months)
-- downloads anonymously. Per-trust mirrors also exist on HF (`DenyTranDFW/<trust>`).

What this proves:
  * Loan-level identities (natural ground truth) hold on real servicer data:
      begin_balance - principal_collected - charged_off (+/- other adj) == end_balance
      end_balance(t) == begin_balance(t+1)          (same asset, consecutive periods)
  * A monthly pool surveillance table (balance, 30+/60+ delinquency, net loss, prepay speed)
    can be computed bottom-up; in the full env it is reconciled to the trust's Form 10-D
    servicer report (pool balance, delinquency and cumulative net loss are reported there).

Usage: python3 -I absee_auto.py --data <dir with parquet/> --out ../samples/absee_world_omni
"""
from __future__ import annotations

import argparse
import json
import pathlib

import duckdb


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="dir containing parquet/absee, parquet/dates_table")
    ap.add_argument("--out", default="../samples/absee_world_omni")
    ap.add_argument("--sample-loans", type=int, default=300)
    args = ap.parse_args()
    data, out = pathlib.Path(args.data), pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(f"""
        CREATE VIEW tape AS
        SELECT a.*, d.date_val AS period_end
        FROM read_parquet('{data}/parquet/absee/*.parquet') a
        JOIN read_parquet('{data}/parquet/dates_table/*.parquet') d
          ON a.reportingPeriodEndingDate_ID = d.date_id
        WHERE d.date_val > DATE '2000-01-01'  -- 28 rows carry the 1900-01-01 null-date sentinel
    """)

    # 1. Within-period loan balance identity. Test sign variants for the "other" adjustment.
    within = con.sql("""
        WITH t AS (
          SELECT reportingPeriodBeginningLoanBalanceAmount b,
                 coalesce(actualPrincipalCollectedAmount,0) p,
                 coalesce(chargedoffPrincipalAmount,0) c,
                 coalesce(otherPrincipalAdjustmentAmount,0) o,
                 reportingPeriodActualEndBalanceAmount e
          FROM tape WHERE reportingPeriodBeginningLoanBalanceAmount IS NOT NULL
                      AND reportingPeriodActualEndBalanceAmount IS NOT NULL)
        SELECT count(*) n,
               avg(CASE WHEN abs(b - p - c - o - e) <= 0.01 THEN 1 ELSE 0 END) tie_minus_other,
               avg(CASE WHEN abs(b - p - c + o - e) <= 0.01 THEN 1 ELSE 0 END) tie_plus_other,
               avg(CASE WHEN abs(b - p - e) <= 0.01 THEN 1 ELSE 0 END) tie_principal_only,
               avg(CASE WHEN least(abs(b-p-c-o-e), abs(b-p-c+o-e), abs(b-p-e)) <= 0.01
                        THEN 1 ELSE 0 END) tie_any
        FROM t
    """).df().iloc[0].to_dict()

    # 2. Across-period continuity per asset.
    across = con.sql("""
        WITH t AS (
          SELECT assetNumber, period_end,
                 reportingPeriodBeginningLoanBalanceAmount b,
                 reportingPeriodActualEndBalanceAmount e,
                 lead(reportingPeriodBeginningLoanBalanceAmount)
                   OVER (PARTITION BY assetNumber ORDER BY period_end) b_next,
                 lead(period_end) OVER (PARTITION BY assetNumber ORDER BY period_end) p_next
          FROM tape)
        SELECT count(*) n_pairs,
               avg(CASE WHEN abs(e - b_next) <= 0.01 THEN 1 ELSE 0 END) tie_rate,
               sum(CASE WHEN abs(e - b_next) > 100 THEN 1 ELSE 0 END) breaks_gt_100,
               sum(CASE WHEN date_diff('month', period_end, p_next) > 1 THEN 1 ELSE 0 END) gaps_gt_1m
        FROM t WHERE b_next IS NOT NULL
    """).df().iloc[0].to_dict()

    # 3. Monthly pool surveillance table (bottom-up).
    pool = con.sql("""
        SELECT period_end,
               count(*) loans_reported,
               sum(reportingPeriodBeginningLoanBalanceAmount) begin_bal,
               sum(reportingPeriodActualEndBalanceAmount) end_bal,
               sum(actualPrincipalCollectedAmount) principal_collected,
               sum(chargedoffPrincipalAmount) gross_chargeoffs,
               -- repossessedProceedsAmount is a component of recoveredAmount (~80% of it);
               -- adding both double-counts recoveries and turns net loss negative.
               sum(coalesce(recoveredAmount,0)) recoveries,
               sum(CASE WHEN currentDelinquencyStatus >= 30
                        THEN reportingPeriodActualEndBalanceAmount END)
                 / sum(reportingPeriodActualEndBalanceAmount) dq30_pct,
               sum(CASE WHEN currentDelinquencyStatus >= 60
                        THEN reportingPeriodActualEndBalanceAmount END)
                 / sum(reportingPeriodActualEndBalanceAmount) dq60_pct,
               sum(CASE WHEN zeroBalanceCode = 1 THEN 1 ELSE 0 END) payoffs_prepaid,
               avg(obligorCreditScore) avg_fico
        FROM tape GROUP BY period_end ORDER BY period_end
    """).df()
    pool["net_loss"] = pool.gross_chargeoffs - pool.recoveries
    pool["annualized_net_loss_pct"] = 12 * pool.net_loss / pool.begin_bal

    # 4. Env seed: full monthly history for a random sample of loans.
    sample = con.sql(f"""
        WITH ids AS (SELECT DISTINCT assetNumber FROM tape USING SAMPLE {args.sample_loans} ROWS
                     (reservoir, 42))
        SELECT t.* EXCLUDE (id) FROM tape t JOIN ids USING (assetNumber)
        ORDER BY assetNumber, period_end
    """).df()

    import pandas as pd
    with pd.ExcelWriter(out / "absee_env_seed.xlsx") as xl:
        pool.to_excel(xl, sheet_name="pool_monthly", index=False)
        sample.to_excel(xl, sheet_name="tape_sample", index=False)

    report = {
        "source": "SEC Form ABS-EE (EX-102 auto loans), World Omni Auto Receivables trusts, "
                  "via Kaggle denytran/10-year-automotive-loans-abs-ee",
        "loan_months": int(con.sql("SELECT count(*) FROM tape").fetchone()[0]),
        "loans": int(con.sql("SELECT count(DISTINCT assetNumber) FROM tape").fetchone()[0]),
        "periods": [str(pool.period_end.min())[:10], str(pool.period_end.max())[:10],
                    int(len(pool))],
        "within_period_balance_identity": {k: (round(float(v), 4) if isinstance(v, float) else int(v))
                                           for k, v in within.items()},
        "across_period_continuity": {k: (round(float(v), 4) if isinstance(v, float) else int(v))
                                     for k, v in across.items()},
        "sample_loans_in_seed": int(sample.assetNumber.nunique()),
    }
    (out / "validation_report.json").write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str))
    print(pool.tail(6).to_string())


if __name__ == "__main__":
    main()
