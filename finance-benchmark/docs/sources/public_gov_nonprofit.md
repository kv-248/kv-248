# Public sector / government / municipal / nonprofit finance — source survey

Prepared 2026-10-17 for the long-horizon spreadsheet finance-agent benchmark.

**How to read this file**
- **VERIFIED**: tested from this sandbox with curl, git, or S3 listing on 2026-10-17. The exact command or URL is given.
- **unverified**: taken from web search snippets or prior knowledge, not tested here.
- I did not fetch any `.gov`, `.gov.uk`, `.gov.in`, `europa.eu`, `worldbank.org`, `imf.org`, or Socrata host. Every one of them is DNS- or proxy-blocked here. Details about those portals come from search results.

---

## 0. Access reality check (VERIFIED in this sandbox)

| Channel | Status here | Notes |
|---|---|---|
| `huggingface.co` API and small (non-LFS) files | OK | `/api/datasets?search=` works, and READMEs plus small files download via `resolve-cache`. |
| HF large-file (Xet/LFS) downloads | **BLOCKED** | `resolve/main/*.parquet` redirects to `us.aws.cdn.hf.co`. The proxy answers 403 to CONNECT for that host. Every multi-MB HF parquet fails here. **Check whether your benchmark container allows `us.aws.cdn.hf.co`, `cas-bridge.xethub.hf.co` and `cdn-lfs*.hf.co`**, or HF mirrors are metadata-only. |
| `github.com` git clone / `git ls-remote` | OK | e.g. `git clone --depth 1 --filter=blob:none https://github.com/Devon-County-Council/spending` |
| `raw.githubusercontent.com` | OK | |
| GitHub REST API (search) | BLOCKED | Returns "sessions are bound to their configured repositories". Repo discovery has to go through web search plus `git ls-remote`. |
| Kaggle API, anonymous | **OK** | `https://www.kaggle.com/api/v1/datasets/download/{owner}/{slug}` returns 302 to a signed `storage.googleapis.com` URL, which is reachable. Range download tested on `tfshiloh/csv-version-missouri-checkbook-fy2010fy2017`. The search endpoint `api/v1/datasets/list?search=` also works without auth. |
| AWS S3 public buckets | **OK** | `gt990datalake-rawdata.s3.amazonaws.com` (IRS 990) and `s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/...` (Harvard LIL data.gov archive, GovText/End-of-Term PDFs). |
| `files.usaspending.gov`, `api.fiscaldata.treasury.gov`, `emma.msrb.org`, all `.gov`, Socrata, `data.gov.uk`, `cag.gov.in`, `openbudgetsindia.org`, `datacatalog.worldbank.org`, `data.imf.org`, `kohesio.ec.europa.eu`, `archive.org`, `zenodo.org`, `source.coop` web UI | BLOCKED | The source.coop *S3 endpoint* works. Only the web UI is blocked. |

### Two mirrors that change what is feasible (both VERIFIED)

**A. Harvard LIL "gov-data": the full Data.gov archive on S3 (about 311,820 datasets, snapshots 2020 to 2025)**
- Bucket: `https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/harvard-lil/gov-data/`
- Index: `metadata.csv.zip` (25 MB, 311,820 rows: name, organization, title, date, paths).
- Data: `collections/data_gov/<slug>/v1.zip` is a BagIt zip. `metadata/data_gov/<slug>/v1.json` has `zip_entries` with `data_offset` and `compress_size`, so a single CSV can be pulled with an HTTP Range request and raw-deflate. Tested on the Oklahoma GL.
- Cities, counties and states federate their Socrata catalogs into data.gov, so many checkbook, payroll and budget CSVs sit here **as full `rows.csv` snapshots**.
- The archive is point-in-time (mostly 2023 to 2024 captures). That makes it good for frozen environments, but it is not live.

**B. GovText / End-of-Term Archive PDFs on S3 (CC0): 9.02M U.S. government PDFs from the 2020 crawl, with olmOCR text**
- `https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/` contains `pdfs/<pdf_id>.pdf`, `ocr_text/<pdf_id>.tar.gz`, `extracted_text/`, `ocr_metadata/`, and `cdx/complete_cdx.parquet` (34.3M capture rows: url, filename, crawl_date, digest = pdf_id).
- I scanned the CDX URL column. **29,678 captures have URLs matching CAFR/ACFR/"comprehensive annual financial", single audit, official statement, actuarial valuation, budget book or adopted budget.**
  - Top hosts: www.seattle.gov 1,604; doa.virginia.gov 1,156; bernco.gov 772; doa.alaska.gov 644; sandiegocounty.gov 538; houstontx.gov 433; ventura.org 425; osa.sc.gov 409; auditors.nebraska.gov 364+297; ofm.wa.gov 337+294; riversideca.gov 328; pima.gov 299; open.omb.delaware.gov 294; nj.gov 251; budget.pa.gov 226; sco.ca.gov 198; finance.ky.gov 190; honolulu.gov 178; nashville.gov 174; comptroller.nyc.gov 153; auditor.illinois.gov 137.
  - Rough keyword counts across all crawls: ACFR/CAFR about 17.9k, budget about 7.8k, single audit about 2.5k, actuarial about 1.3k, official statement about 0.7k.
  - The PDFs themselves exist only for the 2020 crawl. **EOT-2020 subset (PDF + OCR actually present): 13,258 captures and 11,208 distinct PDFs:**
    - ACFR/CAFR/PAFR 6,203
    - budget books / adopted budgets 3,394
    - single audits 872
    - actuarial valuations 433
    - official statements 167
    - federal agency financial reports 140
  - Top ACFR hosts (distinct PDFs): doa.virginia.gov 307, pima.gov 257, doa.alaska.gov 202, bernco.gov 193, sandiegocounty.gov 188, auditors.nebraska.gov 171, ventura.org 166, riversideca.gov 164, houstontx.gov 145, ofm.wa.gov 95, osa.sc.gov 87, cg.sc.gov 80, chattanooga.gov 76, comptroller.texas.gov 71, calaters.ca.gov 71, archives.obm.ohio.gov 61, sco.ca.gov 38, pittsburghpa 37, opers.ok.gov 34, comptroller.nyc.gov 34.
  - HEAD-tested `pdfs/<id>.pdf` and `ocr_text/<id>.tar.gz` for 4 ACFRs; all returned 200. Examples:
    - `23XHJWGNJF33TSUBFMDMECC4DA5DVJEI` (Davis County UT 2018 CAFR)
    - `4HMM3AJMFMJW7VHSEIAW5YYNIWRPD76U` (Pima County CAFR 2018)
    - `SZLGPDLYNNQ4AQS7WBQIIWR7NT3N24PO` (San Diego County FY18-19)
    - `UV7HC6IYQZBXRONMCF32PEM23WV3K6LQ` (Round Rock TX FY2019 CAFR)
  - **My extracted index** (url, WARC filename, digest = pdf_id, crawl_date; 29,741 rows): `/tmp/claude-0/-home-user-kv-248/3c3859ef-413f-59c4-8ab3-825f82564917/scratchpad/govtext_fin.parquet`
  - Caveat: the URL-keyword filter misses ACFRs with non-descriptive filenames, and the corpus is frozen at the 2020 crawl, so it holds FY2019 and earlier reports. Contamination risk is high for well-known cities, lower for small entities.
- This is the only bulk, CC0, reachable source of **real ACFR / budget-book / actuarial-valuation PDFs** I found. It includes older scanned reports, with olmOCR text that can serve as a "reference OCR".

---

## 1. MSRB EMMA (official statements, continuing disclosures, event notices, trade data)

1. **What / URL**: Electronic Municipal Market Access, https://emma.msrb.org. It is the official repository for about 1M+ outstanding muni CUSIPs (unverified count) and holds:
   - Official Statements (OS / POS)
   - Continuing disclosures: annual financial information (usually the ACFR), operating data, and the 17 Rule 15c2-12 event notices (rating changes, defaults, draws on reserves, bank loans)
   - Trade history (RTRS) and yields
2. **Access / ToS**: web UI only. **The ToS prohibit scraping.** The search summary of the MSRB terms says users may not use "data mining, crawling, 'scraping', robot or similar automated ... method to access or copy the site, or to systematically download or store Content", and may not "screen scrape or otherwise programmatically collect, store, transmit Content" (https://emma.msrb.org/tradedata terms; msrb.org/node/13517, last updated Jan 2026).
   - Bulk data is sold as subscriptions: Primary Market and Continuing Disclosure subscription feeds, plus academic RTRS through MSRB/WRDS (unverified pricing).
   - Host is blocked here. **Practical route**: hand-curate a few dozen OS/ACFR PDFs per environment from *issuer* websites (most issuers post their own OS and ACFR, e.g. comptroller.nyc.gov, state treasurer IR pages, BondLink IR sites), or from GovText (§0B) where captured. Cite the CUSIP but do not redistribute EMMA content wholesale.
3. **Formats / messiness**:
   - Searchable PDFs, about 150–600 pages each.
   - Older or small-issuer filings are often scanned. Continuing-disclosure filings are frequently an ACFR *plus* separate "operating data" tables.
   - Debt service schedules are printed tables, often split across pages with footnoted refunding adjustments.
4. **Temporal depth / refresh**: about 2009–present (some earlier OS). New filings arrive daily, so a freshly issued OS after the model cutoff is contamination-resistant.
5. **Breadth**: about 50k issuers (unverified), from states to tiny water districts.
6. **Join keys**:
   - CUSIP-6 (issuer) and CUSIP-9 (maturity)
   - Issuer name
   - Obligor EIN for conduit nonprofit hospital/university deals, which links to the 990 (§15)
   - Census government ID only via manual crosswalk
7. **Natural ground truth**:
   - OS debt-service schedule (principal + interest by year) vs. the ACFR long-term-debt note maturity table (next fiscal year) and vs. the debt-service fund expenditures in the following ACFR.
   - OS "sources & uses" vs. ACFR capital projects fund "proceeds of bonds" and premium.
   - Continuing-disclosure operating-data tables (top taxpayers, tax collection rates) vs. the ACFR statistical section.
   - Coverage ratio stated in the OS vs. a recomputation from revenue-fund statements.
   - Event notices (downgrades) as labels for a credit-deterioration task.
8. **Benchmark use**: none found. Searches for municipal/ACFR/OS LLM benchmarks returned only corporate-filing benchmarks (FinanceBench, Fin-RATE, EDINET-Bench).
9. **Mirrors**: none on HF, GitHub or Kaggle (searched HF for "emma", "msrb", "municipal bond"). Kaggle has only `federalreserve/bond-buyer-go-20-bond-municipal-bond-index` (index level, not documents). Issuer-site PDFs appear in GovText (about 689 URLs containing "official statement" across crawls; 167 distinct PDFs present in EOT-2020).
10. **Workflows**:
   - **(a) Municipal credit analyst: "New-money GO issue credit review" (8–15 h).**
     1. Ingest a POS and three prior ACFRs; build a 10-year operating spreadsheet: governmental funds revenues/expenditures, GF fund balance as % of expenditures. *Checkpoint*: fund-balance roll-forward ties to the ACFR (beginning + net change = ending) every year.
     2. Rebuild aggregate debt service after the new issue: existing schedule from the ACFR debt note plus the new schedule from the POS. *Checkpoint*: year-1 P+I equals the POS table.
     3. Compute debt burden ratios: net direct debt per capita, % of full value, 10-year payout. *Checkpoint*: compare with the OS's own "debt statement".
     4. Compute pension/OPEB burden: ADC vs. actual contributions, NPL % of covered payroll, from RSI schedules.
     5. Run a stress scenario (−10% sales tax) for coverage and fund balance.
     6. Write a 2-page credit memo with rating-factor scoring along the Moody's US local government methodology dimensions (judge-graded).
   - **(b) Revenue-bond surveillance analyst (water/sewer enterprise).**
     - From the continuing disclosure plus the ACFR enterprise fund, compute net revenues under the bond resolution definition, which differs from GAAP: exclude depreciation, add back pension non-cash, and move transfers.
     - Recompute debt service coverage and compare with the issuer-reported covenant DSCR. *Checkpoint*: within $1k.
     - Then compute days cash on hand, a rate-increase sensitivity, and flag an event-notice need.

## 2. ACFR / CAFR PDFs (cities, counties, states, special districts, pension systems)

1. **What**: GASB-basis audited Annual Comprehensive Financial Reports. Sections:
   - MD&A
   - Government-wide statements (accrual)
   - Fund statements (modified accrual)
   - Reconciliations between the two (built into GASB 34 — a gift for verifiability)
   - Notes
   - RSI: budgetary comparison schedules, pension/OPEB schedules
   - Statistical section: 10-year trends
2. **Access**:
   - Issuer websites (finance / comptroller / auditor pages), state comptroller collections (e.g. CA SCO, Nebraska APA, WA OFM, SC OSA), and EMMA continuing disclosures (ToS-restricted).
   - **Reachable bulk source: GovText S3 (§0B), CC0.**
   - The Harvard LIL data.gov archive has a few, e.g. `comptroller-comprehensive-annual-financial-report-cafr` (Cook County) and `pola-finance-annual-financial-report-cafr-fy12-fy13`, mostly as links rather than PDFs (unverified per slug).
   - HF: `gnovoa26/cafr_images` (126 PNGs of single statement pages for about 25 cities, FY2020–2024, no license) is a tiny sample only.
3. **Formats / messiness**:
   - Native PDF for most post-2005 reports.
   - Scanned PDFs for small governments and older years.
   - Multi-column fund statements with 5–15 major funds; parenthesized negatives; "restated" beginning balances (GASB 87/96 implementations); component units.
   - Naming: CAFR renamed ACFR in 2021, which breaks keyword search.
4. **Depth / cadence**: annual, published 6–12 months after FYE; many small governments are late. Statistical sections give 10 years in one PDF.
5. **Breadth**: about 90k US local governments (Census of Governments 2022 count about 90,800, unverified). Only about 30–40k produce GAAP ACFRs (unverified).
6. **Join keys**: no universal ID. Crosswalk via Census Government ID / `FIPS`, EMMA CUSIP-6, FAC UEI/EIN (single audit), state comptroller entity IDs.
7. **Natural ground truth (strong; GASB builds it in)**:
   - Fund balance sheet vs. statement of net position reconciliation.
   - Fund operating statement vs. statement of activities reconciliation.
   - Budgetary comparison schedule (original budget, final budget, actual on budgetary basis, variance) vs. GAAP fund statement, with a basis-difference reconciliation note.
   - Capital asset rollforward note (beginning + additions − disposals = ending), and the same rollforward for long-term debt.
   - Pension NPL = TPL − FNP.
   - The 10-year statistical tables must match the prior 9 ACFRs, which is a cross-year consistency check.
   - Cross-source: ACFR GF expenditures vs. checkbook totals (§3), vs. the Census ASSLGF unit file (§8), vs. the CA SCO FTR (§6).
8. **Benchmark use**: none found for ACFRs specifically.
9. **Mirrors**: GovText S3 (VERIFIED, CC0; 6,203 distinct ACFR/CAFR/PAFR PDFs in EOT-2020, with OCR); `gnovoa26/cafr_images` (HF, verified listing, files behind the blocked CDN). Kaggle `sumukha21/acfr-dataset` is unrelated (an "ACFR" robotics dataset).
10. **Workflows**:
   - **(a) Auditor / state oversight analyst: "Tie-out and analytical review of a county ACFR."**
     1. Extract the governmental fund statements and recompute the GASB 34 reconciliations. *Checkpoint*: zero residual.
     2. Roll forward capital assets and long-term debt.
     3. Rebuild the budgetary comparison from budget ordinance data (§5) and actuals.
     4. Compute variance and over-expenditure by department (legal level of control).
     5. Reconcile pension contributions in RSI to payroll × contribution rate (§4).
     6. Draft findings: material variances, possible noncompliance.
   - **(b) Municipal analyst: "10-year fiscal trend and peer benchmarking."**
     - Pull statistical sections from 3 ACFRs (30 years overlapping) for 5 peer cities.
     - Normalize to per-capita, real dollars with CPI.
     - Compute fund balance, fixed-cost ratio (debt service + pension + OPEB / governmental expenditures), and revenue diversification (HHI).
     - Cross-check against Census ASSLGF.
     - Rank peers and write a memo.

## 3. Open checkbooks / vendor payments / general ledgers (transaction level)

Entries marked LIL are inside the Harvard LIL S3 archive (§0A). Slugs below are exact LIL slugs.

| Dataset | Mirror (exact) | Size / range |
|---|---|---|
| **State of Oklahoma General Ledger** (PeopleSoft chartfields: BUSINESS_UNIT, LEDGER, FISCAL_YEAR, ACCOUNTING_PERIOD, FUND_CODE, CLASS_FLD, DEPTID, ACCOUNT, PROGRAM_CODE, BUDGET_REF, PROJECT_ID, SUM(POSTED_TOTAL_AMT), plus revenue-source classifications) | LIL `general-ledger` (State of Oklahoma; captured 2024-09-27) | 15 quarterly CSVs FY22 Q1 – FY25 Q1, about 2.0 GB uncompressed. VERIFIED: header read via Range request. FY24 Q4: 373k rows, 170 business units (agencies), 31 fund codes, periods 10–12, LEDGER = ACTUALS. |
| **State of Oklahoma Vendor Payments** FY2008–FY2019+ | LIL `state-of-oklahoma-vendor-payments-fiscal-year-2019-6704f` (and `-2008-86d66`, `-2010-eda9a`, `-2016-203fa`, `-2018-bd95b`, ...) | Quarterly CSVs, about 100 MB per quarter (VERIFIED for FY2019). |
| State of Oklahoma Payroll 2011–FY2022 | LIL `state-of-oklahoma-payroll-2011`, `...-2016`, `...-2017`, `...-2018-2720e`, `...-fiscal-year-2021-6454c`, `...-fiscal-year-2022` | listing VERIFIED |
| Oklahoma "Debt Service and Fund Information" | LIL `debt-service-and-fund-information` | small CSV (3.6 KB) |
| **Checkbook NYC** (spending, contracts, payroll, budget, revenue; API at checkbooknyc.com) | LIL `checkbook-nyc-2-0` holds only HTML/metadata, **no data**. Code: `github.com/NYCComptroller/Checkbook` (AGPL; VERIFIED exists). | Live API is blocked here. |
| NYC Citywide Payroll (FY) | LIL `citywide-payroll-data-fiscal-year` `rows.csv` 880 MB (VERIFIED in zip_entries). Kaggle `new-york-city/ny-citywide-payroll-data-fiscal-year` (95 MB, 2021). | |
| NYC Expense Actuals / Revenue Actuals / Expense Budget | LIL `expense-actuals` (83 KB), `revenue-actuals` (35 KB), `expense-budget-debt-service-statement-ii`, `nyc-quarterly-bond-update-debt-service-by-fiscal-year`, `capital-commitment-actuals`. Kaggle `new-york-city/new-york-city-expense-budget`. | |
| **Chicago Payments** (vendor checks 1996–present) | LIL `payments` (City of Chicago; `rows.csv` 33 MB, captured 2024-11-15; VERIFIED). Kaggle `chicago/chicago-payments` (2019). | |
| Chicago Budget Ordinance appropriations / positions & salaries / revenue 2011–2025 | LIL `budget-2025-budget-ordinance-appropriations`, `budget-2024-budget-ordinance-revenue`, `budget-2021-budget-ordinance-positions-and-salaries`, ... (titles VERIFIED). Kaggle `chicago/chicago-budget-ordinance-and-recommendations`. | |
| Cook County employee payroll, budget, CAFR link | LIL `employee-payroll` (Cook County), `annual-budget-appropriations`, `comptroller-comprehensive-annual-financial-report-cafr` | |
| **Austin Finance Online eCheckbook** | LIL `austin-finance-online-echeckbook` `rows.csv` 642 MB (VERIFIED) | |
| **State of Iowa Checkbook** | LIL `state-of-iowa-checkbook` `rows.csv` 6.0 GB (VERIFIED) | |
| Iowa city annual financial reports | LIL `city-annual-financial-reports` | HTML only, no CSV captured |
| Baltimore Open Checkbook FY2021 | LIL `open-checkbook-fy2021-dataset-02dd0`; Kaggle `charlessalsgiver/baltimore-open-checkbook-analysis` (MIT, derived) | |
| Baton Rouge Open Checkbook | LIL `open-checkbook-br` | |
| UConn / UConn Health checkbooks FY2019 | LIL `uconn-checkbook-fy2019`, `uconn-health-center-checkbook-fy2019` | |
| **Missouri Checkbook FY2010–FY2017** | Kaggle `tfshiloh/csv-version-missouri-checkbook-fy2010fy2017` (259 MB, CC0). VERIFIED anonymous download; quarterly CSVs with title rows before the header (messy). | |
| SF Vendor Payments (vouchers) | Kaggle `san-francisco/sf-vendor-payments` (247 MB, 2019) | |
| Oklahoma P-card | Kaggle `thedevastator/oklahoma-state-purchase-card-spending-fiscal-yea` | |
| Ohio Checkbook (state + about 1,000+ opted-in locals, OpenGov) | none found | unverified counts |
| Texas Comptroller payments; CA Open FI$Cal; MA CTHRU | none found in LIL/HF/Kaggle by title search | |

1. **Access**: Socrata SODA APIs (free, app-token rate limits about 1,000 req/h without a token, unverified), OpenGov portals, and bespoke APIs (Checkbook NYC XML API). All live portals are blocked here, so use LIL snapshots and Kaggle.
   - ToS: mostly public domain, CC0 or ODbL per portal (Chicago and NYC: public use; Oklahoma LIL bag carries `cc-by.html`, i.e. CC-BY).
2. **Formats / messiness**:
   - Socrata CSV with consistent schemas within a portal, but schema drift across years (Oklahoma vendor payments 2008 vs. 2019).
   - Redactions ("REDACTED UNDER DP ACT", confidential vendors).
   - Negative voids and reissues; checkbook "payment date" vs. GL "accounting period"; vendor name variants (no clean vendor ID across systems).
   - Missouri quarterly files have banner rows.
3. **Cadence**: live portals refresh daily to monthly (NYC near real-time; Chicago daily), which makes them contamination-resistant if scraped live. LIL snapshots are frozen at 2023–2024.
4. **Breadth**: entity-deep (one city or state). Statewide GLs cover about 150–200 agencies.
5. **Join keys**: fund code, department/agency code, object/account code, vendor ID (portal-specific), contract/PO number (Chicago `CONTRACT NUMBER`), FEIN for some states, UEI only for federal pass-through.
6. **Natural ground truth**:
   - GL ACTUALS by fund and account summed for the year vs. **the state ACFR fund statements and budgetary schedules**. Oklahoma ACFR PDFs are on omes.ok.gov; GovText has OPERS CAFRs (opers.ok.gov actcafr06/07 VERIFIED) and possibly OMES ACFRs (unverified).
   - Vendor payments summed by agency vs. GL expenditure accounts (5xxxxx) for the same period. Differences come from payroll and transfers, which is itself a reconciling-item exercise.
   - Payroll by agency vs. GL salary accounts.
   - Chicago Payments by department vs. budget ordinance appropriations, giving budget-to-actual.
   - NYC Expense Actuals vs. Citywide Payroll, Checkbook and the NYC ACFR.
7. **Benchmark use**: `vibrantlabsai/usaspending-recon` (an OpenEnv) uses *federal* contract data with planted ledger discrepancies. I found no use of state or city checkbooks. Kaggle notebooks do exploratory analysis only.
8. **Workflows**:
   - **(a) State budget officer / comptroller analyst: "Oklahoma FY2024 budget-to-actual and close review" (very long).**
     1. Load 4 quarterly GL CSVs (about 1.5M rows); build a fund × account-class trial balance. *Checkpoint*: per-fund debits = credits; cash accounts (1010xx) match beginning + net activity.
     2. Map PeopleSoft accounts to GASB statement lines (revenue by source, expenditures by function).
     3. Reconcile vendor-payment totals to GL expenditure accounts by agency; explain reconciling items (payroll, interfund transfers 62xxxx, p-card, accrual timing).
     4. Compare with the ACFR general fund and major special revenue funds (budgetary basis). *Checkpoint*: ties within a stated tolerance, or reconciling items are explained.
     5. Compute top variances vs. the enacted appropriation.
     6. Draft a variance commentary for the legislature.
   - **(b) Procurement auditor / IG: "Vendor master and payment anomaly review" (Chicago or Austin).**
     1. De-duplicate the vendor master with fuzzy matching.
     2. Detect split purchases just under bid thresholds.
     3. Find duplicate invoice amounts and dates, and payments without contracts.
     4. Run Benford on amounts.
     5. Tie the sample to the budget ordinance line.
     6. Write an exception report with materiality. Ground truth is partly judge-graded; numeric checks cover totals.

## 4. Public-employee payroll datasets

- **What**: NYC Citywide Payroll (LIL 880 MB; Kaggle), Chicago Employee Payroll/Salaries, LA City Payroll (Kaggle `cityofLA/city-payroll-data`, `dsfelix/employees-payroll-in-los-angeles` CC-BY), SF Employee Compensation (Kaggle `san-francisco/sf-employee-compensation`), Cook County payroll (LIL `employee-payroll`), Oklahoma state payroll (LIL), CT state payroll FY2010–2014 (LIL `state-employee-payroll-data-fy-2010-2014`), Lake County IL employee comp (LIL `employee-compensation-5a157`), Montgomery County MD (HF `multabench/core-text-reg-montgomery-salaries`, an OpenML 42125 derivative, 2016 only).
  - Others not mirrored: Texas Tribune / Comptroller salaries (Kaggle `danofer/texas-government-salaries`, 2020), CA SCO publicpay.ca.gov (blocked).
- **Ground truth**:
  - Payroll by agency vs. GL salary and benefits accounts, and vs. the ACFR functional expenditures.
  - Pensionable payroll × employer contribution rate vs. the contributions reported in the pension ACFR or actuarial valuation (§10).
  - Headcount vs. budget-book authorized positions (Chicago "Positions and Salaries" ordinance data, LIL).
- **Messiness**: multiple rows per employee (title changes), base vs. gross vs. OT, and redacted names (police).
- **Workflow (persona: city budget analyst)**: "Overtime and vacancy savings analysis."
  1. Join payroll to budget positions.
  2. Compute vacancy rate and OT as % of base by department.
  3. Reconcile total gross pay to the expense actuals personal-services line.
  4. Project year-end PS spending.
  5. Recommend mid-year appropriation transfers.

## 5. Adopted / proposed budget books and budget data

- **Structured**: Chicago Budget Ordinance/Recommendations (LIL, 2011–2025), NYS Executive/Enacted Budget Appropriations 2013–2026 (LIL, many slugs e.g. `new-york-state-enacted-budget-appropriations-non-capital-2022-23`), NYC Expense/Revenue Budget & Financial Plan (LIL `revenue-budget-financial-plan-execadptprel`), Austin operating budgets, OMB Public Budget Database (LIL `public-budget-database-outlays-and-offsetting-receipts-1962-current`, containing `outlays_fy2025.xlsx` 2 MB + guide; VERIFIED in zip_entries).
- **PDF budget books**: GovText about 7.8k URLs with "budget" in budget-book / adopted-budget patterns (e.g. budget.pa.gov, open.omb.delaware.gov).
- **Ground truth**:
  - Proposed vs. adopted vs. revised vs. actual chain. The next year's budget book prints the prior-year actual, a natural cross-document check.
  - Budget-book "actual" columns vs. ACFR budgetary comparison schedules.
- **Workflow (persona: OMB analyst)**: "Build the 5-year financial plan baseline."
  1. Combine 3 adopted budgets and actuals.
  2. Compute structural deficit, growth rates, and personnel cost drivers.
  3. Tie to the ACFR budgetary schedule.
  4. Run gap-closing scenarios.

## 6. California State Controller "ByTheNumbers" Financial Transactions Reports (FTR): universe-broad

- **What**: annual, uniform, line-item financial data that every CA city (482), county (58), special district (about 4,700, unverified), pension system, and transit agency must file with the SCO. Source: https://bythenumbers.sco.ca.gov (blocked).
- **Mirror (VERIFIED, LIL)**:
  - `cities-raw-data-for-fiscal-years-2002-03-to-2015-16-4148d` (xlsx 76 MB)
  - `cities-raw-data-for-fiscal-years-2017-18-to-2019-20-e7e8d`, `cities-raw-data-for-fiscal-years-2020-21-2ddcf`, `cities-raw-data-for-fiscal-year-2021-22`, `cities-raw-data-for-fiscal-year-2022-23` (xlsx 6.9 MB)
  - Counties: same pattern (`counties-raw-data-for-fiscal-year-2022-23`, ...)
  - Special districts: `special-districts-raw-data-for-fiscal-years-2002-03-to-2015-16-b4b19`, ...
  - Pension systems: `retirement-systems-raw-data-for-fiscal-years-2002-03-to-2015-16-54f41`, `retirement-systems-raw-data-for-fiscal-year-2021-22`, plus "net pension liability" and "net OPEB" sets
  - "Filed late or failed to file" lists
- **Format**: XLSX/CSV long format (entity, FY, category, subcategory, line description, value). Moderately clean, with category drift across years.
- **Cadence**: annual, about 18-month lag. The mirror ends at FY2022-23 (captured Nov 2024).
- **Join keys**: SCO entity ID, entity name, county. Crosswalk to Census Gov ID needed.
- **Ground truth**:
  - FTR is prepared from the audited ACFR, so FTR totals vs. ACFR (GovText has sco.ca.gov CAFR PDFs and many CA city/county ACFRs: riversideca.gov, sandiegocounty.gov, ventura.org).
  - Internal identities: revenues − expenditures = change in fund balance; net pension liability = TPL − FNP in pension sets.
  - "Late filers" are labels for a compliance task.
- **Benchmark use**: none found.
- **Workflow (persona: state oversight / rating analyst)**: "Screen all 482 CA cities for fiscal distress, then deep-dive 3."
  1. Build the ratio set: operating margin, GF reserves, debt + pension liabilities per capita, revenue volatility.
  2. Replicate the California State Auditor's local high-risk dashboard methodology (unverified that inputs map 1:1).
  3. Validate the 3 deep-dive cities against their ACFRs.
  4. Explain discrepancies (fiscal-year restatements, component units).

## 7. New York State Comptroller: local government Annual Update Documents (AUD) + Fiscal Stress Monitoring System (FSMS)

- **What**: https://osc.ny.gov/local-government/data (blocked). Annual financial data spreadsheets by class of government and year, for about 3,000 NY counties, cities, towns, villages, school districts and fire districts. FSMS publishes **computed fiscal stress scores** (financial and environmental indicators with published point methodology), with "All Data Worksheet (XLSX)" files for 2025 data (updated March 2026) and historical years.
- **Ground truth (excellent)**: FSMS scores are a deterministic function of AUD inputs, so an agent can be asked to *recompute* published scores and stress designations from raw AUD data. This makes for a long, numeric, auditable workflow. The AUD also reconciles to audited statements, where those exist.
- **Mirrors**: none found on HF, GitHub, Kaggle or LIL (State of New York LIL datasets are mainly budget appropriations). **Needs an out-of-sandbox scrape.** Public data; terms unverified.
- **Cadence**: annual; villages released in March/April, others in September. Contamination-resistant for new releases.
- **Workflow (persona: OSC local-government analyst / muni analyst)**: "Reproduce FSMS 2025 for all counties."
  1. Compute the 9 financial indicators (fund balance, operating deficits, cash ratio, short-term borrowing, ...).
  2. Score with the published thresholds. *Checkpoint*: matches published scores per county.
  3. Add environmental indicators.
  4. Identify misclassified entities if a data revision occurred.
  5. Memo on the top 5 stressed entities with ACFR cross-checks.

## 8. Census Annual Survey of State & Local Government Finances (ASSLGF), Census of Governments, and the Government Finance Database

1. **What / URLs**:
   - https://www.census.gov/programs-surveys/gov-finances.html: individual unit files (`government ID + item code + amount`) for all sampled governments, about 90k units in Census years ending in 2/7.
   - Willamette/ICPSR "Government Finance Database" 1967–2023 (ICPSR 37641, v. June 2026): a harmonized unit-level panel.
   - Census Annual Survey of Public Employment & Payroll (ASPEP).
   - Quarterly Survey of Public Pensions.
2. **Access**: Census bulk downloads (blocked here). ICPSR requires login. Willamette page `willamette.edu/mba/research-impact/public-datasets` (blocked). Public domain (Census); the GFD has an academic citation requirement.
3. **Format**: fixed-width / CSV item-code long format with about 400 item codes (e.g. T01 property tax, E-codes for expenditure by function × character). Unit IDs are 14-digit Census Gov IDs.
4. **Cadence**: annual with a 2–3 year lag (FY2023 state tables released March 2025; local summary scheduled for December 2025, unverified).
5. **Breadth**: universe-broad (all US governments in Census years).
6. **Join keys**: Census Government ID (state + type + county + unit), FIPS place codes, and NCES LEA IDs for school districts.
7. **Ground truth**: unit-level sums vs. published state aggregate tables; unit rows vs. the government's ACFR. Census definitions differ from GAAP (no fund accounting; exclusions of intergovernmental transfers), which yields a rich reconciling-items task.
8. **Benchmark use**: academic research. No LLM benchmark found.
9. **Mirrors**:
   - LIL `public-sector-public-sector-annual-surveys` (metadata only, unverified files).
   - LIL `school-district-finance-survey-2007-08-5c237` through `-2013-14-30490` (NCES/Census F-33 school district finance; `sdf14_1a_flat.zip` VERIFIED).
   - Kaggle `noriuk/us-educational-finances` (CC0), `mdnaimislam165436/us-state-government-finance-time-series-dataset` (CC0; provenance unverified).
10. **Workflow (persona: state & local finance researcher / rating analyst)**: "Reconcile the Census profile for 20 school districts to their ACFRs."
   1. Map F-33 item codes to ACFR fund statements.
   2. Explain differences (capital outlay classification, debt service, fiduciary).
   3. Compute per-pupil spending.
   4. Rank, and flag reporting errors.

## 9. Texas Bond Review Board local debt; Washington Public Debt Database

- **Texas BRB** (`brb.texas.gov`, data on data.texas.gov):
  - "Debt Outstanding by Local Government", "Debt Outstanding by Issuance (Local, by Year)" (issue-level), "Local Issuance" (new issues with fees, underwriters, ratings), "Local Debt Bond Election Results".
  - Snapshot at FYE 8/31. Covers cities, counties, ISDs, CCDs, hospital districts, water districts (about 3,000+ issuers, unverified).
  - LIL has only HTML for these slugs (`debt-outstanding-by-issuance-local`, `local-issuance`, ... filed under "City of Austin"), so **no data mirrored**.
- **Ground truth**: BRB outstanding principal by issuer vs. ACFR debt note vs. EMMA OS. Issuance fees vs. OS "costs of issuance".
- **WA Public Debt Database**: LIL `public-debt-database` (HTML only).
- **Workflow (persona: Texas ISD financial advisor)**: "Debt capacity under the $0.50 I&S tax rate test."
  1. Combine BRB debt service, taxable values, and the proposed new issue.
  2. Project the I&S tax rate.
  3. Compare against the ACFR debt service fund.
  4. Present a refunding opportunity analysis with escrow math.

## 10. State and local pension ACFRs, actuarial valuations, Public Plans Data

1. **What**:
   - Pension system ACFRs (GASB 67), employer GASB 68 schedules, actuarial valuation reports (funding basis: ADC, UAAL amortization, assumptions), and experience studies.
   - **Public Plans Data (PPD)**, publicplansdata.org (Boston College CRR + MissionSquare + NASRA): about 220 plans (state and local), FY2001–present, with hundreds of variables collected from ACFRs and valuations. A full download and API are available (blocked here; terms unverified).
2. **Mirrors**:
   - Kaggle `meepbobeep/us-public-pensions-data-fiscal-years-20012016` (CC BY-NC-SA, 1.3 MB) and `eshitakter/public-pension-plans-analysis-20012023` (2.3 MB; provenance unverified).
   - LIL: CA SCO retirement-systems raw FTR data (§6), `lacers-key-facts-and-figures-from-year-end-financial-reports`, NYC Comptroller pension holdings (`office-of-the-comptroller-nycers-holdings-data`, police and fire).
   - GovText: 433 distinct actuarial-valuation PDFs in EOT-2020 (about 1.3k URLs across crawls), plus pension CAFRs (sers.pa.gov, opers.ok.gov 34, calaters.ca.gov 71, ...).
   - Texas PRB data center (data.prb.texas.gov; CSV downloads; blocked).
3. **Messiness**: PDF tables with multi-year schedules (10-year RSI), different measurement dates (employer FY vs. plan FY), roll-forward valuations. Assumption changes are buried in notes.
4. **Ground truth**:
   - NPL = TPL − FNP.
   - The changes-in-NPL schedule must roll year over year.
   - The PPD value vs. the ACFR value.
   - Employer contributions in the plan ACFR = sum of employer GASB 68 contributions (cost-sharing allocation schedules: proportionate shares sum to 100%; very checkable).
   - Actuarial valuation ADC vs. the following year's actual contributions.
   - Discount-rate sensitivity table (±1%) to sanity-check duration.
5. **Breadth / cadence**: about 5,000 public plans in the US (unverified). Annual reports; valuations annual or biennial.
6. **Join keys**: plan name, PPD `ppd_id`, employer Census ID (sponsors), CUSIP-6 of the sponsoring government.
7. **Benchmark use**: none found.
8. **Workflow (persona: pension consultant / credit analyst)**: "Employer pension burden and contribution adequacy for a cost-sharing state plan."
   1. Extract the GASB 68 allocation schedule (hundreds of employers).
   2. Verify proportions sum to 1.
   3. Recompute each employer's NPL share.
   4. Tie the plan ACFR changes-in-NPL.
   5. Compute the "tread water" contribution, and compare with the actuarial ADC and the actual contribution.
   6. Run a −1% return scenario.
   7. Write a memo to a city CFO. Numeric checks at each step.

## 11. USAspending.gov (federal awards, transactions, account data)

1. **What / URL**: https://www.usaspending.gov.
   - Award Data Archive (prime contracts with 297 columns, assistance with 112 columns, FY2001/2007–present, per agency).
   - Custom Account downloads: File A (appropriations by TAS = GTAS SF-133), File B (object class × program activity), File C (award financial: award-level obligations/outlays by TAS).
   - Subawards (FSRS).
   - API `api.usaspending.gov` (no key).
2. **Access**: bulk ZIPs and API, public domain. Blocked here.
3. **Format**: very wide CSV.
   - Messiness: recipient name variants, parent/child UEI, DUNS→UEI transition (April 2022), modification sequences, de-obligations, PIID/FAIN formats, and award "total" fields that differ from summed transactions.
4. **Cadence**: daily (D1 from FPDS nightly); File C monthly/quarterly. Strongly contamination-resistant if refreshed.
5. **Breadth**: every federal agency; recipients include states, cities, nonprofits, and firms.
6. **Join keys**: UEI (and legacy DUNS), recipient EIN (not public generally), Assistance Listing (CFDA/ALN), TAS, PIID/FAIN, DEFC (COVID/IIJA), place-of-performance FIPS.
7. **Ground truth**:
   - File C obligations by TAS vs. File B vs. File A/SF-133 (DATA Act "cross-file validation"; agencies certify these).
   - File C award amounts vs. D1/D2 transaction sums.
   - Assistance obligations to a state vs. the state's **Schedule of Expenditures of Federal Awards (SEFA)** in its single audit (§13), keyed by ALN. This is a classic federal-grants reconciliation with real timing differences.
8. **Benchmark use**: **YES**. `vibrantlabsai/usaspending-recon` (HF, CC0, 2026-10): an OpenEnv contract-reconciliation environment that uses real FY2024 EPA contract actions with a **synthetic ledger and planted discrepancies**. `ggsmith/usa_spending_awards` and other scrapers exist. This source is less differentiated, but real cross-file (A/B/C vs. D) reconciliation is not used yet.
9. **Mirrors**:
   - **HF `abigailhaddad/usaspending-bulk-awards`** (4,912 downloads, updated 2026-10-16; Hive-partitioned Parquet of the full award archive, contracts + assistance FY2007–present; `serve/{contracts,assistance}/YYYY.parquet`; caution: `agency=All` duplicates).
   - HF `zzsi/usaspending_2024_all_contracts` (2024 contracts).
   - Kaggle `skeller/2021-us-federal-award-data` (2 GB), `treygilliland/usaspending-filtered` (FY18–20).
   - LIL `usaspending-gov-federal-award-subaward-and-account-data` (HTML only).
   - **HF file downloads are blocked here by the CDN** (§0). Kaggle works.
10. **Workflow (persona: state single-audit coordinator / federal grants accountant)**: "Reconcile federal awards to the SEFA."
   1. Pull all FY2023 assistance transactions to recipient = State of X (by UEI).
   2. Aggregate obligations by ALN.
   3. Compare with SEFA *expenditures* (different basis: obligation vs. expenditure, pass-through).
   4. Build a timing roll-forward (prior-year obligations spent this year).
   5. Identify ALNs above the Type A threshold to determine major programs (2 CFR 200.518).
   6. Draft a risk-based major-program determination.

## 12. Treasury Fiscal Data (MTS, DTS, Debt to the Penny, MSPD, Treasury Bulletin, Financial Report of the USG)

1. **What / URL**: https://fiscaldata.treasury.gov. REST API `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/...` (no key; e.g. `/v2/accounting/od/debt_to_penny`). Contents:
   - Daily Treasury Statement (operating cash, deposits/withdrawals by category, public debt transactions)
   - Monthly Treasury Statement (receipts/outlays by agency and account)
   - MSPD (security-level outstanding)
   - Debt to the Penny (daily)
   - Treasury Bulletin
   - Financial Report of the U.S. Government (audited, GAO disclaimer)
2. **Access**: API, CSV/JSON/XML, public domain, no published rate limit (unverified). Blocked here.
3. **Messiness**: moderate. DTS table structure changed in 2022 (and earlier). Category labels drift. Fiscal-year vs. calendar handling. Revisions.
4. **Cadence**: daily (DTS, Debt to the Penny) and monthly (MTS, about the 8th business day). Excellent contamination resistance.
5. **Breadth**: one entity (the US federal government), very deep (DTS since 2005; MTS since 1980s in the API, unverified).
6. **Join keys**: account symbols, classification codes, CUSIP (marketable securities in MSPD vs. auction results).
7. **Ground truth (strong)**:
   - DTS daily deposits/withdrawals summed over the month ≈ MTS monthly receipts/outlays (classification differences are known reconciling items).
   - MSPD totals = Debt to the Penny on month-end.
   - Change in debt held by the public ≈ deficit + other means of financing (MTS Table 6).
   - MTS fiscal-year totals vs. the Financial Report "budget deficit vs. net operating cost" reconciliation statement.
8. **Benchmark use**: Treasury-skill wrappers exist (e.g. agent skills "usfiscaldata"). No long-horizon benchmark found.
9. **Mirrors**:
   - LIL `monthly-treasury-statement-mts`, `debt-to-the-penny`, `treasury-bulletin`, `financial-report-fr-of-the-united-states-government`: **HTML landing pages only, no data**.
   - HF `Farmaanaa/us_federal_debt_and_receipts` (CC-BY-4.0, small).
   - Kaggle `vedauv/daily-and-monthly-us-national-debt-and-macro-data` (CC0), `justin2028/us-debt-tracker` (CC BY-NC-SA).
   - **No full DTS/MTS mirror found.** An out-of-sandbox API pull is needed (trivial, keyless).
10. **Workflow (persona: Treasury cash-management / fixed-income strategist)**: "Debt-limit X-date projection."
   1. Load 2 years of DTS.
   2. Build daily cash-flow categories.
   3. Reconcile monthly to the MTS.
   4. Model extraordinary measures from MSPD intragovernmental holdings.
   5. Project the TGA path and X-date under scenarios.
   6. Memo. Checkpoints at the DTS→MTS tie and the MSPD→Debt to the Penny tie.

## 13. Federal Audit Clearinghouse (Single Audits / Data Collection Form)

1. **What / URL**: https://www.fac.gov (GSA, since Oct 2023; Census history migrated).
   - Every non-federal entity spending ≥ $750k (≥ $1M from FY2025, unverified) of federal awards files the Data Collection Form (SF-SAC) plus a single audit PDF package (financial statements, SEFA, auditor opinions, findings).
   - Tables: `general`, `federal_awards` (SEFA lines by ALN), `notes_to_sefa`, `findings`, `findings_text`, `corrective_action_plans`, `passthrough`, `additional_ueis/eins`, `secondary_auditors`.
2. **Access**:
   - API `api.fac.gov` (PostgREST) with a **data.gov API key**.
   - Bulk CSV per table per year: "Current data 2016–present", "Historic 1998–2015" at fac.gov/data/download.
   - Audit report PDFs per report ID (Tribal entities may restrict).
   - Public data under 2 CFR 200.512. Blocked here.
3. **Messiness**: auditor-entered DCF (typos, mis-keyed ALNs, "Other" programs). PDF packages are long (100–400 pages), sometimes scanned.
4. **Cadence**: continuous (due 9 months after FYE). Contamination-resistant.
5. **Breadth**: about 40k audits per year (states, cities, counties, school districts, universities, nonprofits, tribes; unverified count).
6. **Join keys**: **UEI and EIN** (both in `general`), ALN, report_id, auditor EIN. This is the bridge between USAspending (UEI), the IRS 990 (EIN) and ACFRs.
7. **Ground truth**:
   - DCF `federal_awards` totals = SEFA total in the PDF.
   - SEFA by ALN vs. USAspending obligations/outlays (§11).
   - The nonprofit's 990 Part VIII line 1e "government grants" ≈ SEFA expenditures + state/local grants (reconciling items).
   - Major-program determination is rule-based (Type A threshold formula), so it is checkable.
   - Findings are labels (material weakness, questioned costs).
8. **Benchmark use**: none found.
9. **Mirrors**: none on HF, Kaggle or LIL by search (LIL has `port-of-los-angeles-single-audit-report-2013` only). Code `github.com/GSA-TTS/FAC` (VERIFIED) includes schema and data-dictionary docs. GovText has 872 distinct "single audit" PDFs in EOT-2020 (about 2.5k URLs across crawls). **Needs an out-of-sandbox pull.**
10. **Workflow (persona: grant-compliance auditor at a pass-through state agency)**: "Subrecipient monitoring."
   1. For 50 subrecipients (nonprofits), pull FAC DCF and findings.
   2. Tie SEFA lines to the state's own payments to them (from the state checkbook, §3).
   3. Flag ALN mismatches and late filers.
   4. Compute questioned costs.
   5. Prepare management decision letters, a judge-graded memo.

## 14. IRS Form 990 e-file XML (AWS / GivingTuesday datalake), IRS SOI extracts, BMF

1. **What / URL**: XML e-filed returns (990, 990-EZ, 990-PF, 990-T, schedules A–R), released by IRS TEOS as monthly ZIPs (e.g. `2025_TEOS_XML_01A.zip` ... `12A`, with extra parts like `11D`).
   - The **GivingTuesday 990 Data Lake mirrors everything on public S3: VERIFIED, reachable here.**
   - Bucket `https://gt990datalake-rawdata.s3.amazonaws.com/` (anonymous ListBucket allowed):
     - `EfileData/XmlZips/` — `2017_TEOS_XML_CT1.zip` … `2026_TEOS_XML_07A.zip`, plus legacy `download990xml_20xx_n.zip`. Latest seen: **2026_TEOS_XML_07A**.
     - `EfileData/XmlFiles/<ObjectId>_public.xml` — individual returns.
     - `Indices/990xmls/yearly/2025_efiledata_xmls_created_on_2026-08-25.csv` (78 MB) and `..._2024_...` (268 MB). Columns include EIN, FormType, TaxYear, TotalRevenueCY, TotalExpensesCY, TotalAssetsBkEOY, TotalNetAssetsBkEOY, and a direct `URL` to each XML.
     - `Indices/990xmls/index_all_years_*.parquet` (about 1 GB).
     - `EfileData/Extracts/Data/12eofinextract990.dat` … (IRS SOI annual extracts 2012+).
     - `EfileData/BMF/IRS_BMF_2024_12_12_raw.csv` (Exempt Org Business Master File snapshots).
     - `EfileData/PoliticalOrgs/`, `Revocations/`, `Postcards/` (990-N).
   - The old AWS bucket `irs-form-990` is empty and `irs-990-efile` does not exist (VERIFIED).
2. **Access / ToS**: public domain (IRS). The GT datalake is an open S3 bucket, with no auth and no stated rate limits.
3. **Formats / messiness**: deeply nested XML whose **schema changes every year** (`returnVersion` 2008v2.7 … 2025v4.0). Element names changed in 2013, so the Nonprofit Open Data Collective concordance is needed (`github.com/Nonprofit-Open-Data-Collective/irs-efile-master-concordance-file`, VERIFIED). Further issues:
   - Amended returns and group returns.
   - Repeating groups (Schedule I grants, Schedule R related orgs, Part VII compensation).
   - Free-text Schedule O.
   - Paper filers absent. ProPublica has page images, but its host is blocked.
4. **Cadence**: monthly IRS releases (GT index updated 2026-08-25). TY2025 returns filed in 2026 are present, which makes the source contamination-resistant.
5. **Breadth**: about 1.9M BMF orgs; about 300–400k e-filed 990/990-EZ/990-PF per year (unverified).
6. **Join keys**:
   - **EIN** (to BMF, FAC, EMMA conduit obligors, state charity registries)
   - Schedule I recipient EIN (grant networks)
   - Schedule R related-org EINs
   - ObjectId
   - Preparer firm
7. **Natural ground truth (strong, internal)**:
   - Part I summary = Parts VIII/IX/X totals.
   - Part IX functional expense columns (program + management + fundraising) = total.
   - Part X beginning/ending net assets vs. Part XI reconciliation of net assets (revenue − expenses + other changes).
   - Schedule D Part XI/XII reconciliation of revenue/expenses per audited financial statements vs. the return (book-to-990 bridge).
   - Schedule I total grants = Part IX line 1–2.
   - Prior-year column on this year's return = last year's current-year column, a cross-year check.
   - Funder Schedule I grant to EIN X ≈ recipient X's Part VIII contributions (cross-entity).
8. **Benchmark use**: used in many research datasets and nonprofit analytics. No long-horizon spreadsheet benchmark found.
9. **Mirrors**:
   - S3 GT datalake (VERIFIED, best).
   - **HF `piercewetter3/irs-990-parsed`** (CC0, generated 2026-08-17; 34 tables, 459M rows: Charities, Grants (26.2M), Officers, Contractors, BMF, XmlFiles; plus joins to PPP, OFAC, FEC, Medicare). Its files sit behind the HF CDN, which is blocked here.
   - HF `GivingTuesday/opencorporates_IRS990_EIN_matched_organizations`, `mauricedalton/irs-990`, `healthparse/us-nonprofit-health-org-finances-990`.
   - Kaggle `rogergrambihler/irs-form-990-filings-2023-tax-year-sqlite` (25.9 GB, MIT), `katyali/irs-990-2020` (282 MB, CC0), `irs/irs-990` (legacy pointer).
   - LIL `tax-exempt-organizations-except-private-foundations-financial-data-extract` (SOI).
10. **Workflows**:
   - **(a) Foundation grant analyst / program officer: "Due diligence on 10 grantee applicants."**
     1. Pull 5 years of 990 XML per EIN.
     2. Build a normalized spreadsheet (revenue mix, program expense ratio, months of operating reserves, liquidity, executive comp vs. peers by NTEE/size).
     3. *Checkpoint*: Part XI net-asset reconciliation ties every year.
     4. Cross-check government grants (line 1e) against FAC SEFA totals and USAspending assistance by UEI (§11, §13).
     5. Detect related-party flags from Schedule L/R.
     6. Score and write a recommendation memo (judge-graded) with numeric sub-checks.
   - **(b) State charity regulator / auditor: "Hospital system community-benefit and related-org consolidation."**
     1. Take a nonprofit health system with 30 related EINs (Schedule R).
     2. Roll up revenues and expenses, eliminating intra-group grants (Schedule I recipients that are Schedule R entities).
     3. Compare with audited consolidated statements (Schedule D bridge; EMMA hospital bond continuing disclosure where hand-curated).
     4. Compute Schedule H community benefit % of expenses.
     5. Flag inconsistencies.

## 15. ProPublica Nonprofit Explorer

- **What**: https://projects.propublica.org/nonprofits: 990 summaries, PDF page images (including **paper/scanned 990s**), and an API v2 (`/nonprofits/api/v2/organizations/{ein}.json`).
- **Access**: free API without a key; terms request attribution; scraping PDFs at scale is discouraged (unverified). Blocked here (VERIFIED 403/blocked).
- **Unique value**: scanned paper returns (pre-e-file, or small orgs), a natural "scanned PDF" test, plus extracted financial fields for cross-checking the XML parse.
- **Mirrors**: none found. Most content overlaps with the GT datalake.
- **Ground truth**: ProPublica extracted totals vs. the XML.
- **Benchmark use**: commonly used for 990 lookups in tutorials. No benchmarks found.

## 16. UK local council "spend over £500" transparency CSVs (Local Government Transparency Code 2015)

1. **What**: every English local authority (about 317 councils + fire, police and parks bodies) must publish each payment over £500 monthly or quarterly. Required fields: body, date, transaction no., amount, supplier, supplier ID, expense area, expense type, VAT-irrecoverable flag, merchant category, and so on. Published on council sites and data.gov.uk CKAN.
2. **Access**: per-council CSV/XLSX links (no national aggregate, VERIFIED via search). Data.gov.uk CKAN API (blocked here). Licence is mostly OGL v3.
3. **Messiness (high, which is what makes it valuable)**: schema drift across councils and over time. Example from **Devon County Council's GitHub repo, VERIFIED**:
   - 2011 header `Body,Name of Body,Date,Transaction Number,Invoice Number,Amount,Supplier Name,Supplier ID,VAT Reg no,Expense Area,Expense Type,Expense Code,Creditor Type`
   - 2026 header has a BOM, space-padded names (` Body , Name of Body , ...`), new fields `Costcuk`, and amounts as strings `"-1,440.00 "`
   - Some 2026 files start with SQL export junk rows (`query SELECT * FROM [histr]`)
   - Mixed file naming (`DCCSpendingOver500_202607.csv` vs. `202604_DCCSpendingOver500.csv`)
   - Redactions ("REDACTED UNDER DP ACT"), credit notes, and dd/mm/yyyy dates
4. **Cadence**: **monthly; strongly contamination-resistant.** Devon's latest file is `DCCSpendingOver500_202607.csv`, committed 2026-09-17.
5. **Breadth**: universe-broad (about 400 bodies) or entity-deep (Devon 2011-01 to 2026-07, about 186 monthly files).
6. **Join keys**:
   - Supplier name/ID (council-specific); Companies House number sometimes; VAT reg no
   - Expense area / CIPFA SeRCOP service codes (varies)
   - ONS local authority codes (E06/E07/E08/E09/E10)
7. **Ground truth**:
   - Annual sum by service vs. **MHCLG Revenue Outturn (RO) returns**, published per-LA as official statistics, e.g. 2024-25 individual LA outturn (published 18 Sep 2025) and the RO multi-year dataset 2017-18 to 2024-25. Spend >£500 excludes payroll and small items, so the reconciling items are explicit.
   - vs. the council's **Statement of Accounts** (CIPFA Code; the Expenditure and Funding Analysis note).
   - vs. capital outturn (COR).
   - The **local audit backlog** is real context: about 45% of councils received disclaimed opinions for 2023/24 (search result), and backstop dates run 13 Dec 2024 to 30 Nov 2028. An "unaudited vs. audited" dimension is natural.
8. **Benchmark use**: none found.
9. **Mirrors**:
   - **GitHub `https://github.com/Devon-County-Council/spending` (VERIFIED; 188 files, monthly CSVs 2011–2026).**
   - Kaggle `kulbinderdio/graveshamexpenditure` (Gravesham BC, 4.4 MB, licence unknown).
   - Other councils only on their own sites or data.gov.uk (blocked). 360Giving covers grants (§18).
   - Many councils publish via Socrata/CKAN mirrors such as baselight.app (Leeds, unverified).
10. **Workflow (persona: council Section 151 officer's finance business partner / external auditor)**: "Devon FY2024/25 payments-to-outturn reconciliation and supplier risk review."
    1. Ingest 12 monthly CSVs with 3 schema variants. *Checkpoint*: row counts, totals per month, credit notes netted.
    2. Map expense areas and types to SeRCOP service lines.
    3. Reconcile to the RO return service expenditure. Explain gaps (payroll, <£500, accruals, capital, income).
    4. Run a supplier concentration and duplicate-payment test.
    5. Compare with the Statement of Accounts EFA note.
    6. Write a memo to the audit committee.
    - Universe variant: 20 councils × 12 months with normalization of 20 schemas.

## 17. UK Whole of Government Accounts (WGA), MHCLG RO/RA, council Statements of Accounts

- **WGA**: HM Treasury consolidated accounts of about 10,000 UK public bodies (PDF). The 2023-24 WGA (published July 2025) received a **disclaimer of opinion** from the C&AG. 201 bodies did not submit data, and 224 English LAs submitted unaudited data. The Treasury expects 2024-25 to be disclaimed too. Supporting OSCAR/PESA data tables are on gov.uk (unverified formats). Blocked here; no mirrors found.
- **MHCLG RO/RA** (revenue outturn and budget returns), per LA, annual, XLSX/ODS on gov.uk (blocked; no mirror found). Natural pairing: RA (budget) vs. RO (outturn) gives budget-to-actual for all ~410 LAs.
- **Statements of Accounts**: PDFs on council sites (blocked).
- **Workflow (persona: NAO / audit firm analyst)**: "Quantify the impact of missing/unaudited LA data on WGA aggregates." Combine RO, Statements of Accounts, and WGA notes. Scenario analysis.

## 18. UK 360Giving / GrantNav

- **What**: open grants data from about 300 UK funders (government departments, lottery distributors, councils, foundations) in the 360Giving Data Standard.
  - GrantNav (grantnav.threesixtygiving.org) offers full CSV/JSON exports of several hundred MB.
  - 360Giving Datastore/API is refreshed nightly.
- **Licence**: per publisher, mostly CC-BY 4.0 / OGL. A licence statement for the aggregated export was not found (unverified). Blocked here.
- **Join keys**: recipient org IDs (`GB-CHC-` charity number, `GB-COH-` Companies House, `GB-LAE-` council), funder org IDs, grant IDs.
- **Ground truth**:
  - A funder's published grants sum vs. its annual report/accounts (Charity Commission accounts, SORP).
  - Government grants vs. the department's accounts.
  - Council grants in 360Giving vs. the council's spend >£500 file (same payments, different views).
- **Mirrors**: code `github.com/ThreeSixtyGiving/datastore` (VERIFIED exists). No data mirror found.
- **Workflow (persona: grants analyst at a foundation)**: "Funding landscape and duplication check."
  1. Pull all grants to youth charities in a region.
  2. Dedupe by org ID.
  3. Match against council spend files.
  4. Compute funder concentration.
  5. Identify recipients dependent on one funder.
  6. Reconcile a sample to Charity Commission accounts.

## 19. India: Open Budgets India, CAG audit reports and state accounts, RBI State Finances, PRS, CityFinance, municipal bonds

1. **Open Budgets India** (CivicDataLab).
   - Hosted as CKAN at `ndp.ckan.civicdatalab.in` (India Data Platform) and openbudgetsindia.org: Union, state and municipal budget documents (PDF/XLS: Detailed Demands for Grants, Annexures, Receipts).
   - Licence fields mostly "License not specified" (search). Blocked here.
2. **CAG state accounts** (cag.gov.in/en/state-accounts-report).
   - **Monthly Accounts / Monthly Key Indicators** per state, with entries through June 2026 for 2026-27 (Punjab Excel key indicators through August 2026).
   - Annual **Finance Accounts** (Vol I/II) and **Appropriation Accounts** (grant-wise, original + supplementary vs. actual with excess/savings).
   - **State Finances Audit Reports** and performance audits (PDF).
   - Blocked here.
3. **RBI "State Finances: A Study of Budgets"** (annual): statement and appendix tables with Accounts (2023-24), RE (2024-25) and BE (2025-26) columns for all states. Typically XLSX (unverified).
4. **PRS Legislative Research** state budget analyses (PDF/HTML).
5. **CityFinance.in** (MoHUA + Janaagraha): standardized annual accounts (balance sheet, income & expenditure) of about 4,000+ ULBs (unverified count), credit ratings, and municipal bond issuance details. Municipal bond Information Memoranda are on BSE/NSE (Pune 2017, Ahmedabad, Indore, Hyderabad, Vadodara, Lucknow, Ghaziabad).
6. **Messiness**: very high.
   - Scanned PDFs (older CAG and state budget volumes)
   - Hindi/regional-language headings
   - Major/minor head classification (List of Major and Minor Heads, LMMH)
   - Lakh/crore units
   - BE/RE/Actual vintages
   - Grant numbers that change across years
7. **Cadence**: monthly (CAG key indicators, so contamination-resistant) and annual (budgets in Feb–Mar; Finance Accounts about 9–12 months after FY end).
8. **Join keys**: state, grant/demand number, major-minor-sub head codes (LMMH 15-digit), ULB codes (CityFinance), ISIN for municipal bonds.
9. **Ground truth (strong)**:
   - Sum of 12 monthly key-indicator figures ≈ annual Finance Accounts (pre-closing adjustments are reconciling items).
   - Appropriation Accounts actual vs. budget grant (original + supplementary): the excess/savings are computable and printed.
   - Finance Accounts totals vs. RBI State Finances "Accounts" column.
   - Budget BE vs. RE vs. Actual across three budget years (each budget book prints the prior two years).
   - CAG audit report findings quote the same numbers, which allows cross-document consistency checks.
10. **Benchmark use**: none found.
11. **Mirrors**:
    - HF `zennn077/India_budget`, `Dhruvita/IndiaBudget2024` (tiny).
    - Kaggle `prasenjitsharma/indian-union-budget-fy-21-22-till-23-24`, `nouhidsiddiqui/indian-municipal-finance-data-20122018` (2 KB), `arjunsinghgangwar/govt-scheme-fund-utilization-2021-2025-india`.
    - No meaningful mirror of CAG or Open Budgets India found. **Needs an out-of-sandbox scrape.** cag.gov.in PDFs are public; check terms.
12. **Workflows**:
    - **(a) State finance department / CAG auditor: "FY2025-26 fiscal outturn and FRBM compliance for Karnataka."**
      1. Ingest 12 monthly key indicators.
      2. Build a revenue/capital receipts and expenditure table.
      3. Compute revenue deficit, fiscal deficit and primary deficit as % of GSDP.
      4. Compare with BE and RE (budget docs) and RBI State Finances.
      5. Check against Finance Accounts when published.
      6. Analyse grant-wise excess over appropriation requiring legislative regularization (Appropriation Accounts).
      7. Write an audit-style observation.
    - **(b) Municipal bond analyst (India): "Credit review of a municipal corporation bond."**
      1. IM plus 3 years of CityFinance accounts.
      2. Own-source revenue share, property tax collection efficiency, debt service coverage under the escrow structure.
      3. Compare rating rationale numbers.

## 20. World Bank BOOST public expenditure databases

- **What**: World Bank Data Catalog, per-country Excel (sometimes tens of MB). Line-item budget data with administrative × economic × functional × program × geographic classification, and **multiple execution stages** (approved, modified, committed, paid). Burkina Faso, for example, has allocated, modified, committed, validated, ordered to pay, and paid.
  - Examples: Kenya 2006–2022 (CC-BY-4.0), Uganda 2004–22, Burundi 2013–22, Peru, Seychelles, Mali, Niger, Haiti, and subnational Rio Grande do Sul.
  - Licences are mostly "Custom" (check each).
- **Access**: datacatalog.worldbank.org downloads plus API (blocked here).
- **Mirror**: Kaggle `tunguz/croatia-boost-platform-public-expenditure-flows` (3.8 MB, CC0).
- **Ground truth**:
  - Approved → modified → paid identities.
  - Totals vs. IMF GFS/WEO general government expenditure.
  - Totals vs. national budget law / audit reports.
  - Totals vs. PEFA PI-1/PI-2 aggregate and compositional outturn indicators: the **PEFA methodology defines exact variance formulas**, so an agent can compute PI-2 composition variance and check it against published PEFA assessment scores.
- **Cadence**: irregular (country updates every 1–3 years), so contamination resistance is low.
- **Workflow (persona: World Bank PFM specialist)**: "PEFA PI-1/PI-2 outturn assessment for Kenya FY2019–21."
  1. Compute aggregate expenditure outturn vs. approved.
  2. Compute composition variance by function and economic type using the PEFA formula.
  3. Score A–D.
  4. Compare with the published PEFA report (judge).

## 21. IMF Government Finance Statistics (GFS)

- **What**: data.imf.org (new SDMX 3.0 portal; legacy JSON being retired). GFSM 2014 general government revenue, expense, financing and balance sheets, annual and quarterly, about 190 countries.
- **Access**: free API (blocked here). Mirror: HF `econdataverse/imfweo` (WEO, not GFS), `letrinhan/imf-weo-fiscal-panel`.
- **Ground truth**: GFS identities (net lending = revenue − expense − net acquisition of nonfinancial assets; financing = net acquisition of financial assets − net incurrence of liabilities). National-source vs. GFS comparison.
- **Value here**: an aggregate cross-check for BOOST, the Census or UK WGA. It is thin for long workflows on its own.

## 22. EU Kohesio / Cohesion Open Data / EU Financial Transparency System

- **What**:
  - **Kohesio** (kohesio.ec.europa.eu): about 1.5M+ projects co-financed by ERDF/ESF/CF 2014–2020 plus 2021–2027 (being added gradually). Beneficiary, total cost, EU co-financing, region; CSV/XLSX/RDF, SPARQL.
  - **cohesiondata.ec.europa.eu** (Socrata): programme-level planned/decided/spent and payments.
  - **EU FTS** (ec.europa.eu/budget/financial-transparency-system): beneficiaries of directly managed EU budget commitments, yearly XLSX.
- **Licence**: reuse permitted, Commission decision 2011/833/EU (unverified). Blocked here; no mirrors found.
- **Join keys**: CCI programme code, NUTS region, beneficiary name/VAT (partial), project ID.
- **Ground truth**: sum of project EU co-financing by programme vs. the programme "decided" amounts on cohesiondata; payments vs. the EU budget execution in the Annual Management and Performance Report (AMPR). Matching is approximate.
- **Workflow (persona: managing-authority auditor)**: "Absorption analysis for an operational programme."
  1. Project roll-up.
  2. Compare with cohesiondata payments.
  3. Assess decommitment risk (N+3 rule).
  4. Check beneficiary concentration.

## 23. Additional high-value sources found (not in the original list)

### 23a. France: DGFiP "Balances comptables" (trial balances) + "Comptes individuels" (published ratios). Universe-broad, mirrored on HF.
- **What**: account-level trial balances (M14/M57 chart of accounts) for **every French commune (about 35k), groupement, département and région**, plus DGFiP's per-commune computed financial indicators ("comptes individuels": recettes de fonctionnement, CAF, encours de dette per capita, ...).
- **Licence**: Licence Ouverte v2 (CC-BY-compatible).
- **Mirrors (HF, org `Data-Gouv-ML`; listing VERIFIED, parquet behind the blocked CDN here)**:
  - `Data-Gouv-ML/balances-comptables-des-communes-en-2024` (158 MB parquet; data.gouv.fr id `68779e0ce44fae277c74daf2`)
  - `Data-Gouv-ML/balances-comptables-des-departements-depuis-2010`, `...-des-regions-depuis-2010`, `...-des-syndicats-depuis-2010`
  - `Data-Gouv-ML/comptes-individuels-des-communes-fichier-global-2000-2008`, `-2009`, `-2010`, `-2011-2015`, `-2016`, `-2017`, `-2018`, `-2019-2020`, `-2021`, `-2022`, `-2023-2024`
  - Many `french-open-data/compte-administratif-*` / `budget-primitif-*` (budget vs. actual) per city
- **Ground truth (excellent)**:
  - Recompute DGFiP's published per-commune indicators (comptes individuels) from the raw trial balance (balance → fonctionnement/investissement aggregates → CAF brute/nette → encours de dette). Every commune has a published answer.
  - Trial balance debits = credits.
  - Budget primitif vs. compte administratif gives budget-to-actual.
- **Cadence**: annual. Contamination resistance is medium.
- **Workflow (persona: Cour des comptes / chambre régionale des comptes analyst)**: "Financial analysis of 50 communes in a département."
  1. From balances, build fonctionnement and investissement sections.
  2. Compute épargne brute/nette, capacité de désendettement, and fiscal pressure. *Checkpoint*: matches comptes individuels.
  3. Flag the "réseau d'alerte" thresholds.
  4. Write a CRC-style observation.

### 23b. Korea 지방재정365 (Local Finance 365): budget vs. execution for all local governments
- HF `eddmpython/cleangov-fiscal-loc-002`: annual 2016–2025 parquet of 세부사업별 세출현황 (detailed project-level expenditure: national/provincial/municipal funding sources, 예산현액 = budget, 지출액 = actual, 잔액 = balance). Source data.go.kr 15138684, "이용허락범위 제한 없음".
- Also `eddmpython/cleangov-local-fiscal-metrics` (silver metrics).
- The identity budget − spent = balance is built in. Universe-broad (243 local governments).

### 23c. Ontario Financial Information Return (FIR)
- All 444 Ontario municipalities, schedules 10/12/40/70/80 (revenue, expense by function, financial position, reserves).
- Annual CSV by year since 2000 on data.ontario.ca (OGL-Ontario), with an API.
- FIR is prepared from audited statements, which gives ground truth vs. the municipal FS. No mirror found; blocked.

### 23d. Brazil SICONFI (Tesouro Nacional)
- DCA (annual accounts), RREO (bimonthly budget execution), RGF (four-monthly fiscal management), and **MSC (monthly accounting trial balances)** for all 5,570 municipalities, 27 states and the Union.
- API `apidatalake.tesouro.gov.br` (ORDS, 5,000 rows per page; R pkg `tesouror`).
- Monthly MSC is contamination-resistant, and the identity MSC → RREO → DCA is checkable.
- No mirror found; blocked.

### 23e. Connecticut OPM municipal fiscal indicators
- Structured annual data from audited statements for 169 towns (search result). Not checked further.

---

## 24. Ranked top-5 for this slice

Criteria: (D) workflow depth, (R) realness/messiness, (V) verifiability, (X) differentiation vs. existing benchmarks, (S) scrapability/reachability from your container.

**1. US "checkbook-to-ACFR" state/city reconciliation environments (Oklahoma GL + vendor payments + payroll; NYC; Chicago; Austin; Iowa) + ACFR PDFs from GovText.**
- D: very high. GL → trial balance → GASB statements → budget-to-actual → variance memo is literally a comptroller's year-end close.
- R: high. 1–6 GB real ledgers, chartfield mapping, schema drift, redactions, plus real scanned and native ACFR PDFs.
- V: excellent. GASB built-in reconciliations, GL vs. vendor vs. payroll, GL vs. ACFR.
- X: high. I found no use of state or city ledgers in benchmarks.
- S: **reachable now** via the LIL S3 archive (Range-readable) and GovText S3.
- Caveats: snapshots are frozen (2023–24), so contamination is moderate. Supplement with a fresh live scrape out-of-sandbox (Socrata) for contamination-resistant test splits. Pair each environment with the matching-year ACFR.

**2. Nonprofit triangulation: IRS 990 XML (GivingTuesday S3) × Federal Audit Clearinghouse × USAspending.**
- D: high. Grant due diligence or a charity-regulator review chains 990 parsing, net-asset reconciliation, the Schedule D book-to-return bridge, SEFA reconciliation, and related-org consolidation.
- R: high. Year-varying XML schemas, amended and group returns, 30-EIN systems.
- V: strong. Built-in 990 identities, cross-year prior-year columns, EIN/UEI joins.
- X: medium-high. 990s are known in research, not in agentic benchmarks. The USAspending piece overlaps `vibrantlabsai/usaspending-recon`, but that environment uses a synthetic ledger.
- S: **990 fully reachable (S3, monthly refresh through TEOS 2026-07; strongly contamination-resistant)**. USAspending via Kaggle or HF (if the CDN is allowed). FAC needs an out-of-sandbox pull (key required).

**3. Universe-broad local-government annual returns with *published derived metrics as answer keys*: CA SCO FTR (LIL S3, FY2003–FY2023), France DGFiP balances + comptes individuels (HF), NY OSC AUD + FSMS scores (scrape).**
- D: high. Screen hundreds of entities, recompute official ratios and stress scores, then deep-dive and reconcile to ACFRs.
- R: medium-high (long-format, category drift, late filers).
- V: **excellent**. The government already published the "answer" (FSMS scores, comptes individuels ratios), and the FTR ties to the ACFR.
- X: high (nothing like it in benchmarks).
- S: CA data reachable now (LIL). French data on HF (needs the HF CDN). NY needs a scrape.

**4. Municipal credit review packs: EMMA-style OS + 3–5 ACFRs + pension actuarial valuation + Census/GFD profile (+ Texas BRB debt for TX issuers).**
- D: highest. A full municipal credit review is a "big chunk of an analyst's job".
- R: very high (long PDFs, scanned, footnotes, cross-document definitions such as bond-resolution net revenues vs. GAAP).
- V: good. OS debt-service schedule vs. ACFR debt note, DSCR covenant recompute, NPL roll, statistical section vs. prior ACFRs.
- X: very high (no muni benchmark found).
- S: weakest. **EMMA ToS forbid scraping**, so OS documents must be hand-curated from issuer websites or GovText (167 OS PDFs in EOT-2020). ACFRs and actuarial valuations are reachable via GovText S3. Hand-curation fits the expert-curated, few-but-long design.

**5. UK councils: monthly "spend over £500" CSVs + MHCLG RO/RA outturn + Statements of Accounts (+ 360Giving).**
- D: medium-high (payments → service-line mapping → RO reconciliation → audit-committee memo).
- R: **very high and real** (BOM, padded headers, number-as-text, junk export rows, schema drift; Devon 2011–2026 VERIFIED).
- V: good with explicit reconciling items (payroll, <£500, accruals). The audit backlog and disclaimers add realism.
- X: high (non-US, unused).
- S: Devon is reachable via GitHub now. Other councils and RO need an out-of-sandbox scrape. Monthly refresh makes this contamination-resistant.

**Honorable mentions**:
- Treasury DTS → MTS → MSPD (excellent identities, daily refresh, keyless API; single-entity, needs an out-of-sandbox pull).
- India CAG monthly accounts → Finance/Appropriation Accounts → RBI State Finances (excellent identities, monthly; high-messiness PDFs; needs a scrape and terms check).
- World Bank BOOST + PEFA formulas (verifiable scoring; stale cadence).
- Brazil SICONFI MSC monthly trial balances (huge, verifiable; needs an API pull).

---

## 25. Exact reachable URLs and IDs (copy-paste)

```
# IRS 990 (GivingTuesday datalake, public S3; VERIFIED)
https://gt990datalake-rawdata.s3.amazonaws.com/?list-type=2&prefix=EfileData/XmlZips/
https://gt990datalake-rawdata.s3.amazonaws.com/Indices/990xmls/yearly/2025_efiledata_xmls_created_on_2026-08-25.csv
https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/<ObjectId>_public.xml
https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/Extracts/Data/   (SOI extracts)
https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/BMF/IRS_BMF_2024_12_12_raw.csv

# Harvard LIL data.gov archive (public S3; VERIFIED)
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/harvard-lil/gov-data/metadata.csv.zip
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/harvard-lil/gov-data/metadata/data_gov/<slug>/v1.json
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/harvard-lil/gov-data/collections/data_gov/<slug>/v1.zip
  slugs: general-ledger, state-of-oklahoma-vendor-payments-fiscal-year-2019-6704f, payments (Chicago),
         citywide-payroll-data-fiscal-year, austin-finance-online-echeckbook, state-of-iowa-checkbook,
         expense-actuals, revenue-actuals, cities-raw-data-for-fiscal-year-2022-23,
         cities-raw-data-for-fiscal-years-2002-03-to-2015-16-4148d, counties-raw-data-for-fiscal-year-2022-23,
         retirement-systems-raw-data-for-fiscal-years-2002-03-to-2015-16-54f41,
         school-district-finance-survey-2013-14-30490, public-budget-database-outlays-and-offsetting-receipts-1962-current,
         budget-2025-budget-ordinance-appropriations, new-york-state-enacted-budget-appropriations-non-capital-2022-23

# GovText / End-of-Term 2020 PDFs + OCR (public S3, CC0; VERIFIED)
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/README.md
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/cdx/complete_cdx.parquet
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/pdfs/<pdf_id>.pdf
https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/ocr_text/<pdf_id>.tar.gz

# GitHub (VERIFIED)
https://github.com/Devon-County-Council/spending          (UK spend >£500, monthly 2011-01..2026-07)
https://github.com/NYCComptroller/Checkbook               (Checkbook NYC code)
https://github.com/GSA-TTS/FAC                            (Federal Audit Clearinghouse code/docs)
https://github.com/fedspendingtransparency/usaspending-api
https://github.com/Nonprofit-Open-Data-Collective/irs-efile-master-concordance-file
https://github.com/jsfenfen/990-xml-reader
https://github.com/ThreeSixtyGiving/datastore
https://github.com/govscape/govscape

# Kaggle (anonymous download VERIFIED: https://www.kaggle.com/api/v1/datasets/download/<ref>)
tfshiloh/csv-version-missouri-checkbook-fy2010fy2017   san-francisco/sf-vendor-payments
chicago/chicago-payments    chicago/chicago-budget-ordinance-and-recommendations
new-york-city/ny-citywide-payroll-data-fiscal-year     new-york-city/new-york-city-expense-budget
cityofLA/city-payroll-data  san-francisco/sf-employee-compensation  kulbinderdio/graveshamexpenditure
meepbobeep/us-public-pensions-data-fiscal-years-20012016  tunguz/croatia-boost-platform-public-expenditure-flows
rogergrambihler/irs-form-990-filings-2023-tax-year-sqlite  katyali/irs-990-2020
skeller/2021-us-federal-award-data  noriuk/us-educational-finances

# Hugging Face (listing VERIFIED; large files behind us.aws.cdn.hf.co, which is BLOCKED here)
abigailhaddad/usaspending-bulk-awards   vibrantlabsai/usaspending-recon (existing benchmark env)
piercewetter3/irs-990-parsed            GivingTuesday/opencorporates_IRS990_EIN_matched_organizations
Data-Gouv-ML/balances-comptables-des-communes-en-2024   Data-Gouv-ML/comptes-individuels-des-communes-fichier-global-2022
eddmpython/cleangov-fiscal-loc-002      gnovoa26/cafr_images   Farmaanaa/us_federal_debt_and_receipts
```

## 26. Sources consulted (web search results)
- MSRB terms of use: https://emma.msrb.org/tradedata ; https://www.msrb.org/node/13517
- FAC data and API: https://fac.gov/data ; https://www.fac.gov/data/download ; https://fac.gov/api
- FDTA municipal XBRL: https://www.bondbuyer.com/news/bond-buyers-to-cities-states-dont-fear-digital-data-fdta ; SEC S7-2024-05
- Government Finance Database: https://willamette.edu/mba/research-impact/public-datasets ; https://www.icpsr.umich.edu/web/ICPSR/studies/37641
- Census finance datasets: https://www.census.gov/data/datasets/2023/econ/local/public-use-datasets.html
- NY OSC data and FSMS: https://osc.ny.gov/local-government/data ; https://www.osc.ny.gov/local-government/fiscal-monitoring/local-government-and-school-fsms-scores
- Texas BRB: https://www.brb.texas.gov/local-government-services/ ; https://catalog.data.gov/dataset/debt-outstanding-by-local-government
- Ohio Checkbook: https://opengov.com/article/article-ohio-checkbooks-open-gov/
- Checkbook NYC API: https://www.checkbooknyc.com/node/304
- Public Plans Data: https://reason.org/commentary/research-groups-launched-comprehens/ ; https://data.prb.texas.gov
- 360Giving: https://grantnav.readthedocs.io/en/latest/export/ ; https://www.threesixtygiving.org/data/using-the-data/technical-users
- UK audit backlog: https://democracy.reading.gov.uk/documents/s38492/Statement%20of%20Accounts%20202425.pdf ; https://www.surrey-pcc.gov.uk/wp-content/uploads/2025/02/2024-Public-Notice-Surrey-Disclaimed-Audit-Opinion-Accounts-250226.pdf
- WGA: https://www.nao.org.uk/reports/whole-of-government-accounts-2023-24/ ; https://www.civilserviceworld.com/news/article/whole-of-government-accounts-set-to-be-disclaimed-again
- MHCLG RO: https://www.gov.uk/government/statistics/local-authority-revenue-expenditure-and-financing-england-2024-to-2025-individual-local-authority-data-outturn ; https://www.gov.uk/government/statistics/local-authority-revenue-expenditure-and-financing-england-revenue-outturn-multi-year-data-set
- India CAG and RBI: https://cag.gov.in/en/state-accounts-report ; https://cag.gov.in/ae/punjab/en/page-ae-punjab-monthly-key-indicator-excel-for ; https://rbi.org.in/Scripts/PublicationsView.aspx?id=23689
- Open Budgets India CKAN: https://ndp.ckan.civicdatalab.in/dataset/finance-and-planning-department
- CityFinance: https://cips.org.in/innovation-gyan/portal-for-hosting-information-on-hosting-financial-performance-of-urban-local-bodies
- BOOST: https://datacatalog.worldbank.org/search/dataset/0038086/kenya-boost-public-expenditure-database ; https://datacatalog.worldbank.org/search/dataset/0041709/burkina-faso-boost-public-expenditure-database
- Kohesio: https://kohesio.ec.europa.eu/en/faq
- IMF data portal: https://data.imf.org/en/news/accessing
- Ontario FIR: https://data2.ontario.ca/dataset/financial-information-return-fir-for-municipalities/resource/0ba84d5e-1532-4c79-8a7f-ad7609a93013
- SICONFI: https://cran.r-project.org/web/packages/tesouror/readme/README.html
- Benchmarks checked: FinanceBench (arXiv 2311.11944), Fin-RATE (2602.07294), EDINET-Bench (2506.08762), FinBalance (2606.15949; synthetic), SpreadsheetBench 2 (2606.29955), MBABench/WorkstreamBench (2605.22664), "Agent Benchmarks Fail Public Sector Requirements"
