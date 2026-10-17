"""PoC: FERC Form 1 (US electric/gas utility regulatory accounts) via Catalyst PUDL's public S3.

Real source: FERC Form 1 annual reports (1994-present; XBRL since 2021), cleaned by PUDL
(https://catalyst.coop/pudl/). Public bucket, no auth: s3://pudl.catalyst.coop/stable/.

What this proves:
  1. Scrapability: tables download directly from the sandbox.
  2. Depth: one utility has ~30 years of the same schedules (temporal roll-forward envs).
  3. Natural ground truth: schedule identities hold on real data, and the exceptions that do
     not hold are real restatements / reclassifications a strong agent must explain.

Usage:  python3 -I pudl_ferc1.py --utility "Idaho Power" --out ../samples/ferc1_idaho_power
"""
from __future__ import annotations

import argparse
import json
import pathlib
import urllib.request

import pandas as pd

S3 = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/{}.parquet"
TABLES = {
    "plant_in_service": "core_ferc1__yearly_plant_in_service_sched204",
    "balance_sheet_assets": "core_ferc1__yearly_balance_sheet_assets_sched110",
    "balance_sheet_liabilities": "core_ferc1__yearly_balance_sheet_liabilities_sched110",
    "income_statement": "core_ferc1__yearly_income_statements_sched114",
    "retained_earnings": "core_ferc1__yearly_retained_earnings_sched118",
    "depreciation_changes": "core_ferc1__yearly_depreciation_changes_sched219",
    "utilities": "core_pudl__assn_ferc1_pudl_utilities",
}
NUM = ["starting_balance", "additions", "retirements", "adjustments", "transfers", "ending_balance"]


def fetch(name: str, cache: pathlib.Path) -> pd.DataFrame:
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f"{name}.parquet"
    if not path.exists():
        urllib.request.urlretrieve(S3.format(name), path)
    return pd.read_parquet(path)


def plant_rollforward_checks(df: pd.DataFrame) -> dict:
    """Within-year and across-year identities on schedule 204 (plant in service)."""
    d = df[(df.row_type_xbrl == "reported_value") & df.ending_balance.notna()
           & df.starting_balance.notna()].copy()
    for c in NUM:
        d[c] = d[c].astype(float).fillna(0.0)
    # FERC reports retirements as negative amounts, so they are added, not subtracted.
    calc = d.starting_balance + d.additions + d.retirements + d.adjustments + d.transfers
    within = (calc - d.ending_balance).abs() <= 1

    keys = ["utility_id_ferc1", "ferc_account_label", "utility_type", "plant_status"]
    k = d.groupby(keys + ["report_year"], as_index=False)[["starting_balance", "ending_balance"]].sum()
    nxt = k.assign(report_year=k.report_year - 1)
    m = k.merge(nxt, on=keys + ["report_year"], suffixes=("", "_next"))
    gap = m.ending_balance - m.starting_balance_next
    breaks = m.loc[gap.abs() > 1000].assign(gap=gap[gap.abs() > 1000])
    return {
        "within_year_rows": int(len(d)),
        "within_year_tie_rate": round(float(within.mean()), 4),
        "across_year_pairs": int(len(m)),
        "across_year_tie_rate": round(float((gap.abs() <= 1).mean()), 4),
        "across_year_breaks_gt_1000": int(len(breaks)),
        "_breaks": breaks,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--utility", default="Idaho Power")
    ap.add_argument("--out", default="../samples/ferc1_sample")
    ap.add_argument("--cache", default="/tmp/pudl_cache")
    args = ap.parse_args()
    cache, out = pathlib.Path(args.cache), pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    t = {k: fetch(v, cache) for k, v in TABLES.items()}
    util = t["utilities"]
    hits = util[util.utility_name_ferc1.str.contains(args.utility, case=False, na=False)]
    if hits.empty:
        raise SystemExit(f"no utility matching {args.utility!r}")
    uid = int(hits.utility_id_ferc1.iloc[0])
    uname = hits.utility_name_ferc1.iloc[0]

    universe = plant_rollforward_checks(t["plant_in_service"])
    one = plant_rollforward_checks(t["plant_in_service"][t["plant_in_service"].utility_id_ferc1 == uid])

    # Starter workbook: one sheet per schedule for the chosen utility (the "env" seed).
    with pd.ExcelWriter(out / "ferc1_env_seed.xlsx") as xl:
        for k, df in t.items():
            if k == "utilities" or "utility_id_ferc1" not in df:
                continue
            sub = df[df.utility_id_ferc1 == uid].sort_values("report_year")
            sub.to_excel(xl, sheet_name=k[:31], index=False)
        one["_breaks"].to_excel(xl, sheet_name="rollforward_breaks", index=False)

    years = t["plant_in_service"].query("utility_id_ferc1 == @uid").report_year
    report = {
        "source": "FERC Form 1 via Catalyst PUDL stable release (s3://pudl.catalyst.coop/stable/)",
        "utility": uname, "utility_id_ferc1": uid,
        "years": [int(years.min()), int(years.max())], "n_years": int(years.nunique()),
        "universe_utilities": int(t["plant_in_service"].utility_id_ferc1.nunique()),
        "universe_checks": {k: v for k, v in universe.items() if not k.startswith("_")},
        "utility_checks": {k: v for k, v in one.items() if not k.startswith("_")},
    }
    (out / "validation_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
