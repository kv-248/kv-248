# PoC scripts

Each script pulls real data through a path reachable from a locked-down sandbox, writes a small
env seed workbook plus `validation_report.json` under `../samples/<name>/`, and checks the
source's natural ground-truth identities. Requirements: Python 3.11+, `pandas`, `pyarrow`,
`openpyxl`, `duckdb`, `pdfplumber`, `xlrd`. Run with `python3 -I` from this directory.

| Script | Source | Data path | Command |
|---|---|---|---|
| `pudl_ferc1.py` | FERC Form 1 (utilities) | PUDL public S3 (auto-download) | `python3 -I pudl_ferc1.py --utility "Idaho Power" --out ../samples/ferc1_idaho_power` |
| `irs990.py` | IRS 990 XML (nonprofits) | GivingTuesday public S3 (auto-download; index read by HTTP range) | `python3 -I irs990.py --ein 200049703 --out ../samples/irs990_wikimedia` |
| `absee_auto.py` | ABS-EE auto-loan tapes | Kaggle `denytran/10-year-automotive-loans-abs-ee` (download + unzip first) | `python3 -I absee_auto.py --data <unzipped dir> --out ../samples/absee_world_omni` |
| `india_amc_portfolios.py` | India AMC monthly portfolios | `git clone --filter=blob:none --sparse https://github.com/subscriptionmanager26-png/fund-disclosures` then `git sparse-checkout set data/staging/python/amcs` | `python3 -I india_amc_portfolios.py --amcs <repo>/data/staging/python/amcs --out ../samples/india_amc` |
| `acfr_fund_balance.py` | Austin ACFR PDFs | End-of-Term archive S3 `govscape/eota-ocr/pdfs/<id>.pdf` (ids in `samples/acfr_austin/source_manifest.csv`; save as `austin_cafr_YYYY.pdf`). Full finance-PDF index of the archive: `samples/govtext_finance_pdf_index.parquet` | `python3 -I acfr_fund_balance.py --pdfs <dir> --out ../samples/acfr_austin` |
| `hfds.py` | helper | HF datasets-server `/rows`, `/filter` (N-PORT, Call Reports) | library |
| `httprange.py` | helper | seekable HTTP-range file for remote Parquet | library |

Large raw downloads are not committed; `samples/` holds only small seeds (≤2.5 MB each).
