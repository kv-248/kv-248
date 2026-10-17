"""PoC: municipal ACFR PDFs -> multi-year General Fund panel with roll-forward checks.

Real source: City of Austin, TX Comprehensive Annual Financial Reports (FY2001-FY2019), as
captured by the 2020 End-of-Term web archive and published with OCR on public S3 (CC0):
  https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/pdfs/<id>.pdf
(index of ~11k finance PDFs built in the discovery phase: 6,203 ACFRs, 3,394 budget books,
872 single audits, 433 actuarial valuations, 167 official statements).

What this proves: the governmental-funds "Statement of Revenues, Expenditures, and Changes in
Fund Balances" can be located and parsed across ~20 years of layout drift, and it carries
natural ground truth:
  * within year:  beginning fund balance + net change == ending fund balance
  * across years: ending(t) == beginning(t+1)   (breaks = restatements, explained in the notes)

Usage: python3 -I acfr_fund_balance.py --pdfs <dir of austin_cafr_YYYY.pdf> --out ../samples/acfr_austin
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

import pandas as pd
import pdfplumber

ROWS = {
    "total_revenues": r"^total revenues",
    "total_expenditures": r"^total expenditures",
    "net_change": r"^net change in fund balances?",
    "fb_beginning": r"^fund balances?,? (at )?beginning|^fund balances? - beginning",
    "fb_end": r"^fund balances?,? (at )?end|^fund balances? - end",
}
NUM = re.compile(r"\(?-?\d[\d,]*\)?|--")


def numbers(line: str) -> list[float]:
    """Numbers on a statement line, handling '(1,234)' negatives, '--' zeros and digits that
    PDF text extraction split apart ('$ 1 30,163' == 130,163)."""
    toks = NUM.findall(line.replace("$", " "))
    merged: list[str] = []
    for t in toks:
        if (merged and re.fullmatch(r"\(?\d{1,2}", merged[-1]) and re.match(r"\d{1,2},\d{3}", t)
                and len(merged[-1].lstrip("(")) + len(t.split(",")[0]) <= 3):
            merged[-1] = merged[-1] + t
        else:
            merged.append(t)
    out = []
    for t in merged:
        if t == "--":
            out.append(0.0)
            continue
        neg = t.startswith("(") or t.startswith("-")
        v = float(t.strip("()-").replace(",", "") or 0)
        out.append(-v if neg else v)
    return out


def find_statement(pdf: pdfplumber.PDF) -> tuple[int, str] | None:
    for i, page in enumerate(pdf.pages[:150]):
        t = page.extract_text() or ""
        head = " ".join(t.splitlines()[:6]).lower()
        if ("changes in fund balance" in head and "governmental funds" in head
                and "general" in t.lower() and re.search(r"beginning", t, re.I)):
            return i + 1, t
    return None


def parse_year(path: pathlib.Path) -> dict:
    with pdfplumber.open(path) as pdf:
        hit = find_statement(pdf)
    if hit is None:
        return {"file": path.name, "status": "statement_not_found"}
    page, text = hit
    rec: dict = {"file": path.name, "page": page, "status": "ok", "special_items": 0.0,
                 "restated_beginning": False}
    for line in text.splitlines():
        # Strip running-header debris such as "Ye"/"No" glued to the left margin.
        clean = re.sub(r"^[A-Za-z]{0,2}(?=[A-Z][a-z])", "", line.strip())
        # "(See Note 16)" would otherwise be read as the General Fund amount.
        nums = numbers(re.sub(r"\(see notes? [\d, and]+\)", " ", clean, flags=re.I))
        if not nums:
            continue
        if re.match(r"special items?\b", clean, re.I):
            rec["special_items"] += nums[0]
        for key, pat in ROWS.items():
            # "Net change" appears twice when special items exist; the last one is final.
            if re.search(pat, clean, re.I) and (key not in rec or key == "net_change"):
                rec[key] = nums[0]  # first numeric column = General Fund
                if key == "fb_beginning" and "restated" in clean.lower():
                    rec["restated_beginning"] = True
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfs", required=True)
    ap.add_argument("--out", default="../samples/acfr_austin")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(pathlib.Path(args.pdfs).glob("austin_cafr_*.pdf")):
        year = re.search(r"(\d{4})", p.stem)
        if not year:
            continue  # the undated "latest" copy duplicates one of the dated years
        rows.append({"fiscal_year": int(year.group(1)), **parse_year(p)})
    df = pd.DataFrame(rows).sort_values("fiscal_year").reset_index(drop=True)
    df["chk_within_year"] = df.fb_beginning + df.net_change - df.fb_end
    nxt = df.set_index("fiscal_year").fb_beginning
    df["chk_next_year_beginning"] = [
        (r.fb_end - nxt.get(r.fiscal_year + 1)) if (r.fiscal_year + 1) in nxt.index else None
        for r in df.itertuples()]
    df.to_excel(out / "acfr_general_fund_panel.xlsx", index=False)
    ok = df[df.status == "ok"]
    report = {
        "source": "City of Austin ACFRs via End-of-Term 2020 archive PDFs (govscape/eota-ocr, CC0)",
        "years_found": int(len(df)), "statement_located": int(len(ok)),
        "within_year_ties": int((ok.chk_within_year.abs() <= 1).sum()),
        "within_year_checked": int(ok.chk_within_year.notna().sum()),
        "across_year_ties": int((pd.to_numeric(ok.chk_next_year_beginning).abs() <= 1).sum()),
        "across_year_checked": int(pd.to_numeric(ok.chk_next_year_beginning).notna().sum()),
    }
    (out / "validation_report.json").write_text(json.dumps(report, indent=2))
    pd.set_option("display.width", 200)
    print(df.drop(columns=["file"]).to_string())
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
