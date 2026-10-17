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
| 5 | SEC Form ABS-EE auto-loan tapes (World Omni trusts 2017–2024) | Kaggle `denytran/10-year-automotive-loans-abs-ee` (anonymous download, 1 GB Parquet) | EDGAR ABS-EE EX-102 XML + 10-D | ✅ pulled + validated |
| 6 | City of Chicago vendor payments (checkbook) | Kaggle `chicago/chicago-payments` (2019 snapshot) | Socrata `data.cityofchicago.org` (weekly refresh) | ✅ pulled + profiled |
| 7 | India AMC monthly portfolio disclosures (SEBI-mandated, Aug-2026) | GitHub `subscriptionmanager26-png/fund-disclosures` (sparse clone) | Each AMC's website (manifests record source URLs) | ✅ pulled + parsed + validated |
| 8 | Municipal ACFR PDFs (City of Austin FY2001–FY2019) | End-of-Term 2020 web archive on public S3 (`govscape/eota-ocr`, CC0, PDFs + OCR) | Issuer websites / EMMA (EMMA ToS forbid scraping) | ✅ pulled + parsed + validated |

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

## PoC 5: ABS-EE auto-loan tapes (`poc/absee_auto.py`)

**Fetched:** 35,676,547 loan-month records, 1,148,191 loans, 86 monthly periods
(2017-02 → 2024-03) from World Omni Auto Receivables trusts' EX-102 asset-level exhibits.
Env seed `samples/absee_world_omni/absee_env_seed.xlsx` = bottom-up monthly pool surveillance
table + full monthly history of 300 sampled loans.

**Natural ground truth tested:**

| Check | Result |
|---|---|
| Loan-level: begin − principal collected − charged-off − other adj. = end | **100.0%** of 35.7M loan-months tie to the cent |
| Continuity: end(t) = begin(t+1), same asset | **99.62%** of 34.5M pairs; 129k breaks > $100; 55.7k reporting gaps > 1 month |
| Pool level vs. Form 10-D servicer report | needs EDGAR (blocked here); 10-D reports pool balance, delinquencies, cumulative net loss, so the bottom-up table is checkable |

**Traps hit (real data, not planted):**
1. `repossessedProceedsAmount` is a *component* of `recoveredAmount` (~80% of it). Summing both
   double-counts recoveries and makes net losses negative. Correct net-loss rate ≈ 0.4–0.7%
   annualized (plausible for a prime auto book); 30+ DPD ≈ 2.2–2.6%.
2. 28 records carry a `1900-01-01` null-date sentinel as the reporting period.
3. Loans drop out and reappear (55.7k gaps), and balances jump on 129k transitions. These are
   real servicing events (repurchases, modifications, trust-level reporting gaps) that a
   surveillance analyst must explain, not smooth over.
4. The Kaggle mirror pools several trusts without a deal identifier; per-deal envs should use the
   per-trust HF repos (`DenyTranDFW/<Trust_Name>_<CIK>`, 1,072 repos) or EDGAR directly.

**Workflow scope:** monthly surveillance roll-forward (strats → roll rates → CPR/CDR/severity →
reconcile to 10-D → waterfall & trigger tests from the 424B prospectus → note), repeated for
36–80 months per trust, across ~650 auto trusts (+ ~375 CMBS trusts with property-level data).

## PoC 6: City of Chicago vendor payments (checkbook)

**Fetched:** 829,738 payment vouchers, $97.5B, 53 departments, 342k vendors, 75k contracts
(Kaggle snapshot, Dec 2019; the live Socrata dataset refreshes weekly).

**Messiness observed:** pre-2018 payments are rolled up to a bare year (`"2013"`) instead of a
check date (18.5% of rows); department is missing on 78% of rows (direct vouchers, `DV`, are 71%);
97,974 rows share vendor + amount + date with another row (duplicate-payment *candidates*, most
of which are legitimate, so separating them is real audit judgment).

**Workflow scope:** fiscal-year budget-to-actual and duplicate-payment testing, reconciled to the
city's ACFR and annual appropriation ordinance (PDFs, not reachable from the sandbox).

## PoC 7: India AMC monthly portfolio workbooks (`poc/india_amc_portfolios.py`)

**Fetched:** raw month-end (31-Aug-2026) portfolio workbooks of 13 Indian AMCs (SBI, ICICI Pru,
DSP, Mirae, Franklin, Baroda BNP, UTI, PGIM, Union, Navi, JM, Old Bridge, Abakkus): `.xlsx`,
legacy `.xls`, and zips of workbooks; up to 229 scheme sheets per AMC. One generic heuristic
parser (header detection by ISIN / "% to Net Assets" / "Market value" cues) → 715 schemes.
Layout survey: `samples/india_amc/india_amc_layout_survey.xlsx`.

**Layout drift observed (raw-to-workbook burden):** header row anywhere from row 2 to row 12;
ISIN in column 0, 2, 3 or 7; % of NAV as a *percentage* at 6 AMCs and as a *fraction* at 6
(SBI uses both in the same month); values in ₹ lakh; per-scheme sheets with cryptic codes
(`T0MD09`, `FIONF`) resolved via an index sheet; UTI's layout defeats the heuristic entirely.

**Natural ground truth:** each holding's implied net assets (market value ÷ % of NAV) must equal
the scheme's Grand Total. **99.2%** of the 715 parsed schemes tie within 0.5%; per-holding
implied values agree within 0.5% for 80% of schemes (the rest is the 2-decimal rounding of % on
small positions, which an agent must recognise rather than "fix").

**Workflow scope:** see `docs/sources/funds_portfolios_pensions.md` §I (wealth-client quarterly
review + rebalance across schemes with look-through, overlap, SEBI category-rule compliance,
Regular→Direct switch with TER from AMFI and capital-gains tax). Monthly + fortnightly cadence
makes it contamination-resistant.

## PoC 8: Austin ACFR PDFs → 17-year General Fund panel (`poc/acfr_fund_balance.py`)

**Fetched:** 17 City of Austin ACFR PDFs (FY2001–FY2019, ~270 pages each) from the End-of-Term
2020 archive on S3. The discovery-phase index of that archive lists **6,203 ACFR/CAFR PDFs, 3,394
budget books, 872 single audits, 433 actuarial valuations and 167 official statements** (2020 crawl,
PDF + OCR present). The parser locates the governmental-funds *Statement of Revenues, Expenditures
and Changes in Fund Balances* in each year and extracts the General Fund column.

| Check | Result |
|---|---|
| Statement located | 15 / 16 dated years (FY2001 layout not found) |
| Within year: beginning FB + net change (incl. special items) = ending FB | **15 / 15** tie to the $1k |
| Across years: ending FB(t) = beginning FB(t+1) | **11 / 12** tie; the one break is FY2011's **restated** beginning balance (+$19.3M, "as restated, see Note 16"), a genuine, documented exception |

**Traps hit (each one broke a check until handled):** PDF text extraction splits digits
(`$ 1 30,163` = 130,163); running-header debris glued to labels (`Ye`, `No`) and draft
timestamps (`03/27 5:24p`); `--` for zero and parentheses for negatives; **special items**
(2004 hospital-district reserve payment, 2014/2019 land sales) create two "Net change" lines;
`(See Note 16)` gets read as the amount; restated opening balances.

**Workflow scope:** this is checkpoint 1 of the municipal credit review (W2 in the concept
library). The same PDFs carry the debt, pension and statistical sections; the Data.gov archive
(Harvard LIL, public S3) holds the matching Austin eCheckbook (642 MB) for checkbook-to-ACFR
reconciliation.

## PoC 3/4: N-PORT and Call Reports via Hugging Face datasets-server

Large Parquet mirrors cannot be downloaded (CDN blocked), but the datasets-server `/rows` and
`/filter` endpoints are reachable; `poc/hfds.py` wraps them. Schemas verified:

* `trader298/sec-nport`: all 29 SEC N-PORT tables (FUND_REPORTED_INFO, FUND_REPORTED_HOLDING
  145.6M rows, MONTHLY_TOTAL_RETURN, DEBT_SECURITY, DERIVATIVE_COUNTERPARTY, …), 2019Q4–2026Q2.
* `kairusama/call-report-one`: 671,000 bank-quarters, 2001Q1–2026, 224 income/supplemental
  columns, 1,442 canonical columns.

`/filter` on these multi-GB configs first returns "dataset index is loading". A background poll
is running; results will be appended here.
