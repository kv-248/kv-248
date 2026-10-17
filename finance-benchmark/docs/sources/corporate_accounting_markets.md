# Source scouting: Corporate disclosures, accounting operations, market data, household/SMB

Slice: (a) corporate disclosures beyond plain 10-K QA, (b) accounting-operations data (ledgers, transactions, invoices), (c) market data for investment workflows, (d) household/SMB/nonprofit finance.
Compiled 2026-10-17. Every dataset ID below was checked live (HF API / Kaggle API / S3 listing) unless marked **unverified**.

---

## 0. Access findings from this container (read first)

Tested with curl from the sandbox:

| Channel | Status | Evidence |
|---|---|---|
| `s3.us-west-2.amazonaws.com/pudl.catalyst.coop` (Catalyst PUDL public bucket) | **WORKS**, listing and download | Listed about 1,562 objects under `stable/`. Downloaded 3 parquet tables (2.7–2.8 MB each) and the 8.5 MB taxonomy JSON |
| Kaggle API `www.kaggle.com/api/v1/datasets/{list,view,download}` | **WORKS without auth**. Download is a 302 to a signed `storage.googleapis.com` URL | Downloaded the Berka zip (18 MB) and the UK accounts README and dictionary |
| `huggingface.co` API, README/raw, datasets-server `/rows` `/first-rows` | WORKS | Used for all HF metadata. `/rows` pages JSON rows (for example 109,087-row DEF14A set) |
| HF **LFS/Xet file downloads** (`/resolve/...` → `us.aws.cdn.hf.co`) | **BLOCKED** (proxy `connect_rejected`) | Fails for TeraflopAI, DenyTranDFW, dartlab and the Enron `index.json`. Only very small non-LFS files (for example a 22 KB Enron .xls) come back through `/api/resolve-cache` |
| `raw.githubusercontent.com` and `git clone` from github.com | WORKS | Cloned `SheetJS/enron_xls` (blobless) and listed 20,901 files |
| github.com web UI, GitHub search API | 403 | |
| All `.gov` hosts, zenodo, figshare, archive.org, fred/alfred.stlouisfed.org, Ken French site, stooq, binance, cboe, EDINET, OpenDART, BSE/NSE, CNINFO, ASX, SEDAR+, filings.xbrl.org (403), Companies House, CourtListener, claims agents (Kroll/Stretto/Epiq/Omni), pcaobus.org | BLOCKED (000 or 403) | |

**Implication:** the realistic in-container ingest paths are **PUDL S3, Kaggle, git clones and the HF datasets-server rows API**. HF-only mirrors with large files (TeraflopAI EDGAR, dartlab, DenyTranDFW companyfacts, robosystems, USAspending) need either an egress exception for `us.aws.cdn.hf.co` / `cas-bridge.xethub.hf.co` or an out-of-container fetch.

Legend for each source: (1) what/URL · (2) access/auth/ToS · (3) formats/messiness · (4) temporal depth/cadence · (5) entity breadth · (6) join keys · (7) natural ground truth · (8) existing-benchmark use · (9) mirrors · (10) workflow sketches.

---

## (a) CORPORATE AND REGULATORY DISCLOSURES BEYOND 10-K QA

### A1. FERC utility financial forms (Form 1 electric, Form 2 gas pipelines, Form 6 oil pipelines, Form 60 service companies, Form 714) via Catalyst PUDL. ★ Top pick
1. **What:** Annual regulatory financial reports filed under FERC's Uniform System of Accounts (USofA). They cover balance sheet, income statement, cash flow, plant in service by FERC account (sched 204), accumulated depreciation (219), depreciation rates (336), O&M by function (320), purchased power by counterparty (326), sales for resale (310), long-term debt, ADIT (accounts 190/281/282/283), regulatory assets and liabilities (232/278), officers' pay and plant operating data. PUDL cleans and links these. Home: https://catalyst.coop/pudl/ · docs https://docs.catalyst.coop/pudl/
2. **Access:** Public S3 bucket, no auth (verified): `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/…` plus versioned folders `v2022.11.30 … v2026.10.0` and `nightly/`. License CC BY 4.0 (PUDL); the underlying FERC data is public domain.
3. **Formats:** Raw FERC data is FoxPro DBF (1994–2020) and XBRL (2021+, verified raw zips `zenodo/ferc1/10.5281-zenodo.22172378/ferc1-xbrl-2021.zip … ferc1-xbrl-2025.zip` plus `ferc1-xbrl-taxonomies.zip`). PUDL republishes it as SQLite, DuckDB and Parquet. Messiness: PUDL docs call the FERC 1 database "poorly normalized" with little QC. There is a DBF→XBRL schema break in 2021, free-text plant names, footnotes, respondent-ID changes, and mixed electric/gas/common utility types.
4. **Depth:** Form 1 covers 1994–2025. Verified: `out_ferc1__yearly_income_statements_sched114` spans report_year 1994–2025, 374,486 rows. Annual refresh; PUDL makes roughly monthly releases.
5. **Breadth:** About 385 Form 1 respondents (verified distinct `utility_id_ferc1`). Forms 2, 6 and 60 add gas and oil pipelines and holding-company service companies.
6. **Join keys:** `utility_id_ferc1`, `utility_id_pudl`, `utility_id_ferc1_xbrl` (FERC CID, for example `C000029`), EIA utility/plant IDs, FERC account numbers (`ferc_account`, for example 411.10). There is also a **SEC CIK link**: `core_sec10k__assn_sec10k_filers_and_eia_utilities`, `out_sec10k__parents_and_subsidiaries` (Exhibit 21 subsidiaries) tie opcos to SEC-filing parents.
7. **Ground truth (strong):**
   - `stable/ferc1_xbrl_taxonomy_metadata.json` carries FERC XBRL calculation rules with weights. Verified: 274 calculated facts, for example `utility_operating_expenses = operation + maintenance + depreciation + … + regulatory_debits − regulatory_credits − gains_from_disposition…`.
   - Debit/credit `balance` attribute on every row.
   - `row_type_xbrl` (reported_value vs calculated) and PUDL's `ReconcileTableCalculations` error checks.
   - Cross-schedule tie-outs: 204 plant ↔ 200 summary ↔ 110 balance sheet, 219 ↔ 110, 114 ↔ 118 retained earnings ↔ 120 cash flow.
   - PUDL publishes a derived **`out_ferc1__yearly_rate_base`** (456,906 rows, verified). It works as a reference answer for rate-base rebuild tasks.
8. **Benchmarks:** No LLM benchmark found using FERC Form 1 data (search on 2026-10-17).
9. **Mirrors:**
   - S3 (above, in-container verified): `stable/ferc1_xbrl.sqlite.zip` 246.9 MB, `ferc1_xbrl.duckdb` 1.23 GB, `ferc1_dbf.sqlite.zip` 275 MB, `ferc2_xbrl.sqlite.zip` 37 MB, `ferc6_xbrl.sqlite.zip` 30 MB, `ferc60_xbrl.sqlite.zip` 5.6 MB, `ferc714_xbrl.sqlite.zip` 243 MB, `pudl.sqlite.zip` 3.47 GB, `pudl_parquet.zip` 12 GB, plus per-table parquet such as `stable/out_ferc1__yearly_plant_in_service_sched204.parquet`.
   - Kaggle: `catalystcooperative/pudl-project` (CC BY 4.0, 40.7 GB) and `catalystcooperative/ferc-annual-reports` (5.9 GB, Forms 1/2/6/60 raw-ish SQLite).
   - Zenodo copies of raw archives sit under S3 `zenodo/`.
10. **Workflows:**
   - **W-A1a "Test-year revenue requirement rebuild" (persona: rate-case analyst at a state PUC staff or intervenor consultancy).** Steps:
     (i) Pull schedules 200/204/219/110/114/300/320/336/256-257/272-277 for one opco, 2021–2025.
     (ii) Checkpoint 1: plant-in-service by function ties to sched 200 and the balance sheet, with exact match.
     (iii) Build rate base = gross plant − accumulated depreciation + CWIP (policy choice) + M&S + prepayments + regulatory assets − ADIT (281–283 net of 190) − customer advances. Checkpoint 2: compare to `out_ferc1__yearly_rate_base`.
     (iv) Derive implied depreciation rates by function and flag outliers (checkpoint 3).
     (v) Compute embedded cost of debt from the LTD schedule, then WACC at an assumed ROE and capital structure.
     (vi) Revenue requirement = RB×WACC + O&M + D&A + taxes other + grossed-up income tax. Revenue deficiency vs sched 300 operating revenues (checkpoint 4).
     (vii) Write a sensitivity table (ROE ±50 bp, CWIP in/out) and a testimony-style memo.
     Concepts: rate base, ADIT normalization, depreciation studies, cost of capital, tax gross-up, regulatory assets.
   - **W-A1b "Holding-company segment ↔ regulated opco bridge" (persona: utility equity analyst).** Steps:
     (i) Use the PUDL Exhibit 21 tables to map a SEC-filing parent (CIK) to its FERC opcos.
     (ii) Sum the opcos' Form 1 revenues, O&M and net plant.
     (iii) Reconcile to the parent's 10-K "Regulated Electric" segment (SEC XBRL dimensional facts, A3). Checkpoint: explained gap from gas ops, non-regulated subsidiaries, and purchase accounting.
     (iv) Compute earned ROE per opco vs authorized.
     (v) Produce a regulatory-lag watchlist.
     Concepts: segment reporting, consolidation eliminations, earned vs allowed ROE, rate-base growth.

### A1-bis. RUS Form 7 / Form 12 (rural electric cooperatives and G&T co-op financial statements). PUDL
1. **What:** USDA Rural Utilities Service borrower financial and operating reports. Includes statement of operations **with budget column**, balance sheet, long-term debt, patronage capital, loans, investments, plant changes and "external financial risk ratio".
2. **Access:** Same PUDL S3 (`stable/core_rus7__*.parquet`, `stable/core_rus12__*.parquet`; raw `zenodo/rus7/…/rus7-2006.zip …`). Public.
3. **Formats:** Parquet. The raw source is per-year zipped CSV/Excel extracts (unverified). Long tables with `opex_group/opex_type/is_total`.
4. **Depth:** The statement of operations covers 2006-12 to 2021-12 (verified on `core_rus7__yearly_statement_of_operations`, 199,762 rows). Annual.
5. **Breadth:** 613 distribution co-op borrowers (verified) plus Form 12 G&T co-ops.
6. **Join keys:** `borrower_id_rus`. PUDL forensic entity resolution links it to EIA utility IDs (`_core_rus7__forensics_entity_resolution_borrowers`).
7. **Ground truth:** `is_total` rows (totals vs components), `opex_ytd` vs `opex_ytd_budget` (budget variance), and balance-sheet identity. Lender covenant ratios (TIER, DSC, equity ratio) are formula-defined.
8. **Benchmarks:** None found.
9. **Mirrors:** PUDL S3 (verified). Kaggle `catalystcooperative/pudl-project` (bundled).
10. **W-A1c "Co-op lender covenant and budget review" (persona: credit analyst at a co-op lender such as CFC, or a co-op CFO).** Steps:
    (i) Load 5 years of Form 7.
    (ii) Compute TIER, OTIER, DSC, MDSC and equity/assets. Checkpoint: recomputed totals equal `is_total` rows.
    (iii) Analyse budget vs actual variance by expense function and explain drivers with purchased-power cost per MWh (join Form 7 energy purchased).
    (iv) Roll forward patronage capital (allocated − retired).
    (v) Run a covenant headroom stress at +10% power cost and write a credit memo.

### A1-ter. FERC Electric Quarterly Reports (EQR, Form 920). Contract- and transaction-level wholesale sales. See B2 (transactions).

### A2. SEC XBRL structured data: Financial Statement & Notes (FSN), Financial Statement Data Sets (FSDS), companyfacts and frames
1. **What:** Every XBRL fact from 10-K, 10-Q, 20-F, 40-F and 8-K exhibits since 2009.
   - **FSN** (monthly since Nov 2020, quarterly before) includes the notes, dimensional facts and linkbases. Tables: `sub num pre tag dim txt ren cal`. **`cal` is the calculation linkbase.** Verified in a Kaggle copy of 2020Q3: `cal.tsv, dim.tsv, num.tsv, pre.tsv, ren.tsv, sub.tsv`.
   - **FSDS** is the face-statements-only subset.
   - **companyfacts / frames API** (data.sec.gov) gives per-company or per-period facts with the `filed` date, which yields as-filed vintages.
   - Official pages: https://www.sec.gov/dera/data/financial-statement-and-notes-data-set (blocked here).
2. **Access:** Free, no key. SEC fair-access policy (declared User-Agent, ≤10 req/s per the TeraflopAI README). US government work, public domain.
3. **Formats:** Tab-delimited TXT in zips (FSN about 2.5 GB uncompressed per quarter for 2020Q3). Messiness: custom extension tags, sign conventions (`negating` in pre), dimensional members per filer, amended filings, scale errors (Kaggle `vadimvanak/enhanced-us-gaap…` exists purely to correct outliers and amendments).
4. **Depth:** Apr 2009 → present, monthly.
5. **Breadth:** All XBRL filers, roughly 6–8k active registrants. Also includes IFRS filers (20-F) and investment companies.
6. **Join keys:** CIK, accession number (`adsh`/`accn`), tag+version, period (`ddate`, `qtrs`), `frame` (for example CY2010Q3I), segments/dims; ticker via SEC company_tickers (HF `DenyTranDFW/SEC_Company_Tickers_Exchange`).
7. **Ground truth:**
   - The calc linkbase (`cal`) gives parent = Σ weight×child, for every filing.
   - Balance-sheet identity and cash-flow roll (beginning cash + net change = ending cash).
   - Dimensional totals (Σ segments + reconciling items = consolidated).
   - **Vintages:** the same (CIK, tag, period) filed in multiple accessions reveals restatements and reclassifications.
8. **Benchmarks:** Heavy. FinanceBench, Finance Agent Benchmark (10-K QA); **FinTagging** (arXiv 2505.20650, XBRL tagging); **FinAuditing** (XBRL taxonomy and calc consistency, about 1,102 instances from 218 filings per a secondary blog; **unverified**); HF `KirkHan/XBRL_Formula_Calculation`, `mirageco/XBRLBench`, `wangd12/XBRL_analysis` (not inspected). Differentiation must come from **notes-level, dimensional, multi-vintage, and cross-source** use, not face-statement QA.
9. **Mirrors (verified IDs):**
   - Kaggle `plarmuseau/financial-statement-and-notes-data-sets-2020q3`: FSN one quarter with cal/dim/pre/ren, 2.5 GB, license Unknown.
   - Kaggle `dhruvb2028/financial-statement-data-sets`: FSDS 2025Q4 num/pre/sub/tag, CC0.
   - Kaggle `securities-exchange-commission/financial-statement-extracts`: official SEC account, CC0, FSDS 2015Q3–2017Q2 as JSON, 3.7 GB.
   - Kaggle `vadimvanak/company-facts-2`: CC0, US-GAAP facts since Jan 2009, facts.parquet 305 MB plus submissions.csv; updated 2026-10-09.
   - Kaggle `vadimvanak/enhanced-us-gaap-financial-statement-data-set`: CC0, outlier and amendment adjusted; updated 2026-10-16.
   - Kaggle `wbqrmgmcia7lhhq/sec-financial-statement-data-in-json`: BS/IS/CF per filing 2010Q1–2026Q2, 9.2 GB.
   - HF `DenyTranDFW/edgar_xbrl_companyfacts`: 1.7 GB parquet. Fields `end, accn, fy, fp, form, filed, frame, label, description, unit, val_text, val_dec`. Non-dimensional only. Card says GPL. **HF CDN-blocked here.**
   - HF `robosystems/sec-xbrl-knowledge-graphs`: CC BY 4.0, 42 GB; all XBRL filings since Jan 2024 including **DEF 14A**; 8,525 filers, 84.1M facts; LadybugDB format; CDN-blocked here.
   - HF `CyberMax-tools/figurewell-sec-xbrl-financials`: CC0 snapshot, 60 MB.
   - No full-history FSN mirror with `cal`/`dim` found. It would need an out-of-container fetch from SEC.
10. **Workflows:**
   - **W-A2a "Segment economics after ASU 2023-07" (persona: sell-side equity research associate).** Steps:
     (i) For 15 peers, pull FY2023–FY2025 dimensional facts on `StatementBusinessSegmentsAxis` (FSN `num`+`dim`), including newly required significant segment expenses.
     (ii) Map heterogeneous member names to a common segment taxonomy.
     (iii) Checkpoint: Σ segment revenue + eliminations = consolidated revenue (cal/pre).
     (iv) Rebuild segment margins and incremental margins.
     (v) Reconcile management's non-GAAP segment EBITDA in the EX-99.1 earnings release (A3) to GAAP segment profit.
     (vi) Write a peer comp table and note.
     Concepts: segment reporting, non-GAAP reconciliation, operating leverage, eliminations.
   - **W-A2b "As-filed vs restated forensic" (persona: forensic accountant or short-seller analyst).** Steps:
     (i) From companyfacts, find (CIK, tag, period) facts with differing values across accessions.
     (ii) Classify each as restatement vs reclassification using 8-K Item 4.02 filings (HF `hammerlabs/sec-restatement-8k-402`, **unverified contents**) and 10-K/A forms.
     (iii) Quantify the cumulative EPS and equity impact.
     (iv) Recompute ratios as-first-reported vs latest. Checkpoint: restated statements still satisfy the calc linkbase.
     (v) Write an audit-committee style memo.

### A3. SEC EDGAR documents beyond 10-K: 8-K EX-99.1 earnings releases and investor decks, DEF 14A pay-versus-performance, N-PORT, 13F, Forms 3/4/5
1. **What:**
   - 8-K Item 2.02 exhibits (EX-99.1 press releases with non-GAAP reconciliations, EX-99.2 slides, sometimes call transcripts).
   - DEF 14A proxies. Since FY2022 proxies they carry the **Item 402(v) pay-versus-performance table tagged in Inline XBRL (ECD taxonomy)**.
   - **N-PORT** monthly fund holdings (all positions including bonds, derivatives, loans).
   - 13F institutional equity holdings.
   - Form 4 insider trades.
   - EDGAR full-text search (efts.sec.gov) covers 2001+ text search, but is live-only.
2. **Access:** SEC, free, fair-access policy; blocked here.
3. **Formats:** HTML/ASCII/PDF exhibits (messy tables, images in decks). N-PORT is XML, and its structured data sets are 30 tables (CSVW schema). The PvP table is HTML plus iXBRL ECD tags.
4. **Depth:** 8-K 1990s+, DEF 14A 1990s+ (PvP tags 2023+), N-PORT 2019-09+, 13F 1999+ (structured 2013+).
5. **Breadth:** All registrants. N-PORT covers 17,513 funds (ZipLime).
6. **Join keys:** CIK, accession, CUSIP/ISIN/LEI (N-PORT), series/class IDs, ticker.
7. **Ground truth:**
   - Earnings release numbers ↔ subsequent 10-Q XBRL. Non-GAAP reconciliation tables must sum.
   - PvP: compensation actually paid (CAP) = SCT total − grant-date FV + adjustments (table footnotes). TSR is recomputable from prices and dividends.
   - N-PORT: Σ positions ≈ total investments; total assets − liabilities = net assets (reported fields).
8. **Benchmarks:** Finance Agent Benchmark touches 8-Ks (unverified scope). No PvP or N-PORT benchmark found.
9. **Mirrors:**
   - HF `TeraflopAI/SEC-EDGAR` (apache-2.0; listing shows 10-Q 132 GB, 10-K 92 GB, 20-F 30 GB, S-1 19 GB, 8-K 14.6 GB, Forms 3/4/5/144/S-8). The datasets-server sample shows `metadata_documents` with **only the primary document**, so **EX-99.1 coverage is unverified/likely absent**. CDN-blocked here.
   - HF `pierjoe/SEC-DEF14A-2005-2022`: MIT, 109,087 proxies, full text, 7.8 GB. Pre-PvP years mostly.
   - HF `alea-institute/kl3m-index-edgar-filings-8-k` (not inspected).
   - **N-PORT:** HF `ZipLime/fund-holdings-nport` (Apache-2.0, 145,630,731 positions, 341,049 monthly reports, 2019-09-30 → 2026-05-31) and HF `trader298/sec-nport` (CC0, 30 official tables, 2019Q4+, 9.45 GB).
   - 13F: HF `ZipLime/institutional-portfolio-13f`, Kaggle `jamesfromalphasmo/13f-institutional-holdings-sec-edgar` (CC0).
   - Form 4: HF `CyberMax-tools/sec-form4-insider-transactions`.
10. **Workflows:**
   - **W-A3a "Pay-versus-performance audit" (persona: compensation consultant or proxy-advisor analyst).** Steps:
     (i) Extract 2023–2026 PvP tables (ECD tags via robosystems or SEC).
     (ii) Recompute company and peer-group TSR from prices (C3) and dividends (ZipLime `corporate-actions`). Checkpoint: within ±1 pp of reported.
     (iii) Rebuild CAP from SCT total and equity-award FV adjustments in footnotes. Checkpoint: footnote adjustments sum to the reported CAP.
     (iv) Regress CAP on TSR and the company-selected measure.
     (v) Write a say-on-pay vote recommendation.
   - **W-A3b "Fund look-through and NAV tie-out" (persona: fund-administration or fund-of-funds risk analyst).** Steps:
     (i) For a fund-of-funds, pull monthly N-PORT holdings for parent and underlying funds.
     (ii) Checkpoint: Σ position values + other assets − liabilities = reported net assets.
     (iii) Look through to underlying securities by CUSIP and compute issuer, sector and duration exposure.
     (iv) Reconcile the adviser's 13F equity positions vs N-PORT equity sleeves.
     (v) Flag liquidity-bucket migrations and derivative notional.

### A4. State PUC rate-case filings (revenue-requirement models in live Excel)
1. **What:** Utility general rate case dockets. Several commissions **require native Excel with formulas intact**: Utah (Admin Code R746-700-22: "live" models with formulas and input data), Michigan (standard exhibits in native Excel with links active), FERC Order 884 for gas pipeline NGA §4 cases, and Ontario OEB's Revenue Requirement Work Form (Excel with macros). These are some of the few public, formula-rich, professional-grade finance spreadsheets.
2. **Access:** Docket systems per state (pscdocs.utah.gov, michigan.gov, rds.oeb.ca, etc.). Public records, but each docket portal is different. Scraping ToS varies (**unverified**).
3. **Formats:** xlsx/xlsm with cross-workbook links, plus PDF testimony and data-request responses. Very messy and huge.
4. **Depth:** Typically 2000s+ e-filing. Rate cases come every 2–4 years per utility.
5. **Breadth:** Hundreds of utilities across 50 states plus Canadian provinces.
6. **Join keys:** Utility name and docket number. Map to FERC respondent ID (A1) manually.
7. **Ground truth:** The model's own formulas, the commission's final order (approved revenue requirement), and Form 1 actuals for the test year.
8. **Benchmarks:** None found.
9. **Mirrors:** **None found** on HF, Kaggle or GitHub. All hosts are blocked from this container, so an out-of-container crawl is required.
10. **W-A4 "Intervenor adjustment to a filed revenue requirement" (persona: consumer-advocate analyst).** Steps:
    (i) Ingest the utility's filed RRM workbook plus Form 1 for the historical year.
    (ii) Checkpoint: the workbook's historical rate base ties to Form 1 sched 204/219 (A1).
    (iii) Apply 3 adjustments (remove CWIP, normalize storm O&M to a 5-year average, use the authorized ROE).
    (iv) Recalculate the revenue requirement through the workbook's own formula chain without breaking links.
    (v) Compare to the commission's final order.
    (vi) Write a testimony exhibit.

### A5. UK Companies House accounts (iXBRL). Millions of private-company and small-company accounts. ★
1. **What:** Statutory accounts filed electronically by UK companies. About 75% of the roughly 2.2M accounts filed per year are electronic. Mostly micro and small entities under FRS 105/102 "filleted" accounts (balance sheet only, often no P&L). Official: https://download.companieshouse.gov.uk/en_accountsdata.html (daily about 30 MB, monthly about 500 MB). Historic monthly archives start in 2008 (`historicmonthlyaccountsdata.html`), with a newer 12-month rolling-window statement (conflict noted in the CH guidance).
2. **Access:** Free bulk zips, "provided free of charge and not supported". Open Government Licence v3.0 per the Kaggle mirror card. API needs a free key. Blocked here.
3. **Formats:** Inline XBRL (.html), some plain XBRL (.xml), nested zips. Messiness (documented by the Kaggle mirror author):
   - prefix/namespace variants;
   - comma-decimal formats misread ×100–1000;
   - 29% of employee counts tagged in GBP;
   - bare `Creditors` total is often just one maturity bucket;
   - dashes mean nil;
   - 25%/20% of filings use multi-member or typed dimensional contexts;
   - a reporting-regime break in 2020–21;
   - **9.36% of repeated figures restated** later.
4. **Depth:** iXBRL is near-universal from 2014 (97%). Archives exist 2008/2010+. Daily and monthly refresh.
5. **Breadth:** All UK companies, about 5M+ on the register. 33.5M company-period rows (2014–2026).
6. **Join keys:** Company number (8 chars, leading zeros), period_end, SIC code (company data product), FCA/LEI (rare). Charity number for charitable companies (D8).
7. **Ground truth:** Balance-sheet identities (CurrentAssets − creditors<1yr = NetCurrentAssets; fixed assets + NCA = TotalAssetsLessCurrentLiabilities; TALCL − creditors>1yr − provisions = Equity = share capital + reserves). Comparative-year columns in the next filing give natural restatement checks.
8. **Benchmarks:** No LLM workflow benchmark found. HF `fabsssss/ixbrl-disclosure-benchmark` measures tagging coverage on one day of filings (8,856 filings); it is not an LLM task.
9. **Mirrors:**
   - Kaggle **`thomassimm/uk-company-accounts-wide-2014-2026`** (verified; OGL v3.0; 2.78 GB). Files: `accounts-wide-as_first_reported.parquet` (708 MB, 33,513,017 rows), `accounts-wide-latest.parquet` (782 MB, 36.7M rows), cell-level provenance parquet files and a column dictionary. Covers 152 monthly archives 2014-01→2026-08. Holds only 9 core concepts plus dimensional splits; the README says a full LONG companion (about 4,593 concepts) is published separately (**not found on Kaggle**).
   - Kaggle `rzykov/uk-corporate-data-company-house-2023` (1.19 GB, MIT; contents **unverified**).
   - Kaggle `crimsoneer/companies-house-company-data-product-2023-03-01` (register snapshot).
   - **Raw iXBRL documents are not mirrored.** They are needed if agents should read the rendered accounts.
10. **Workflows:**
   - **W-A5a "SME credit underwriting on filleted accounts" (persona: credit analyst at a UK challenger bank).** Steps:
     (i) Pull 5 years of filings for 50 applicants in one SIC code.
     (ii) Checkpoint: identity residuals per year; flag inconsistent filings.
     (iii) Compare as_first_reported vs latest to flag restated comparatives.
     (iv) Infer profit from the Δ retained earnings when no P&L is filed, with a dividend assumption.
     (v) Compute working-capital days proxies, gearing and cash runway.
     (vi) Score, set limits and write a credit memo with exceptions. Employee-unit anomalies must be detected.
   - **W-A5b "Private-comps screen for a buy-and-build" (persona: PE associate).** Universe-broad: filter about 30k companies by size band and growth in net assets and employees, de-duplicate group structures, apply size-threshold rules (small vs medium company exemptions), and produce a target long-list with data-quality caveats.

### A6. EU ESEF filings (IFRS iXBRL) via filings.xbrl.org
1. **What:** European Single Electronic Format annual reports (IFRS consolidated statements tagged in iXBRL, with a full report package), from FY2020. Repository by XBRL International: https://filings.xbrl.org (API `https://filings.xbrl.org/api/filings`, JSON-API; xBRL-JSON per filing).
2. **Access:** Free. The repository is "not complete". Some filings lack xBRL-JSON because of errors. **403 from this container.**
3. **Formats:** iXBRL XHTML report packages (multi-hundred-page annual reports), xBRL-JSON. Messiness: extension taxonomies anchored to IFRS, block-tagged notes, multi-language reports.
4. **Depth:** FY2020+, annual.
5. **Breadth:** Over 4,000 reports as of Sep 2022 (latest count found; current count unverified). EU/EEA plus UK filings.
6. **Join keys:** LEI, country, period end.
7. **Ground truth:** Calc linkbase in the report package, IFRS taxonomy relationships, prior-year comparatives.
8. **Benchmarks:** None found for LLM workflows.
9. **Mirrors:** **None found** on HF or Kaggle (searched "esef", "xbrl.org"). Kaggle `alexandrefrank/european-fundamental-stock-data` and `fliarbi/european-company-financials-2019-2025` are derived fundamentals (not inspected; the latter is CC BY-NC-SA). Python wrapper: `xbrl-filings-api` (PyPI).
10. **W-A6 "IFRS 16 lease-adjusted peer comps across 6 EU countries" (persona: buy-side credit analyst).** Steps:
    (i) Pull lease liabilities, right-of-use assets and lease interest from notes.
    (ii) Normalize EBITDA pre/post IFRS 16.
    (iii) Translate to EUR at period-end and average FX.
    (iv) Checkpoint: the calc linkbase holds after adjustments.
    (v) Produce a leverage table and memo.

### A7. Japan EDINET (annual securities reports, XBRL/iXBRL, J-GAAP/IFRS/US-GAAP)
1. **What:** FSA's EDINET disclosure system. Annual securities reports (有価証券報告書), quarterly and semiannual reports, **audit reports (AuditDoc, with KAMs)**, large-shareholding reports. API v2: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html (blocked here).
2. **Access:** Free API. **v2 requires a `Subscription-Key`** issued via an EDINET account (verified via FSA material). Rate limit undocumented (**unverified**). Content license: Public Data License (PDL) 1.0 per the EDINET terms cited by `range3/edinet-annual` and SakanaAI.
3. **Formats:** Zip packages with `PublicDoc/*_ixbrl.htm`, `.xbrl`, `_cal.xml`, `_def.xml`, `_pre.xml`, `_lab.xml`, `_lab-en.xml`, and `AuditDoc/` (verified in the Kaggle file list). Also PDFs. Japanese text, multiple GAAPs, extension elements.
4. **Depth:** XBRL from 2008. API window is about 10 years. Daily refresh.
5. **Breadth:** About 4,000 listed companies plus funds and unlisted reporting companies.
6. **Join keys:** EDINET code (E0xxxx), securities code (4-digit), JCN corporate number.
7. **Ground truth:** `_cal.xml` calc linkbase per filing, prior-period comparatives, audit report ↔ financial statement consistency.
8. **Benchmarks:** **EDINET-Bench** (SakanaAI, arXiv 2506.08762; fraud detection, earnings forecast, industry prediction as classification/regression tasks; HF `SakanaAI/EDINET-Bench`, PDL 1.0). Workflow-style use is not covered.
9. **Mirrors:**
   - Kaggle **`sirokujira/edinet2017` … `sirokujira/edinet2022`** (raw EDINET XBRL packages by day; edinet2022 lists about 55.8 GB; license field "Unknown" but source is PDL 1.0), plus `sirokujira/edinettaxonomy` and `sirokujira/edinetcodelist`.
   - HF `range3/edinet-annual` (2024 annual-report PDFs, 3,945 files, 3.2 GB, PDL 1.0).
   - HF `japan-ai-official/edinet-bench-*-curated`.
10. **W-A7 "J-GAAP→IFRS-comparable peer bridge with audit-risk overlay" (persona: Japan equities analyst at a global fund).** Steps:
    (i) For 10 peers mixing J-GAAP and IFRS, extract statements and the segment note.
    (ii) Checkpoint: the `_cal.xml` relations hold.
    (iii) Adjust J-GAAP goodwill amortization and extraordinary items to IFRS-like operating profit.
    (iv) Parse KAMs from AuditDoc and map them to the affected line items.
    (v) Compute adjusted ROIC and write the comps memo in English.

### A8. Korea DART (OpenDART; K-IFRS XBRL, separate and consolidated)
1. **What:** FSS electronic disclosure. OpenDART API: https://opendart.fss.or.kr (blocked here). `fnlttSinglAcntAll` returns full statements with XBRL account IDs. It also offers filing lists, report bodies and raw XBRL zips.
2. **Access:** Free key. **20,000 requests/day**, key not shareable (per third-party guides; official page unverified).
3. **Formats:** JSON/XML/XBRL zip. Korean labels. Separate (OFS) vs consolidated (CFS) variants. Filings lag period-end (use receipt date for point-in-time).
4. **Depth:** Structured financials from FY2015 (per a third-party guide). Filings back to 1999. Daily refresh.
5. **Breadth:** About 2,700 listed companies plus large unlisted ones.
6. **Join keys:** `corp_code` (8-digit), `stock_code` (6-digit), receipt number (`rcept_no`), `account_id`.
7. **Ground truth:** BS identity, OFS vs CFS reconciliation, quarterly YTD vs discrete quarter (Q4 = FY − 9M YTD).
8. **Benchmarks:** None found for workflows.
9. **Mirrors:** HF **`eddmpython/dartlab-data`** (CC BY 4.0; about 1.05 TB, 83,309 files, updated daily). Contents include `dart/finance/{stock_code}.parquet` (OpenDART XBRL BS/IS/CF/SCE), `dart/report`, `dart/docs` (report body text), `dart/allFilings/YYYYMMDD.parquet` (2015+), and `edgar/{finance,financeStmt,prices,…}` for about 1,000 US companies. **CDN-blocked here** (needs egress). HF `eddmpython/cleangov-local-budgets` (Korean local-government budgets).
10. **W-A8 "Chaebol affiliate credit review" (persona: Korean bank corporate-credit analyst).** Steps:
    (i) Pull OFS and CFS for a group's 6 listed affiliates for 5 years.
    (ii) Derive discrete Q4 from YTD (checkpoint).
    (iii) Reconcile OFS→CFS (intra-group eliminations estimate).
    (iv) Compute interest coverage and net debt/EBITDA.
    (v) Cross-check related-party transaction disclosures in report bodies.
    (vi) Write the group exposure memo.

### A9. India (BSE/NSE XBRL results, annual reports, MCA)
1. **What:** Listed-company quarterly results in XBRL (NSE "Integrated Filing – Financials" from quarter ended Mar-2025; BSE Excel utility→XBRL) and annual-report PDFs. MCA21 holds statutory filings for all companies (XBRL AOC-4).
2. **Access:** Exchange websites (per-filing XBRL links; no bulk feature found). MCA documents are paid per company (**unverified current fee**). Blocked here.
3. **Formats:** XBRL instances, PDFs (often scanned), Excel utilities.
4. **Depth:** XBRL results since about 2011–2018 (unverified).
5. **Breadth:** About 5,000 BSE and 2,000+ NSE listed companies. MCA covers about 1.5M+ active companies (unverified).
6. **Join keys:** ISIN, scrip code, symbol, CIN.
7. **Ground truth:** XBRL calcs. Results ↔ annual report.
8. **Benchmarks:** HF `sohomghosh/MiMIC_Multi-Modal_Indian_Earnings_Calls_Dataset` (calls, not statements).
9. **Mirrors:** No bulk statement mirror found. Market-side mirrors: Kaggle `tanay001/nseindia-futures-options-daily` (C5), HF `tickertruthorg/nse-india-security-master`.
10. A workflow is not recommended until a scrapable bulk path is confirmed.

### A10. China CNINFO, Canada SEDAR+, Australia ASX
- **CNINFO (cninfo.com.cn):** A-share announcements and periodic-report PDFs. No HF/Kaggle bulk mirror found (HF `smalltalk96/cninfo_stock_filings` has only a README). Paid scrapers on Apify. Copyright and ToS caveats. Blocked here.
- **SEDAR+:** The **Terms of Use prohibit "scraping or the use of any automated means to use or reproduce multiple pieces of Public Information"**. Viewing is limited to the browser. **Exclude.**
- **ASX announcements:** No bulk API found. HF `mktmind/asx-lake` holds about 12k "served cells" from 63 ASX mining issuers' PDFs (license "other"). Kaggle `techsalerator/corporate-actions-data-australia-techsalerator`. Low priority.

### A11. Indonesia IDX Excel financial statements (new find; spreadsheet-native disclosures)
1. **What:** Financial statements of IDX-listed companies from the exchange's **Excel-based submission format**: statement of financial position, P&L/OCI, cash flows, changes in equity.
2. **Access:** HF **`Azzindani/IDX_Financial_Statements_Excel`** (CC BY 4.0; `Financial_Statement_2015_2021_Excel.zip` and `Financial_Statement_2021_2025_Excel.zip`, 5.37 GB total). Also `Azzindani/IDX_Financial_Statements` (processed), HF `horelulus/IDX_Financial_Statements2015-2025Q2`, Kaggle `kalkulasi/financial-statement-data-idx-2020-2023`. CDN-blocked here except via Kaggle.
3. **Formats:** Native Excel workbooks with Indonesian/English bilingual labels and a PSAK (IFRS-converged) structure. The workbook format itself is the disclosure (unverified detail).
4. **Depth:** 2015–2025, quarterly and annual.
5. **Breadth:** About 900 listed companies (unverified).
6. **Join keys:** IDX ticker.
7. **Ground truth:** BS identity, CF roll, equity roll-forward across columns.
8. **Benchmarks:** None found.
9. **Mirrors:** As above.
10. **W-A11 "Equity roll-forward and dividend capacity" (persona: Jakarta-based equity analyst).** Steps:
    (i) Ingest 8 quarters of workbooks.
    (ii) Checkpoint: the SCE roll-forward ties to BS equity.
    (iii) Compute retained earnings available and payout.
    (iv) Translate IDR to USD.
    (v) Run a peer screen.

### A12. Earnings-call transcripts (are there free, legally clean sources?)
- **Clean sources:** Company IR sites (per company), and **8-K exhibits where companies file the transcript** (for example ACS 2003 and CSC 2010 file transcripts as EX-99.1). Coverage is sparse and the copyright position of filed transcripts is unclear (no explicit license).
- **HF/Kaggle sets have provenance risk:**
  - HF `kurry/sp500_earnings_transcripts`: "MIT"; 33k+ transcripts 2005–2025; source not stated, likely a vendor API.
  - HF `glopardo/sp500-earnings-transcripts`: 20,681 transcripts, 2013Q2–2025Q1, 496 companies; used in ECB Working Paper 3093; license None.
  - HF `jlh-ibm/earnings_call`: 188 transcripts; CC0 label, but the text comes from Thomson Reuters Eikon.
  - Kaggle `tpotterer/motley-fool-scraped-earnings-call-transcripts`: Unknown license, scraped.
  - S&P's Kensho SPGISpeech is gated.
- **Recommendation:** Use only as an auxiliary narrative channel, with legal review. Do not make transcripts load-bearing for ground truth.

### A13. Insurance statutory statements (NAIC)
- NAIC is not a government agency. Basic financial and complaint info is free via the NAIC Consumer Information Source. **Detailed annual statement pages cost a nominal fee per download** (ND Insurance Dept page). Bulk statutory data is a paid NAIC product. Some state departments post PDFs (unverified coverage).
- **Not free in bulk. Exclude** unless licensed. Public-insurer GAAP data is available via SEC (A2).

### A14. Audit and oversight metadata (PCAOB Form AP, AAER, restatement events)
- **PCAOB AuditorSearch / Form AP:** engagement partner, audit firm, and other-firm participation % per issuer audit. CSV download from pcaobus.org (blocked here; no mirror found). HF `emperor-mew/pcaob-inspections` exists (not inspected).
- **SEC AAERs:** HF `yiyna/aaer` exists (not inspected).
- **Restatement 8-K Item 4.02:** HF `hammerlabs/sec-restatement-8k-402` (not inspected).
- Useful as **labels/joins** for A2 forensic workflows rather than as standalone environments.

---

## (b) ACCOUNTING-OPERATIONS DATA (real ledgers, transactions, invoices)

### B1. Enron spreadsheets and emails (real trading, risk, accounting and logistics workbooks with email context). ★
1. **What:**
   - The FERC-released Enron email corpus (about 150 custodians) with **tens of thousands of real Excel attachments**: desk P&L, position reports, price curves, deal reports, capital-book roll-forwards, tax reserves, bonus pools, budgets and plans.
   - Verified filenames in mailbox `kitchen-l` (Louise Kitchen, President of Enron Americas; role is background knowledge): "Pwr west P&L.xls", "West Position0209-01.xls", "West Prices0209-01.xls", "Capital Book Rollforward.xls", "AES Transaction Tax Reserve.xls", "Weekly Deal Report 6-20-01 A.xls", "2002 Plan Worksheet Texas Orig.xls", "Turbine Position Report 092101.xls", "Asset Marketing WIP Report (9-04-01).xls".
   - Hermans & Murphy-Hill (ICSE/MSR 2015) extracted 15,770 spreadsheets, 9,120 with formulas. VEnron/VEnron2 (TU Graz) add **version groups** (successive versions of the same workbook).
2. **Access:** The corpus has been public since the FERC investigation. No explicit license; widely used in research (**license status unverified**). PII exists in the original EDRM set (SSNs, birthdates). The Nuix-cleaned version and the HF PST mirror claim privacy reductions.
3. **Formats:** BIFF .xls (Excel 97–2003), some BIFF2/SYLK/TSV/HTML-as-XLS (per SheetJS), PST/EML. Extreme messiness: multi-block sheets, hard-coded numbers mixed with formulas, external links, Excel date serials (for example 37173 = 2001-10-09), hidden rows, many near-duplicate daily versions. Note: xlrd reads values only; formulas need LibreOffice or a BIFF formula parser.
4. **Depth:** 1997–2002 (static; no refresh).
5. **Breadth:** One entity (Enron and subsidiaries), but about 150 custodians across trading, origination, logistics, legal, accounting, and the executive office.
6. **Join keys:** Email message-ID ↔ attachment hash. Custodian. Deal numbers and counterparty names inside sheets. Possibly Portland General Electric (an Enron subsidiary and FERC Form 1 respondent) ↔ PUDL Form 1 (**speculative link, unverified**).
7. **Ground truth:**
   - Workbook formulas: recompute and compare to cached values.
   - **Version pairs** (VEnron, or daily file series such as "West Position MMDD-01") give before/after ground truth for roll-forward tasks.
   - Email threads state what changed or why (Finch used exactly this).
   - Totals inside P&L and position sheets.
8. **Benchmarks:** **Already used.** **Finch / FinWorkBench** (HF `FinWorkBench/Finch`, arXiv 2512.13168, ACL 2026 Findings) derives 172 F&A workflows from Enron emails plus versioned spreadsheets plus EUSES. Spreadsheet-research corpora (Enron error corpus, VEnron) are also built on it. Differentiation requires deeper chains, different custodians and desks, cross-file reconciliation, and pairing with external real data (for example FERC EQR or Form 1).
9. **Mirrors:**
   - HF **`enronarchive/mail`**: per-mailbox folders `mail/{custodian}/attachments/{hash}_{original filename}` plus `mail/{custodian}/index.json` (email metadata; 34.5 MB for kitchen-l). 155 mailbox dirs. In 6 sampled mailboxes (kitchen-l, lay-k, skilling-j, delainey-d, germany-c, farmer-d) there are **8,258 .xls attachments** (farmer-d 4,376; germany-c 2,170). Small files download in-container; large files and index.json hit the blocked CDN.
   - GitHub **`SheetJS/enron_xls`**: `git clone` works here. 20,276 files under `edrm/` (MD5-deduplicated from the EDRM v2 set, opaque names) and 617 under `nuix/` (from the Nuix-cleaned PSTs).
   - HF `intellekthq/enron-ferc-pst`: EDRM v2 in native PST, 171 PSTs, 1,226,178 messages, **453,832 attachments**, 83 GB, privacy-modified, license "other". Readable with the `duckdb-pst` extension.
   - Original research release: figshare article 1222882 (Hermans & Murphy-Hill) and felienne.com/enron (blocked or unverified live).
   - Text-only email mirrors: HF `corbt/enron-emails`, Kaggle `jivfur/enron-emails`.
   - **FUSE** (Barik et al. MSR 2015; 249,376 Common-Crawl spreadsheets; Zenodo record 581678, `fuse.zip` 9.4 GB; blocked here; web-scraped, mostly not finance-ops). **Sheetpedia** (NeurIPS 2025, 300K spreadsheets) integrates FUSE (mirror not checked).
10. **Workflows:**
   - **W-B1a "Desk month-end close and P&L explain" (persona: product controller for the West Power desk, Oct 2001).** Steps:
     (i) Ingest a daily series of position, price and desk-P&L workbooks plus the related emails.
     (ii) Recompute daily MTM change = Σ position × Δcurve + new-deal origination + realized settlements. Checkpoint: within tolerance of the desk P&L total per day.
     (iii) Attribute the residual (unexplained P&L) and identify reserve or prudency moves.
     (iv) Roll the Capital Book forward month to month (beginning + additions − terminations = ending). Checkpoint: ties to the "Capital Book Rollforward" sheet.
     (v) Draft month-end JEs for unrealized MTM and reserves.
     (vi) Write variance commentary for management.
     Concepts: MTM accounting, forward curves, P&L attribution, reserves, roll-forwards, close JEs.
   - **W-B1b "Gas volume accounting and imbalance accrual" (persona: logistics or volume-management accountant; mailbox farmer-d, role inferred, sheet contents unverified).** Steps:
     (i) Reconcile nominations vs scheduled vs actual meter volumes by day and meter.
     (ii) Compute imbalances and cash-out at index prices.
     (iii) Accrue unbilled volumes at month-end.
     (iv) Reconcile to the pipeline-statement spreadsheet.
     (v) Write an exceptions log. Checkpoints: volume balance per meter-day, accrual totals.

### B2. FERC Electric Quarterly Reports (EQR): transaction-level wholesale power sales ledger. ★
1. **What:** Every FERC-jurisdictional seller reports its contracts and **individual transactions**: counterparty, product (energy, capacity, ancillary), delivery point, price, quantity, total charges, from 5-minute spot to multi-year PPAs. Docs: https://docs.catalyst.coop/pudl/en/stable/data_sources/ferceqr.html
2. **Access:** PUDL S3, public, verified: `ferceqr/core_ferceqr__transactions/{YYYYqN}.parquet` (52 files, **2013q3→2026q2, 125.4 GB total**; 2013q3 368 MB, 2026q1 3.9 GB), `ferceqr/core_ferceqr__contracts/…` (about 2–3 MB each), `core_ferceqr__quarterly_identity`, `core_ferceqr__quarterly_index_pub`. CC BY 4.0.
3. **Formats:** Parquet; FERC's raw source is nested zips of CSV. Messiness: seller-reported free-text counterparty names, unit inconsistencies ($/MWh vs $/MW-month), booked-out transactions, rate units, time-zone fields.
4. **Depth:** 2013Q3–2026Q2, quarterly.
5. **Breadth:** About 2,000+ sellers (utilities, IPPs, marketers; **count unverified**). Universe-broad.
6. **Join keys:** FERC CID (seller/buyer), contract unique ID, `utility_id_ferc1_xbrl` (FERC CID) to Form 1, balancing authority, hub/point of delivery.
7. **Ground truth:**
   - Transactions roll up to contracts.
   - Quantity × price = total charge (row-level identity, with exceptions as test cases).
   - Cross-filer: seller A's sales to buyer B vs **B's Form 1 sched 326 purchased power from A** (annual MWh and $). Independent, real, imperfect reconciliation, which is great for variance explanation.
8. **Benchmarks:** None found.
9. **Mirrors:** PUDL S3 (verified in-container), Zenodo DOIs referenced under `zenodo/ferceqr/`.
10. **Workflows:**
   - **W-B2a "Purchased-power three-way reconciliation" (persona: utility power-settlements accountant or FERC audit staff).** Steps:
     (i) For utility U (FY2024), list Form 1 sched 326 purchases by seller (MWh, demand $, energy $, other $).
     (ii) Aggregate EQR transactions where buyer = U by seller and quarter.
     (iii) Map counterparty names (fuzzy match against FERC CIDs).
     (iv) Reconcile MWh and $. Checkpoint: per-seller variance table.
     (v) Explain variances: capacity vs energy classification, booked-out deals, affiliate exchanges, accrual timing, and RTO-cleared purchases not in EQR.
     (vi) Propose adjusting entries and an audit finding.
     Concepts: accrual vs settlement, demand vs energy charges, affiliate transactions, ledger-to-subledger reconciliation.
   - **W-B2b "PPA portfolio valuation" (persona: corporate development analyst).** Steps:
     (i) Extract a seller's long-term contracts and realized prices from EQR.
     (ii) Build contract-level cash-flow projections.
     (iii) Discount at a WACC.
     (iv) Compare realized price vs index (`quarterly_index_pub`).
     (v) Produce a mark-to-model summary.

### B3. Government accounts-payable, vendor-payment and P-card ledgers (real AP transactions). ★
1. **What:** Real disbursement ledgers with vendor, amount, date, department, fund/object code, and sometimes the PO/contract link.
   - **San Francisco** vendor payments: vouchers 1.43 GB plus purchase-order summary 400 MB, with Excel/PDF data dictionaries.
   - **Chicago** payments.
   - **Missouri "Checkbook"** FY2010–FY2017: about 1.8 GB of quarterly CSVs, obtained via a records request by the Show-Me Institute.
   - **Oklahoma** state and higher-ed purchase-card transactions (FY2014 file).
   - **Canada** Receiver General accounting transactions (bilingual).
   - **New Hampshire** state spending.
   - **USAspending** award transactions (FY2007+, all federal agencies).
   - UK councils' >£500 spend files (Local Government Transparency Code): no mirror found.
2. **Access:** Open-data portals (Socrata, gov.uk, etc.) are blocked here. **Kaggle mirrors work.** Licenses: SF "Other (specified)" (city open data), Chicago CC0, Missouri CC0, NH CC0, Oklahoma "Other", Canada "Other" (likely OGL-Canada, unverified), USAspending "other" on HF.
3. **Formats:** CSV/XLSX. Messiness: vendor-name variants, negative and adjusting vouchers, fiscal-year vs calendar periods, recoded departments, truncated descriptions, duplicate vouchers.
4. **Depth:** SF snapshot 2019 (Kaggle; the city updates weekly). Missouri FY2010–2017. USAspending FY2007–present (HF updated 2026-10-16).
5. **Breadth:** Single government entity each (one entity deep), or all federal agencies (USAspending, universe-broad).
6. **Join keys:** Vendor name and ID, PO/contract number (SF voucher ↔ PO summary), department/fund/account codes; USAspending award ID, UEI/DUNS, CFDA.
7. **Ground truth:**
   - SF: **PO summary amounts vs Σ vouchers per PO** (natural three-way-match style check).
   - Fiscal totals vs published budgets or ACFRs (ACFRs not mirrored).
   - Duplicate and split-purchase patterns are discoverable but need expert labels.
   - USAspending: transaction-level obligations sum to award totals.
8. **Benchmarks:** None found (USAspending appears in generic data-analysis sets: HF `vibrantlabsai/usaspending-recon`, not inspected).
9. **Mirrors (verified IDs):**
   - Kaggle `san-francisco/sf-vendor-payments` (1.83 GB).
   - Kaggle `chicago/chicago-payments` (CC0).
   - Kaggle `tfshiloh/csv-version-missouri-checkbook-fy2010fy2017` (CC0).
   - Kaggle `thedevastator/oklahoma-state-purchase-card-spending-fiscal-yea` (83 MB).
   - Kaggle `imtkaggleteam/receiver-general-accounting-transactions` (Canada, 0.9 MB).
   - Kaggle `katedavis/state-of-new-hampshire-spending-data` (CC0).
   - Kaggle `shivd24coder/canadian-government-open-transactions-dataset` (CC0).
   - HF `abigailhaddad/usaspending-bulk-awards` (92 GB parquet, contracts 297 cols / assistance 112 cols, partitioned by FY/agency; CDN-blocked here).
10. **Workflows:**
   - **W-B3a "AP continuous-audit sweep" (persona: internal auditor in the City Controller's office).** Steps:
     (i) Load SF vouchers plus PO summary for FY2016–FY2019.
     (ii) Checkpoint: Σ vouchers per PO ≤ PO amount. List overruns.
     (iii) Detect duplicate payments (same vendor ± name variants, same amount within 30 days).
     (iv) Detect split purchases under approval thresholds.
     (v) Run Benford and outlier tests by department.
     (vi) Clean up vendor-master fuzzy duplicates.
     (vii) Write a findings report with $ at risk.
     Concepts: three-way match, segregation of duties, cut-off, vendor master controls.
   - **W-B3b "P-card policy compliance and accrual" (persona: state controller staff).** Steps:
     (i) Oklahoma P-card: MCC/vendor category spend.
     (ii) Flag weekend, holiday and split transactions.
     (iii) Accrue June-posted July-statement charges for fiscal year-end cut-off.
     (iv) Summarize agency-level exceptions.

### B4. Receipts and invoices (real scanned documents)
1. **What / IDs:**
   - **SROIE** (ICDAR 2019; real Malaysian receipts with company, date, address, total): HF `jsdnrs/ICDAR2019-SROIE`, `darentang/sroie`, Kaggle `urbikn/sroie-datasetv2`.
   - **CORD v2** (real Indonesian restaurant receipts, line items, subtotals and tax): HF `naver-clova-ix/cord-v2`.
   - **Jens Walter "my receipts"** (CC0, real personal business-trip receipts across countries, scanned PDFs 2017+): Kaggle `jenswalter/receipts` (256 MB) and GitHub `JensWalter/my-receipts` (clone works).
   - **RVL-CDIP invoice class** (real 1980s–90s scanned invoices from tobacco-litigation documents, IIT-CDIP): HF `chainyo/rvl-cdip-invoice`, `aharley/rvl_cdip`.
   - **XRechnung** (official German e-invoice test-suite invoices; XML is the gold, 34 invoices): HF `bks-lab/xrechnung-invoice-fields`. These are **test fixtures, not real commerce**.
   - Many "invoice" sets on HF are synthetic. Excluded.
2. **Access:** Free. Licenses: SROIE/CORD research; Jens Walter CC0; RVL-CDIP research.
3. **Formats:** JPG/PDF scans, OCR boxes, JSON labels. Messiness: skew, thermal fade, multilingual, currencies.
4. **Depth:** Static.
5. **Breadth:** Thousands of documents. Weak entity linkage.
6. **Join keys:** Merchant name, date, total. Almost none across sets.
7. **Ground truth:** Labelled fields. CORD subtotal + tax = total (internal arithmetic). XRechnung XML.
8. **Benchmarks:** **Heavily used** for document-AI (SROIE, CORD, RVL-CDIP, Kleister). Low differentiation alone.
9. **Mirrors:** As above.
10. **W-B4 "Multi-currency T&E expense report and VAT reclaim" (persona: travel and expense accountant).** Steps:
    (i) Ingest one traveler-year of Jens Walter receipts (multi-country).
    (ii) Extract merchant, date, gross, VAT and currency.
    (iii) Convert at the ECB/Treasury daily FX of the transaction date (C6).
    (iv) Apply per-diem and policy caps.
    (v) Compute reclaimable foreign VAT by country.
    (vi) Post the expense JE by GL account. Checkpoints: extracted totals per receipt, FX-converted totals, VAT by country.
    Note: there is no external ground truth beyond the receipts themselves; expert-labelled answers are needed.

### B5. Bank statements and transaction ledgers (real, anonymized)
- **Berka / PKDD'99 Czech bank** (real anonymized retail-bank data, 1993–1998): Kaggle **`marceloventura/the-berka-dataset`** (CC0 label; verified files `account.csv, card.csv, client.csv, disp.csv, district.csv, loan.csv, order.csv, trans.csv` (69 MB); trans columns `trans_id, account_id, date(YYMMDD), type(PRIJEM/VYDAJ), operation, amount, balance, k_symbol(SIPO/UVER/POJISTNE…), bank, account`). Natural ground truth: **running `balance` identity**; loan status vs payment history; standing orders (`order.csv`) vs actual debits. 4,500 accounts and 682 loans (counts from literature, **unverified**). Czech codes add realistic messiness. Downloaded in-container. Also used by household workflows (D).
- HF `tusharshah2006/bank_statements_transactions`: images of Indian bank statements (Bank of Baroda, HDFC, IOB, UCO). **Provenance and consent unknown. Avoid.**
- IBM AML (`ealtman2019/ibm-transactions-for-anti-money-laundering-aml`), BankSim, PaySim and `mindweave/*` are **synthetic. Exclude.**
- **W-B5 "Retail-bank statement reconstruction and affordability review" (persona: bank credit-risk analyst).** Steps:
  (i) For 200 loan accounts, rebuild monthly statements from trans.
  (ii) Checkpoint: balance continuity.
  (iii) Classify inflows (salary-like recurring credits) and outflows (SIPO household payments, insurance, loan UVER).
  (iv) Reconcile scheduled loan installments (loan.csv payments × months) vs observed debits.
  (v) Compute DTI and cash buffers.
  (vi) Compare with loan status A/B/C/D and write a model memo.

### B6. Bankruptcy monthly operating reports (MORs) and DIP budget variance
- Real chapter 11 MORs (UST forms with cash receipts and disbursements, bank reconciliations, projected-vs-actual) and 13-week DIP budget variance exhibits (for example a 2026 YesCare/CHS cash-collateral exhibit with budget, actual, variance and variance % columns). Hosts: PACER, CourtListener RECAP (`storage.courtlistener.com`), claims agents (Kroll, Stretto, Epiq, Omni). **All blocked here. No dataset or mirror found.** Excellent workflow material (restructuring advisor: variance report → covenant test → JE), but it requires an out-of-container PDF crawl. Scanned and inconsistent formats.

### B7. Real SMB sales ledgers
- **UCI Online Retail II** (real UK online gift-ware wholesaler; about 1M invoice lines Dec 2009–Dec 2011; invoice no., StockCode, qty, price, customer, country; credit notes prefixed "C"): Kaggle `mashlyn/online-retail-ii-uci` (CC0 label; UCI's own license CC BY 4.0, unverified), HF `attik/Online-Retail-II-UCI` (CSV 0.09 GB).
- **Olist Brazilian e-commerce marketplace** (about 100k real anonymized orders 2016–2018 with payments (installments, vouchers), freight, sellers, reviews): Kaggle `olistbr/brazilian-ecommerce` (**CC BY-NC-SA 4.0**; the NC term may conflict with commercial benchmark use).
- Ground truth: invoice-line sums; cancellations net against originals; payments sum to order totals (Olist).
- Benchmarks: widely used for analytics tutorials; no finance-workflow benchmark found.
- **W-B7 "Fractional-CFO monthly pack for a wholesaler" (Online Retail II).** Steps:
  (i) Monthly net revenue after credit notes. Checkpoint: Σ lines.
  (ii) Returns-reserve estimate from the historical credit-note lag.
  (iii) Customer concentration and cohort retention.
  (iv) Price-volume-mix variance vs prior year.
  (v) GBP vs non-UK revenue split (FX exposure) and a VAT-registration sanity check.
  (vi) Write the board commentary.

---

## (c) MARKET DATA FOR INVESTMENT WORKFLOWS

### C1. FRED / ALFRED vintage macro data
1. **What:** FRED has 800k+ series. **ALFRED** archives historical vintages (real-time data as published on each date): https://alfred.stlouisfed.org.
2. **Access:** Free API key. Some series are third-party copyrighted (FRED terms; detail unverified). **Blocked here.**
3. **Formats:** CSV/JSON/XLS via API. Vintage dates (realtime_start/end).
4. **Depth:** Decades. ALFRED vintages from about 2006 onward for many series (older for key series).
5. **Breadth:** US plus international macro.
6. **Join keys:** Series ID, observation date, vintage date.
7. **Ground truth:** Vintages are exact. Revision triangles. Annual revisions.
8. **Benchmarks:** Used in forecasting research (FRED-MD); no agent benchmark found.
9. **Mirrors:** **No ALFRED vintage mirror found** on HF or Kaggle. HF `THULab/fred_md` and `THULab/fred_md_2025` are single snapshots (Monash TSF conversion; no vintages). R package `onnokleen/alfred` on GitHub needs an API key. **Workaround for corporate "vintages":** companyfacts `filed` dates (A2) and UK `as_first_reported` vs `latest` (A5) give real point-in-time revision structure without ALFRED.
10. **W-C1 "Real-time policy-rule backtest" (persona: macro strategist).** Steps:
    (i) Pull GDP, core PCE and unemployment vintages.
    (ii) Compute output gaps as known at each FOMC date vs latest data.
    (iii) Compute Taylor-rule rates for both and the revision-driven error.
    (iv) Relate them to the 2y Treasury yield (C6).
    Checkpoints: vintage values on 5 named dates. **Requires out-of-container fetch.**

### C2. Kenneth French Data Library (factors and portfolios)
- **Kaggle `nikitamanaenkov/famafrench-factors-and-portfolios`** (CC BY 4.0 label; 787 MB; FF3/FF5/MOM for US, Developed, regional; size/BM/OP/Inv sorts; industries; built from the 202508 CRSP vintage per the file headers). HF `krishnakamath/fama_french_data` (small). Original site blocked. The library is free; its redistribution terms are not stated (**unverified**). Ground truth: factor definitions are reproducible only with CRSP (not free), so these files serve as **reference inputs**, not targets. Note also that French data itself gets revised across vintages.
- **W-C2 "Manager due-diligence factor attribution" (persona: allocator analyst).** Steps:
  (i) Compute monthly returns of a mutual fund from N-PORT holdings × prices (A3 + C3) or from NAV.
  (ii) Regress on FF5+MOM.
  (iii) Compute alpha t-stat and rolling betas.
  (iv) Look through to sector tilts.
  (v) Write the IC memo. Checkpoint: replicated holdings-based returns vs NAV returns.

### C3. Equity prices (stooq, Yahoo-derived, others)
- Kaggle `antonhyonhi/stock-market-dataset-stooq-sec` (MIT label; 1.59 GB; stooq prices plus SEC EPS).
- HF `eddmpython/dartlab-data` `edgar/prices` (about 1,000 US companies).
- HF `no-ry/world-stock-prices-daily-updating`.
- Many Yahoo-derived sets (for example Kaggle `sachingupta26/yfinance-stock-data`). **Yahoo's ToS restrict redistribution. Avoid.**
- Stooq's terms are unverified.
- Survivorship and adjustment caveats: ZipLime `corporate-actions` documents a real split-adjustment trap (Deckers P/E 1.8 from mixing unadjusted EPS with adjusted prices).
- Pair prices with HF **`ZipLime/security-master`** (Apache-2.0; 23,553 filers, 144,054 identifier spans, ticker↔CIK↔CUSIP history 1960–2026) and **`ZipLime/corporate-actions`** (391,639 dividends, 5,619 splits, 2005–2026, from SEC data; no ex/record/pay dates).

### C4. Crypto exchange data
- **Binance public klines** mirrored on HF: `vaquum/binance_btcusdt_{1m,15m,1h,2h,4h}_klines`, `HaianCao/Binance-Public-OHLCV`, `rogerdehe/mktdata-binance-2026`, `predict-quant/binance-future-orderbook`.
- Kaggle `binance/binance-crypto-klines` (CC0; 1-minute klines 2017–2018; appears to be an official Binance account, **unverified**) and Kaggle `jorijnsmit/binance-full-history` (28 GB).
- Original data.binance.vision is blocked here.
- Ground truth: OHLCV consistency and trade aggregation.
- **W-C4 "Digital-asset treasury accounting under ASU 2023-08" (persona: corporate controller).** Steps:
  (i) Record a company's BTC/ETH purchase lots.
  (ii) Fair-value them at quarter-end (exchange close).
  (iii) Compute realized gains (FIFO vs specific-ID).
  (iv) Calculate deferred tax on unrealized gains.
  (v) Produce disclosure tables (roll-forward of holdings). Checkpoint: roll-forward ties.

### C5. Options chains (free historical)
- Kaggle `kylegraupe/spy-daily-eod-options-quotes-2020-2022` (CC0 label; 1.28 GB). Similar files exist for AAPL (`kylegraupe/aapl-options-data-2016-2020`) and TSLA. **Upstream source unverified; likely vendor EOD data, ToS risk.**
- **Kaggle `tanay001/nseindia-futures-options-daily`** (CC0 label; 9.56 GB; **NSE official daily F&O bhavcopies** 2000-06-12→2020-08-31: OHLC, OI and volume by expiry and strike; exchange-published data).
- HF `thetrademarkk/india-index-options-1m`, `rissin/nse-options-intraday`, `gauss314/options-IV-SP500`.
- Cboe free data (VIX history, put/call ratios) is subject to Cboe website terms. Detailed history is paid via DataShop. Blocked here.
- Ground truth: **put-call parity** (C − P = S − K·e^{−rT} adjusted for dividends) with Treasury yields (C6), no-arbitrage bounds, and expiry settlement values.
- **W-C5 "Hedged book P&L explain and IV surface QC" (persona: derivatives risk analyst).** Steps:
  (i) Build the daily SPY IV surface.
  (ii) QC quotes via parity residuals and bounds. Checkpoint: count of violations.
  (iii) Compute Greeks for a sample book.
  (iv) Decompose daily P&L (delta, gamma, vega, theta, residual).
  (v) Run a VaR backtest and write the risk report.

### C6. Treasury yield curves
- HF `Farmaanaa/us_treasury_yield_curve_daily` (CC BY 4.0; 1990→2026; 69,600 observations; Persian-language card; source home.treasury.gov). Kaggle `liamhealy/us-yield-curves` (Apache-2.0; 1990–2023). Kaggle `odezi45/daily-treasury-real-yield-curve-rates`. Kaggle `allratestoday/central-bank-exchange-rates` (FX 1914→today; license "Other", unverified).
- Ground truth: par-curve bootstrapping consistency.
- Use as a **supporting input** for discounting, parity and FX tasks.

### C7. CFTC Commitments of Traders
- **Kaggle `arimancy/cftc-commitments-of-traders-weekly`** (CC BY 4.0; 1986→last Friday; all report families (legacy, disaggregated, TFF) harmonized with release provenance, including the Oct–Dec 2025 appropriations-lapse backfill). HF `Chainticks/cftc-cot` (2026 partitions). HF `ZipLime/commitments-of-traders`. Kaggle `xoomar/cftc-commitments-of-traders`.
- The CFTC source is public domain.
- Ground truth: long − short = net; Σ categories = open interest.
- **W-C7 "Positioning signal and hedge-ratio review" (persona: commodity strategist at a corporate treasury).** Steps:
  (i) Compute managed-money net and COT index for crude, corn and copper.
  (ii) Relate them to futures returns.
  (iii) Size the hedge program.
  (iv) Write the treasury memo.

### C8. FINRA short interest, Nasdaq symbol files
- **FINRA short interest:** an HF `ZipLime/us-short-interest` audit (13 Sep 2026) says **FINRA terms forbid the redistribution pattern**. HF `FinzData/finra-short-interest` offers a 12-month sample (522,296 rows, license "other"). Use only within ToS. Exclude from redistributed environments.
- **Nasdaq Trader symbol directory:** nasdaqtrader.com is blocked. Alternatives: SEC company_tickers (HF `DenyTranDFW/SEC_Company_Tickers_Exchange`) and the ZipLime security master.

---

## (d) HOUSEHOLD / SMB / NONPROFIT FINANCE

### D1. IRS Statistics of Income (SOI) tables
- Official irs.gov is blocked. Mirrors: Kaggle `wpncrh/zip-code-income-tax-data-2014` (CC0; ZIP-level individual income data 2014), `dmwvanity/2016-soi-tax-stats`, `namratanyam/wealth-segmentation-of-u-s-zip-codes`. These are aggregate tables, so they serve as benchmarks and inputs, not entities. Ground truth: table totals and cross-tab sums.

### D2. Fed Survey of Consumer Finances (SCF)
- federalreserve.gov is blocked. Kaggle mirrors: `sayem01k/survey-of-consumer-finances` (49 MB, Apache-2.0 label), `nasimetemadi/survey-of-consumer-finances-scf` (2.7 MB, likely the summary extract), `syntheticprogrammer/survey-of-consumer-finances-2022`, `allankirwa/survey-of-consumer-finances-data`.
- Microdata uses 5 implicates and replicate weights, which creates realistic statistical complexity. Natural checks: published Fed percentile tables (not mirrored).

### D3. BLS Consumer Expenditure Survey (CEX)
- bls.gov is blocked. Only small table extracts were found (Kaggle `danicacortez/bls-consumer-expenditure-survey-2023-2024`, 20 KB). **PUMD microdata mirror not found.**

### D4. CFPB consumer complaints
- HF **`Mouwiya/cfpb-consumer-complaints`** (1.03 GB parquet from the official CSV; license "other"; the source is public domain). HF `CFPB/consumer-finance-complaints` (loader script, 2024). Narrative text plus company, product, issue and response.
- Join to lenders via company name. Joins to HMDA by LEI are approximate.
- Benchmarks: used for text classification (FinBen-style).

### D5. HMDA and loan-level credit data
- HMDA LAR: Kaggle `vigneshwaransundar/hmda-modified-loanapplication-register-lar-2025` (CC0 label, 457 MB), `yangyangzhu0412/2021-hmda` (1.6 GB).
- LendingClub: Kaggle `wordsforthewise/lending-club` (CC0 label; 2007–2018 Q4, 1.36 GB; real loans with payment outcomes).
- Fannie Mae / Freddie Mac loan performance: Kaggle mirrors exist (`qhhuang/fannie-mae-single-family-loan-performance`, `jeromeblanchet/fannie-mae-freddie-mac-public-use-database`), but **the agencies' terms require registration and restrict redistribution (unverified). Avoid.**

### D6. SBA PPP and 7(a) loans (SMB)
- PPP FOIA loan-level: Kaggle `nflovejoy/paycheck-protection-program-loan-data` (CC0), `govtrades/sba-paycheck-protection-program-loan-data`, `danb91/covid-ppp-loan-data-with-fraud-examples`. Also inside HF `piercewetter3/irs-990-parsed` (D7).
- 7(a)/504 FOIA: no mirror found.
- Ground truth: forgiveness amount ≤ loan; payroll-cost caps (rule-based checks).

### D7. IRS Form 990 (nonprofit financial returns). Strong for (d)
1. **What:** Form 990/990-EZ/990-PF e-file returns: revenue by source, functional expenses (program, management, fundraising), balance sheet (Part X), compensation (Schedule J), grants (Schedule I).
2. **Access:** IRS bulk zips (blocked here). The AWS `irs-form-990` S3 feed was discontinued (background knowledge, unverified). HF mirror below.
3. **Formats:** XML (multiple schema versions) → parsed relational tables.
4. **Depth:** E-file 2011+ (unverified exact start). Annual.
5. **Breadth:** About 1.5M+ exempt orgs (EO BMF). Universe-broad.
6. **Join keys:** EIN, tax period, NTEE code; links to PPP loans and FEC committees in the HF mirror.
7. **Ground truth:** Strong internal arithmetic. Part I summary lines equal Part VIII/IX/X totals. Functional expense columns sum to the total. Beginning vs end-of-year balance sheet with net-asset reconciliation (Part XI).
8. **Benchmarks:** None found for workflows.
9. **Mirrors:** HF **`piercewetter3/irs-990-parsed`** (CC0; 34 tables, 459,069,505 rows, 20.96 GB; also CMS NPPES/Medicare spend, FMCSA, OFAC SDN, FEC, **SBA PPP FOIA loans**, IRS EO BMF; generated 2026-08-17; CDN-blocked here). HF `healthparse/us-nonprofit-health-org-finances-990`. Kaggle `abbas829/us-nonprofit-healthcare-organizations-financials` (CC BY-SA).
10. **W-D7 "Grantmaker due diligence" (persona: foundation program-finance officer).** Steps:
    (i) For 40 grantee candidates, pull 5 years of 990s.
    (ii) Checkpoint: Part I ↔ Part VIII/IX/X tie-outs and the net-asset roll.
    (iii) Compute program-expense ratio, months of operating reserves and revenue concentration.
    (iv) Benchmark executive compensation (Schedule J) vs peers by NTEE and size.
    (v) Cross-check PPP loans and forgiveness.
    (vi) Write a risk-tiered funding memo.

### D8. UK charity annual reports: Kleister-Charity (scanned PDFs with labels)
- Real annual reports and accounts filed with the Charity Commission for England and Wales (many scanned). Labels: charity name and number, address, report date, **annual income and spending**. HF **`DeepRead/kleister-charity-dev0`** (440 PDFs plus `expected.tsv`, 1.72 GB; originally from Applica's public S3 git-annex). HF `orgrctera/kleister_charity_train` (1,729 labelled items). Source repo `applicaai/kleister-charity`.
- **Used** as a document-IE benchmark (Kleister, Stanisławek et al. 2021).
- Joinable to Companies House (charitable companies) and Charity Commission register extracts (not mirrored).
- **W-D8 "Charity sector financial-health panel" (persona: social-sector lender).** Steps:
  (i) Extract the SOFA (income and expenditure by fund: restricted vs unrestricted) and balance sheet from scanned reports.
  (ii) Checkpoint: extracted income and spending vs Kleister labels.
  (iii) Compute free reserves = unrestricted funds − designated − fixed assets.
  (iv) Calculate reserves cover in months.
  (v) Flag going-concern language and write a lending shortlist.

### D9. Household-level real transactions
- Only **Berka** (B5) is real and broad.
- **Jens Walter receipts** (B4) cover one real person's expenses.
- The rest found are synthetic.
- **W-D9 "Household cash-flow plan from bank history" (persona: financial planner).** Steps:
  (i) From a Berka account, categorize 3 years of transactions (Czech k_symbol codes).
  (ii) Build a budget vs actual.
  (iii) Compute emergency-fund months and the loan payoff schedule (amortization from loan.csv amount, duration and payments).
  (iv) Benchmark against SCF-style ratios (D2).
  (v) Write recommendations. Checkpoint: balance identity and amortization tie-out to observed debits.

---

## 1. Existing-benchmark overlap (for differentiation)

| Benchmark | Data used | Overlap with this slice |
|---|---|---|
| FinanceBench; Finance Agent Benchmark (Vals) | US 10-K/10-Q/8-K text | A2/A3 face-statement QA (avoid) |
| SpreadsheetBench 2 (HF `KAKA22/SpreadsheetBench-v2`) | Business/financial spreadsheets, financial reports | Generic spreadsheet workflows |
| **Finch / FinWorkBench** (HF `FinWorkBench/Finch`, arXiv 2512.13168, ACL 2026 Findings) | **Enron emails plus versioned Enron/EUSES spreadsheets** plus 2024–25 artifacts (World Bank, Canadian/UK gov) | **B1 directly**: 172 workflows, top pass rate 38% (GPT 5.1 Pro), Claude Sonnet 4.5 at 25% |
| APEX-Accounting (Mercor + Ramp; HF `mercor/apex-accounting`) | **Synthetic** company worlds, accountant-authored tasks; 160 closed tasks | Same task family (close, recs, accruals) but synthetic, so real data differentiates |
| EDINET-Bench (SakanaAI, arXiv 2506.08762) | EDINET reports | A7 classification and forecast only |
| FinTagging (arXiv 2505.20650); FinAuditing (unverified details) | SEC XBRL tagging and calc consistency | A2 calc-linkbase checks |
| Kleister; SROIE; CORD; RVL-CDIP | Charity PDFs, receipts, invoices | B4/D8 extraction only |
| — none found — | **FERC Form 1/2/6/60, EQR, RUS 7/12, Companies House accounts, gov AP ledgers, N-PORT, IRS 990, IDX Excel** | Clear whitespace |

---

## 2. RANKED TOP-5 FOR THIS SLICE

Scores are 1–5 on Workflow depth, Realness/messiness, Verifiability, Differentiation and Scrapability (from this container).

1. **PUDL utility-regulatory accounting universe: FERC Form 1/2/6/60 + EQR transactions + RUS 7/12 + SEC Ex.21 linkage.** (D5 R5 V5 Df5 S5)
   USofA account-level statements are among the most granular public accounting data anywhere (1994–2025, about 385 Form 1 respondents; 613 co-ops). They come with XBRL calc rules and weights, debit/credit attributes, cross-schedule tie-outs, a published rate-base table usable as a reference answer, and budget columns (RUS 7).
   EQR adds 125 GB of **real transaction-level** sales that reconcile (imperfectly, realistically) to buyers' Form 1 purchased-power schedules. That covers both "universe-broad" and "one entity deep".
   No LLM benchmark uses it. It is the only large source fully downloadable in-container (public S3, CC BY 4.0), plus Kaggle.
2. **Enron spreadsheet and email corpus** (HF `enronarchive/mail` with original filenames and email index; GitHub `SheetJS/enron_xls`; HF `intellekthq/enron-ferc-pst`). (D5 R5 V4 Df3 S3)
   The only large corpus of *real* working finance-ops spreadsheets: desk P&L, positions, capital-book roll-forwards, tax reserves, gas volume accounting, plans. Daily version series and email threads give before/after ground truth.
   Differentiation is reduced because **Finch already uses it**. Avoid by targeting other custodians and desks (logistics, tax, origination), longer chains, and joins to external real data (FERC Form 1 or EQR context).
   Access: git clone works. HF large files need CDN egress.
3. **UK Companies House accounts (iXBRL)**, Kaggle `thomassimm/uk-company-accounts-wide-2014-2026`. (D4 R5 V4 Df5 S4)
   Private and small-company (SMB) financials at national scale (33.5M company-periods). Plenty of genuine mess: filleted accounts, unit and tagging anomalies, and a 9.36% restatement rate with first-reported vs latest vintages built in. Balance-sheet identities serve as checks.
   UK GAAP (FRS 102/105) gives a non-US jurisdiction. No benchmark found.
   Caveat: the mirror is parsed facts only. Raw iXBRL documents (for document-reading tasks) require Companies House access from outside the container.
4. **SEC structured disclosures beyond 10-K: FSN notes and dimensions + calc linkbase, companyfacts as-filed vintages, 8-K earnings releases, DEF 14A pay-versus-performance (ECD), N-PORT and 13F.** (D5 R4 V5 Df3 S3)
   Supports segment (ASU 2023-07), restatement-forensics, PvP-recompute and fund look-through workflows with machine-checkable answers (calc linkbase, net-asset identities, TSR recompute).
   Differentiation is moderate (SEC is crowded) but strong if tasks avoid 10-K QA.
   Kaggle CC0 mirrors cover companyfacts (2009+). The full FSN history with `cal`/`dim` and EX-99.1 exhibits need a SEC fetch outside the container. HF N-PORT and robosystems need CDN egress.
5. **Government AP, vendor-payment and P-card ledgers** (Kaggle `san-francisco/sf-vendor-payments` vouchers + PO summary, `tfshiloh/csv-version-missouri-checkbook-fy2010fy2017`, `chicago/chicago-payments`, Oklahoma P-card, Canada Receiver General; HF USAspending). (D4 R5 V3 Df5 S5)
   The rarest category, real transactional AP, and it is in-container downloadable. It supports audit, controls, close and cut-off workflows (three-way-match style PO-vs-voucher checks, duplicates, splits, vendor master).
   Verifiability is weaker (PO-vs-voucher sums are natural, but anomaly labels need experts and there are no ACFR tie-outs in the mirrors).

**Honorable mentions:**
- **Japan EDINET raw XBRL** (Kaggle `sirokujira/edinet20xx`, with `_cal.xml` and AuditDoc/KAMs; PDL 1.0).
- **Korea DART** (HF `eddmpython/dartlab-data`, CC BY 4.0, needs CDN egress).
- **IRS 990** (HF `piercewetter3/irs-990-parsed`, CC0, strong internal arithmetic).
- **Berka** real bank ledger (Kaggle, in-container).
- **IDX Excel statements** (spreadsheet-native disclosures).

Avoid or deprioritize:
- SEDAR+ (ToS bans scraping).
- NAIC (paid).
- FINRA short interest, Yahoo-derived prices, Fannie/Freddie loan files (redistribution terms).
- Scraped transcripts (provenance).
- Synthetic ledgers (mindweave, IBM AML, APEX worlds).

## 3. Open items and unverified claims
- License of the Enron corpus and the PII posture of each mirror. Whether `enronarchive/mail` `index.json` links each attachment to its email (likely, unverified because the CDN is blocked).
- Whether `TeraflopAI/SEC-EDGAR` 8-K rows contain exhibits (the sample suggests primary document only).
- The full LONG Companies House facts dataset location. Whether CH historic monthly archives back to 2008 are still downloadable.
- Number of EQR sellers. FERC EQR row counts per quarter.
- EDINET API rate limits. OpenDART limits come from third-party sources only.
- Upstream source and license of Kaggle SPY/AAPL/TSLA options chains and the stooq-based price set.
- FinAuditing benchmark details came from a secondary blog. XBRLBench and XBRL_Formula_Calculation were not inspected.
- PCAOB Form AP and UK council >£500 spend have no mirror found. Bankruptcy MORs have no dataset; they need a PACER/RECAP crawl outside the container.
