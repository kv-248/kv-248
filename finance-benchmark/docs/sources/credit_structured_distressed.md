# Slice: Credit, Lending, Banking, Structured Finance, Distressed / Restructuring — Source Catalog

Researched 2026-10-17. Ranked top-5 is in §6. The mirror quick-reference (exact IDs) is in §7.

Evidence tags:
- **[V-box]**: checked with curl from this container (HF Hub API, HF datasets-server, Kaggle API, GitHub contents API).
- **[V-web]**: confirmed by a WebSearch result snippet. I could not open the page, because WebFetch fails DNS on every host tried.
- **[unverified]**: from background knowledge, or inferred. Check before building on it.

---

## 0. What this container can reach (affects every "mirror" claim)

| Host | Status here | Notes |
|---|---|---|
| huggingface.co (Hub API, repo metadata, small README/git files) | OK [V-box] | `api/datasets?search=`, `api/datasets/{id}?blobs=true`, and `resolve/main/README.md` all work. |
| datasets-server.huggingface.co (`/first-rows`, `/size`, `/splits`) | OK [V-box] | `/rows` paging returned "Unexpected error" on the one ABS-EE repo I tried. `/search` timed out on a 16 GB repo. |
| **HF LFS/Xet CDN (us.aws.cdn.hf.co, cdn-lfs*.hf.co, cas-bridge.xethub.hf.co)** | **BLOCKED (403 CONNECT)** [V-box] | Parquet and zip payloads on HF **cannot be downloaded from this container**. Pull them in the build environment, or ask for an allowlist change. |
| kaggle.com API + storage.googleapis.com (download redirect) | OK, **no auth needed** [V-box] | Downloaded `cmdrvl/cmbs-deals-edgar-cik-and-collateral-distribution` end to end. |
| raw.githubusercontent.com, api.github.com/repos/... | OK [V-box] | **GitHub search API is blocked** ("sessions are bound to their configured repositories"). |
| sec.gov, data.sec.gov, ffiec.gov, fdic.gov, federalreserve.gov, consumerfinance.gov, sba.gov, ginniemae.gov, justice.gov, uscourts.gov | BLOCKED [V-box] | |
| Claims agents (restructuring.ra.kroll.com, cases.stretto.com, dm.epiq11.com, omniagentsolutions.com, veritaglobal.net, kccllc.net) | BLOCKED [V-box] | |
| courtlistener.com, storage.courtlistener.com, finra.org, emma.msrb.org, fred.stlouisfed.org, eba.europa.eu, ecb.europa.eu, rbi.org.in, ibbi.gov.in, Companies House, bank websites, rating agency sites, zenodo, archive.org | BLOCKED [V-box] | |

**Implication:** every primary source in this slice has to be scraped **outside** this container. In-container work is limited to Kaggle downloads and HF metadata and previews.

---

## 1. STRUCTURED FINANCE

### 1.1 SEC Reg AB II asset-level data (Form ABS-EE, EX-102/EX-103) + Form 10-D + 424B prospectus — ★ TOP PICK
1. **What & URL.** EDGAR filings by registered ABS trusts. Form ABS-EE carries EX-102, the Asset Data File (Schedule AL XML, one record per loan/lease/property, every month), and EX-103, the Asset Related Document. Form 10-D carries the monthly distribution/servicer report, usually EX-99.1 in HTML. The 424B2/424B5 prospectus holds the waterfall, triggers and cutoff-date stratification tables. `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<trust CIK>`. Example 10-D servicer report: `https://www.sec.gov/Archives/edgar/data/0001260125/000114420416125488/v449368_ex99-1.htm` (Hyundai) [V-web].
   - **Asset classes covered.** Residential mortgages, commercial mortgages, auto loans, auto leases, and debt securities including resecuritizations. Compliance began 2016-11-23 [V-web]. Motorcycle loans (e.g., Harley-Davidson Motorcycle Trust) file under the auto-loan schedule [V-box, mirror].
   - **RMBS is effectively empty.** The SEC says there have been no SEC-registered RMBS offerings since the 2014 rules. A Sept-2025 concept release revisits Item 1125 [V-web].
   - **Not covered:** credit cards, student loans, equipment and floorplan [V-web]. Their 10-Ds carry only pool-level data (see 1.2).
2. **Access / ToS.** EDGAR is public domain. SEC fair-access policy: at most 10 requests/second and a declared User-Agent [unverified, standard]. Full-text search covers 2001+. No auth.
3. **Formats & messiness.**
   - EX-102 XML is clean and schema-valid, but data quality varies by issuer: codes vs. labels, missing optional fields, `ABS-EE/A` restatements, and loan IDs that change format between early and later filings.
   - 10-D EX-99.1 servicer certificates are HTML tables that differ by issuer, sometimes PDF.
   - 424B5 is long HTML or PDF. The waterfall is in legal prose, and the strats are HTML tables.
   - CMBS 10-D trustee statements follow the CREFC IRP layout [unverified].
   - Field counts: auto loans 72 fields, auto leases 66 [V-web], CMBS about 113 columns in the mirror [V-box].
4. **Depth & cadence.** Monthly from 2016-11 to now, filed about 15 days after the period end. One deal runs 2–10 years.
5. **Breadth.** About 260 CMBS deals with Schedule AL through 2023 [V-box: Kaggle `cmdrvl` list has 262 rows]. Several hundred auto trusts (Ally, AmeriCredit/GM Financial, CarMax, Carvana, Ford, Honda, Hyundai, Nissan, Santander Drive, Toyota, World Omni, BMW, Mercedes, Porsche, Bridgecrest, and others).
6. **Join keys.**
   - Trust CIK and depositor CIK.
   - Accession number (adsh).
   - `assetNumber` (loan ID, stable within a trust).
   - `reportingPeriodEndDate`.
   - Class CUSIPs, in the 10-D and 424B.
   - CMBS only: prospectus loan ID, property name and address. Joins across deals for pari-passu notes go on property address [unverified].
7. **Natural ground truth / internal checks.**
   - Σ loan `reportingPeriodEndActualBalanceAmount` (or securitization value for leases) should equal the 10-D pool balance.
   - Beginning balance − scheduled principal − prepayments − charge-offs = ending balance, at both loan and pool level.
   - CMBS interest can be recomputed exactly. Mirror row for BANK 2021-BNK31 loan 1: $54,000,000 × 3.309% × 28/360 = **$138,978 = `scheduledInterestAmount`** [V-box].
   - Delinquency buckets from `currentDelinquencyStatus` / `paymentStatusLoanCode` vs. the 10-D delinquency table.
   - Cumulative net loss vs. the 10-D CNL. Reserve account and OC target vs. 424B formulas. Class balances after the waterfall vs. the 10-D note balances.
   - Cutoff strats in 424B vs. the first EX-102.
   - Trigger tests (e.g., 60+ DQ ratio) vs. the reported trigger status.
8. **Existing benchmarks.** None found for ABS surveillance, waterfalls or Reg AB data [V-web: searches for structured-finance LLM benchmarks returned only general finance benchmarks such as FinMaster and FrontierFinance]. HF has two small ML derivatives:
   - `catyung/cre-cmbs-loans` (2,313 properties from 22 CMBS trusts).
   - `commandreveal/cmbs-special-servicing-*` (CC-BY-NC, gated auto).
9. **Mirrors.**
   - **HF `DenyTranDFW/*`: 1,072 repos [V-box].** About 656 auto/lease/motorcycle and about 375 CMBS trust repos, plus depositor-level repos such as `DenyTranDFW/SANTANDER_DRIVE_AUTO_RECEIVABLES_LLC_1383094` (2,785 filings indexed) and `DenyTranDFW/AFS_SENSUB_CORP_1347185`.
     - Layout: one repo per trust, named `<Trust_Name>_<CIK>`, with parquet at `{accession}/{exhibit}.parquet`. The README has a filing index with sec.gov URLs. Tags: `abs-ee`. License label: "gpl".
     - **Coverage is uneven** (sample of 40 READMEs) [V-box]:
       - Complete examples: `DenyTranDFW/AmeriCredit_Automobile_Receivables_Trust_2020_1_1801390` (54/54 filings, 148 MB), `DenyTranDFW/Toyota_Auto_Receivables_2021_C_Owner_Trust_1878610` (231 MB), `DenyTranDFW/Honda_Auto_Receivables_2021_1_Owner_Trust_1840882` (193 MB), `DenyTranDFW/Ford_Credit_Auto_Lease_Trust_2020_B_1816750` (31/31), `DenyTranDFW/World_Omni_Automobile_Lease_Securitization_Trust_2021_A_1863708` (31 files, 77.6 MB).
       - Partial examples: many repos hold only 1–8 parquet files for 40–60 filings (e.g., `DenyTranDFW/CITIGROUP_COMMERCIAL_MORTGAGE_TRUST_2019_GC43_0001791183`: 66 filings, 7 parquets).
       - **Check per trust before you pick one.**
     - Schema: CMBS has about 113 columns, auto lease 55 [V-box].
     - **Holds ABS-EE only. No 10-D or 424B.**
   - **Kaggle `denytran/10-year-automotive-loans-abs-ee`:** "35M+ lines" of auto loans, U.S. Government Works, 803 MB [V-box]. Downloadable here.
   - **Kaggle `cmdrvl/cmbs-deals-edgar-cik-and-collateral-distribution`:** CC0. 262 CMBS deals with EDGAR CIK, shelf, first/last filing, property-type mix [V-box, downloaded]. Good as a CIK index.
   - **10-D and 424B: no mirror found.** `TeraflopAI/SEC-EDGAR` covers 10-K/10-Q/8-K/S-1/20-F/3/4/5/144/S-8 only [V-box]. `anonymous-md/EDGAR_FILINGS_DATASET_2022_2026H1` holds 1.72M parsed filings of all form types for 2023–2026H1 (fields include `has_ocr`) [V-box]. It **may** include 10-D/424B, but the full-text search timed out, so that is unverified.
10. **Workflow sketches.**
    - **(a) Auto ABS monthly surveillance. Persona: ABS surveillance analyst at an insurer holding the Class B notes of AmeriCredit 2020-1 (subprime).**
      1. *Tape cut:* load 24 monthly EX-102 tapes, build a loan × month panel, and flag payoffs, charge-offs (Schedule AL charge-off fields; exact auto-loan field names unverified) and repurchases (`assetSubjectDemandIndicator`). **CP1:** Σ ending balance = 10-D pool balance.
      2. *Stratification:* rebuild the cutoff strats (APR, FICO, original term, LTV, state, new/used). **CP2:** match the 424B5 tables.
      3. *Performance:* roll-rate matrix, monthly gross and net losses, recovery rate, ABS prepayment speed, cumulative net loss curve and annualized net loss. **CP3:** the 10-D delinquency % and CNL %.
      4. *Waterfall:* encode the 424B priority of payments (servicing fee → Class A interest → … → principal distributable amount → reserve to target → OC/turbo → residual) and run it on the collections. **CP4:** post-distribution note balances and reserve balance in the 10-D.
      5. *Triggers:* compute the CNL/delinquency triggers. **CP5:** reported trigger status.
      6. *Projection:* fit a loss timing curve, project CNL, compute breakeven loss multiples for Class B/C/D. The memo is scored by LLM judge.
    - **(b) CMBS watchlist and refinance-risk review. Persona: CMBS B-piece / special-servicing analyst, BANK 2021-BNK31.**
      1. Recompute the DSCR (NOI and NCF bases), debt yield and current LTV from `mostRecent*` fields. **CP:** the reported DSCR fields.
      2. Recompute interest, Actual/360. **CP:** `scheduledInterestAmount`.
      3. Watchlist flags: DSCR < 1.10x, occupancy drop, largest-tenant rollover before loan maturity.
      4. Maturity wall: refinance test at the current Treasury curve plus a spread (Treasury curve from HF `Farmaanaa/us_treasury_yield_curve_daily`).
      5. Appraisal Reduction Amount for delinquent loans (balance + advances − 90% × appraisal), then allocate losses bottom-up through the tranche stack from the 424B. **CP:** ARA and realized loss in the 10-D.
      6. Credit-enhancement erosion memo.

### 1.2 Pool-level-only ABS 10-Ds (credit cards, student loans, equipment, floorplan)
1. Credit-card master trust 10-Ds report portfolio yield, charge-offs, payment rate, excess spread and the 3-month average excess spread vs. the early-amortization trigger. Student-loan trusts report FFELP/private pool data. Same EDGAR access as 1.1 [unverified detail; the absence of asset-level data is V-web].
2–6. Same as 1.1. Monthly. Join key: trust CIK.
7. Excess spread = yield − charge-offs − coupon − servicing, recomputable. 3-month average vs. trigger.
8. No benchmark use found. 9. No mirror found.
10. Persona: card ABS analyst. Rebuild 36 months of excess spread, forecast the trigger cushion under a stress scenario, and compare issuers. Secondary priority.

### 1.3 Freddie Mac SFLLD / Fannie Mae Single-Family Loan Performance / CAS & STACR
1. About 55M Freddie loans originated 1999-01 to 2025-09, with monthly performance. Fannie's set is similar [V-web].
2. **Registration required. Internal or non-commercial research use only. Redistribution needs a paid license** (Freddie template ~$26k; Fannie $25k/$50k) [V-web]. **Flag: shipping this data inside a benchmark environment is likely redistribution.**
3. Clean pipe-delimited text.
4. 1999/2000 to present, quarterly refresh.
5. National.
6. Loan sequence number, pool ID, CRT deal reference.
7. Balance roll-forward; zero-balance codes vs. loss fields. Natural CDR/CPR.
8. Widely used in ML. Not in LLM-agent benchmarks.
9. HF `yeigen/fannie-mae-loan-performance` and `Alej0909/fannie-mae-loan-performance-raw` (31.6 GB each, quarterly parquet 2000Q1+), and `Shlok112003/Fannie_Mae_Single-Family_Loan_Performance` (48.8 GB, six quarters) [V-box]. Kaggle `qhhuang/fannie-mae-single-family-loan-performance` (400 MB, licence "Unknown"). Kaggle `jeromeblanchet/fannie-mae-freddie-mac-public-use-database` (FHFA PUDB, 2.6 GB). **All have licence risk.**
10. Persona: GSE CRT analyst. Vintage CDR/CPR curves → loss severity → CAS/STACR tranche write-down estimate. **Recommend excluding** because of licensing. Use Ginnie (1.4) or ABS-EE instead.

### 1.4 Ginnie Mae disclosure data (MBS SF loan-level, pool, factor files)
1. Monthly loan-level portfolio files for Ginnie I and II, new issuance, liquidations, and pool/factor files. `https://bulk.ginniemae.gov/layout_sample.aspx` [V-web].
2. You agree to Terms of Use on the download page. Use is limited to analysing Ginnie MBS, and identifying individuals is forbidden [V-web]. Whether registration is required is unverified.
3. Fixed-width or delimited text. Some fields are truncated or masked: actual UPB is blanked for the first 6 months, and the MSA is masked [V-web].
4. Monthly (around the 10th business day [V-web]), 2013/2014+.
5. All Ginnie SF pools (FHA/VA/USDA).
6. Pool ID, CUSIP, loan sequence, issuer ID.
7. Σ loan UPB vs. pool factor × original face. Delinquent buyouts visible in the liquidation files.
8. None found.
9. **Kaggle `riziles/mbs-sf-port-loan-level-ginnie-ii`:** "Ginnie Mae Single Family Loan Level Data", U.S. Government Works, 559 MB [V-box]. Probably one month.
10. Persona: agency MBS prepayment analyst. Pool CPR from loan level → reconcile to factor → split voluntary vs. buyout (involuntary) speeds by issuer → servicer buyout behaviour memo.

### 1.5 European / UK structured finance and covered bonds
- **Covered bonds, ECBC/Covered Bond Label Harmonised Transparency Template (HTT).**
  - What it is: issuer-published Excel/PDF workbooks with Tab A (general and OC), B1 (mortgage assets), B2 (public sector) and C (glossary). Published at least quarterly; many issuers publish monthly [V-web].
  - Examples: Société Générale SFH, e.g. `https://www.societegenerale.com/sites/default/files/documents/2026-09/sg-sfh-htt-covered-bond-label-reporting-31-07-2026.pdf`; Nordea Kredit; CGD [V-web].
  - No central bulk download found.
  - Natural checks: nominal and NPV OC recomputation, LTV and maturity buckets summing to the cover pool, OC vs. the legal minimum.
  - No mirror. Workflow persona: covered-bond investor comparing OC buffers and maturity mismatch across 5 issuers.
- **UK RMBS/ABS investor reports.** Monthly PDF/XLS on issuer sites (master trusts). Loan-level data sits in securitisation repositories (EDW/SecRep) that need registration [unverified]. Not prioritized.
- **UK securitisation SPVs.** HF `dacheah/uk-securitisation-spv-charges`: 25-entity teaser of Companies House charges for 478 SPVs; full set gated or paid [V-box].

### 1.6 CLO trustee reports
- **Generally not public.** They go to noteholders via Intex, Trepp or trustee portals. Rare exceptions: a 2011 8-K shows a BDC (TICC) posting its CLO's monthly trustee report on its IR site [V-web]. Some Irish-listed CLOs may post reports [unverified].
- **Practical proxy:** BDCs' consolidated CLO subsidiaries and CLO-equity funds (N-PORT/N-CSR), plus N-PORT holdings of CLO tranches (see 3.2). Not ranked.

---

## 2. BANKING (REGULATORY)

### 2.1 FFIEC Call Reports (CDR bulk) + UBPR — ★ TOP PICK
1. Quarterly Reports of Condition and Income (FFIEC 031/041/051) for every insured US bank, at `cdr.ffiec.gov` (bulk "Call Reports – Single Period"). UBPR is the FFIEC-computed ratio report derived from the Call Report.
2. Public. No auth for bulk download. Blocked here.
3. Bulk files are tab-delimited, one per schedule, keyed by MDRM codes. Messy points:
   - Schedules and line items change over time (CECL/ACL from 2019+, the 051 short form, CBLR).
   - Confidential items are blank.
   - Individual Call Report PDFs are image-like forms.
4. Quarterly. Mirror covers 2001Q1 to the latest quarter; UBPR 2002+.
5. About 4,500 banks now, about 10,000 in 2001.
6. **IDRSSD** (primary), FDIC cert, CIK of the holding company via the NIC hierarchy, LEI [unverified in bulk].
7. **Natural ground truth (strong).**
   - RC: total assets = total liabilities + equity capital.
   - RC-C loan categories sum to RC line 4.
   - RI-B Part II ACL roll-forward: beginning + provision − charge-offs + recoveries ± adjustments = ending, and ending ties to RC.
   - RC-N past-due/nonaccrual by category.
   - RC-R capital ratios recomputable from components.
   - **UBPR ratios are an independent, FFIEC-computed answer key for any ratio the agent derives.**
   - RC-B AFS/HTM amortized cost vs. fair value gives unrealized losses.
   - RC-O uninsured-deposit memo items.
8. Existing benchmarks: none found for Call Reports [V-web search]. One Pillar-3/bank-statement QA benchmark exists (see 2.5).
9. **Mirrors.**
   - **HF `kairusama/call-report-one`:** CC0, 817 files, 2.91 GB, `data/call_report_YYYYMMDD.parquet` for 2001-03-31 onward, plus views (`consolidated_gs/hjk/rest`, `domestic_*`, `income_and_supplemental`) and `metadata/column_dictionary.json`. Join on `Reporting Period` + `ID RSSD`. Updated 2026-10-16 [V-box].
   - **HF `kairusama/ubpr-one`:** CC0, 171 files, 4.81 GB, `data/ubpr_YYYY.parquet` from 2002 [V-box].
   - **Kaggle `neutrino404/all-us-banks-financial-quarterly-ratios-2001-2023`:** CC0, 1.42 GB [V-box]. FDIC-derived ratios.
   - **Kaggle `fdic/bank-failures`:** CC0, 1934+. **Kaggle `utkarshx27/failed-banks-database`:** U.S. Gov Works, "failed since 2000–2023 with balance sheet". **HF `emperor-mew/fdic-failures`:** 4,114 records [V-box].
10. **Workflow sketches.**
    - **(a) Failed-bank post-mortem / early warning. Persona: FDIC/state bank examiner.**
      1. Pull 16 quarters for a bank that failed in 2023–24 (from the failures list).
      2. Rebuild the balance sheet and P&L from MDRM codes. **CP:** RC and RI identities.
      3. ACL roll-forward. **CP:** RI-B ties.
      4. Compute NIM, efficiency, NCO, Tier 1 leverage, noncore funding and loan/deposit ratios. **CP:** UBPR values.
      5. Securities: AOCI and HTM mark-to-market as % of Tier 1, and CET1 pro forma for HTM losses.
      6. Liquidity: uninsured deposits / total deposits; borrowings capacity.
      7. CRE concentration tests: CRE / (Tier 1 + ACL) ≥ 300% and CLD ≥ 100% (2006 guidance), plus 36-month CRE growth.
      8. Peer percentile vs. a universe of the same size class.
      9. CAMELS-style memo naming the earliest quarter that should have triggered heightened supervision. Scored by LLM judge plus numeric CPs.
    - **(b) Universe screen. Persona: bank credit analyst at a deposit broker / FHLB.** Screen all banks each quarter for capital, asset quality and liquidity red flags. Build a rating model with weighted scores. Back-test against the failures list (natural labels).

### 2.2 FR Y-9C (BHC consolidated) / FFIEC NIC
1. Quarterly consolidated BHC financials (Fed/FFIEC NIC "Financial Data Download") [unverified URL].
2. Public. Blocked here.
3. MDRM-coded CSV. Schedules HC, HI, HC-R.
4. Quarterly, 1986+ [unverified].
5. Several hundred BHCs above the asset threshold.
6. RSSD, plus CIK via the NIC.
7. Same identities as the Call Report. Parent-only Y-9LP vs. consolidated.
8. None.
9. HF `Wgurtler/y9c-data`: about 20 MB, processed, no licence, unknown provenance [V-box]. **No full mirror.**
10. Persona: bank-holding-company credit analyst. Combine with 10-K and DFAST results (2.4).

### 2.3 FDIC BankFind Suite API / SDI / failed-bank list / Summary of Deposits
1. `api.fdic.gov` / BankFind. Institutions, financials (SDI), history, failures, branch deposits [unverified URLs].
2. Free API, no key [unverified]. Blocked here.
3. JSON/CSV.
4. Quarterly. Failures from 1934.
5. All insured institutions.
6. FDIC cert, RSSD.
7. Failures list: DIF cost estimate, assets and deposits at failure.
8. None.
9. Mirrors are listed in 2.1(9).
10. Combine with 2.1(a).

### 2.4 Federal Reserve supervisory stress test (DFAST) results + bank-run DFAST disclosures
1. Annual June results.
   - Fed side: a results PDF with bank-level appendix tables (projected loan losses by portfolio, PPNR, minimum capital ratios), a "Results Data" download, scenario CSVs, and a data dictionary (`https://www.federalreserve.gov/supervisionreg/files/DFAST_data_dictionary_2026.pdf`) [V-web].
   - Bank side: each bank publishes its own company-run results (PDF) on its website.
2. Public. Blocked here.
3. PDF tables plus CSV.
4. Annual, 2013+.
5. About 20–35 large banks.
6. RSSD, bank name, CIK.
7. Capital roll: starting CET1 − losses + PPNR − taxes … = minimum CET1. SCB = (start CET1 − min CET1) + 4 quarters of planned dividends / RWA, floored at 2.5%. Check it against the Fed-announced SCB [unverified that the formula is still current; the Fed has proposed averaging].
8. None found.
9. No mirror.
10. Persona: bank capital planner / sell-side bank analyst. Rebuild each bank's stress-capital path, compute the implied SCB, then estimate the excess capital and buyback capacity given Y-9C RWA.

### 2.5 Pillar 3 disclosures (EU/UK/other banks) + EBA Pillar 3 Data Hub + EBA Transparency Exercise — ★ #5
1. Basel Pillar 3 reports: quarterly, semi-annual or annual PDF plus XLSX, standardized templates (KM1, OV1, CC1/CC2, LR1/LR2, CR1–CR10, CCR, MR, IRRBB1, LIQ1/2).
   - **EBA Pillar 3 Data Hub (P3DH)** went live around end-January 2026. Banks submit in XBRL-CSV, and selected templates download in machine-readable form [V-web].
   - **The EBA Transparency Exercise was discontinued from June 2025.** The last results cover 119 banks at four dates, 2024Q3–2025Q2, published as an xlsx annex. Older CSVs (2015, 2020) exist [V-web].
2. Bank websites and EBA are public. Blocked here.
3. PDF tables that sometimes span pages, XLSX with merged cells, XBRL-CSV. Each bank uses its own formatting. **High messiness.**
4. Quarterly. EU CRR2 template set since 2021.
5. All EU large institutions; UK under the PRA; also CH, CA, AU, IN (India's RBI Basel III Pillar 3).
6. LEI (P3DH), bank name.
7. **Rich internal reconciliations.**
   - OV1 RWA components sum to the total, and capital requirement = 8% × RWA.
   - KM1 ratios = CC1 capital ÷ OV1 RWA.
   - CC2 reconciles the balance sheet to regulatory scope.
   - LR2 exposure measure components; LIQ1 LCR = HQLA ÷ net outflows.
   - CR1 NPE ratio. Values tie across quarters and to the annual report.
8. **Existing:** arXiv 2609.03654, "Enhancing Financial Question Answering: A Novel Benchmark Dataset of Banks' financial statements". Per the snippet it pairs 89 Pillar 3 reports with 120 annual reports from 24 EU and US banks and has 10 indicators such as CET1 [V-web snippet only]. **It is QA/RAG, not a workflow.**
9. **No mirror found** on HF or Kaggle.
10. Persona: bank credit analyst or supervisor doing a peer review of 6 EU/UK banks.
    1. Extract KM1, OV1, CC1, LR2 and LIQ1 over 8 quarters. **CP:** internal sums and ratio recomputation.
    2. RWA-density and IRB-vs-SA analysis (CR4/CR6).
    3. NPE/coverage from CR1.
    4. Capital headroom vs. the MDA threshold. SREP/P2R comes from the bank's PDF text.
    5. Leverage-constraint test.
    6. Memo ranking the banks' resilience.

### 2.6 RBI bank-wise data (India)
1. "Statistical Tables Relating to Banks in India": bank-wise balance sheet, P&L and NPA (Table 28), via DBIE `dbie.rbi.org.in`. The latest edition confirmed is 2021-22 [V-web]. Also bank-wise Basel III Pillar 3 on bank sites.
2. Public. Blocked here (`rbi.org.in`).
3. XLSX/PDF.
4. Annual.
5. About 90+ scheduled commercial banks [unverified].
6. Bank name. No standard ID.
7. GNPA − provisions = NNPA. Balance-sheet identity.
8. IndiaFinBench (arXiv 2604.19298) uses SEBI/RBI *regulatory text*, not bank data [V-web].
9. No mirror (HF `gtfintechlab/reserve_bank_of_india` is text).
10. Persona: Indian bank analyst. NPA migration and provision-coverage peer study. Lower priority.

### 2.7 Consumer/mortgage lending regulators: HMDA, CFPB complaints, CFPB credit-card agreements, NCUA 5300
- **HMDA LAR.**
  - About 12M loan applications a year with 99 fields (pricing, rate spread, denial reasons).
  - Mirrors: HF `retrogradespace/hmda_2024` (CC0, 0.54 GB, 12,229,298 rows) [V-box]; HF `xaheli/HMDA_LAR_2017-23` (12.2 GB, MIT label); `adi-123/hmda-2023-snapshot`; `leonardo-alexander/national-hmda-2022`.
  - Join keys: LEI, census tract.
  - Ground truth: FFIEC aggregate and disclosure reports.
  - Persona: fair-lending compliance analyst. Lender-level denial and pricing disparity analysis with controls, peer benchmarking and a matched-pair file review.
  - Common in ML; moderate differentiation.
- **CFPB complaints:** HF `CFPB/consumer-finance-complaints` and many copies. Text-heavy. Low numeric depth.
- **CFPB credit-card agreements:** HF `yonathanarbel/Credit_Card_Agreements` (PDF/text) [V-box]. Possible APR/fee-term extraction.
- **NCUA 5300 credit-union call reports:** no mirror found (HF has only `emperor-mew/ncua-enforcement`).

---

## 3. LEVERAGED LOANS / PRIVATE CREDIT

### 3.1 BDC filings: 10-K/10-Q Schedule of Investments (iXBRL) + SEC "BDC Data Sets" — ★ TOP PICK
1. About 196 BDCs (SEC BDC report) file quarterly 10-Q/10-K with a full Schedule of Investments (SOI): borrower, industry, instrument (1L/2L/unitranche/equity), reference rate + spread, floor, PIK, maturity, par, cost, fair value, % of net assets, non-accrual flags.
   - **SEC DERA "BDC Data Sets"** (announced June 2025) are flat files extracted from BDC XBRL: tables SUB, TAG, NUM, TXT, PRE, CAL, NON **and SOI**. Updated monthly (2026 Jan–Mar ZIPs listed, e.g. 39.8 MB) [V-web]. Earlier quarterly ZIPs (2022Q4, 2023Q1) are mentioned on data.gov [V-web, unverified start date].
   - URLs: `https://www.sec.gov/data-research/sec-markets-data/bdc-data-sets`; readme `https://www.sec.gov/files/bdc_readme.pdf`.
2. Public domain. Blocked here.
3. Raw HTML SOIs run to hundreds of pages. Messy points:
   - Multi-page tables with industry subtotals.
   - Footnote markers carry the meaning (non-accrual, PIK, unfunded).
   - Text formats vary ("S + 5.75% (1.00% floor)").
   - XBRL tagging errors are common: subtotals tagged on the InvestmentIdentifierAxis and missing issuer-affiliation enumerations. The SEC flagged these in June 2025 [V-web]. XBRL US DQC rules 0142 and 0218 target them [V-web].
4. Quarterly. XBRL SOI tagging in practice from about 2022–23 [unverified start]. HTML back to the 2000s.
5. About 150 BDCs with detailed SOI XBRL. edgartools reports 148 BDCs and 106,715 SOI entries for 2024Q3 [V-box, edgartools docs].
6. BDC CIK, file number 814-xxxxx, borrower name (needs entity resolution), CUSIP/LoanX rarely, industry.
7. **Natural ground truth.**
   - Σ SOI fair value = balance-sheet "investments at fair value". edgartools exposes `reconciliation_gap` and handles unfunded-commitment netting: FSK rows sum to $14.5B vs. $13.0B reported until netting [V-box, edgartools docs].
   - Σ cost vs. reported cost. % of net assets vs. NAV.
   - Weighted-average yield vs. the MD&A figure. Non-accrual % at cost and at FV vs. MD&A.
   - The asset-coverage ratio (1940 Act, 150% if elected) is disclosed in the notes and recomputable.
   - Same borrower held by several BDCs gives a cross-filer mark-consistency check.
8. Not used by existing benchmarks [V-web; FinanceBench and similar cover operating companies' 10-Ks].
9. **Mirrors.**
   - BDC Data Sets: **no mirror found.**
   - 10-K/10-Q text: HF `TeraflopAI/SEC-EDGAR` (10-K 91.8 GB, 10-Q 132 GB parquet, Apache-2.0) [V-box]. Includes BDC filings, but whether table structure survives is unverified.
   - `alea-institute/kl3m-data-edgar-10-q` and `-10-k` are tokenized text.
   - XBRL company facts: HF `DenyTranDFW/edgar_xbrl_companyfacts`. No dimensional SOI.
   - Parsing code: GitHub `dgunning/edgartools`, `edgar.bdc` module (`portfolio_investments()`, `fetch_bdc_dataset(y,q)`, `reconciliation_gap`) [V-box]. Docs at `https://raw.githubusercontent.com/dgunning/edgartools/main/docs/guides/bdc-guide.md`.
10. **Workflow sketches.**
    - **(a) Private-credit cross-BDC surveillance. Persona: private credit analyst at an LP / BDC investor.**
      1. Parse SOIs for 6 large BDCs (ARCC, FSK, OBDC, BXSL, GBDC, MAIN) for 8 quarters. **CP:** Σ FV vs. balance sheet, within the netting rules.
      2. Normalize borrower and tranche names across BDCs (entity resolution) and build an overlap matrix.
      3. Mark dispersion: FV/par for the same tranche across holders. Flag outliers more than 5 points apart.
      4. Rebuild the all-in coupon from base rate (SOFR, from the rates mirror) + spread + floor + PIK. **CP:** reported weighted-average yield.
      5. Non-accrual and PIK migration and the realized/unrealized loss bridge. **CP:** MD&A tables.
      6. Industry concentration and top-10 exposure. Memo on which BDC marks are most stale.
    - **(b) BDC leverage and covenant headroom. Persona: BDC unsecured-bond credit analyst.**
      1. From the BDC's 10-Q and the EX-10 revolver and indenture (3.3), compute asset coverage. **CP:** disclosed ratio.
      2. Compute the borrowing base under the revolver's advance rates by asset type, unencumbered-asset coverage, and the minimum-equity covenant.
      3. Stress the FV marks by −10/−20% and find the covenant breach point.

### 3.2 SEC Form N-PORT Data Sets (monthly fund holdings: loans, CLO tranches, HY bonds)
1. Monthly portfolio holdings of all registered funds and ETFs, including bank-loan funds, interval/private-credit funds and CLO ETFs. Tables include FUND_REPORTED_HOLDING, DEBT_SECURITY, IDENTIFIERS, BORROWER and more (≥30 tables) [V-box mirror README]. Source: `https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets` [V-box, cited in the mirror].
2. Public domain. Released quarterly.
3. Structured TSV. Messy points: self-reported asset categories, mixed identifier quality, amended filings.
4. 2019-10 to present, quarterly releases.
5. About 17,500 funds; 145.6M positions over 2019-09 to 2026-05 [V-box, ZipLime README].
6. CUSIP, ISIN, LEI (issuer and fund), series/class IDs, accession number.
7. Σ position `valUSD` vs. net assets (`pctVal` sums to about 100%). DEBT_SECURITY coupon/maturity vs. holding. Fund-level interest-rate risk (DV01) vs. a bottom-up duration.
8. Not in finance LLM benchmarks found.
9. **HF `trader298/sec-nport`:** CC0, 830 files, 9.45 GB, typed parquet by table/year/quarter [V-box]. **HF `ZipLime/fund-holdings-nport`:** Apache-2.0, 5.3 GB [V-box].
10. Persona: leveraged-loan PM / CLO manager. Take 20 bank-loan funds over 12 months.
    1. Reconcile holdings to NAV.
    2. Build an issuer-level exposure map by LEI/CUSIP.
    3. Compute a price-distribution "distress ratio" (share of positions priced below 80).
    4. Track one issuer's marks through a default, and cross-check against BDC marks (3.1) and the bankruptcy docket (4.1).

### 3.3 Credit agreements & indentures on EDGAR (EX-10 / EX-4 exhibits)
1. Material contracts on 8-K/10-Q/10-K: credit agreements, amendments, DIP credit agreements, indentures (usually EX-4.x).
2. Public domain.
3. HTML, txt or **scanned PDF** (older or amended exhibits). 100–300+ pages with defined-term cross-references. **Very high messiness.**
4. 1993+.
5. Tens of thousands of agreements.
6. Filer CIK, accession, exhibit number. Borrower name links to 10-K financials.
7. Covenant ratios computed from 10-K/10-Q numbers vs. the company's disclosed "in compliance" status or ratio. Leverage step-down schedules. Pricing grids (margin vs. leverage) vs. the 10-Q interest-rate disclosure.
8. No open covenant-calculation benchmark found [V-web]. CM-LRS (arXiv 2607.21340) extracts debt terms from 15 bond prospectuses [V-web snippet]. CUAD, LEDGAR and MAUD are clause classification without credit math [unverified for each].
9. **Mirrors.**
   - **HF `yonathanarbel/SEC_Exhibit_10`:** MIT, 66.7 GB, by-year zips 2001–2024, originals plus text [V-box].
   - **HF `arthrod/sec-ex10-exhibits`:** 15,360 recent exhibits in Markdown **plus page images for scanned, image-only exhibits** [V-box].
   - **HF `alea-institute/kl3m-data-edgar-agreements`:** 31 GB, 1.45M rows, tokenized; `laion/edgar_agreements` is the detokenized jsonl, 25.6 GB [V-box].
10. **Persona: leveraged-finance credit analyst.**
    1. Take the borrower's credit agreement plus 3 amendments, and its 10-K/10-Qs.
    2. Extract Consolidated EBITDA with add-backs and caps (e.g., synergies capped at X% of EBITDA).
    3. Compute covenant EBITDA vs. reported EBITDA, then Total and First-Lien Net Leverage and FCCR at the test date vs. the step-down grid.
    4. Compute available incremental capacity (free-and-clear plus ratio basket) and the RP builder basket.
    5. Compute the pricing-grid margin.
    6. **CP:** the company's own covenant disclosure and the interest rate in the 10-Q.
    7. Write an amend-and-extend term sheet critique (judge-scored).

### 3.4 SBA 7(a)/504 FOIA loan data
1. Loan-level 7(a) (four decade files) and 504 (two files), FY1991+, with a data dictionary xlsx. `https://data.sba.gov/dataset/7a-504-foia` [V-web].
2. Public. Updated quarterly ("as of June 30, 2026") [V-web].
3. CSV. Fields include status (COMMIT/PIF/CHGOFF/CANCLD/EXEMPT), charge-off date and amount, gross and guaranteed approval, NAICS, lender, and borrower location [V-web, third-party].
4. FY1991 to present.
5. Millions of loans.
6. Loan number [unverified], lender name, NAICS, ZIP.
7. Charge-off ≤ disbursed; guaranteed share ≤ program limits; vintage cumulative charge-off curves.
8. The Kaggle "Should This Loan be Approved or Denied?" set is a common ML classroom set.
9. **Kaggle `mirbektoktogaraev/should-this-loan-be-approved-or-denied`:** SBA national 1987–2014, CC BY-SA 4.0, 48.7 MB [V-box]. Also HF `MaddRaf/SBAnational` (0.18 GB, same data) and HF `emperor-mew/sba-ppp-loans`. Kaggle PPP copies: `susuwatari/...`, `cwhiteprofessional/sba-covid19-eidl-loans`.
10. Persona: SBA lender portfolio manager / SBA-loan securitization buyer. Vintage loss curves by NAICS and state → expected-loss pricing of the unguaranteed retained piece → lender-level performance ranking. Medium differentiation; weak external ground truth.

### 3.5 LendingClub (consumer marketplace loans)
- Kaggle `wordsforthewise/lending-club` (CC0, 1.36 GB, 2007–2018 accepted and rejected) [V-box]. HF `codesignal/lending-club-loan-accepted`.
- **Already used in FinBen/PIXIU and CALM credit-scoring tasks** (HF `TheFinAI/en-lendingclub`, `daishen/cra-lendingclub`) [V-box]. **Low differentiation. Deprioritize.**

---

## 4. DISTRESSED / RESTRUCTURING

### 4.1 US Chapter 11 case dockets: claims-agent sites + PACER/RECAP — ★ TOP PICK
1. **What & URL.** Large Chapter 11 cases publish the full docket for free on the claims/noticing agent's site: Kroll (`restructuring.ra.kroll.com/<case>`), Stretto (`cases.stretto.com/<case>`), Epiq (`dm.epiq11.com/<case>`), Omni (`omniagentsolutions.com/<case>`; documents at `casedocs.omniagentsolutions.com/...` [V-web]), Verita/KCC (`veritaglobal.net/<case>`). Key documents:
   - First-day declaration (capital structure, liquidity).
   - DIP motion with the 13-week budget, and DIP orders.
   - **Weekly variance reports.** Example: YesCare/CHS, Doc 417, budget/actual/variance columns [V-web].
   - **UST Form 11-MOR**, the uniform monthly operating report for non-small-business debtors since 2021-06-21, due by the 21st of the following month [V-web]. Supporting bank statements are often scanned.
   - Schedules of assets and liabilities (SOAL) and Statements of Financial Affairs (SOFA).
   - **Claims register** (searchable, often exportable [unverified per agent]).
   - Plan and disclosure statement with valuation, liquidation analysis, projections and a recovery table by class.
   - Fee applications with time entries. Sale (§363) bid procedures and auction results.
   - Free alternative: CourtListener RECAP (PACER documents uploaded by users), REST API and bulk data [V-web].
2. **Access / ToS.** Agent sites are free to view. **Corporate terms (e.g., kroll.com/legal) bar redistribution without permission; no case-site-specific ToS was found** [V-web]. Court filings themselves are public records. CourtListener has a free API with a token (rate-limited). PACER charges $0.10/page.
3. **Formats & messiness. Highest in the slice.**
   - MORs are scanned or fillable PDFs with bank-statement attachments.
   - Budgets and variance reports are PDF printouts of Excel.
   - Claims registers are PDF, CSV or web tables, with duplicates, amended and superseded claims and unliquidated "$0 + unknown" amounts.
   - SOALs are 1,000+ page PDFs.
   - Disclosure-statement tables are embedded in PDFs.
4. **Depth & cadence.** One case spans 6–36 months of monthly MORs, weekly variance reports and rolling claims. CourtListener has cases back to the 2000s.
5. **Breadth.** Hundreds of large cases a year (D. Del., S.D. Tex., D.N.J., S.D.N.Y.).
6. **Join keys.** Court + case number (e.g., Bankr. D. Del. 23-xxxxx), docket number, claim number, debtor entity, CIK if public, CUSIPs of prepetition bonds.
7. **Natural ground truth.**
   - MOR cash roll-forward (beginning + receipts − disbursements = ending, per debtor), which ties to bank statements.
   - UST quarterly fee recomputed from disbursements (statutory schedule).
   - Professional-fee accruals vs. fee applications. Fee apps: hours × rate = fees, and task-code subtotals.
   - Variance report: variance = actual − budget; cumulative variance vs. the DIP covenant tolerance (commonly 10–15% over a 4-week test [V-web clauses]); the rolled-forward liquidity forecast.
   - Claims register totals by class/priority vs. SOAL scheduled amounts and vs. the disclosure statement's estimated allowed claims.
   - Disclosure-statement recovery table: distributable value allocated down the priority stack should reproduce the stated recovery %s. Liquidation analysis supports the best-interests test.
   - First-day capital structure ties to the 10-K debt footnote.
8. **Existing benchmarks.** None found for restructuring documents [V-web]. Bankruptcy-*prediction* work exists: ECL (arXiv 2401.12652, LoPucki labels) and V4FinBench (arXiv 2605.10896) [V-web]. HF has caselaw only (`docketx/us-caselaw-fed-bankruptcy`, CourtListener bankruptcy *opinions*, CC0, 0.64 GB) [V-box].
9. **Mirrors.**
   - **HF `alea-institute/kl3m-data-pacer-deb`** (D. Del. Bankruptcy): 473,877 rows, 2.57 GB [V-box]. RECAP PDFs as KL3M-*tokenized* text/markdown, keyed by RECAP identifiers such as `gov.uscourts.deb.154432.10897.0.pdf`. The originals live at `storage.courtlistener.com/recap/...` [unverified path].
     - 29 bankruptcy-court repos exist, alphabetically `akb`…`ilnb`. **No `njb`, `nysb` or `txsb`** [V-box].
     - Tables are flattened. Decoding needs the KL3M tokenizer.
   - **No mirror of claims registers, MOR PDFs or claims-agent data.**
10. **Workflow sketches.**
    - **(a) UCC financial advisor, months 1–6 of a large retail Chapter 11.**
      1. From the first-day declaration, build the prepetition capital structure. **CP:** 10-K footnote and the DIP order recitals.
      2. Ingest 6 MORs (scanned). Roll cash per debtor. **CP:** the roll-forward identity; UST fee recomputation.
      3. Ingest 20 weekly variance reports vs. the approved budget. Recompute variances and the 4-week cumulative test. **CP:** reported variance and covenant compliance. Re-forecast the liquidity runway.
      4. Claims register: dedupe amended claims, classify secured, 503(b)(9), priority tax, GUC and intercompany, and reconcile to the SOAL. **CP:** register totals.
      5. Fee monitoring: aggregate fee apps vs. the budgeted professional fee carve-out.
      6. Build a GUC recovery waterfall from the plan's valuation range. **CP:** the disclosure-statement recovery %.
      7. Write an objection-strategy memo. Scored by LLM judge.
    - **(b) Distressed investor, plan-value / fulcrum analysis.** Take the disclosure statement, valuation, projections and claims.
      1. Identify the fulcrum class.
      2. Compute recovery per $ of claim under low/mid/high TEV, including rights-offering and backstop economics and MIP dilution.
      3. Compare to trading prices (N-PORT marks, 3.2) to get the implied TEV.

### 4.2 Post-confirmation trusts that report on EDGAR (liquidating / GUC / plan trusts)
1. Examples:
   - **Lehman Brothers Holdings Inc. Plan Trust** (CIK 806085): 8-Ks furnish quarterly post-effective reports with balance sheets, schedules and **post-distribution cash flow estimates**, 2012→2025 [V-web, e.g. `https://www.sec.gov/Archives/edgar/data/806085/000119312525134082/d543988d8k.htm`].
   - **Motors Liquidation Company GUC Trust** (CIK 40730): 10-Q/10-K covering allowed vs. disputed GUC claims, distributions and GUC Trust Units [V-web, e.g. `https://www.sec.gov/Archives/edgar/data/40730/000119312520292369/d62579d10q.htm`].
2. Public domain.
3. HTML plus PDF exhibits. Non-GAAP liquidation-basis accounting.
4. Quarterly over 10+ years.
5. A handful of trusts. Deep one-entity environments.
6. CIK, class/claim categories.
7. Cumulative distributions + reserves + remaining assets ≈ estimated recoveries. Quarter-over-quarter roll-forwards. Distributions per class as % of allowed claims.
8. None.
9. No mirror (8-K text may be in `TeraflopAI/SEC-EDGAR` 8-K, 14.6 GB [V-box, unverified for these CIKs]).
10. Persona: distressed claims trader. Rebuild class-level recovery histories, the remaining recovery and the NPV-implied claim price. Then run a sensitivity on disputed-claim reserve releases.

### 4.3 Florida-UCLA-LoPucki Bankruptcy Research Database (BRD)
- Large public-company bankruptcies, 1979–2022. **No updates after December 2022.** The "Cases" table is a free download at `lopucki.law.ufl.edu` [V-web]. Blocked here; no mirror found.
- Use: case index and labels (filing date, court, prepack, emergence, refiling) for picking cases in 4.1.

### 4.4 UK administrations (Companies House + insolvency practitioner websites)
1. Administrator filings: AM03 (statement of proposals with statement of affairs and estimated outcome), AM06, AM10 progress reports with the **receipts & payments account**, final reports. Also SoA forms [V-web]. IP firms post the same PDFs, e.g. PwC `https://www.pwc.co.uk/business-recovery/administrations/assets/mccolls/am06_cml.pdf` [V-web].
2. Companies House documents are free (API key for the REST API) [unverified detail]. Blocked here.
3. **Often scanned PDFs.** Formats vary by firm.
4. Every six months per case.
5. Thousands of administrations a year.
6. Company number.
7. R&P roll-forward across progress reports. Prescribed part = 50% of the first £10k + 20% thereafter, capped at £800k for charges after April 2020. Fixed vs. floating charge allocation. Dividend per £.
8. None.
9. HF `kelanokane/companies-house-db` (2.78 GB duckdb of company register, no filings) [V-box]. No document mirror.
10. Persona: UK IP / unsecured creditor. Rebuild the estimated outcome statement and update it with the actual R&P across 3 progress reports. Compute the prescribed part and floating-charge shortfall, then the unsecured dividend.

### 4.5 India IBC (IBBI / NCLT)
- IBBI quarterly newsletters and CIRP data: as of 2025-12-31, 1,376 approved resolution plans, realization about 31.6% of admitted claims and about 172% of liquidation value [V-web secondary]. Bulk access is unclear.
- NCLT orders summarize resolution plans, which are mostly not public.
- `ibbi.gov.in` is blocked. No mirror. Low scrapability → not ranked.

---

## 5. BONDS, RATES, RATINGS

### 5.1 FINRA TRACE
- Public dissemination is real-time on finra.org. **Historical bulk is paid**: the Academic Corporate Bond TRACE product is limited to universities, has a 36-month delay, about $500/yr per the 2017 price, and forbids redistribution [V-web].
- Blocked here. No mirror.
- **Not usable for a redistributed benchmark.** Substitute N-PORT fund marks (3.2).

### 5.2 MSRB EMMA (muni continuing disclosures and trades)
- **The ToS (updated 2026-01-02) prohibits scraping and systematic downloading without MSRB authorization. Bulk is a paid subscription** [V-web].
- Disclosures are rich (ACFRs, many scanned), but **licence-blocked**. Exclude unless the MSRB grants permission.

### 5.3 Treasury yield curve / H.15 / FRED
- Use: discount and reference-rate curves for refinance tests and coupon resets.
- HF `Farmaanaa/us_treasury_yield_curve_daily`: CC-BY-4.0, daily 1990+, from Treasury [V-box].
- FRED is blocked here. Kaggle has `federalreserve/*` series copies (2019 vintage).

### 5.4 NRSRO rating histories under Rule 17g-7(b) (XBRL)
1. Each NRSRO publishes XBRL (ROCR taxonomy) histories for ratings outstanding on or after 2012-06-15, with upgrades, downgrades and withdrawals, on its own website. The link is in Form NRSRO Exhibit 1. Files are large and split into zips [V-web]. Egan-Jones offers one zip [V-web]. Taxonomy guide: `https://www.sec.gov/data-research/structured-data/rating-history-files-publication-guide` [V-web].
2. Public, but each agency's site terms apply [unverified]. Blocked here.
3. XBRL-XML. Identifier schemes vary (CUSIP, ISIN, LEI, CIK, agency IDs); duplicates and withdrawals need cleaning.
4. 2012→present, updated monthly with a 12-month lag [unverified lag].
5. Millions of instrument and obligor ratings across corporates, financials, sovereigns and structured finance.
6. Obligor LEI/CIK, instrument CUSIP/ISIN.
7. **Ground truth:** Form NRSRO Exhibit 1 publishes each agency's 1-, 3- and 10-year transition and default statistics by class [unverified that they are reproducible from the 17g-7 files]. Rating actions on ABS-EE trusts' classes can cross-check deal performance.
8. None found.
9. **No mirror found** on HF, Kaggle or GitHub (GitHub search is blocked; the WebSearch for a GitHub merge project found none [V-web]).
10. Persona: credit-risk quant. Build cohort transition matrices and default rates per agency → compare to Exhibit 1 → split rating drift across CMBS vintages vs. ABS-EE delinquency.

### 5.5 Other EDGAR credit corpora (supporting)
- HF `XOOMAR/sec-structured-notes-424b2`: 424B2 structured-note terms, licence "other" [V-box]. Bank-issued notes; tangential.
- SEC Financial Statement & Notes data: HF `DenyTranDFW/SEC_10K_FSNoNDS_Zip` (0.21 GB, rar by SIC) [V-box].

---

## 6. RANKED TOP-5 FOR THIS SLICE

Scores run 1–5 on: **D** = workflow depth, **R** = realness/messiness, **V** = verifiability through natural checks, **X** = differentiation from existing benchmarks, **S** = scrapability (incl. mirror and licence).

| Rank | Source / environment | D | R | V | X | S | Why |
|---|---|---|---|---|---|---|---|
| **1** | **Reg AB II ABS-EE + 10-D + 424B (auto loans/leases and CMBS)**: "one-deal-deep" and "shelf-broad" ABS surveillance | 5 | 4 | **5** | **5** | 4 | Monthly loan-level XML plus HTML servicer reports plus legal-prose waterfalls. Tape cut, strats, roll rates, CPR/ABS speed, CNL, waterfall replication and trigger tests chain naturally. Identities are exact (Σ loan balances = pool balance; Actual/360 interest reproduces filed interest). No benchmark covers it. Public domain. ~1,070 trust repos already mirrored on HF (uneven completeness) plus an 800 MB Kaggle auto set. The 10-D and 424B must be scraped. |
| **2** | **US Chapter 11 case docket** (claims-agent site + RECAP): first-day decl → DIP budget/variance → MORs → claims register → SOAL → disclosure statement waterfall → fee apps | **5** | **5** | 4 | **5** | 2 | The closest thing to "a big chunk of a restructuring professional's job". Scanned MORs, PDF budgets and messy claims registers are exactly what separates frontier models. Many arithmetic identities (cash roll-forward, variance math, claim totals, recovery waterfall). Weak points: claims-agent ToS on redistribution, and no mirror beyond the tokenized D. Del. text in `alea-institute/kl3m-data-pacer-deb`. Prefer CourtListener RECAP originals. |
| **3** | **FFIEC Call Reports + UBPR (+ FDIC failures)**: bank-examiner post-mortem and universe screens | 4 | 3 | **5** | 4 | **5** | Best mirror situation: CC0 full history 2001–2026 on HF (`kairusama/call-report-one`, `kairusama/ubpr-one`). The UBPR is an **independent FFIEC answer key** for every derived ratio. Balance-sheet, ACL and capital identities hold. Failures give outcome labels. Messiness is moderate (MDRM codes, schedule changes), but the work spans one entity in depth or the whole universe. |
| **4** | **BDC Schedules of Investments (SEC BDC Data Sets + 10-K/10-Q) + N-PORT loan holdings + EX-10 credit agreements**: private-credit surveillance and covenant/borrowing-base analysis | **5** | 4 | 4 | **5** | 3 | Huge, messy loan-by-loan tables. Cross-BDC entity resolution and mark dispersion. Known XBRL tagging errors are "traps". The SOI↔balance-sheet reconciliation and asset-coverage checks are natural. Credit agreements (scanned images in `arthrod/sec-ex10-exhibits`; 2001–2024 in `yonathanarbel/SEC_Exhibit_10`) add covenant-definition reasoning. The BDC Data Sets themselves are unmirrored; N-PORT is CC0-mirrored. |
| **5** | **Pillar 3 (EU/UK banks) + EBA P3DH (+ Fed DFAST results)**: cross-jurisdiction bank capital and credit-risk peer review | 4 | **5** | 4 | 3 | 2 | Standardized templates (KM1/OV1/CC1/CC2/LR2/LIQ1/CR*) give many reconciliation identities, inside PDF/XLSX layouts that differ by bank. Non-US coverage. A QA-style Pillar 3 benchmark already exists (arXiv 2609.03654), but workflows do not. No mirror; bank websites and the EBA must be scraped. The EBA Transparency Exercise ended in 2025, and the P3DH (live 2026) is the new structured source. |

Honorable mentions:
- 17g-7 rating histories: great for transition matrices, but no mirror and the XBRL is heavy.
- Post-confirmation trusts on EDGAR (LBHI Plan Trust, Motors Liquidation GUC Trust): deep one-entity distressed environments, public domain.
- Ginnie Mae loan-level data (Kaggle mirror).
- SBA 7(a) (Kaggle mirror, weak external ground truth).
- HMDA (mirrored, but common in ML).

Avoid for licensing reasons:
- Freddie/Fannie loan-level and CRT data (no redistribution without a $25k+ licence, despite HF copies).
- FINRA TRACE historical (paid, no redistribution).
- MSRB EMMA (scraping prohibited).
- LendingClub: low differentiation, already in FinBen/CALM.

**Suggested combined "universe-broad" credit environment:** Call Reports (bank lenders), plus BDC SOI and N-PORT (non-bank lenders), plus ABS-EE (securitized consumer and CRE credit), plus Chapter 11 dockets (defaulted names). Two joins connect them: a borrower appearing in a BDC SOI, in N-PORT loan holdings and in a bankruptcy claims register; and CRE loans that sit both in CMBS ABS-EE and on bank balance sheets, linked through RC-C CRE concentration.

---

## 7. MIRROR QUICK REFERENCE (exact IDs; all verified to exist via HF/Kaggle API from this container)

| Source | Mirror | Size / licence | Notes |
|---|---|---|---|
| ABS-EE (auto, lease, CMBS) | HF `DenyTranDFW/<Trust>_<CIK>` (1,072 repos), e.g. `DenyTranDFW/AmeriCredit_Automobile_Receivables_Trust_2020_1_1801390`, `DenyTranDFW/BANK_2021_BNK31_1840121`, `DenyTranDFW/World_Omni_Automobile_Lease_Securitization_Trust_2021_A_1863708` | KB–300 MB per repo; "gpl" | Coverage varies per trust. EX-102/103 only. |
| ABS-EE auto | Kaggle `denytran/10-year-automotive-loans-abs-ee` | 803 MB; US Gov Works | Downloadable here. |
| CMBS deal index | Kaggle `cmdrvl/cmbs-deals-edgar-cik-and-collateral-distribution` | 37 KB; CC0 | Downloaded; 262 deals. |
| CMBS derivatives | HF `catyung/cre-cmbs-loans`; HF `commandreveal/cmbs-special-servicing-transfer` | small; other / CC-BY-NC | |
| Call Reports | HF `kairusama/call-report-one` | 2.91 GB; CC0 | 2001Q1→2026. |
| UBPR | HF `kairusama/ubpr-one` | 4.81 GB; CC0 | 2002→. |
| Bank ratios (FDIC) | Kaggle `neutrino404/all-us-banks-financial-quarterly-ratios-2001-2023` | 1.42 GB; CC0 | |
| Bank failures | Kaggle `fdic/bank-failures`; Kaggle `utkarshx27/failed-banks-database`; HF `emperor-mew/fdic-failures` | small | |
| Y-9C (partial) | HF `Wgurtler/y9c-data` | 20 MB; none | Processed; provenance unclear. |
| N-PORT | HF `trader298/sec-nport`; HF `ZipLime/fund-holdings-nport` | 9.45 GB CC0; 5.3 GB Apache-2.0 | 2019Q4→. |
| 10-K/10-Q (BDCs) | HF `TeraflopAI/SEC-EDGAR` (10-K, 10-Q, 8-K folders) | 295 GB total; Apache-2.0 | |
| EDGAR all forms 2023–26H1 | HF `anonymous-md/EDGAR_FILINGS_DATASET_2022_2026H1` | 16.5 GB; none | 10-D/424B inclusion unverified. |
| EX-10 credit agreements | HF `yonathanarbel/SEC_Exhibit_10`; HF `arthrod/sec-ex10-exhibits`; HF `alea-institute/kl3m-data-edgar-agreements`; HF `laion/edgar_agreements` | 66.7 GB MIT; 1 GB other; 31 GB; 25.6 GB | arthrod has scanned page images. |
| Bankruptcy dockets (text) | HF `alea-institute/kl3m-data-pacer-deb` (+28 other `-…b` courts, akb…ilnb) | 2.57 GB | Tokenized RECAP text. |
| Bankruptcy opinions | HF `docketx/us-caselaw-fed-bankruptcy` | 0.64 GB; CC0 | Opinions only. |
| HMDA | HF `retrogradespace/hmda_2024`; HF `xaheli/HMDA_LAR_2017-23` | 0.54 GB CC0; 12.2 GB MIT | |
| SBA | Kaggle `mirbektoktogaraev/should-this-loan-be-approved-or-denied`; HF `MaddRaf/SBAnational`; HF `emperor-mew/sba-ppp-loans` | 49 MB CC BY-SA | 1987–2014. |
| Ginnie Mae loan-level | Kaggle `riziles/mbs-sf-port-loan-level-ginnie-ii` | 559 MB; US Gov Works | |
| Fannie Mae (licence risk) | HF `yeigen/fannie-mae-loan-performance`; HF `Alej0909/fannie-mae-loan-performance-raw` | 31.6 GB each | Redistribution restricted by Fannie terms. |
| LendingClub | Kaggle `wordsforthewise/lending-club` | 1.36 GB CC0 | Already in FinBen/CALM. |
| Treasury curve | HF `Farmaanaa/us_treasury_yield_curve_daily` | small; CC-BY-4.0 | |
| BDC parsing code | GitHub `dgunning/edgartools` (`edgar.bdc`) | MIT [unverified] | |
| Not mirrored anywhere found | 10-D, 424B, BDC Data Sets, MORs and claims registers, Pillar 3, DFAST, 17g-7, TRACE, EMMA, IBBI, Companies House documents, RBI | — | Scrape in the build environment. |

**Container caveat (repeat):** HF payload downloads fail here because the LFS/Xet CDN returns 403. Kaggle downloads work.

---

## 8. Existing-benchmark landscape relevant to this slice (from search snippets; details unverified)
- **10-K / equity-centric:** FinanceBench, FinQA/TAT-QA/ConvFinQA/DocFinQA, Fin-RATE (arXiv 2602.07294), FinMaster (2505.13533), FrontierFinance (2604.05912, modeling tasks), Vals AI Finance Agent.
- **Credit-adjacent:**
  - FinBen/PIXIU and CALM: tabular credit scoring on LendingClub, German credit and similar.
  - MortarBench (arXiv 2606.19416): mortgage-origination agents.
  - Pillar 3 QA benchmark (arXiv 2609.03654).
  - CM-LRS (arXiv 2607.21340): bond prospectus term extraction, 15 prospectuses.
  - ECL (2401.12652) and V4FinBench (2605.10896): bankruptcy prediction.
  - IndiaFinBench (2604.19298): RBI/SEBI regulatory text QA.
- **Gap:** no long-horizon agent benchmark found for ABS surveillance, Call Report examination, BDC/private-credit portfolio work, covenant calculations or Chapter 11 case administration.
