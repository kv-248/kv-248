"""PoC: Indian mutual-fund monthly portfolio disclosures (SEBI-mandated, one workbook per AMC).

Real source: each Asset Management Company publishes month-end (and fortnightly for debt
schemes) portfolio workbooks on its own website, in its own layout. Reachable mirror: GitHub
`subscriptionmanager26-png/fund-disclosures` (raw Aug-2026 files for 13 AMCs, with download
manifests pointing at the AMC URLs).

What this proves: the raw-to-workbook acquisition step is genuinely hard (layout per AMC,
header row position, % vs. fraction, Rs. lakh units, zips, .xls), yet every scheme carries a
natural checksum: each holding's implied net assets  MV_i / pct_i  must agree across the scheme
and with the scheme's Grand Total / Net Assets row.

Usage: python3 -I india_amc_portfolios.py --amcs <.../amcs> --month 2026-08 --out ../samples/india_amc
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import tempfile
import zipfile

import pandas as pd

ISIN = re.compile(r"^IN[A-Z0-9]{10}$")
PCT_HDR = re.compile(r"%\s*(to|of)?\s*(net\s*assets|nav|aum)", re.I)
MV_HDR = re.compile(r"market.*value|fair\s*value", re.I)
TOTAL_ROW = re.compile(r"^(grand\s*total|net\s*assets|total\s*net\s*assets)", re.I)


def find_header(df: pd.DataFrame) -> tuple[int, dict] | None:
    for i in range(min(len(df), 40)):
        cells = [str(c) for c in df.iloc[i].tolist()]
        cols = {}
        for j, c in enumerate(cells):
            if "isin" in c.lower() and "isin" not in cols:
                cols["isin"] = j
            elif PCT_HDR.search(c) and "pct" not in cols:
                cols["pct"] = j
            elif MV_HDR.search(c) and "mv" not in cols:
                cols["mv"] = j
            elif re.search(r"name\s*of|instrument|issuer", c, re.I) and "name" not in cols:
                cols["name"] = j
        if {"isin", "pct", "mv"} <= cols.keys():
            return i, cols
    return None


def parse_sheet(df: pd.DataFrame) -> dict | None:
    hdr = find_header(df)
    if hdr is None:
        return None
    h, cols = hdr
    body = df.iloc[h + 1:]
    isin = body.iloc[:, cols["isin"]].astype(str).str.strip()
    hold = body[isin.str.match(ISIN)].copy()
    if hold.empty:
        return None
    mv = pd.to_numeric(hold.iloc[:, cols["mv"]], errors="coerce")
    pct = pd.to_numeric(hold.iloc[:, cols["pct"]], errors="coerce")
    # Grand total / net assets row: first column cell (any of the first 3) matching TOTAL_ROW.
    total_mv = total_pct = None
    for _, row in body.iterrows():
        label = " ".join(str(x) for x in row.iloc[:3].tolist() if pd.notna(x))
        if TOTAL_ROW.search(label.strip()):
            total_mv = pd.to_numeric(row.iloc[cols["mv"]], errors="coerce")
            total_pct = pd.to_numeric(row.iloc[cols["pct"]], errors="coerce")
            break
    scale = 100.0 if (total_pct is not None and pd.notna(total_pct) and total_pct <= 1.5) \
        or pct.max() <= 1.0 else 1.0
    pct_frac = pct * scale / 100.0
    ok = (mv > 0) & (pct_frac > 0.001)
    implied = (mv[ok] / pct_frac[ok])
    med = float(implied.median()) if len(implied) else float("nan")
    return {
        "header_row": h, "isin_col": cols["isin"], "pct_scale": "fraction" if scale == 100 else "percent",
        "n_holdings": int(len(hold)), "sum_pct_holdings": round(float(pct_frac.sum() * 100), 3),
        "implied_net_assets_median": round(med, 2),
        "implied_dispersion_pct": round(float((implied / med - 1).abs().quantile(0.9) * 100), 3)
        if len(implied) else None,
        "grand_total_mv": None if total_mv is None or pd.isna(total_mv) else round(float(total_mv), 2),
        "scheme_title": str(df.iloc[:3, :3].stack().astype(str).iloc[0])[:90] if df.iloc[:3, :3].notna().any().any() else None,
    }


def workbooks(folder: pathlib.Path, tmp: pathlib.Path):
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() in (".xls", ".xlsx"):
            yield f.name, f
        elif f.suffix.lower() == ".zip":
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    if n.lower().endswith((".xls", ".xlsx")):
                        p = tmp / pathlib.Path(n).name
                        p.write_bytes(z.read(n))
                        yield f"{f.name}::{n}", p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--amcs", required=True)
    ap.add_argument("--month", default="2026-08")
    ap.add_argument("--out", default="../samples/india_amc")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for amc in sorted(pathlib.Path(args.amcs).iterdir()):
            folder = amc / args.month
            if not folder.is_dir():
                continue
            for name, path in workbooks(folder, pathlib.Path(td)):
                try:
                    xl = pd.ExcelFile(path)
                except Exception as e:  # corrupt / mislabelled files are part of the mess
                    rows.append({"amc": amc.name, "file": name, "error": type(e).__name__})
                    continue
                for sh in xl.sheet_names:
                    try:
                        r = parse_sheet(xl.parse(sh, header=None))
                    except Exception as e:
                        r = {"error": type(e).__name__}
                    if r:
                        rows.append({"amc": amc.name, "file": name, "sheet": sh, **r})
    df = pd.DataFrame(rows)
    ok = df[df.get("error").isna()] if "error" in df else df
    ok = ok.assign(
        implied_consistent=ok.implied_dispersion_pct < 0.5,
        ties_grand_total=(ok.grand_total_mv.notna()
                          & ((ok.implied_net_assets_median / ok.grand_total_mv - 1).abs() < 0.005)))
    by_amc = ok.groupby("amc").agg(
        schemes=("sheet", "count"), header_rows=("header_row", lambda s: sorted(set(s))),
        isin_cols=("isin_col", lambda s: sorted(set(s))),
        pct_scales=("pct_scale", lambda s: sorted(set(s))),
        implied_consistent=("implied_consistent", "mean"),
        ties_grand_total=("ties_grand_total", "mean"))
    with pd.ExcelWriter(out / "india_amc_layout_survey.xlsx") as xl:
        by_amc.to_excel(xl, sheet_name="by_amc")
        df.to_excel(xl, sheet_name="by_scheme", index=False)
    report = {
        "source": "SEBI monthly portfolio disclosures (AMC websites) via GitHub "
                  "subscriptionmanager26-png/fund-disclosures",
        "month": args.month, "amcs": int(df.amc.nunique()), "schemes_parsed": int(len(ok)),
        "files_or_sheets_failed": int(df["error"].notna().sum()) if "error" in df else 0,
        "share_implied_net_assets_consistent_<0.5%": round(float(ok.implied_consistent.mean()), 3),
        "share_tie_to_grand_total_<0.5%": round(float(ok.ties_grand_total.mean()), 3),
    }
    (out / "validation_report.json").write_text(json.dumps(report, indent=2))
    print(by_amc.to_string())
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
