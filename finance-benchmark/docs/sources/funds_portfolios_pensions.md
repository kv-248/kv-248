# Slice: Funds, portfolios, asset management, wealth and pension. Source profiles

Researched 2026-10-17. Each profile covers ten fields: (1) what/URL, (2) access/ToS, (3) formats/messiness, (4) depth/cadence, (5) breadth, (6) join keys, (7) natural ground truth, (8) benchmark usage, (9) mirrors, (10) workflow sketches.
"VERIFIED" means I checked it myself from this container (download, API call, or computation). "unverified" means it comes only from search snippets or memory.

---

## 0. Access from our container (tested 2026-10-17). Read this first

| Route | Status | Notes |
|---|---|---|
| sec.gov, amfiindia.com, nbim.no, dartmouth.edu (French), ishares.com, mfapi.in, dados.cvm.gov.br, calpers.ca.gov, federalreserve.gov, zenodo | BLOCKED (DNS 000). WebFetch also fails (ENOTFOUND) | Every primary source needs a mirror |
| huggingface.co API and small non-LFS files (README, JSON) | OK | `https://huggingface.co/api/datasets?search=...` works |
| **HF LFS/xet file downloads** (`/resolve/main/*.parquet` returns 302 to `us.aws.cdn.hf.co`) | **BLOCKED by the egress proxy in this session** (connect_rejected) | **Action:** allowlist `us.aws.cdn.hf.co` (and probably `cas-bridge.xethub.hf.co`, `cdn-lfs*.hf.co`). Without that, large HF parquet files cannot be fetched |
| `datasets-server.huggingface.co` (`/rows`, `/info`, `/statistics`, `/filter`) | OK, but slow | Pages of 100 rows. `/filter` timed out on the 586M-row N-PORT table. `/statistics` works |
| Kaggle API: search, file list, **anonymous download** of public datasets | OK | `https://www.kaggle.com/api/v1/datasets/download/{owner}/{slug}` redirects to `storage.googleapis.com` and works without a token. VERIFIED on 21 MB and 33 MB datasets |
| github.com `git clone` | OK | Use `--filter=blob:none --no-checkout`, then `git show HEAD:path`. Do not run `ls-tree -l` (it fetches every blob). The GitHub REST search API is blocked from bash. GitHub search through the MCP tool works |
| Public S3 buckets (`*.s3.amazonaws.com`) | OK | GivingTuesday IRS-990 data lake `gt990datalake-rawdata` lists and downloads. VERIFIED |
| pypi.org, files.pythonhosted.org | OK | Packages such as edgartools or etf_scraper install, but they still call blocked hosts |

---

## Quick mirror reference (exact IDs; checked live unless noted)

| Source | Mirror | Size / coverage | License | Updated |
|---|---|---|---|---|
| N-PORT (raw, all 32 SEC tables) | HF `trader298/sec-nport` | 9.4 GB parquet, 586.9M rows, 2019Q4 to 2026Q2, partitioned `TABLE/year=/quarter=` | CC0 | 2026-07-10 |
| N-PORT (curated: holdings, filings, returns, flows, pit) | HF `ZipLime/fund-holdings-nport` | 5.3 GB. 145.6M positions, 17,513 funds, 341,049 reports, 2019-09-30 to 2026-05-31 | Apache-2.0 | 2026-10-12 |
| N-PORT 2020Q1 only | Kaggle `robotgames/sec-edgar-archive-nport-form-data-2020-quarter-1` | 250 MB csv | CC BY 4.0 | 2024 |
| 13F (info-table rows plus filings with control totals) | HF `ZipLime/institutional-portfolio-13f` | 5.5 GB. 124.1M holdings rows, 409,891 filings, 16,538 managers, 2013Q2 to 2026Q2 | Apache-2.0 | 2026-10-16 |
| 13F, curated famous managers | HF `eagle0504/sec-13f-holdings` (38 MB csv), `AllenHF/superinvestor-13f-holdings` (54 MB), `FinzData/sec-13f-institutional-ownership`, `XOOMAR/sec-13f-holdings`. Kaggle `josedavidpoveda/13f-consensus-of-64-fund-managers-2016-2026`, `simagholamiunsw/sec-13f-berkshire-and-75-super-investors-20132023`, `aneeshpanoli/sec-13fhr-institutional-investment-data` (2015-17) | small | CC0 or CC-BY (varies) | 2026 |
| 13F, bulk (unlicensed) | HF `kurry/institutional-holdings-13f-quarterly` (14.3 GB arrow, no license). Kaggle `samsonqian/sec-13f-filings` (4.6 GB pickle) | | none stated | 2025 / 2022 |
| CUSIP to CIK/ticker bridge | HF `ZipLime/security-master` | | Apache-2.0 | 2026-10-12 |
| SEC fund series/class/ticker map | HF `DenyTranDFW/SEC_Company_Tickers_MF_MutualFunds` (parquet copy of company_tickers_mf) | 0.4 MB | GPL | 2026-10-12 |
| India AMC portfolio XLS (raw) | GitHub `subscriptionmanager26-png/fund-disclosures`: `data/staging/python/amcs/*/2026-08/` | 314 xlsx, 2 xls, 3 zip for 13 AMCs, Aug-2026. Format survey of 51 AMCs | none stated (statutory disclosures) | 2026-10-11 |
| India AMC portfolios (parsed JSON) | GitHub `kushagra-agarwal-a/fund-holdings-data`: `portfolios/asof/{date}/{amfi_code}.json` | About 2,100 schemes per month-end (2026-06-30 to 2026-09-30) plus about 550 fortnightly (15th) | none stated | 2026-10 |
| AMFI NAV history | Kaggle `tharunreddy2911/mutual-fund-historic-nav-data` (20M+ rows, updated daily), `darshshah1010/india-mutual-fund-20062026` (NAV plus fund_master with SEBI category and AUM, CC0), `hk7797/mutual-fund-india` (daily files from 2006-04-01, CC BY-NC-SA), `shauryasayshi/indian-mutual-fund-nav-history-20062026`. GitHub `iambalaji-k/Indian-MF-NAV-history` (daily NAVAll from 2026-04-20) | 130 to 650 MB | various | 2026-10-15 / 16 |
| AMFI TER (daily) | Kaggle `neeeeeemo/indian-mutual-funds-ter-total-expense-ratios` (GitHub-synced) | 132 KB | MIT | 2026-10-16 |
| Brazil CVM daily NAV/flows | HF `Shote/fundos-cvm` (CNPJ, DT_COMPTC, VL_QUOTA, CAPTC_DIA, RESG_DIA, VL_PATRIM_LIQ, NR_COTST) | 1.4 GB, 8,193 files | none stated | last data 2026-10-15 |
| Brazil CVM holdings, fees, flows | HF `PrumoFS/acompanhamento-fundos-site` (`carteira_ativos/2016..2026`, `carac_fundo`, `flow_diario`, `cota_diaria`, ...) | 0.47 GB | none stated | 2026-10-16 |
| NBIM GPFG holdings 1998-2023 | Kaggle `alialmulla97/norway-fund-1-5-trillion-managed-1998-2023` (equity.xlsx 170,085 rows, fixed_income.xlsx 29,504, real_estate, renewables, norges.xlsx combined) | 21 MB | Apache-2.0 (as stated by uploader) | 2024-06 |
| WSIB private equity quarterly reports | Kaggle `jblumenstein/wsib-private-equity-data-q1-2009-to-q2-2021`: original PDFs (`Research/`), OCR'd xlsx, cleaned CSV (3,333 rows, 163 funds, 50 quarters) | 33 MB | Unknown | 2022-02 |
| Public Plans Data (US public pensions) | Kaggle `eshitakter/public-pension-plans-analysis-20012023` (2001-2024, 9.3 MB). Kaggle `meepbobeep/us-public-pensions-data-fiscal-years-20012016` (with codebook, CC BY-NC-SA). GitHub `megharaj2/Public-Pension-Plans-Analysis-2001-2023` (pension_data.csv) | | PPD terms (unverified) | 2025-10 |
| IRS 990 / 990-PF raw XML | S3 `https://gt990datalake-rawdata.s3.amazonaws.com/` (`EfileData/XmlFiles/{objectid}_public.xml`, `EfileData/XmlZips/{YYYY}_TEOS_XML_*.zip`, `Indices/990xmls/index_all_years_*.parquet`) | Multi-TB. 2026 zips dated 2026-08-25 | public IRS data | 2026-08 |
| Fama-French library | Kaggle `nikitamanaenkov/famafrench-factors-and-portfolios` (regions, factors, portfolios; files dated 2025-10-30; CC BY 4.0). Kaggle `waelelghazzawi/fama-french-factor-zoo-benchmarks` (daily 1990-2026, monthly 1970-2026; 2026-09-24; CC0). HF `krishnakamath/fama_french_data` (daily Mkt-RF, SMB, HML, RF, Mom from 2000; 6,517 rows) | small | | |
| ARK ETF daily holdings | GitHub `tigger0jk/ark-invest-scraper` (git-scraping: the history of `holdings/*.csv` holds about 914 daily snapshots for ARKK, 2020-11-22 to 2024-06-05. HEAD is a broken 301 page, so read older commits) | | none stated | 2024-06 |
| ETF issuer scraper (code and samples) | GitHub `nikulpatel3141/ETF-Scraper` (iShares, SSGA, Vanguard, Invesco; supports historical as-of dates for iShares; sample files in `test/test_data/`) | | | 2024-12 |
| ETF/index holdings, misc | Kaggle `jackstev298/full-holdings-data-for-the-top-100-etfs`, `devaangbarthwal/s-and-p-500-holdings-and-weights-spy-2000-2024` (SPY annual-report holdings) | | | |
| Australia MySuper stats | Kaggle `darylb/superannuation-mysuper-product-by-product-2013-20` | 51 MB | CC BY-SA 3.0 | |
| Endowment market values (NACUBO FY21) | Kaggle `hayawi/us-and-canadian-2021-ntse-endowment-market-value` | small | | |
| No mirror found | N-MFP, N-CEN, N-CSR/TSR iXBRL, RR prospectus data sets, Form ADV/IAPD, Fed Z.1, GPIF, CPP, UCITS KIID/PRIIPs KID, CalPERS PEP tables | | | |

---

## A. SEC Form N-PORT (monthly portfolio reports of registered funds and ETFs)

1. **What:** Each registered open-end fund and ETF (and closed-end funds except MMFs) files NPORT-P monthly. SEC DERA publishes quarterly "Form N-PORT Data Sets": https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets. Raw XML per filing is on EDGAR.
2. **Access:** Free bulk zip (about 400 MB per quarter. The trader298 `_source/2025q4.json` gives content_length 417,802,295). EDGAR fair-access limit is 10 req/s with a declared User-Agent. Public domain. Disclosure caveat: historically only the third month of each fiscal quarter is public, about 60 days after period end. The 2024 amendments for public monthly reporting were postponed: compliance moved to Nov-17-2027 (large groups) and May-18-2028, and a Feb-2026 proposal would make publication quarterly (search results; partly unverified).
3. **Formats:** Tab-separated tables (32 in the mirror: SUBMISSION, REGISTRANT, FUND_REPORTED_INFO, FUND_REPORTED_HOLDING, IDENTIFIERS, DEBT_SECURITY, MONTHLY_TOTAL_RETURN, MONTHLY_RETURN_CAT_INSTRUMENT, INTEREST_RATE_RISK, BORROWER, REPURCHASE_*, SECURITIES_LENDING, derivative tables, EXPLANATORY_NOTE, FUND_VAR_INFO...). Known traps (ZipLime PIPELINE.md): placeholder CUSIP `999999999`, one row per identifier (joining raw duplicates positions), BALANCE strings like `-.5`, MON1..MON3 return dating, and series versus registrant confusion. Moderately messy.
4. **Depth/cadence:** 2019Q4 to present. Refreshed quarterly; the mirror runs to 2026Q2. Holdings at quarter-end for each fund (fiscal quarters are staggered, so the universe covers every calendar month). Returns and flows are monthly, three months per filing.
5. **Breadth:** About 17.5k fund series. 341k reports (ZipLime). 145.6M positions across equity, debt, loans, ABS/MBS and derivatives.
6. **Join keys:** Registrant CIK, SERIES_ID (S000...), CLASS_ID (C000...), series LEI, holding CUSIP, ISIN, ticker and issuer LEI. Joins to 13F (CUSIP), RR/N-CSR/N-CEN (series and class IDs), N-MFP (series ID, CUSIP) and ADV (adviser names, LEI).
7. **Natural ground truth (strong):** Total assets minus liabilities equals net assets. Σ holding values ≈ net assets after cash and other items (`pctVal` sums to about 100). Monthly net-asset roll-forward: NA(t) ≈ NA(t−1) + sales − redemptions + reinvestment + realized gains + unrealized change + net income − distributions (all reported per month). Class total returns can be checked against N-CSR financial highlights and the RR bar chart. Reported DV01/SDV01 (INTEREST_RATE_RISK) can be checked against duration recomputed from DEBT_SECURITY maturity and coupon. VERIFIED that the schema carries these fields (ZipLime `flows` has sales, reinvestment, redemption, net_flow, realized_gain_nonderivative, unrealized_appreciation_nonderivative; `filings` has total and net assets).
8. **Benchmark usage:** Light. No LLM or agent benchmark found that uses N-PORT. DeepFund, PortBench and InvestorBench use price series. Common in academic finance.
9. **Mirrors:** `trader298/sec-nport` (raw, CC0) and `ZipLime/fund-holdings-nport` (curated). Both are on HF; LFS downloads are blocked here, so see section 0. Kaggle 2020Q1 only.
10. **Workflows:**
   - **W-A1. Target-date fund series due diligence.** Persona: OCIO/consultant manager-research analyst. (i) Resolve a TDF family's series IDs and pull 8 quarterly reports per vintage. CP1: net-asset roll-forward residual under 0.5% per month, with outliers explained (mergers, distributions). (ii) Look-through: the underlying holdings are funds, so join their CUSIP/LEI to the underlying series' N-PORT. CP2: look-through weights sum to 100%, and an equity-share glide path by vintage. (iii) Chain monthly class returns into calendar-year returns. CP3: they match the RR prospectus bar chart and N-CSR financial highlights within about 5 bp. (iv) FF5+Mom regression per vintage. CP4: betas and alpha with t-stats. (v) Fee drag from RR fee tables and TSR expense ratios. CP5: TSR "costs paid on a $10k investment" ≈ ER × average value. Deliverable: scorecard and IC memo workbook.
   - **W-A2. Liquidity and concentration stress for a high-yield or bank-loan fund.** Persona: fund-complex liquidity risk manager (Rule 22e-4 program). Classify holdings by asset category, fair-value level, restricted flag and maturity. Compute issuer and industry HHI and the 1940-Act diversification (75/5/10) test. Recompute DV01 and CP-check it against reported INTEREST_RATE_RISK. Run a redemption stress using the worst historical monthly net flow as a percentage of net assets. CP: share of Level-3 plus restricted holdings against a 15% illiquid proxy. Then a pro-forma sale plan (sell most-liquid first versus pro-rata) and the resulting concentration after the stress.

## B. SEC Form 13F (quarterly long US-equity holdings of managers with more than $100M)

1. **What:** 13F-HR info tables (XML since 2013Q2). DERA "Form 13F Data Sets": https://www.sec.gov/dera/data/form-13f (quarterly since March 2024, covering the prior three months).
2. **Access:** Free zip TSV (SUBMISSION, COVERPAGE, INFOTABLE, SUMMARYPAGE, OTHERMANAGER...). Public domain. EDGAR fair-access rules apply.
3. **Formats:** Flattened TSV, plus XML per filing. Messy: the value unit switched from thousands to dollars in 2023 (ZipLime counts 262,316 filings in thousands and 148,825 in dollars). Amendments: restatements and NEW HOLDINGS confidential-treatment reveals up to 452 days late. One manager is reported across sub-managers. Put/call rows are included.
4. **Depth/cadence:** 2013Q2 to 2026Q2 (mirror current to 2026-09-29 acceptances). Quarterly with a 45-day lag.
5. **Breadth:** 16,538 managers, 409,891 filings, 124.1M info-table rows (ZipLime).
6. **Join keys:** Manager CIK, 13F file number, CUSIP, FIGI/ticker (via security-master), issuer CIK.
7. **Natural ground truth:** Cover-page `tableEntryTotal` and `tableValueTotal` against the parsed info-table sums. VERIFIED via datasets-server statistics on ZipLime `filings`: `control_totals_match` is True for 313,070 filings, False for 14,499, null for 83,638 (mostly notices). Implied price (value/shares) should agree across managers for the same CUSIP and quarter, which is a strong unit-error detector. N-PORT positions of funds advised by a 13F manager should sum (by CUSIP) to at most the 13F holding.
8. **Benchmark usage:** Heavy in hobby datasets and academia (Berkshire etc.), and LLMs know the famous books well. **Contamination risk is high for famous managers; use obscure managers or recent quarters.** No agent benchmark found built on it.
9. **Mirrors:** See the table (ZipLime best; eagle0504, AllenHF, Kaggle sets).
10. **Workflows:**
   - **W-B1. Manager shortlist: overlap, conviction and style drift for 12 small-cap managers.** Persona: fund-of-funds manager-selection analyst. Build 8-quarter books. CP1: control totals match (exclude or flag mismatches; fix thousands/dollars units). Compute active share against an ETF benchmark proxy (iShares or ARK holdings, or N-PORT of an index fund). CP2: overlap matrix Σmin(w_i, w_j). Compute turnover and holding period. Do holdings-based style (size and value from FF breakpoints). CP3: style drift chart. Then a combined-portfolio concentration check (top-10 issuer exposure across selected managers). Output: ranked shortlist with rationale.
   - **W-B2. Crowding risk monitor.** Persona: hedge-fund risk manager. Aggregate ownership by CUSIP as a percentage of shares outstanding (from company XBRL in ZipLime company-fundamentals). Compute days-to-liquidate using ADV. CP: aggregate manager ownership against N-PORT fund ownership. Flag crowded names. Stress the P&L for a forced-deleveraging scenario.

## C. SEC Form N-MFP (money market funds, monthly)

1. **What:** Monthly portfolio and statistics for every MMF. DERA N-MFP data sets: https://www.sec.gov/dera/data/form-nmfp-data-sets. N-MFP3 since June 2024 (data sets include it since July 2025).
2. **Access:** Monthly zip; EDGAR XML per filing; public with no delay (unverified). No mirror found.
3. **Formats:** Flat TSV from XML. N-MFP2 and N-MFP3 schemas differ, which is good messiness.
4. **Depth/cadence:** About 2010-09 to present, **monthly refresh**, which helps against contamination.
5. **Breadth:** About 300 to 400 MMF series and their share classes (unverified count).
6. **Join keys:** Series ID, class ID, CUSIP, LEI, issuer names; repo counterparties and collateral.
7. **Natural ground truth (very strong):** WAM and WAL are recomputable from holdings (maturity dates, amortized cost) and reported. Daily and weekly liquid assets are recomputable against the reported daily or weekly values. Market-based (shadow) NAV per share can be checked against holdings market value divided by shares. Under the 2023 reforms the minimums are 25% DLA and 50% WLA (from memory, unverified). Gross and net yields can be checked against expense ratios.
8. **Benchmark usage:** Essentially none.
9. **Mirrors:** None found on HF, Kaggle or GitHub. **This is a gap. Would need a sec.gov fetch outside the container.**
10. **Workflow W-C1. Corporate cash-investment policy compliance review.** Persona: corporate treasurer. Pick 6 government and prime MMFs over 12 months. Recompute WAM/WAL (CP1 against reported). Recompute DLA/WLA against regulatory minimums and policy thresholds (CP2). Compute issuer concentration and repo-counterparty exposure. Shadow-NAV deviation (CP3). Net-yield ranking after fees. Recommend reallocation within the policy limits.

## D. SEC Form N-CEN (annual fund census)

1. **What:** Annual report of every registered investment company: service providers (adviser, sub-adviser, custodian, auditor, transfer agent, pricing service), securities lending (agents, fee splits, average loan value, net income), brokerage commissions and principal transactions, ETF creation-unit size, APs, and line-of-credit usage. https://www.sec.gov/dera/data/form-ncen-data-sets.
2. **Access:** Quarterly zips. Caveat: filings on the 3.1 schema (EDGAR 25.2) are not yet included (SEC note via search).
3. **Formats:** Many flat TSVs from XML. Heavy one-to-many joins.
4. **Depth/cadence:** 2018 to present, quarterly posting of annual filings.
5. **Breadth:** All registered investment companies (thousands of registrants and about 12k series, unverified).
6. **Join keys:** CIK, series ID, LEI of service providers, file numbers.
7. **Ground truth:** Securities-lending net income against the N-CSR income statement. Brokerage commissions against the N-CSR/SAI. ETF creation-unit fields against N-PORT shares outstanding (weak to moderate).
8. **Usage:** None found.
9. **Mirrors:** None found.
10. **Workflow W-D1. Operational due diligence and vendor concentration.** Persona: fund board or ODD analyst. Map each fund in a complex to custodian, administrator, auditor and pricing vendor. Compute vendor-concentration HHI across the family. Securities-lending economics: fund share of gross revenue and implied fee split. CP: N-CSR reported lending income. Brokerage commission per $ of turnover (turnover from N-CSR financial highlights). Flag outliers for the board.

## E. N-CSR / N-CSRS shareholder reports (plus Tailored Shareholder Reports in iXBRL since 2024)

1. **What:** Annual and semi-annual reports: schedule of investments, statements of assets and liabilities, operations and changes in net assets, financial highlights, notes. Since compliance on 2024-07-24, the TSR (class-level 2-4 page report) is Inline XBRL tagged with the OEF taxonomy (expense ratio, costs paid, performance table, holdings summaries).
2. **Access:** EDGAR only (HTML, iXBRL, sometimes PDF exhibits). No DERA bulk data set for TSR found. Parsers such as edgartools exist but need sec.gov.
3. **Formats:** Very messy HTML tables (schedule of investments across dozens of pages), iXBRL with OEF and US-GAAP facts, plus older scanned or PDF items in historical filings.
4. **Depth/cadence:** Electronic since about 2003. iXBRL TSR from mid-2024, semiannual per fund.
5. **Breadth:** Every registered fund.
6. **Join keys:** CIK, series and class IDs (contexts in iXBRL), tickers.
7. **Ground truth (strong):** Financial-highlights NAV-per-share roll-forward (beginning NAV + net investment income + realized/unrealized gains − distributions = ending NAV). Reported total return against NAV and distributions. Statement of changes in net assets against N-PORT flows. Schedule-of-investments total against total investments on the balance sheet. TSR expense ratio against the financial highlights.
8. **Usage:** Not used in LLM benchmarks as far as found (FinanceBench and similar use 10-K/10-Q).
9. **Mirrors:** None found (TeraflopAI/SEC-EDGAR covers 10-K/10-Q/8-K/Forms 3/4/5, not N-CSR).
10. **Workflow W-E1. Reconstruct a fund's NAV and verify the shareholder report.** Persona: fund accountant or auditor. From the N-CSR HTML, extract the schedule of investments (about 800 lines). CP1: sum equals reported investments at value. Rebuild the statement of changes in net assets from N-PORT monthly flows and gains (CP2). Rebuild per-share financial highlights (CP3). Recompute expense ratio = expenses / average net assets (CP4 against highlights and TSR). Write up discrepancies.

## F. SEC Mutual Fund Prospectus Risk/Return Summary data sets (RR)

1. **What:** XBRL-tagged fee table (management fee, 12b-1, other, waivers, net expense), expense example (1/3/5/10-year costs), annual total-return bar chart, average annual returns against the benchmark, and portfolio turnover. https://www.sec.gov/data-research/sec-markets-data/mutual-fund-prospectus-riskreturn-summary-data-sets.
2. **Access:** Quarterly zips (SUB/TAG/NUM/TXT style, like the Financial Statement data sets).
3. **Formats:** Numeric facts with contexts by series and class. Text blocks.
4. **Depth/cadence:** About 2011 to present (unverified start). Quarterly; 2026Q1 posted.
5. **Breadth:** All N-1A open-end funds and classes.
6. **Join keys:** CIK, series and class IDs, ticker.
7. **Ground truth:** The expense example is recomputable from the net expense ratio with 5% growth (deterministic formula). Bar-chart annual returns against returns chained from N-PORT monthly data. Fee-table arithmetic: gross − waiver = net.
8. **Usage:** Not used in LLM benchmarks found.
9. **Mirrors:** None found.
10. **Workflow W-F1. Share-class selection and fee audit for a 401(k) menu.** Persona: retirement-plan advisor or fiduciary. For 25 funds × all share classes: verify fee-table arithmetic and the expense example (CP1). Compute 10-year cost to participants at plan size. Compare net returns across classes (CP2: return gap ≈ fee gap). Identify the cheapest eligible class. Quantify savings and flag funds whose 5-year return is below benchmark net of fees.

## G. Form ADV (investment advisers; IAPD bulk data)

1. **What:** Part 1A data for SEC-registered and exempt-reporting advisers: RAUM (discretionary and non-discretionary), number and type of clients, fee types, custody, affiliations, disciplinary history, and Schedule D 7.B.1 private funds (gross asset value, number of owners, % owned by funds of funds, auditor, prime broker, custodian, administrator). https://www.sec.gov/foia-services/frequently-requested-documents/form-adv-data. Monthly "IA FOIA" reports cover Jul-2006 to Mar-2026. Bulk CSV covers 2001 to 2024; 2025 onward is on IAPD.
2. **Access:** Free zip CSV (monthly files of 385 to 663 MB in 2024, per search). Public. Part 2 brochures are PDFs on IAPD.
3. **Formats:** Many linked CSV tables. Part 2A brochures are messy PDFs with fee schedules.
4. **Depth/cadence:** 2001 to present, monthly.
5. **Breadth:** About 15k SEC RIAs plus about 5k ERAs, and about 100k private funds (unverified).
6. **Join keys:** CRD number, SEC file number (801-, 802-), private fund ID (805-), LEI. Names map to 13F filers and N-CEN advisers.
7. **Ground truth:** Σ private fund GAV ≤ RAUM (with gross-versus-net caveats). Client-count buckets against AUM buckets. RAUM changes over time against 13F book changes. Brochure fee schedule against ADV fee checkboxes.
8. **Usage:** None in LLM benchmarks found.
9. **Mirrors:** None found.
10. **Workflow W-G1. ODD pre-screen of 20 hedge-fund managers.** Persona: allocator ODD analyst. Pull ADV time series: RAUM growth, private-fund GAV and investor counts. Service-provider quality (Big-4 auditor, independent administrator). CP1: GAV against 13F long book (implied leverage or shorts). Disciplinary flags. Fee structure from the brochure PDF (CP2: consistent with ADV checkboxes). Output a scored red/amber/green table.

## H. ETF issuer daily holdings files (iShares, SPDR/SSGA, Vanguard, Invesco, ARK)

1. **What:** Issuers post daily full holdings (CSV, XLSX, JSON): ticker, name, CUSIP/ISIN/SEDOL, shares, market value, weight, sector, plus cash and derivatives.
2. **Access:** Scrape issuer sites (iShares `.ajax?fileType=csv`, SSGA xlsx, Vanguard JSON API; ARK CSVs, which went behind a Cloudflare anti-bot wall in 2021). **ToS risk:** index constituent and weight data are often licensed by S&P/MSCI/FTSE, and issuer terms may restrict redistribution (unverified). Use for research only and avoid republishing.
3. **Formats:** A different layout per issuer, header junk rows, footnotes, and as-of date conventions (ARK prints the next trading day's date).
4. **Depth/cadence:** Daily. The iShares historical as-of parameter is reportedly supported (ETF-Scraper README). Archive depth depends on the mirror.
5. **Breadth:** Thousands of ETFs (live). The mirror covers ARK's 9 ETFs.
6. **Join keys:** CUSIP, ISIN, ticker. Fund ticker to N-PORT series (via company_tickers_mf).
7. **Ground truth:** Σ weights = 100%. MV/shares gives an implied price that must agree across ARK funds holding the same CUSIP on the same day. Day-over-day share changes give implied trades (ARK also published daily trade notices). Quarter-end snapshot against N-PORT holdings.
8. **Usage:** Used in hobby tracking apps. Not used in agent benchmarks found.
9. **Mirrors:** `tigger0jk/ark-invest-scraper` git history (VERIFIED: about 914 ARKK snapshots, 2020-11-22 to 2024-06-05; row example `06/14/2022,ARKK,"ZOOM VIDEO COMMUNICATIONS-A",ZM,98980L101,"7,207,572","$744,686,339.04",10.62%`). `nikulpatel3141/ETF-Scraper` (sample files). Kaggle `jackstev298/full-holdings-data-for-the-top-100-etfs`.
10. **Workflow W-H1. Reverse-engineer an active ETF's trading and attribution.** Persona: ETF analyst or competitor PM. From 250 daily snapshots: reconstruct trades. CP1: implied prices consistent across sibling funds. Compute daily holdings-based return against the fund's N-PORT monthly return (CP2: tracking residual). Brinson sector attribution against a benchmark ETF's holdings. Turnover and tax-efficiency implications (in-kind creations). CP3: the quarter-end book equals the N-PORT holdings.

## I. India: AMC monthly and fortnightly scheme portfolio disclosures (SEBI)  [HIGH VALUE]

1. **What:** By SEBI circular (2018) every AMC must publish the month-end portfolio of every scheme, with ISIN, within 10 days, in downloadable spreadsheet format, on its own site and AMFI's. Debt schemes also publish fortnightly (the mirror holds 15th-of-month files; the exact rule is unverified).
2. **Access:** Scrape about 50 AMC websites. Each has its own URL scheme, some sit behind proxies or anti-bot measures (the repo uses a Webshare proxy for unionmf.com), and some ship ZIPs. Statutory public disclosures; check each AMC's ToS.
3. **Formats (very messy, VERIFIED from the repo's `data/sources/amc_format_survey.json`):** 51 AMCs, 46 "SEBI-title" layout families plus 5 CAMS layouts. 27 AMCs use multi-sheet workbooks with 1 to 108 sheets each (one sheet per scheme, named by short code such as `YY07`). Header aliases vary ("% to NAV", "Percentage to Net Assets", "Yield of the Instrument (%)", "~YTC (AT1/Tier 2 bonds)"...). There are leading blank rows, section subtotals ("(a) Listed / awaiting listing..."), derivatives and hedged positions, market value in ₹ lakh, and .xls/.xlsx/.zip, including "revised_final" re-uploads.
4. **Depth/cadence:** Monthly plus fortnightly. **Strongly contamination-resistant** (mirror data is Jun to Sep 2026). History back to about 2009 is available on AMC sites (varies).
5. **Breadth:** About 1,500 to 2,100 schemes and 50 AMCs (₹70+ trn AUM).
6. **Join keys:** ISIN (for every security). AMFI scheme code (via NAVAll mapping in the repo's `data/sources/disclosure_to_amfi_global_mapping.json`). NSE/BSE symbols via ISIN.
7. **Ground truth (VERIFIED):** Σ % to NAV ≈ 100. In 120 sampled Aug-2026 parsed schemes the median was 100.0 and 93% fell within 99 to 101, with outliers (32%, 67%, 107%) where derivative or hedge sections or revised files broke parsing, which makes good "agent must notice" cases. Market value / quantity gives a price that should agree across AMCs on the same ISIN and date. Scheme AUM equals Σ market value, checkable against AMFI monthly AUM. Holdings-implied return can be checked against the NAV change.
8. **Usage:** Not in any benchmark found. Only small hobby projects (for example GitHub `divyadharshini-1306/Mutual-Fund-Style-Drifter`).
9. **Mirrors:** Raw: GitHub `subscriptionmanager26-png/fund-disclosures` (Aug-2026 raw XLS/XLSX/ZIP for SBI, Mirae, ICICI Pru, Union, PGIM, Navi, JM, DSP, Franklin, UTI, Baroda BNP, Abakkus, Old Bridge, plus parsers and maps). Parsed: GitHub `kushagra-agarwal-a/fund-holdings-data` (`portfolios/asof/2026-06-15 ... 2026-09-30/{amfi_code}.json`; fields holding_type, instrument, isin, section, industry, rating, coupon, maturity_date, quantity, market_value (₹ lakh), pct_nav, ytm, ytc).
10. **Workflows:**
   - **W-I1. Quarterly wealth-client review and rebalance across 8 schemes.** Persona: Indian MFD or RIA (wealth manager). (i) Parse 8 AMC workbooks with different layouts (CP1: each scheme's % NAV sums to 100 ± 0.5). (ii) Look-through exposure by ISIN, sector and market-cap bucket using the AMFI semi-annual large/mid/small list. CP2: a large-cap scheme holds at least 80% in the top-100 per its SEBI category rule. (iii) Pairwise overlap Σmin(w) (CP3). (iv) Trailing returns, volatility and Sharpe from AMFI NAV history (CP4: matches AMC factsheet figures). (v) Regular-to-Direct switch analysis: TER gap from the AMFI TER file. CP5: the Direct/Regular NAV ratio drifts at about the TER gap. Capital-gains tax on the switch (current equity STCG/LTCG rules; verify rates). (vi) Rebalance to the target allocation, minimising tax and exit loads.
   - **W-I2. Debt fund credit and duration monitor.** Persona: institutional treasury investor or debt-fund DD analyst. From fortnightly disclosures of 10 debt schemes: rating migration of each ISIN between fortnights, issuer-group concentration, and recomputed portfolio YTM and Macaulay duration from coupon and maturity. CP: against the scheme's reported YTM/duration, and duration against the SEBI category band. AT1/Tier-2 exposure (YTC column). Liquidity bucket (G-sec + T-bill + TREPS share). Recommend exits.

## J. AMFI NAV history, TER and AUM (India)

1. **What:** Daily NAV for every scheme (AMFI NAVAll plus history portal, 90 days per request, semicolon-delimited). Daily TER per scheme (regular and direct). Monthly and quarterly AUM. https://www.amfiindia.com/net-asset-value/nav-download.
2. **Access:** Free (blocked here). mfapi.in community API (blocked here).
3. **Formats:** Semicolon text with AMC header lines interleaved and ISIN payout/reinvest columns. Scheme renames and mergers make it messy.
4. **Depth/cadence:** April 2006 to present. **Daily**.
5. **Breadth:** About 6,000 to 38,000 scheme codes including closed ones (darshshah1010 fund_master has 38,135 rows).
6. **Join keys:** AMFI scheme code, ISIN (growth and IDCW), AMC name.
7. **Ground truth:** NAV-based returns against AMC factsheet-reported returns. Direct-versus-Regular NAV ratio against the TER gap. IDCW NAV drops on record date against dividends declared.
8. **Usage:** Many Kaggle notebooks. Not in agent benchmarks.
9. **Mirrors:** See the table (Kaggle tharunreddy2911 daily-updated; darshshah1010 CC0 with category and AUM; GitHub iambalaji-k).
10. **Workflow W-J1. SIP performance attribution and category ranking.** Persona: robo-advisor product analyst. XIRR of monthly SIPs over 5 years for all flexi-cap schemes (CP: against a known AMC SIP-return table). Rolling-return percentile. TER-adjusted alpha against the Nifty 500 TRI (if available) or the category median. Survivorship check (closed or merged schemes from fund_master).

## K. Brazil CVM fund open data (Informe Diário, CDA holdings, Lâmina, Perfil Mensal)

1. **What:** CVM "Dados Abertos": the daily report gives every fund's quota value, net equity, daily subscriptions and redemptions, and number of holders. CDA is the monthly portfolio composition in blocks 1 to 8 (government bonds, funds, swaps, equities...); detail is withheld during a confidentiality window. The Lâmina is the factsheet (fees, returns). https://dados.cvm.gov.br/dataset/fi-doc-cda and the `fi-doc-inf_diario` group.
2. **Access:** Free CSV/ZIP; open data (license claimed to be ODbL-style, unverified). Blocked here; mirrors exist.
3. **Formats:** Portuguese, `;` separated, latin-1, monthly zips with many block files, and CNPJ formatting variants (and the 2023 CVM 175 regime change: classes and subclasses). Messy.
4. **Depth/cadence:** Daily informes from about 2000 (PrumoFS `dt_inicio_historico` 2000-01-03). CDA monthly from 2018 in open data (mirror has 2016). Daily refresh.
5. **Breadth:** Tens of thousands of funds (FI, FIDC, FIP, FII...).
6. **Join keys:** CNPJ (fund and manager), ISIN in CDA, B3 tickers.
7. **Ground truth (strong):** VL_PATRIM_LIQ(t) ≈ VL_PATRIM_LIQ(t−1) × VL_QUOTA(t)/VL_QUOTA(t−1) + CAPTC_DIA − RESG_DIA (daily flow-adjusted roll-forward). CDA Σ ≈ net equity. Fee drag can be checked against the gap between the quota return and gross portfolio return.
8. **Usage:** None in LLM benchmarks found. Non-English, so it is differentiating.
9. **Mirrors:** HF `Shote/fundos-cvm` (daily quota series; meta.json: last data 2026-10-15). HF `PrumoFS/acompanhamento-fundos-site` (CDA holdings 2016-2026, characteristics, daily flows and quotas, benchmarks). Neither states a license.
10. **Workflow W-K1. Multimercado manager selection for a fund-of-funds.** Persona: Brazilian FoF allocator. Daily returns against CDI. CP1: flow-adjusted equity roll-forward residuals (detect errors or merged classes). Sharpe, max drawdown and up/down capture. Flow persistence (net flows as % of equity). Look-through CDA exposure to government bonds and derivatives (CP2: Σ matches equity). Fee check from the Lâmina. Output a shortlist plus a sizing that respects liquidity (redemption terms).

## L. Norway NBIM, Government Pension Fund Global holdings

1. **What:** Year-end (and reportedly half-year) list of every equity, bond issuer and real-estate/renewables asset, 1998 onward, with market value (NOK and USD), voting % and ownership %, country and industry. Also returns, benchmark and exclusion decisions. https://www.nbim.no/en/investments/all-investments/ (format details from search; unverified).
2. **Access:** Free download (xlsx/csv/pdf, unverified). Blocked here.
3. **Formats:** Spreadsheet or PDF by country. **No ISINs**, only names, so entity resolution across years is hard and messy.
4. **Depth/cadence:** 1998 to 2025, annual.
5. **Breadth:** About 9,000 equities and about 1,300 FI issuers per year (VERIFIED mirror: 170,085 equity rows and 29,504 FI rows over 26 years).
6. **Join keys:** Company name plus country (fuzzy). Can map to ISIN via OpenFIGI or 13F names (hard).
7. **Ground truth:** Σ market value by asset class against the annual report totals. Ownership % × market cap ≈ market value. Excluded companies must disappear after the exclusion date.
8. **Usage:** Kaggle notebooks. Not in benchmarks.
9. **Mirrors:** Kaggle `alialmulla97/norway-fund-1-5-trillion-managed-1998-2023` (VERIFIED download; columns region, country, name, industry, year, market_value, ownership, investment_type). GitHub `ukavlie/NBIM-Analysis` (1998-2025; contents not checked).
10. **Workflow W-L1. Holdings-based style and exclusion-compliance audit.** Persona: SWF or ESG research analyst. Resolve entities across 26 years (CP1: count of continuous holdings). Country, sector and size weights over time. Compare to the policy (strategic) allocation. CP2: excluded companies (NBIM exclusion list) absent after their decision dates. Implied ownership drift. Report.

## M. Other asset-owner holdings: GPIF (Japan), CPP Investments, NZ Super, AP funds

1. **What:** GPIF publishes a full holdings list at fiscal year-end (1,749 domestic stocks for FY2025, released 2026-07-03, per search) alongside the policy asset mix with deviation bands (for example 25% each ±6-8% in 2020). CPP Investments publishes annual Canadian and foreign equity holding lists in HTML (for example `Canadian-Public-Disclosure_ibfs-Q4F25.html`). NZ Super and Swedish AP funds also publish lists (unverified detail).
2. **Access:** Free downloads, blocked here. No mirrors found.
3. **Formats:** Japanese-language xlsx/PDF (GPIF), HTML tables (CPP).
4. **Depth/cadence:** Annual (GPIF since about FY2015/16).
5. **Breadth:** Thousands of holdings each.
6. **Join keys:** Names, sometimes securities codes (GPIF lists stock name, shares and market value).
7. **Ground truth:** Allocation against policy bands. Σ holdings against the reported asset-class totals.
8. **Usage:** None.
9. **Mirrors:** None found.
10. **Workflow W-M1. Policy-portfolio compliance across three asset owners.** Persona: asset-owner peer-benchmarking consultant. Actual against policy weights and bands. Rebalancing trades needed. Overlap of top holdings across NBIM, GPIF and CPP. Home bias.

## N. US public-pension private-equity fund-level reports (WSIB, CalPERS PEP, CalSTRS, Oregon...)  [HIGH VALUE]

1. **What:** Quarterly fund-by-fund tables: commitment, paid-in (contributions), unfunded, distributions, market value, total value, TVPI and net IRR. WSIB: `https://www.sib.wa.gov/docs/reports/quarterly/irMMDDYY.pdf` (latest seen ir093025). CalPERS PEP Fund Performance Review (cash in, cash out, remaining value, net IRR, multiple; since-inception 11.6% and 1.5x as of 2025-12-31, per search). Board meeting decks also carry asset allocation against targets.
2. **Access:** Public (FOIA-driven). PDFs and HTML tables. Blocked here except via mirror.
3. **Formats:** **PDF tables, some image-like or scanned in older years**. The mirror required OCR ("pdftoexcelconverter", "PDF2XL"). Fund-name variants across quarters. Footnotes.
4. **Depth/cadence:** Quarterly (2-quarter GP reporting lag). WSIB from at least 2009 (mirror) to 2025.
5. **Breadth:** WSIB about 160+ partnerships (mirror: 163 funds × 50 quarters = 3,333 rows). CalPERS several hundred.
6. **Join keys:** Fund name (fuzzy). Vintage. GP name, which maps to Form ADV/Form D. The same fund appears across LPs, which allows a cross-check.
7. **Ground truth (VERIFIED on the mirror):** total_value = MV + distributions in 99.9% of rows. net_benefit = TV − contributions in 99.3%. TVPI ≈ TV/contributions in 99.5%. **Net IRR recomputed from quarter-to-quarter deltas of cumulative contributions and distributions plus ending NAV gave 13.07% against a reported 12.90%** (Endeavour Capital VI, 39 quarters). unfunded = commitment − contributions holds in only 39% of rows (recallable distributions and fees outside the commitment), which is a good reasoning trap. The same fund at another LP should show a similar TVPI.
8. **Usage:** None found in LLM benchmarks.
9. **Mirrors:** Kaggle `jblumenstein/wsib-private-equity-data-q1-2009-to-q2-2021` (original PDFs in `Research/`, OCR xlsx, cleaned CSV). GitHub `nichtaylor/Private-Equity-Fund-Analysis` (CalPERS SQL only, no data).
10. **Workflows:**
   - **W-N1. PE pacing plan and portfolio benchmarking.** Persona: public-pension private-markets investment officer. (i) Parse 50 quarterly PDFs into a fund × quarter panel (CP1: the identities above hold, and fund-name resolution is consistent). (ii) Derive quarterly cash flows from differences in cumulative values (CP2: recomputed IRR within 50 bp of reported for at least 90% of funds; explain outliers such as recallables, fee offsets or restatements). (iii) DPI, RVPI and TVPI by vintage and strategy; Kaplan-Schoar PME against the Fama-French market or S&P (CP3). (iv) Takahashi-Alexander pacing model to reach a target PE allocation of X% of plan assets, with total assets from PPD (CP4: projected NAV path stays within the policy range). Deliverable: commitment schedule by year and strategy.
   - **W-N2. Secondary-sale candidate screen.** Persona: same. Rank tail-end funds (age over 10 years, low unfunded, NAV share of TV over 50%). Estimate a discount needed to beat a hold-scenario IRR. Liquidity benefit for rebalancing back to policy.

## O. US public pension plan-level data (Public Plans Data) plus ACFRs and board decks

1. **What:** PPD (Center for Retirement Research at Boston College, MissionSquare, NASRA, GFOA): 250+ state and local plans, 100+ variables, annual since 2001. Includes actuarial assets and liabilities, funded ratio, contributions, benefits, investment returns (1/5/10-year), assumed return, and actual and target asset allocation (unverified exact fields). ACFR PDFs add detailed investment sections.
2. **Access:** Free download (terms unverified). ACFRs are PDFs on each system's site.
3. **Formats:** CSV (PPD). ACFRs are long PDFs (some scanned), very messy.
4. **Depth/cadence:** 2001 to 2024/25, annual. ACFRs annual, board decks monthly.
5. **Breadth:** 250+ plans (PPD); thousands of ACFRs.
6. **Join keys:** PPD plan ID, state, Census Government ID.
7. **Ground truth:** Market-value roll-forward: MVA_end = MVA_begin + contributions − benefits − expenses + investment income. Funded ratio = AVA/AAL. Asset allocation weights sum to 1. Geometric linking of annual returns against the reported 5/10-year returns.
8. **Usage:** Policy research (Pew, Equable); not in LLM benchmarks.
9. **Mirrors:** Kaggle `eshitakter/public-pension-plans-analysis-20012023` (2001-2024), Kaggle `meepbobeep/us-public-pensions-data-fiscal-years-20012016` (plus codebook), GitHub `donboyd5/pdata` (R, older), GitHub `megharaj2/Public-Pension-Plans-Analysis-2001-2023`.
10. **Workflow W-O1. Asset allocation against policy, with rebalancing.** Persona: pension board investment consultant. For one plan over 10 years: roll-forward check (CP1). Actual against target allocation and ranges (from the ACFR investment policy, PDF) (CP2: breach list). Required rebalancing trades. Realized geometric return against the assumed return. Contribution adequacy (actuarially determined against actual). Peer percentile against 50 plans.

## P. IRS Form 990 / 990-PF (endowments, foundations): GivingTuesday 990 data lake  [HIGH VALUE, REACHABLE]

1. **What:** IRS e-file XML of 990 (Schedule D Part V endowment roll-forward for 5 years: beginning balance, contributions, net investment earnings, grants or scholarships, other expenditures, administrative expenses, ending balance; Part VII/VIII investment detail) and 990-PF (Part I investment income; Part II balance sheet at book value and FMV with attached schedules of corporate stock and bonds; **Part IV lot-level capital gains**; Part XI/XII minimum investment return and distributable amount).
2. **Access:** Public S3 bucket `gt990datalake-rawdata` (VERIFIED reachable and listable). IRS TEOS public data.
3. **Formats:** XML with schema versions changing yearly. Attached statements are free-form (StockNm strings often prefix CUSIPs, for example `023135106 AMAZON COM INC`). Lots may be summarized ("595 TR Russell 1000 Value"). Messy.
4. **Depth/cadence:** 2009 to 2026 (2026 TEOS zips dated 2026-08-25). Monthly IRS batches. Contamination-resistant.
5. **Breadth:** 3.6M+ filings in total. About 100k+ 990-PF per year (unverified). All universities and hospitals file 990s.
6. **Join keys:** EIN. CUSIP inside the stock schedules, which joins to 13F/N-PORT. NTEE codes (BMF).
7. **Ground truth (VERIFIED fields):** In 40 large 2024 sample filings, 990-PF lot lines carry PropertyDesc, HowAcquiredCd, AcquiredDt, SoldDt, GrossSalesPriceAmt, CostOrOtherBasisAmt and GainOrLossAmt (up to 4,296 lots in one return). Schedule D `CYEndwmtFundGrp` is present in university returns. Checks: endowment EOY(t) = BOY(t+1) across the 5-year columns and across successive filings; BOY + contributions + earnings − grants − other − admin = EOY; gain = proceeds − basis per lot; Σ lots against the reported net gain. **In one sampled return Σ lot gains (15.6M) ≠ reported net gain (−10.6k)**, because lot detail mixes summary rows or pass-throughs. That messiness forces reasoning. Minimum distribution = 5% × average FMV of non-charitable-use assets, recomputable from Part X/XI.
8. **Usage:** Used by nonprofit researchers (ProPublica Explorer, IRSx). Not used by finance LLM benchmarks found.
9. **Mirrors:** S3 (above, the primary mirror). HF `piercewetter3/irs-990-parsed` (CC0, 20 GB) covers officers, grants and BMF but NOT Schedule D or Part IV investment detail. Kaggle `hayawi/...ntse-endowment-market-value` (NACUBO FY21 table for cross-checks).
10. **Workflows:**
   - **W-P1. Private-foundation year-end investment close and payout plan.** Persona: foundation CFO or outsourced tax preparer. (i) Parse 4,000 lot lines; classify short- or long-term by holding period (CP1: the counts implied by the reported ST and LT totals). (ii) Reconcile Σ lots to the Part I and Part IV net gain and explain the gap (K-1 pass-throughs, summary lines) (CP2). (iii) Recompute the 1.39% excise tax on net investment income (CP3 against reported). (iv) Recompute the distributable amount from average monthly FMV (CP4). (v) Join the CUSIP-tagged stock schedule to N-PORT/13F sector data, then plan next-year sales to fund the payout using tax-lot selection (HIFO) while rebalancing to a 70/30 policy.
   - **W-P2. University endowment peer analysis.** Persona: endowment office analyst. For 40 universities × 5 years from Schedule D Part V: implied Modified-Dietz return, effective spending rate, gift inflow rate (CP1: roll-forward and cross-filing consistency). Compare to NACUBO tables. Rank peers. Decompose growth into return, gifts and spending.

## Q. Kenneth R. French Data Library (factor and portfolio returns)

1. **What:** FF 3- and 5-factor, momentum, ST/LT reversal, size/BM/OP/Inv portfolios, 5-49 industry portfolios; US, developed, emerging and regional; daily, weekly and monthly. https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html.
2. **Access:** Free CSV zips. No formal license; academic norms. Blocked here.
3. **Formats:** CSV with text headers and multiple blocks per file (monthly and annual stacked), which is mildly messy.
4. **Depth/cadence:** 1926 to Jul-2026 (per a cached page). Monthly updates. Built from CRSP CIZ since the Jan-2025 release, and historical vintages are revised.
5. **Breadth:** Hundreds of series.
6. **Join keys:** Date (YYYYMM).
7. **Ground truth:** Used as a regressor; vintage differences matter (pin the vintage).
8. **Usage:** Ubiquitous in academia; LLMs know it well. Used here as a supporting input, not a core source.
9. **Mirrors:** Kaggle `nikitamanaenkov/famafrench-factors-and-portfolios`, Kaggle `waelelghazzawi/fama-french-factor-zoo-benchmarks` (to 2026), HF `krishnakamath/fama_french_data` (daily 2000+, 5 columns, VERIFIED via datasets-server).
10. **Workflow:** A component of W-A1, W-H1 and W-N1 (attribution and PME).

## R. Federal Reserve Z.1 Financial Accounts

1. **What:** Quarterly sector balance sheets, including private and public pension funds (L.117-L.120 family), mutual funds, MMFs and ETFs (L.121-L.124, unverified table numbers). https://www.federalreserve.gov/releases/z1/.
2. **Access:** DDP CSV zips with data dictionaries. Free. Blocked here.
3. **Formats:** CSV with series codes (FL/FU/FR prefixes); clean.
4. **Depth/cadence:** 1945 to present, quarterly (2025Q4 released 2026-03-19).
5. **Breadth:** Macro only.
6. **Join keys:** Series codes, quarter.
7. **Ground truth:** Flows equal the change in levels minus revaluations (FU vs FL vs FR identities).
8. **Usage:** Macro research; not in agent benchmarks.
9. **Mirrors:** None found (Kaggle `federalreserve/*` has a few FRED series from 2019, for example `institutional-money-funds`).
10. **Workflow:** Context layer for pension allocation (aggregate public-pension equity share against a plan's share). Low priority.

## S. UK/EU: UCITS KIID, PRIIPs KID, EMT/EPT files, UK LGPS documents

1. **What:** KIID/KID PDFs (ongoing charges, SRI 1-7, performance scenarios, cost tables). EMT/EPT pipe-delimited CSVs (FinDatEx templates) that some manufacturers publish (unverified which). UK LGPS Investment Strategy Statements and committee reports with strategic allocation and tolerance ranges (for example Barnet Mar-2025 ISS: listed equity 24% ±3%, credit 39.5% ±5%).
2. **Access:** Manufacturer and council websites. Scraping ToS varies. ESMA and FRC XBRL hosts were seen blocked in the proxy log.
3. **Formats:** PDFs (multi-language), CSV templates, council moderngov PDFs (messy and sometimes scanned).
4. **Depth/cadence:** KID updates at least annually; LGPS committee reports quarterly.
5. **Breadth:** Tens of thousands of UCITS; 86 LGPS funds plus 8 pools.
6. **Join keys:** ISIN (KIDs, EMT), LEI.
7. **Ground truth:** KID cost tables (entry, exit, ongoing, transaction, performance fee) sum to total cost. RIY recomputable. LGPS actual against target allocation.
8. **Usage:** None found.
9. **Mirrors:** None found.
10. **Workflow W-S1. UK LGPS quarterly rebalancing paper.** Persona: LGPS pension fund officer. From 4 quarterly committee PDFs: actual against strategic allocation and ranges, breach list, rebalancing cash flows across pool sub-funds, fee comparison from the pool sub-funds' KIDs. Low priority because there is no mirror.

## T. Australia superannuation (APRA statistics, Portfolio Holdings Disclosure)

1. **What:** Since 31-Mar-2022, RSE licensees must publish portfolio holdings semi-annually (identity, value, weight; unlisted assets aggregated). APRA MySuper and quarterly statistics publish product-level returns, fees and allocations.
2. **Access:** Fund websites (formats vary, unverified) and APRA xlsx.
3. **Formats:** XLSX/CSV/PDF by fund. Messy.
4. **Depth/cadence:** PHD semi-annual from 2022; APRA quarterly or annual.
5. **Breadth:** About 60 RSEs and hundreds of investment options.
6. **Join keys:** ISIN or ticker (listed), names.
7. **Ground truth:** Σ weights = 100%. Option asset allocation against the PDS strategic allocation. APRA fee and return identities.
8. **Usage:** None.
9. **Mirrors:** Kaggle `darylb/superannuation-mysuper-product-by-product-2013-20` (APRA MySuper 2013-2020). No PHD mirror found.
10. **Workflow W-T1. Member switch analysis.** Persona: Australian financial adviser. Compare 5 balanced options on fees, look-through holdings and returns; check the performance-test outcome (YFYS). Low priority.

## U. Lower-value or derivative datasets (noted, not recommended as cores)

- Kaggle `stefanoleone992/mutual-funds-and-etfs` (Yahoo Finance scrape, 23,783 MFs and 2,310 ETFs, Nov-2021; CC0 claimed but derived from Yahoo ToS; not primary).
- Kaggle `andrezaza/large-etfs-with-size-allocations-and-exposures`; EDHEC hedge fund index sets (`yousefsaeedian/edhec-investment-management-datasets`).
- ZipLime/company-fundamentals and ZipLime/security-master as join helpers (Apache-2.0).

---

## Ranked top 5 for this slice

**1. US fund stack built on N-PORT** (plus RR fees, N-CSR/TSR, 13F, FF factors, security-master). Mirrors: `trader298/sec-nport`, `ZipLime/fund-holdings-nport`, `ZipLime/institutional-portfolio-13f`.
- *Workflow depth:* the deepest in the slice. Holdings, flows, returns, derivatives, DV01 and net assets for about 17.5k funds support due diligence, look-through, liquidity, attribution and fee analysis in one place.
- *Verifiability:* monthly net-asset roll-forwards, Σholdings ≈ NA, and 13F control totals (95.6% match, so 4.4% need investigation) give numeric checks at every step.
- *Messiness:* moderate (TSV traps). Add N-CSR HTML for harder parsing.
- *Differentiation:* no agent benchmark uses N-PORT.
- *Scrapability:* bulk and public domain.
- *Risk:* quarterly refresh; the HF LFS CDN must be unblocked; N-MFP, N-CEN, RR and N-CSR have no mirrors.

**2. India AMC monthly and fortnightly portfolio XLS plus AMFI NAV and TER.** Mirrors: GitHub `subscriptionmanager26-png/fund-disclosures` (raw), `kushagra-agarwal-a/fund-holdings-data` (parsed), Kaggle `tharunreddy2911/...`, `darshshah1010/...`, `neeeeeemo/...ter...`.
- *Messiness:* the most realistic spreadsheet mess found (51 AMC layouts, up to 108 sheets per workbook, ₹ lakh units, ZIPs, revised files).
- *Contamination:* very fresh data (Jun to Sep 2026, monthly plus fortnightly); daily NAV and TER.
- *Verifiability:* natural checksums (% NAV sums to 100 for 93% of sampled schemes, and the outliers make good traps; NAV against holdings; Direct/Regular against TER).
- *Breadth:* a real wealth-manager workflow (review, overlap, category compliance, tax-aware switch).
- *Risk:* the raw mirror holds one month; more months need scraping AMC sites (blocked here); no explicit licenses.

**3. Public-pension private-equity fund reports (WSIB/CalPERS PDFs) plus PPD plan data.** Mirrors: Kaggle `jblumenstein/wsib-private-equity-data-q1-2009-to-q2-2021` (original PDFs and OCR) and `eshitakter/public-pension-plans-analysis-20012023`.
- *Format:* raw PDF tables that needed OCR, covering 50 quarters.
- *Verifiability:* VERIFIED accounting identities above 99%, and net IRR recomputed from quarterly deltas within 17 bp of reported.
- *Workflow:* the classic long CIO-office job (cash-flow derivation, IRR/TVPI/PME, vintage analysis, pacing toward a policy target).
- *Differentiation:* no prior benchmark use.
- *Risk:* the mirror stops at 2021Q2. Newer quarters (to 2025Q3) exist at sib.wa.gov but are blocked here. License unknown (public records).

**4. IRS 990-PF / 990 XML (GivingTuesday S3).**
- *Access:* the only primary raw source in this slice that is directly reachable from the container; refreshed to Aug-2026.
- *Unique content:* real **lot-level tax data** (acquired and sold dates, proceeds, basis, gain), CUSIP-tagged holdings schedules, endowment 5-year roll-forwards and payout rules. Supports tax-lot reasoning, excise tax, minimum distribution and endowment spending analysis.
- *Verifiability and messiness:* strong identities, and the gaps found (for example Σ lots ≠ reported gain) force explanation.
- *Differentiation:* near zero overlap with finance benchmarks.
- *Risk:* heavy XML schema variation, and lot detail quality varies by preparer.

**5. Brazil CVM fund open data (daily NAV and flows plus monthly CDA holdings).** Mirrors: HF `Shote/fundos-cvm`, `PrumoFS/acompanhamento-fundos-site`.
- *Breadth and cadence:* universe-wide daily quota, equity, flows and holders, updated to 2026-10-15.
- *Verifiability:* flow-adjusted equity roll-forward every day, CDA Σ against equity, and fee checks.
- *Differentiation:* Portuguese, the CVM 175 regime change, CNPJ keys. Allocator workflows (manager selection, drawdown, liquidity sizing).
- *Risk:* mirrors state no license, and CDA history in open data starts in 2018.

**Honorable mentions:**
- **13F with the ARK daily-holdings git history** (overlap and conviction, trade reconstruction; strong, but the famous books are contamination-prone).
- **N-MFP** (excellent WAM/WAL/DLA/WLA recompute checks, monthly; no mirror).
- **NBIM 1998-2023** (entity resolution without ISINs; Kaggle mirror).
- **GPIF/CPP** (policy bands; no mirror).

**Suggested composite environments:**
- (a) *"One fund complex deep"*: N-PORT + RR + N-CSR + N-CEN for one family over 6 years.
- (b) *"Universe broad"*: N-PORT plus 13F across 500 equity funds for overlap and crowding.
- (c) *"India wealth desk"*: AMC XLS + AMFI NAV/TER for 40 schemes.
- (d) *"Pension CIO office"*: WSIB PE PDFs + PPD + FF factors + NBIM/GPIF peers.
- (e) *"Foundation finance office"*: 990-PF lots and holdings joined to N-PORT/13F sector data.
