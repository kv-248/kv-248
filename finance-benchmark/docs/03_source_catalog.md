# Source Catalog: real, scrapable data with long-horizon finance workflow scope

Synthesised from four parallel source surveys (raw notes in `docs/sources/`), the benchmark
survey (`01`), the concept library (`02`) and eight proof-of-concept pulls run in the sandbox
(`04`). Everything here is **real primary-source data**; nothing is synthetic.

---

## 0. TL;DR

**Where the whitespace is.** Existing finance benchmarks are dominated by (a) QA over US 10-Ks
(FinanceBench, Finance Agent, FinSearchComp) and (b) single-snapshot modeling deliverables
(SpreadsheetBench 2, BankerToolBench, FrontierFinance). The survey found **no open benchmark** with
multi-period state on real data, and none touching structured credit surveillance, municipal/
government accounts, utility regulatory accounting, fund holdings (N-PORT), nonprofit returns,
Chapter 11 case work, or non-US fund disclosures. Those are the areas below.

**Selection principle.** Prefer sources where **the source itself reports totals that bottom-up
work must reproduce** (natural ground truth). That is what keeps a long, messy, real trajectory
gradeable. Every PoC confirmed such identities hold on real data at 98–100%, and the *exceptions*
are real restatements, mergers and special items: exactly the judgment points that separate
strong models.

### Ranked shortlist

Scores 1–5. **D** concept depth · **T** temporal depth / refresh · **M** messiness (raw-to-workbook
burden) · **G** natural ground truth · **X** differentiation · **S** scrapability + licence.

| # | Source (env) | D | T | M | G | X | S | PoC in sandbox |
|---|---|---|---|---|---|---|---|---|
| 1 | **Municipal finance pack**: ACFR PDFs + checkbook/GL + official statements + actuarial valuations | 5 | 4 | 5 | 5 | 5 | 3 | ✅ Austin ACFR 17 yrs (PDF→panel, 15/15 ties); Chicago checkbook |
| 2 | **SEC Reg AB II ABS-EE loan tapes + 10-D servicer reports + 424B waterfalls** (auto, CMBS) | 5 | 5 | 4 | 5 | 5 | 4 | ✅ 35.7M loan-months, 100% loan identity |
| 3 | **FERC Form 1/2/6/60 + EQR + RUS 7/12** utility regulatory accounting (PUDL) | 5 | 5 | 3 | 5 | 5 | 5 | ✅ 375 utilities × 32 yrs, 99.7% roll-forward ties |
| 4 | **US fund stack**: N-PORT (+13F, N-CSR, prospectus fees, Fama-French) | 5 | 4 | 3 | 5 | 5 | 3 | ◐ fund-level pulled (A−L=NA 100%); holdings index warming |
| 5 | **India AMC monthly portfolio workbooks + AMFI NAV/TER** | 4 | 5 | 5 | 4 | 5 | 3 | ✅ 13 AMCs, 715 schemes, 99.2% tie to Grand Total |
| 6 | **IRS 990 / 990-PF e-file XML** (+ Federal Audit Clearinghouse, USAspending) | 4 | 5 | 4 | 5 | 5 | 5 | ✅ 14 yrs Wikimedia, all identities tie |
| 7 | **US Chapter 11 dockets**: first-day decl., DIP budgets/variance, scanned MORs, claims registers, disclosure-statement waterfalls | 5 | 3 | 5 | 4 | 5 | 2 | ✗ (claims-agent sites blocked; no mirror of MORs) |
| 8 | **FFIEC Call Reports + UBPR** (+ FDIC failures) | 4 | 5 | 3 | 5 | 4 | 4 | ◐ schema verified (CC0 mirror, 2001–2026) |
| 9 | **BDC schedules of investments + EX-10 credit agreements** (+ N-PORT loan holdings) | 5 | 4 | 4 | 4 | 5 | 3 | — (mirrors identified) |
| 10 | **UK Companies House accounts** (iXBRL, 33.5M company-periods, first-reported vs. latest) | 4 | 4 | 4 | 4 | 5 | 4 | — (Kaggle mirror identified) |
| 11 | **Public-pension PE fund reports (WSIB PDFs) + Public Plans Data** | 4 | 4 | 5 | 4 | 5 | 3 | — (survey agent verified identities, IRR within 17 bp) |
| 12 | **UK council "spend over £500" + RO outturn + Statements of Accounts** | 4 | 5 | 5 | 3 | 5 | 3 | — (Devon 2011–2026 on GitHub) |

Tier 3 (useful supplements or answer keys): CA State Controller FTR and France DGFiP trial
balances (government-published ratios as answer keys), Pillar 3 / EBA Data Hub, Japan EDINET
raw XBRL, Brazil CVM funds, Enron spreadsheets (already used by Finch), Treasury DTS→MTS, FRED/
ALFRED vintages, Ken French factors.

**Recommended flagship environments to deepen first** (§3): **F1 municipal credit review**,
**F2 ABS surveillance desk**, **F3 portfolio rebalance (US TDF and India wealth desk)**, and
**F4 utility rate case**. Together they cover four personas, three jurisdictions' worth of
messiness, and the strongest natural ground truth.

---

## 1. Scoring rubric

The lens comes from `02_concept_library.md` §4. A source has long-horizon scope when it scores
high on the **five horizon multipliers** (acquisition burden, concept depth, temporal roll-forward,
breadth, exceptions) *and* has natural ground truth to keep that horizon gradeable.

| Criterion | 5 means |
|---|---|
| D: concept depth | ≥3 concept families (A–K) exercised on the same records, DAG of ≥6 concepts |
| T: temporal | ≥10 periods of same-schema data per entity **and** refreshes monthly or faster (contamination-resistant) |
| M: messiness | scans / layout drift / units / restatements make raw→workbook a real task |
| G: natural ground truth | source reports totals or identities the bottom-up computation must hit |
| X: differentiation | not used by any benchmark in `01` |
| S: scrapability + licence | bulk or API, public domain / research-OK, reachable mirror exists |

---

## 2. Source cards (Tier 1 and 2)

Each card: what it is, access, what makes it long-horizon, natural ground truth, risks. Exact
mirror IDs and the remaining 10-field profiles are in `docs/sources/*.md`.

### 2.1 Municipal finance pack: ACFRs + checkbooks/GLs + official statements + actuarial valuations
- **What:** audited annual reports (ACFRs, ~250 pages, native and scanned PDF) of cities,
  counties, states, school districts; transaction-level open checkbooks and general ledgers;
  bond official statements (OS); pension actuarial valuations; budget books.
- **Access:** ACFR/OS/actuarial PDFs via the **End-of-Term 2020 web archive on public S3** (CC0;
  PDFs + OCR; our index lists 6,203 ACFRs, 3,394 budget books, 872 single audits, 433 actuarial
  valuations, 167 OS). Ledgers via the **Harvard LIL Data.gov archive on public S3** (Range-
  readable BagIt zips): Oklahoma statewide GL FY22–FY25 (2 GB), Oklahoma vendor payments
  FY2008–FY2019, Iowa checkbook (6 GB), Austin eCheckbook (642 MB), NYC payroll/actuals, Chicago
  payments and budget ordinances, CA State Controller returns FY2003–FY2023. Live: issuer sites,
  Socrata portals. **MSRB EMMA ToS forbid scraping**, so OS documents are hand-curated from issuer
  sites or the archive.
- **Long-horizon because:** a credit review or year-end close chains PDF extraction across
  5–10 years (A1–A5), fund accounting (B3, H1–H2), debt schedules (F3, H3), pensions (H4),
  budget-to-actual (H6) and audit tests on the checkbook (J1–J5).
- **Natural ground truth:** fund-balance roll-forwards (PoC: 15/15 within-year, 11/12 across-year;
  the break is a documented restatement); the ACFR's own government-wide↔fund reconciliation
  schedules; budgetary comparison schedules; statistical section vs. prior ACFRs; OS debt-service
  schedule vs. ACFR debt note; checkbook totals by fund vs. ACFR expenditures.
- **Risks:** period matching (archive PDFs are mostly FY2001–FY2019 while some ledgers are FY2022+,
  so pair carefully: Oklahoma vendor payments FY2019, Austin checkbook + FY2019 ACFR); frozen
  snapshots, so fresh test splits need a live scrape.

### 2.2 Structured credit: ABS-EE loan tapes + 10-D servicer reports + 424B prospectus
- **What:** Reg AB II monthly loan-level XML (EX-102) for auto loans/leases and CMBS (property-
  level), the monthly 10-D distribution report, and the prospectus's waterfall/trigger prose. (No
  registered RMBS since 2014.)
- **Access:** EDGAR (blocked here); Kaggle `denytran/10-year-automotive-loans-abs-ee` (pulled);
  HF `DenyTranDFW/<Trust>_<CIK>`, 1,072 per-trust repos (uneven completeness). 10-D and 424B need an
  EDGAR fetch. Public domain.
- **Long-horizon because:** each month repeats a 7–8 concept DAG (F10 strats → F5 roll rates →
  F4 CPR/CDR/severity → B1 pool roll-forward → reconcile to 10-D → F6 waterfall and triggers →
  forecast) and state carries forward (cumulative net loss, trigger history) for 36–80 months.
- **Natural ground truth:** loan identity holds on 100% of 35.7M loan-months; continuity on 99.62%
  (129k real breaks to explain); 10-D reports pool balance, delinquencies and cumulative net loss;
  CMBS scheduled interest reproduces exactly (Actual/360).
- **Traps found:** repossession proceeds are a subset of recoveries (double-count → negative
  losses); null-date sentinel; loans that drop out and reappear.

### 2.3 Utility regulatory accounting: FERC Form 1/2/6/60 + EQR + RUS 7/12 (via PUDL)
- **What:** Uniform-System-of-Accounts statements of ~375 electric utilities (1994–2025), gas and
  oil pipelines, service companies, 613 rural co-ops (RUS), and 125 GB of transaction-level
  wholesale power sales (EQR, 2013Q3–2026Q2).
- **Access:** **fully downloadable here** (public S3 `pudl.catalyst.coop`, CC BY 4.0; also Kaggle).
  Raw XBRL/DBF at FERC.
- **Long-horizon because:** rate-base roll-forward (B1, B6) → cost of capital (C7) → revenue
  requirement → test-year adjustments → peer benchmarking; 30 years deep or 375 broad; EQR adds a
  sub-ledger to reconcile to purchased-power schedules.
- **Natural ground truth:** PoC: 99.72% within-year and 98.82% across-year plant roll-forward
  ties (1,849 real breaks); XBRL calculation rules with weights (274 calculated facts); PUDL's
  published rate-base table as a reference answer.
- **Trap found:** retirements are stored as negatives (textbook sign → only 43% tie).
- **Risk:** cleaned by PUDL (less raw mess). Use raw FERC XBRL or DBF for the acquisition step.

### 2.4 US fund stack: N-PORT (+13F, N-CSR/TSR, prospectus fee data, Fama-French)
- **What:** monthly position-level holdings of ~17.5k mutual funds/ETFs (145.6M positions,
  2019Q4–2026Q2) including bonds, loans, ABS and derivatives; monthly returns and flows; 13F
  manager holdings 2013+.
- **Access:** HF `trader298/sec-nport` (CC0, all 29 SEC tables) and `ZipLime/fund-holdings-nport`;
  `ZipLime/institutional-portfolio-13f`. Reachable here only via datasets-server `/filter`
  (works; large-config index warm-up is slow); file CDN needs allowlisting.
- **Long-horizon because:** due diligence or rebalancing chains E1–E12: look-through (fund-of-
  funds → underlying N-PORTs), return chaining vs. prospectus, attribution, liquidity bucketing,
  fee drag, drift vs. glide path, constrained trade list.
- **Natural ground truth:** total assets − liabilities = net assets (100% on pulled sample);
  Σ holdings ≈ net assets; monthly net-asset roll-forward from reported flows/returns; 13F
  control totals (95.6% match).
- **Real event found:** Vanguard Institutional TR 2050 stops filing while Vanguard TR 2050 net
  assets jump $22B → $54B in 2022 (fund merger), a break the roll-forward must explain.

### 2.5 India AMC monthly portfolio workbooks + AMFI NAV/TER
- **What:** SEBI-mandated month-end (and fortnightly, debt) portfolio disclosures, one workbook
  per AMC in its own layout; daily NAV and TER from AMFI.
- **Access:** AMC websites (blocked here); GitHub `subscriptionmanager26-png/fund-disclosures`
  (raw Aug-2026, 13 AMCs, pulled); `kushagra-agarwal-a/fund-holdings-data` (parsed Jun–Sep 2026);
  Kaggle NAV and TER mirrors refreshed daily. Licence: statutory disclosures, not stated.
- **Long-horizon because:** the raw-to-workbook step is real work (header row 2–12, ISIN column
  0/2/3/7, percent vs. fraction even within one AMC, ₹ lakh, zips), then the wealth-desk chain:
  look-through → overlap → SEBI category-rule compliance → return/risk from NAV → Regular→Direct
  switch (TER) → tax-aware rebalance.
- **Natural ground truth:** implied net assets per holding vs. Grand Total, which ties for 99.2% of
  715 schemes.
- **Differentiation:** non-US, fresh (2026), maximally messy spreadsheets. SpreadsheetBench 2
  uses Indian *company* data (Screener.in/BSE), not fund disclosures.

### 2.6 IRS 990 / 990-PF e-file XML (+ Federal Audit Clearinghouse, USAspending)
- **What:** ~6.2M nonprofit returns 2009–2026: full financials, Schedule D endowment
  roll-forwards, Schedule I grants, 990-PF **lot-level capital gains** (up to 4,296 lots per return)
  and CUSIP-tagged stock schedules.
- **Access:** **fully reachable** (GivingTuesday public S3, monthly IRS batches; PoC reads the
  Parquet index by HTTP range).
- **Long-horizon because:** a foundation year-end close or grant due diligence chains schema-
  drifting XML extraction (13 schema versions in 14 years) → net-asset reconciliation → functional
  expenses → endowment analysis → tax-lot classification and excise tax → payout plan → (join)
  SEFA/single-audit reconciliation.
- **Natural ground truth:** Part XI reconciliation, net-asset roll-forward, Part IX functional
  totals (all tie for Wikimedia 2009–2022); minimum-distribution recompute; lot gains vs. reported
  net gain (gaps exist and must be explained).

### 2.7 US Chapter 11 case dockets
- **What:** per-case documents on claims-agent sites (Kroll, Stretto, Epiq, Omni, Verita) and
  PACER/RECAP: first-day declarations, DIP budgets and weekly variance reports, **monthly
  operating reports (often scanned)**, schedules of assets and liabilities, claims registers, plan
  and disclosure statement (recovery waterfall), fee applications. Post-confirmation trusts also
  file on EDGAR (e.g., Lehman Plan Trust, Motors Liquidation GUC Trust).
- **Access:** weakest: hosts blocked here, no MOR/claims mirror (HF `alea-institute/kl3m-data-pacer-*`
  has tokenized text only), claims-agent ToS vary. Prefer CourtListener RECAP originals.
- **Why still Tier 1:** deepest and messiest real workflow of all (I1–I6, C4, F8); a single case
  supplies 12–24 MORs plus weekly variance reports. No benchmark covers it. Ideal for the
  "few-but-long, expert-curated" design if 5–10 cases are hand-collected.

### 2.8 FFIEC Call Reports + UBPR (+ FDIC failures)
- **What:** quarterly balance sheet, income, capital, allowance and loan schedules for every US
  bank 2001–2026 (671k bank-quarters, up to 1,442 columns); UBPR derived ratios.
- **Access:** HF `kairusama/call-report-one` and `kairusama/ubpr-one` (CC0); datasets-server
  reachable; FFIEC CDR bulk primary.
- **Long-horizon because:** examiner post-mortem or peer surveillance (G1–G6) over 20+ quarters,
  across a peer group; failures give outcome labels.
- **Natural ground truth:** **UBPR is an independent answer key** for every ratio the agent
  computes; allowance and capital roll-forwards.
- **Risk:** structured (less acquisition burden); pair with bank 10-K/Pillar-3 PDFs for mess.

### 2.9 Tier 2 in brief
| Source | Why | Main caveat |
|---|---|---|
| BDC schedules of investments + EX-10 credit agreements (HF `yonathanarbel/SEC_Exhibit_10`, `arthrod/sec-ex10-exhibits` incl. scanned page images) | private-credit marks across holders, covenant definitions buried in legal text (C5) | SEC BDC Data Sets unmirrored; XBRL tagging errors |
| UK Companies House accounts (Kaggle `thomassimm/uk-company-accounts-wide-2014-2026`, OGL) | 33.5M SMB company-periods, UK GAAP, **first-reported vs. latest (9.36% restated)** | mirror is parsed facts; raw iXBRL needs Companies House |
| WSIB private-equity quarterly PDFs (Kaggle, original PDFs + OCR) + Public Plans Data | CIO-office PE pacing: cash flows from cumulative deltas, IRR (recomputed within 17 bp), PME | mirror stops 2021Q2; newer quarters on sib.wa.gov |
| UK council monthly payments > £500 (Devon on GitHub 2011–2026) + RO outturn + accounts | non-US government, very messy CSVs, monthly refresh | needs reconciling-item judgment; RO pulls blocked here |
| CA SCO FTR, France DGFiP balances, NY OSC FSMS | government-published ratios and stress scores = free answer keys over hundreds of entities | French data behind HF CDN |
| Pillar 3 / EBA Pillar 3 Data Hub | EU/UK bank templates with many reconciliations | QA benchmark exists (arXiv 2609.03654); no mirror |
| Japan EDINET raw XBRL (Kaggle `sirokujira/edinet20xx`) / Korea DART | non-US GAAP/IFRS with calc linkbases and audit reports | language; DART behind HF CDN |
| Enron spreadsheets + emails | only large corpus of real working finance-ops workbooks | **Finch already built 172 workflows on it**; differentiate by desk and chain length |

### 2.10 Avoid / deprioritise
- **Licence:** Freddie Mac / Fannie Mae loan-level (redistribution needs paid licence), FINRA TRACE
  history (paid), NAIC statements (paid), SEDAR+ and MSRB EMMA (ToS forbid scraping; hand-curate
  from issuers instead), Yahoo-derived prices.
- **Low differentiation:** plain 10-K/10-Q QA, LendingClub (FinBen/CALM), synthetic ledgers.

---

## 3. Flagship long-horizon workflows (from the user's seat)

Each is one *episode* a finance expert would recognise as "a big chunk of my job". Horizon
estimates are rough (documents × periods × concept steps) and meant to show scale, not to be
exact. Checkpoints marked **[GT]** have natural ground truth from the source.

### F1. Municipal credit review + annual surveillance (persona: muni credit analyst / rating analyst)
*Env:* one city: 5–10 ACFR PDFs, 1–2 official statements, latest actuarial valuation,
checkbook for the overlapping years; plus a 20-city peer set (CA SCO FTR or Census) for benchmarking.
1. Extract governmental-fund and government-wide statements for each year **[GT: fund-balance
   roll-forward; gov-wide↔fund reconciliation schedule]**.
2. Normalise restatements, special items, fiscal-year changes (A4/A5).
3. Fund-balance and liquidity trend (H1); revenue concentration and intergovernmental reliance (H5).
4. Build the debt-service schedule from the OS; tie to the ACFR debt note **[GT]**; compute DSCR
   under the bond resolution's *net revenues* definition (not GAAP) (H3, C5).
5. Pension and OPEB: NPL roll-forward, ADC vs. actual contributions (H4) **[GT: actuarial report vs. ACFR RSI]**.
6. Checkbook test: vendor totals by fund vs. ACFR expenditures; duplicate/split payments (J3) **[GT: partial]**.
7. Peer percentile; memo with rating-factor scorecard (LLM-judged).
*Horizon:* ~10 long PDFs × 6–8 statements + 1–6M ledger rows → plausibly hundreds of actions.
*What separates models:* definitions that differ across documents (resolution vs. GAAP), restatements, and real reconciling items.

### F2. ABS surveillance desk, 24 months (persona: structured-credit surveillance analyst)
*Env:* one auto trust (or a shelf of 5): 24 monthly ABS-EE tapes (~10⁴–10⁵ loans each), 24 10-D
servicer reports (HTML), the 424B prospectus.
1. Each month: ingest tape, cut by FICO/LTV/term/state (F10) **[GT: strata sum to pool]**.
2. Delinquency transition matrix and roll rates (F5); CPR/ABS speed, CDR, severity (F4).
3. Pool roll-forward and reconciliation to the 10-D **[GT: pool balance, delinquencies, CNL]**.
4. Parse the prospectus waterfall and trigger definitions; replicate the month's distribution
   and test triggers (F6) **[GT: 10-D distribution amounts]**.
5. Carry state: cumulative net loss curve vs. pricing assumption; projected trigger breach date.
6. Monthly note to the PM (LLM-judged); repeat for 24 periods with compounding state.
*Horizon:* 24 periods × 6 steps, and early mistakes (e.g., the recoveries double-count) poison later months.

### F3. Portfolio rebalancing (two variants)
**F3a. US target-date fund due diligence + glide-path drift (persona: OCIO manager researcher).**
N-PORT for a TDF family's vintages (8+ quarters) and their underlying index funds; prospectus
glide path; Fama-French factors. Look-through (E1) **[GT: Σ = net assets]** → return chaining vs.
reported (E2) **[GT]** → drift vs. glide path (E3) → attribution (E8) → fee drag (E11) → handle the
2022 Institutional→Investor merger break → recommendation.

**F3b. India wealth desk quarterly review + rebalance (persona: mutual-fund distributor / RIA).**
Client holds 8 schemes across 6 AMCs. Parse each AMC's raw workbook (different layouts)
**[GT: Grand Total]** → look-through by ISIN/sector/market-cap bucket → overlap matrix → SEBI
category-rule check → trailing return/vol from AMFI NAV → Regular→Direct switch via TER → tax-aware
trade list to a target allocation (E4, E5, K2) → client letter. Repeat monthly for 6 months (state:
lots, holding periods for LTCG).

### F4. Utility rate case (persona: regulatory analyst at a utility or a commission)
FERC Form 1 for one utility over 10 years + 15 peers. Rate-base roll-forward from plant in
service, accumulated depreciation, regulatory assets (B1, B6) **[GT: 99.7% roll-forward; PUDL
rate-base table]** → capital structure and cost of capital (C7) → revenue requirement → test-year
normalisation → O&M peer benchmarking → explain the cross-year breaks (restatements,
reclassifications) → testimony-style summary.

### F5. Chapter 11 creditor-committee monitoring (persona: restructuring financial advisor)
One case: first-day declaration, DIP budget, 30 weekly variance reports, 12 MORs (scanned),
claims register, disclosure statement. MOR OCR + cash roll-forward (I2) **[GT: bank balances]** →
cumulative DIP variance vs. covenant tolerance (I1) **[GT]** → liquidity runway (C4) → professional
fees vs. budget (I6) → claims reconciliation by class (I3) **[GT: register totals]** → recovery
waterfall vs. disclosure statement (I4) **[GT]** → committee update.

### F6. Private-foundation year-end close + payout plan (persona: foundation CFO / tax preparer)
990-PF for 5 years. Parse ~4k lot lines, classify ST/LT **[GT: reported totals]** → reconcile Σ lots to
net gain and explain gaps → excise tax → minimum distributable amount **[GT]** → join CUSIP holdings
to N-PORT/13F sectors → next-year sale plan via HIFO lots while rebalancing to policy.

---

## 4. Cross-cutting findings from the PoCs

**Real traps we hit (none planted).** These are the failure modes a benchmark built on this data
would test, and each one broke a naive check until handled:

| Source | Trap |
|---|---|
| FERC | retirements stored as negatives |
| IRS 990 | identical element names in schedules; 13 schema versions; IRS renamed elements in 2013; sign ambiguity on Part XI line 7 |
| ABS-EE | repossession proceeds ⊂ recoveries (double count → negative losses); 1900-01-01 sentinel; loans dropping out/reappearing |
| India AMC | header row 2–12; ISIN column moves; % vs. fraction within one AMC; ₹ lakh; zips; one AMC defeats heuristics |
| ACFR PDFs | split digits (`$ 1 30,163`); header debris; `--` zeros; special items create a second "net change" line; "(See Note 16)" read as an amount; restated openings |
| N-PORT | fund mergers break net-asset roll-forwards |
| Chicago checkbook | pre-2018 rows dated by year only; 78% missing department; ~98k same-vendor/amount/date candidates |

**Contamination.** Refresh cadences make test splits regenerable after model cutoffs: monthly
(ABS-EE, 990 batches, India AMC, UK councils), quarterly (N-PORT, Call Reports, FERC EQR), annual
(ACFR, FERC Form 1). Archive snapshots (LIL, End-of-Term) are fine for dev splits only.

**Multi-source joins that add horizon:** CUSIP (N-PORT ↔ 13F ↔ 990-PF stock schedules ↔ muni OS);
EIN (990 ↔ FAC single audits ↔ USAspending UEI); CIK (ABS trusts ↔ 10-D ↔ 424B; BDC ↔ EX-10;
utility parents via PUDL `core_sec10k__*`); borrower names across BDC SOIs, N-PORT loans and
bankruptcy claims registers.

---

## 5. Access requirements for the build environment

The sandbox egress policy blocked every primary host. A production scraper needs these allowlisted
(steps: https://code.claude.com/docs/en/cloud-environments#network-access):

`www.sec.gov`, `data.sec.gov`, `efts.sec.gov` (declare a User-Agent, ≤10 req/s) ·
`us.aws.cdn.hf.co`, `cas-bridge.xethub.hf.co` (HF file CDN for the N-PORT/13F/Call Report/UBPR mirrors) ·
`ecollection.ferc.gov` · `cdr.ffiec.gov`, `banks.data.fdic.gov` · `api.fac.gov` · `api.usaspending.gov` ·
`fiscaldata.treasury.gov` · `www.courtlistener.com`, `storage.courtlistener.com` · AMC sites and
`www.amfiindia.com` · `find-and-update.company-information.service.gov.uk` · `filings.xbrl.org` ·
Socrata portals (`data.cityofchicago.org`, `data.sfgov.org`, ...) · issuer sites for ACFR/OS.

Already reachable and sufficient for a first build: public S3 (PUDL, GivingTuesday 990, Harvard LIL
Data.gov archive, End-of-Term PDFs), Kaggle anonymous downloads, GitHub clones, HF datasets-server.

---

## 6. Open questions for you (to steer the next phase)

1. **Which 2–3 flagships should be built into full envs first?** My recommendation: F1 (municipal),
   F2 (ABS) and F3 (rebalance). F4 is the cheapest to build (all data reachable now).
2. **Hand-curation appetite:** F1 (official statements) and F5 (Chapter 11) need a few dozen PDFs
   collected by hand because EMMA and claims-agent ToS forbid bulk scraping. Acceptable?
3. **Jurisdiction mix:** keep India (F3b) as the non-US anchor, or add UK (councils, Companies House)?
4. **Grading:** the natural-GT checkpoints above allow deterministic per-checkpoint scoring plus an
   LLM judge for memos. Do you want deterministic checkpoints first-class, or a final-deliverable
   rubric only?
5. **Episode length target:** one long episode per env (e.g., 24-month ABS desk), or a ladder of
   sub-tasks with increasing horizon on the same env (useful for measuring where models break)?
