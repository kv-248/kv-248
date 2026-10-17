"""PoC: IRS Form 990 e-file XML (US nonprofits) via the GivingTuesday 990 data lake (public S3).

Real source: IRS-released 990/990-EZ/990-PF e-file XML, ~6.2M returns indexed.
Bucket: https://gt990datalake-rawdata.s3.amazonaws.com/ (no auth). We range-read the Parquet
index (only the columns we need), pick one organization by EIN, fetch every return, and test
the form's own identities, which act as natural ground truth:

  * Part X / Part I net assets roll-forward:  EOY(t) == BOY(t+1)
  * Part XI reconciliation: revenue - expenses + other changes == EOY - BOY
  * Part IX functional expenses: program + management + fundraising == total

Usage: python3 -I irs990.py --ein 200049703 --out ../samples/irs990_wikimedia
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httprange import HTTPRangeFile  # noqa: E402

BUCKET = "https://gt990datalake-rawdata.s3.amazonaws.com"
INDEX = f"{BUCKET}/Indices/990xmls/index_all_years_efiledata_xmls_created_on_2024-07-23.parquet"
COLS = ["EIN", "ObjectId", "TaxYear", "TaxPeriodEndDate", "FormType", "OrganizationName",
        "ReturnVersion", "URL"]

# Element local-names, searched only inside the <IRS990> main form (the same names recur in
# schedules). The IRS renamed elements in 2013, so each field lists (2013+ name, 2009-12 name).
FIELDS = {
    "revenue_cy": ("CYTotalRevenueAmt", "TotalRevenueCurrentYear"),
    "expenses_cy": ("CYTotalExpensesAmt", "TotalExpensesCurrentYear"),
    "net_assets_boy": ("NetAssetsOrFundBalancesBOYAmt", "NetAssetsOrFundBalancesBOY"),
    "net_assets_eoy": ("NetAssetsOrFundBalancesEOYAmt", "NetAssetsOrFundBalancesEOY"),
    # Part XI reconciliation of net assets exists only in the 2013+ schema.
    "recon_rev_less_exp": ("ReconcilationRevenueExpnssAmt",),
    "recon_unrealized_gains": ("NetUnrlzdGainsLossesInvstAmt",),
    "recon_donated_services": ("DonatedServicesAndUseFcltsAmt",),
    "recon_investment_expense": ("InvestmentExpenseAmt",),
    "recon_prior_period_adj": ("PriorPeriodAdjustmentsAmt",),
    "recon_other_changes": ("OtherChangesInNetAssetsAmt",),
}
# Part IX total-functional-expenses group and its column children, per schema.
FUNCTIONAL = {"TotalFunctionalExpensesGrp": {"TotalAmt": "total", "ProgramServicesAmt": "program",
                                             "ManagementAndGeneralAmt": "mgmt",
                                             "FundraisingAmt": "fundraising"},
              "TotalFunctionalExpenses": {"Total": "total", "ProgramServices": "program",
                                          "ManagementAndGeneral": "mgmt",
                                          "Fundraising": "fundraising"}}


def find_returns(ein: str) -> pd.DataFrame:
    pf = pq.ParquetFile(HTTPRangeFile(INDEX))
    parts = []
    for i in range(pf.metadata.num_row_groups):
        t = pf.read_row_group(i, columns=COLS).to_pandas()
        parts.append(t[t.EIN == ein])
    return pd.concat(parts).drop_duplicates("ObjectId").sort_values("TaxYear")


def _local(tag: str) -> str:
    return re.sub(r"^\{.*\}", "", tag)


def parse(xml: bytes) -> dict:
    root = ET.fromstring(xml)
    form = next((el for el in root.iter() if _local(el.tag) == "IRS990"), None)
    vals: dict = {"schema": root.get("returnVersion")}
    if form is None:
        return vals
    by_name: dict[str, ET.Element] = {}
    for el in form.iter():
        by_name.setdefault(_local(el.tag), el)
    for key, names in FIELDS.items():
        el = next((by_name[n] for n in names if n in by_name), None)
        vals[key] = float(el.text) if el is not None and el.text else float("nan")
    for grp, cols in FUNCTIONAL.items():
        if grp in by_name:
            for ch in by_name[grp]:
                if _local(ch.tag) in cols:
                    vals[f"fx_{cols[_local(ch.tag)]}"] = float(ch.text)
    return vals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ein", default="200049703")  # Wikimedia Foundation
    ap.add_argument("--out", default="../samples/irs990_sample")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    (out / "xml").mkdir(parents=True, exist_ok=True)

    idx = find_returns(args.ein)
    idx = idx[idx.FormType == "990"]
    rows = []
    for r in idx.itertuples():
        xml_path = out / "xml" / f"{r.ObjectId}_public.xml"
        if not xml_path.exists():
            url = f"{BUCKET}/EfileData/XmlFiles/{r.ObjectId}_public.xml"
            xml_path.write_bytes(urllib.request.urlopen(url, timeout=120).read())
        rows.append({"tax_year": int(r.TaxYear), "object_id": r.ObjectId,
                     "org": r.OrganizationName, **parse(xml_path.read_bytes())})
    df = pd.DataFrame(rows).sort_values(["tax_year", "object_id"])
    # Amended returns duplicate a tax year; keep the latest filing per year.
    df = df.drop_duplicates("tax_year", keep="last").reset_index(drop=True)

    # Part XI line 10 = combine lines 3-9. Filers disagree on the sign of line 7 (investment
    # expenses), so accept either sign. NaN where the return has no Part XI (pre-2013 schema).
    base = (df.recon_rev_less_exp + df[["recon_unrealized_gains", "recon_donated_services",
                                        "recon_prior_period_adj", "recon_other_changes"]]
            .fillna(0).sum(axis=1) - (df.net_assets_eoy - df.net_assets_boy))
    inv = df.recon_investment_expense.fillna(0)
    best = base.where((base - inv).abs() >= (base + inv).abs(), base + inv)
    df["chk_recon"] = best.where((best - inv).abs() > 1, best - inv).round(0)
    df["chk_rollforward_next_boy"] = (df.net_assets_eoy - df.net_assets_boy.shift(-1)).round(0)
    if "fx_total" in df:
        df["chk_functional"] = (df[["fx_program", "fx_mgmt", "fx_fundraising"]].sum(axis=1)
                                - df.fx_total).where(df.fx_total.notna()).round(0)

    with pd.ExcelWriter(out / "irs990_env_seed.xlsx") as xl:
        df.to_excel(xl, sheet_name="990_panel", index=False)
    checks = {c: {"n": int(df[c].notna().sum()), "ties_within_1": int((df[c].abs() <= 1).sum())}
              for c in df if c.startswith("chk_")}
    report = {"source": "IRS 990 e-file XML via GivingTuesday data lake (public S3)",
              "ein": args.ein, "org": df.org.iloc[-1] if len(df) else None,
              "tax_years": df.tax_year.tolist(), "checks": checks}
    (out / "validation_report.json").write_text(json.dumps(report, indent=2))
    print(df.drop(columns=["object_id"]).to_string())
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
