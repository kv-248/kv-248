# Proof-of-concept pulls: what we actually fetched and verified

All pulls ran inside the sandbox on 2026-10-17. **Network constraint:** the sandbox's egress policy
blocks the primary government hosts (`sec.gov`, `data.sec.gov`, `efts.sec.gov`, `emma.msrb.org`,
`api.usaspending.gov`, `banks.data.fdic.gov`, `ffiec.gov`, `fred.stlouisfed.org`,
`fiscaldata.treasury.gov`, `amfiindia.com`, `bseindia.com`, `nseindia.com`,
Companies House, `filings.xbrl.org`, ...) and the Hugging Face file CDN (`*.cdn.hf.co`,
`*.xethub.hf.co`). Reachable: `huggingface.co` API, `datasets-server.huggingface.co`,
`raw.githubusercontent.com`/GitHub, public **S3** buckets, `kaggle.com`, `arxiv.org`.

So each PoC uses the best reachable path. The "primary path" column says how a production
scraper would fetch it once those hosts are allowlisted (see
https://code.claude.com/docs/en/cloud-environments#network-access).

| # | Source | Reachable path used | Primary path (production) | Status |
|---|---|---|---|---|
| 1 | FERC Form 1 (utility regulatory accounts) | Catalyst PUDL public S3 `pudl.catalyst.coop/stable/*.parquet` | FERC eCollection XBRL (2021+) / VFP DBF (1994–2020) | ✅ pulled + validated |
| 2 | IRS Form 990 e-file XML (nonprofits) | GivingTuesday public S3 `gt990datalake-rawdata` (Parquet index via HTTP range + raw XML) | IRS bulk XML zips | ✅ pulled + validated |
| 3 | SEC Form N-PORT (monthly fund holdings) | HF mirror `trader298/sec-nport` (CC0) via datasets-server `/filter` | SEC N-PORT quarterly data sets | ⏳ server-side index warming; schema verified |
| 4 | FFIEC Call Reports (banks, 2001–2026 quarterly) | HF mirror `kairusama/call-report-one` (CC0) via datasets-server | FFIEC CDR bulk | ⏳ schema verified (224–1,442 cols) |

---

## PoC 1: FERC Form 1 via PUDL (`poc/pudl_ferc1.py`)

**Fetched:** schedules 204 (plant in service), 110 (balance sheet), 114 (income statement),
118 (retained earnings), 219 (accumulated depreciation changes), 375 utilities, 1994–2025.
Sample env seed for **Idaho Power Company (32 years)** in
`samples/ferc1_idaho_power/ferc1_env_seed.xlsx`.

**Natural ground truth tested (plant-in-service roll-forward):**

| Check | Universe (375 utilities) | Idaho Power |
|---|---|---|
| Within-year: begin + additions + retirements + adjustments + transfers = end | **99.72%** of 226,738 rows tie | **100%** of 1,762 |
| Across-year: end(t) = begin(t+1) | **98.82%** of 211,729 pairs tie | **99.7%**; 4 breaks > $1k |

**Trap observed (real, not planted):** FERC reports *retirements as negative numbers*. With the
"textbook" sign (`− retirements`) only 43% of rows tie. That is exactly the kind of convention a
model must infer from the data, and the ~1,850 cross-year breaks are real restatements and
reclassifications that a strong agent should find and explain.

**Workflow scope:** rate-base roll-forward → depreciation reserve → revenue requirement → peer
O&M benchmarking; 30 years × 375 utilities supports both deep and broad envs. Joins to EIA
(plant-level), SEC 10-K (parent holding companies, via PUDL's `core_sec10k__*` association tables).

## PoC 2: IRS Form 990 via GivingTuesday data lake (`poc/irs990.py`)

**Fetched:** Parquet index (6,245,445 returns; we read only 8 columns via HTTP range requests,
no full download) → all Form 990 returns for **Wikimedia Foundation (EIN 20-0049703),
tax years 2009–2022** → raw XML (in `samples/irs990_wikimedia/xml/`) → parsed panel
`irs990_env_seed.xlsx`.

**Natural ground truth tested:**

| Check | Result |
|---|---|
| Part XI net-asset reconciliation (lines 3–9 = EOY − BOY), 2013+ schema | 10/10 years tie within $1 |
| Net-asset roll-forward EOY(t) = BOY(t+1) | 13/13 year pairs tie within $1 |
| Part IX functional expenses: program + management + fundraising = total | 14/14 |

**Traps hit while building the PoC (the same ones an agent hits):**
1. *Same element names recur in schedules.* Grabbing the first match in the document picked up a
   Schedule value and broke the reconciliation. The parse must be scoped to the main form.
2. *Schema drift.* 14 returns span 13 schema versions; the IRS renamed elements in 2013
   (`TotalRevenueCurrentYear` → `CYTotalRevenueAmt`), and Part XI reconciliation does not exist
   before 2013. A naive parser silently returns NaN (and a naive check counts NaN as a tie).
3. *Sign ambiguity.* Part XI line 7 (investment expenses) is entered with inconsistent signs
   across filers.

**Workflow scope:** nonprofit financial health review over 10+ years (program ratio, months of
reserves, revenue concentration, executive comp from Schedule J, grants paid from Schedule I),
universe screens across 6M returns, and joins to Single Audit (Federal Audit Clearinghouse, by EIN)
and to grant-maker 990-PF Schedule I (grants paid ↔ grants received).

## PoC 3/4: N-PORT and Call Reports via Hugging Face datasets-server

Large Parquet mirrors cannot be downloaded (CDN blocked), but the datasets-server `/rows` and
`/filter` endpoints are reachable; `poc/hfds.py` wraps them. Schemas verified:

* `trader298/sec-nport`: all 29 SEC N-PORT tables (FUND_REPORTED_INFO, FUND_REPORTED_HOLDING
  145.6M rows, MONTHLY_TOTAL_RETURN, DEBT_SECURITY, DERIVATIVE_COUNTERPARTY, …), 2019Q4–2026Q2.
* `kairusama/call-report-one`: 671,000 bank-quarters, 2001Q1–2026, 224 income/supplemental
  columns, 1,442 canonical columns.

`/filter` on these multi-GB configs first returns "dataset index is loading". A background poll
is running; results will be appended here.
