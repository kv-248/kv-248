# Finance Concept Library: plug-and-play building blocks for long-horizon workflows

The goal of this file is an *intuition* for how long finance workflows break down into reusable
concepts, so that when we look at a data source we can ask: **"which concepts does this data
let me exercise, and how many of them chain together on the same entity / period?"**

A data source has *long-horizon scope* when it supports a deep chain of concepts on the same
data (depth), over many periods (time), across many documents or entities (breadth), with
natural ways to check intermediate results (verifiability).

---

## 1. Vocabulary

| Term | Meaning in this project |
|---|---|
| **Concept** | An atomic, reusable unit of finance reasoning with defined inputs, outputs, and at least one invariant/check (e.g., *roll-forward*, *drift calculation*, *waterfall*). |
| **Workflow** | A persona-driven job ("do the Q3 rebalance", "prepare the monthly ABS surveillance pack") = a DAG of concepts executed over a real environment, producing stateful workbook artifacts and a deliverable. |
| **Checkpoint** | An intermediate artifact (sheet/table/number) that can be graded on its own: deterministic where an invariant exists, rubric/LLM-judge where it is judgment. |
| **Natural ground truth** | A number the *source itself* reports (an audited total, a reported NAV, a servicer-reported pool balance) that the agent's bottom-up computation must reproduce. This is how we keep long, messy trajectories verifiable without synthetic data. |
| **Env** | The staged, offline snapshot of raw materials (PDFs, scans, CSV, XML) plus a starter workbook. *Deep* env = one entity over many periods; *broad* env = a universe of entities. |

---

## 2. Concept families

Each concept lists: **I/O → invariant/check → typical model failure modes** (the last column is where
frontier models are separated).

### A. Acquisition & normalization (the hidden 40% of real work)

| ID | Concept | Inputs → Outputs | Invariant / check | Where models fail |
|---|---|---|---|---|
| A1 | Table extraction from PDF / scan | statement PDF → tidy table | column totals = printed totals | merged cells, multi-page tables, OCR digit errors (8↔3, 1↔7), parentheses = negatives |
| A2 | Scale & unit normalization | mixed tables → common units | magnitudes consistent across periods | "(in thousands)" headers, per-share vs. total, bps vs. % |
| A3 | Sign & presentation conventions | raw lines → signed ledger | Assets = Liabilities + Equity | contra accounts, expenses shown positive, credit-normal accounts |
| A4 | Fiscal calendar alignment | entities with different FYEs → aligned panel | LTM = FY + YTD − prior YTD | June FYE governments, 52/53-week years, stub periods |
| A5 | Restatement / vintage handling | multiple filings of the same period → "as-first-reported" vs. "latest" | prior-period column in year t+1 vs. year t | silently mixing restated and original numbers |
| A6 | Entity resolution | names/IDs across sources → join keys | 1:1 mapping coverage | CUSIP vs. ISIN vs. ticker vs. LEI, issuer name drift, share classes |
| A7 | Chart-of-accounts mapping | entity-specific GL/fund codes → standard taxonomy | mapped total = unmapped total | many-to-one mappings, "other" buckets, governmental fund types |
| A8 | FX conversion | multi-currency → reporting currency | avg-rate for P&L, spot for B/S | using wrong rate type, CTA plug |

### B. Accounting mechanics

| ID | Concept | Invariant / check | Where models fail |
|---|---|---|---|
| B1 | Roll-forward (beg + adds − reductions = end) | ties to next period's opening balance | the universal check: PP&E, debt, allowance, claims, fund balance, pool balance |
| B2 | Three-statement linkage | NI → RE; ΔCash(CF) = ΔCash(BS) | indirect cash-flow sign errors, non-cash items |
| B3 | Accrual vs. cash / modified accrual | cash receipts ↔ revenue via ΔAR | government funds (modified accrual) vs. government-wide (full accrual) reconciliation |
| B4 | Reconciliation (sub-ledger ↔ GL, bank rec, intercompany) | unreconciled difference explained to zero | timing vs. permanent differences, duplicate detection |
| B5 | Journal entries & adjustments | debits = credits | cut-off, reclassification vs. correction |
| B6 | Depreciation / amortization schedules | accumulated dep. roll-forward | mid-year conventions, impairments |
| B7 | Leases (ASC 842 / IFRS 16 / GASB 87) | liability amortization ties to payments | discount rate, short-term exemptions |
| B8 | Consolidation & eliminations | consolidated = Σ entities − eliminations | minority interest, intercompany transfers (interfund transfers in governments) |
| B9 | Revenue recognition / deferred revenue | deferred rev roll-forward | multi-element contracts |
| B10 | Materiality & disclosure judgment | rubric | over/under-flagging |

### C. Corporate finance / FP&A

| ID | Concept | Invariant / check |
|---|---|---|
| C1 | Budget vs. actual & variance analysis (price/volume/mix bridge) | bridge sums to total variance |
| C2 | Driver-based / rolling forecast | forecast reconciles to drivers; roll forward each period |
| C3 | Working capital (DSO/DIO/DPO, cash conversion cycle) | formula consistency over periods |
| C4 | 13-week cash flow / liquidity runway | ending cash(t) = beginning cash(t+1) |
| C5 | Covenant compliance (leverage, coverage, with *contract-defined* EBITDA add-backs) | ratio vs. threshold per credit agreement definition |
| C6 | Capital budgeting (NPV/IRR/payback) | IRR solves NPV=0 |
| C7 | Cost of capital (WACC, CAPM) | weights sum to 1 |
| C8 | Scenario & sensitivity tables | base case reproduces |

### D. Valuation & equity research

| ID | Concept | Invariant / check |
|---|---|---|
| D1 | EBITDA normalization / quality of earnings | adjusted − reported = itemized adjustments |
| D2 | DCF (UFCF, terminal value, discounting) | EV → equity bridge (net debt, minorities, NOLs) |
| D3 | Trading comps / multiples | consistent LTM & share counts |
| D4 | Diluted shares (treasury stock method, converts) | share count roll-forward |
| D5 | LBO (sources & uses, debt schedule, returns) | S = U; debt schedule roll-forward |
| D6 | Segment / SOTP | Σ segments = consolidated (± corporate) |
| D7 | Earnings-quality screens (accruals, Beneish, Piotroski) | formula |

### E. Portfolio & asset management

| ID | Concept | Invariant / check |
|---|---|---|
| E1 | Holdings ingestion & position reconciliation | Σ market value = reported NAV/net assets (± cash, accruals) |
| E2 | Returns: TWR vs. MWR/IRR, linking sub-periods | geometric linking; reproduces reported return |
| E3 | Drift vs. target / policy weights | weights sum to 100% |
| E4 | Rebalancing with constraints (bands, position/sector caps, liquidity, turnover) | post-trade weights within bands |
| E5 | Tax-lot selection (FIFO/HIFO/spec-ID), wash sales | realized G/L consistency |
| E6 | Transaction-cost / market-impact estimate | |
| E7 | Risk: vol, beta, tracking error, factor regression, VaR | |
| E8 | Performance attribution (Brinson allocation/selection/interaction) | Σ effects = active return |
| E9 | Overlap, concentration (HHI, top-10), style drift | |
| E10 | Liquidity bucketing (e.g., N-PORT 4-bucket classification) | buckets sum to 100% |
| E11 | Fee & expense analysis (expense ratio, fee drag, share-class comparison) | |
| E12 | Policy/IPS compliance & asset-allocation vs. policy ranges (pensions) | |

### F. Fixed income, credit & structured finance

| ID | Concept | Invariant / check |
|---|---|---|
| F1 | Bond math (YTM, duration, convexity, accrued interest) | price ↔ yield round trip |
| F2 | Curve construction / spread to benchmark | |
| F3 | Amortization & debt-service schedules | Σ principal = original par |
| F4 | Prepayment / default / severity (SMM→CPR, CDR, LGD) | pool balance roll-forward |
| F5 | Delinquency buckets & roll-rate / transition matrices | rows sum to 1 |
| F6 | Cash-flow waterfall (sequential/pro-rata, OC/IC tests, triggers) | collections = Σ distributions |
| F7 | Credit ratios & debt capacity | |
| F8 | Recovery analysis / absolute priority rule | Σ recoveries ≤ distributable value |
| F9 | Ratings migration | |
| F10 | Stratification / pool cuts (by FICO, LTV, vintage, geography) | strata sum to pool total |

### G. Banking & prudential

| ID | Concept | Invariant / check |
|---|---|---|
| G1 | Capital ratios (CET1, Tier 1 leverage), RWA | |
| G2 | Liquidity (LCR, NSFR, loan-to-deposit) | |
| G3 | Allowance (CECL / IFRS 9 ECL), charge-off roll-forward | allowance roll-forward |
| G4 | NIM decomposition (rate/volume) | bridge sums |
| G5 | Peer benchmarking (UBPR-style percentiles) | |
| G6 | Concentration (CRE / construction to capital) | |

### H. Public & nonprofit finance

| ID | Concept | Invariant / check |
|---|---|---|
| H1 | Fund balance analysis (unassigned FB % of expenditures) | fund balance roll-forward |
| H2 | Government-wide ↔ fund statement reconciliation | the published reconciliation schedule |
| H3 | Debt service coverage (revenue bonds rate covenant), legal debt margin | |
| H4 | Pension / OPEB (NPL, funded ratio, ADC vs. contributions) | NPL roll-forward |
| H5 | Revenue base & concentration (top taxpayers, intergovernmental reliance) | |
| H6 | Budget amendments & budget-to-actual (legal level of control) | original → final → actual |
| H7 | Single audit / federal expenditure schedules (SEFA) | Σ programs = SEFA total |
| H8 | Nonprofit functional expense allocation, program ratio | Σ functions = total expenses |

### I. Restructuring & distressed

| ID | Concept | Invariant / check |
|---|---|---|
| I1 | DIP budget vs. actual variance reporting (weekly) | cumulative variance roll-forward |
| I2 | Monthly operating report (MOR) cash roll-forward | ties to bank statements reported |
| I3 | Claims register reconciliation (scheduled vs. filed vs. allowed, by class) | Σ by class |
| I4 | Plan recovery waterfall by class | APR consistency; matches disclosure statement |
| I5 | Liquidation analysis | |
| I6 | Professional fee tracking vs. budget/carve-out | |

### J. Audit, controls & forensics

| ID | Concept | Invariant / check |
|---|---|---|
| J1 | Sampling (MUS, stratified) & extrapolation | |
| J2 | Analytical procedures (expectations vs. actual, thresholds) | |
| J3 | Duplicate / split-payment detection, vendor-master anomalies | |
| J4 | Benford & digit tests | |
| J5 | Three-way match (PO–receipt–invoice) | |
| J6 | Related-party / conflict screens | |

### K. Household / SMB

| ID | Concept | Invariant / check |
|---|---|---|
| K1 | Transaction categorization & budgeting | categories sum to total spend |
| K2 | Tax computation (brackets, capital gains, deductions) | |
| K3 | Loan amortization / refinance break-even | |
| K4 | Retirement contribution & withdrawal sequencing | |
| K5 | Small-business bookkeeping & Schedule C | |

---

## 3. Composition: how a "big" workflow emerges from concepts

**Grammar.** `Workflow = Persona × Trigger × Env(sources, periods, entities) × DAG(concepts) × Checkpoints × Judgment points → Deliverable`

The horizon of a workflow (roughly, number of agent actions) comes from **five multipliers**:

1. **Acquisition burden**: raw docs → usable tables (A-family) for every period and entity.
2. **Concept depth**: length of the DAG (e.g., rebalancing needs 7 to 9 concepts).
3. **Temporal roll-forward**: repeat the DAG for each period, carrying state (positions, balances, cumulative variances) forward. Errors compound.
4. **Breadth**: number of entities (a 40-fund universe, 120 municipalities).
5. **Exceptions & judgment**: definitions buried in legal text (credit agreement EBITDA, indenture triggers), restatements, missing months, corporate actions.

A source with high scores on (1), (3) *and* natural ground truth is the jackpot: long, hard, and still gradeable.

### Worked compositions (illustrations, sources detailed in the catalog)

**W1. Quarterly portfolio rebalance (wealth/PM persona)**
`A1/A6 ingest holdings → E1 reconcile to NAV → (prices, corporate actions) → E3 drift vs. policy → E12 IPS constraints → E4 constrained trade list → E5 tax-lot selection → E6 cost estimate → E10 post-trade liquidity check → memo`
Roll it over 8 quarters with real fund holdings (e.g., N-PORT / AMFI monthly portfolios), so state carries forward (lots, wash-sale windows).

**W2. Municipal credit review (muni analyst persona)**
`A1 extract 5–10 years of ACFR statements (scanned/native PDF) → A4/A5 align & handle restatements → H1 fund balance trend → H2 gov-wide↔fund recon → H3 debt service schedule from Official Statement → H4 pension NPL/ADC → H5 revenue concentration → peer benchmarking → rating-style memo`
Natural ground truth: ACFR's own reconciliation schedules and statistical section.

**W3. Monthly ABS surveillance (structured-credit persona)**
`ingest loan-level tape (XML, ~10^4–10^5 loans) → F10 strats → F5 delinquency roll rates → F4 CPR/CDR/severity → B1 pool balance roll-forward → reconcile to servicer report (natural GT) → F6 waterfall & trigger tests vs. prospectus → forecast → surveillance note`
Repeat for 12+ monthly periods; trigger breaches are real events.

**W4. Chapter 11 case monitoring (restructuring advisor persona)**
`A1 OCR monthly operating reports → I2 cash roll-forward → I1 DIP budget variance (weekly) → C4 liquidity runway → I6 professional fees → I3 claims reconciliation → I4 recovery waterfall vs. disclosure statement → creditor-committee update`

**W5. Fiscal-year close & budget-to-actual from a government checkbook (controller/auditor persona)**
`A7 map transaction-level payments to fund/function → B3 cash→modified-accrual adjustments → H6 budget-to-actual → J3 duplicate/split payment tests → J1 sample for vouching → reconcile to ACFR fund statements (natural GT) → findings memo`

**W6. Bank peer surveillance (examiner/bank analyst persona)**
`ingest call reports (many quarters, many banks) → G1/G2 capital & liquidity → G3 allowance roll-forward → G4 NIM bridge → G6 CRE concentration → G5 peer percentiles → watchlist + memo`

**W7. Fund due diligence (manager-selection persona)**
`E1 holdings history → E2 reconstruct returns vs. reported → E8 attribution vs. benchmark → E9 style drift/overlap → E10 liquidity → E11 fee analysis from shareholder reports → IC memo`

**W8. Utility rate-case model (regulatory analyst persona)**
`extract regulatory accounts (FERC-style) → B1 rate-base roll-forward → C7 cost of capital → revenue requirement = rate base × ROR + O&M + depreciation + taxes → test-year adjustments → C1 variance vs. prior case → testimony-style summary`

---

## 4. What a data source must offer for long-horizon scope (scoring lens)

| Criterion | Question to ask of a source | Why it matters |
|---|---|---|
| Realness | Is it primary-source, unmodified real data? | goal requirement |
| Concept depth | How many families (A–K) can be exercised on the *same* records? | DAG length |
| Temporal depth | Many periods, same schema/entity? Refresh cadence? | roll-forward + contamination resistance |
| Breadth | Many comparable entities? | universe envs, screens, peers |
| Messiness | Scans, layout drift, units, restatements? | acquisition burden, realism |
| Natural ground truth | Does the source report totals that bottom-up work must hit? | verifiability of long trajectories |
| Join keys | CUSIP/ISIN/CIK/LEI/EIN/case no. to other sources | multi-source envs |
| Benchmark saturation | Already used by FinanceBench / SpreadsheetBench 2 / etc.? | differentiation |
| Scrapability | Bulk/API vs. brittle scraping; ToS; rate limits; mirrors | build cost |
