# Public-sector & nonprofit finance: practitioner videos (cluster: public)

What this covers: YouTube videos where practitioners do, or closely narrate, five public and nonprofit finance workflows. Every video listed had its metadata fetched with `yt_tool.py meta`. Every row marked *transcript read* had its auto-caption transcript downloaded and read, and the steps and timestamps come from that transcript. One candidate (ZTgdYJF1rNY) has no downloadable captions and is marked as unverified.

How the videos were rated: **A** means the video covers the full chain: source documents, then a workbook, then a deliverable. **B** means it covers a substantial part of that chain, for example reading and extracting, or analysis on numbers already given. **C** means concept explanation only.

Data-source codes: #1 = municipal ACFR and official-statement PDFs (GovText); #2 = state and city ledgers and checkbooks; #7 = IRS 990 XML.

Search effort: about 100 YouTube queries plus web search, about 55 candidates screened by metadata and 22 transcripts read.

## Best picks at a glance

| Workflow | Video | Fit | Why |
|---|---|---|---|
| Muni credit / ACFR | Strong Towns Finance Decoder Part 5 + Part 6 (yAbiyx0cgM8, me1fyWbfu9M) | A (pair) | A real county ACFR is hand-keyed into a ratio template, then the ratios are interpreted with thresholds |
| Muni credit / ACFR | Anchorage Assembly bond-rating work session (_Im0iXY2SgA) | B | How S&P factors map onto ACFR fund balance; why a policy breach led to a downgrade from AAA to AA+ |
| Muni credit / ACFR | Truth in Accounting, How to Read Your Government's CAFR (Fh4JZCB-Aus) | B | The LA CAFR, with PDF page numbers for each figure extracted |
| Fund accounting | Farhat, GASB 34 conversion worksheet (qRHDkeXv8Sk) | B | Excel worksheet converting fund statements to government-wide statements, entry by entry |
| Fund accounting | Cherry Bekaert, ACFR Preparation Guide (wW3hW_sqRP8) | B | A four-phase ACFR build and its most common errors (a ready list of checks) |
| Fund accounting | Forvis Mazars, year-end close and audit prep (h_BmT8Zck_0) | B | A close calendar from a former city controller, including budget-to-actual |
| Pension | CalPERS GASB 68 Employer Tool (lrorAMC4JJs) | **A** | Actuarial PDFs are keyed into Excel, which produces journal entries and note tables |
| Pension | GovInvest, Understanding the CalPERS valuation (NU6EniOwjm0) | B | Page-by-page reading of a real valuation report, with reconciliations |
| Pension | CalPERS, Managing your UAL (jhPxGjreVrI) | B | Scenario analysis of extra payments and fresh starts, quantified |
| Nonprofit | ProPublica Nonprofit Explorer webinar (4CJHqj8bxAE) | B | A journalist's 990 triage and multi-year tracking sheet; reproduces a NYT investigation |
| Nonprofit | GuideStar/NFF Financial SCAN demo (PDvt7L8U1Vg) | B | The ratio dashboard funders build from 990s, with peer medians |
| Nonprofit | Wallace/BDO FMA, Understanding Audited Financial Statements (_VimoYczo38) | B | LUNA reserves and the unrestricted operating result, with worked numbers |
| Single audit | CPA Hall Talk, Major Program Determination (Una0wGzoO9Q) | B | Excel example of the deterministic four-step rule |
| Single audit | Harshwal, Opinion-unit materiality (5GD4WGr5NXQ) | B | Disbursement population filtered into a selection workpaper (search for unrecorded liabilities) |
| Single audit | San Mateo County, Single Audit Process (hxoSq_NJ84w) | C | SEFA columns, threshold test with worked numbers, list of common findings |


---

## W1. Municipal bond credit analysis from ACFR / official statement


### [Let's Insert the Numbers USA 🦅 (Part 5) | Finance Decoder Tutorial](https://www.youtube.com/watch?v=yAbiyx0cgM8)

- **Channel:** Strong Towns Library · **Duration:** 16:17 · **Uploaded:** 2025-08-22 · **Views:** 196
- **Fit:** A · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 municipal ACFR PDFs (GovText archive)
- **Persona:** Local fiscal-health analyst (Strong Towns Finance Decoder volunteer/staff) transcribing a US county ACFR into a standard ratio template
- **Inputs:** FY2024 ACFR PDF of a US county (GFOA-award report; name garbled in captions as 'Kier County') - MD&A condensed statement of net position and changes in net position (current + prior year columns); Note 6 Capital Assets (governmental and business-type: not-depreciated, depreciated/amortized gross); Strong Towns Finance Decoder Google-Sheet template (US version)
- **Output / deliverable:** Completed Finance Decoder workbook (2 fiscal years entered, raw ratios and 7 trend graphs) shared view-only with the requesting member and submitted to strongtowns.org/decoder
- **Steps:**
  - `00:00` Open ACFR PDF; jump to MD&A (p.24) where condensed net position is; note GFOA certificate means better navigation
  - `01:04` Set template units to 'millions' to match the report; enter current and prior year side by side from the comparative MD&A table
  - `01:35` Current and other assets (governmental + business-type combined) 2,360.3 / 2,156.9; PDF text is OCR'd but not copyable, so key by hand
  - `02:41` Capital assets net 3,159.9 / 3,037.8; sanity-check combined total assets (5,195) against report
  - `04:22` Deferred outflows 147.5 / 131.7 and deferred inflows 66.1 / 41.7
  - `05:33` Total liabilities (not just current; long-term is the focus) 1,395.1 / 1,421.9
  - `06:11` Changes in net position: total revenues 1,488.8 / 1,493.9; operating grants 89.7 / 116.2; capital grants 108.7 / 99.9
  - `08:29` Interest on long-term debt 10.4 / 10.3
  - `10:17` Go to Note 6: governmental capital assets not being depreciated 852.1 / 790.7 and being depreciated (gross) 2,658.7 / 2,544.0
  - `13:05` Business-type capital assets: not depreciated 248.4; depreciated 1,896.1 / 1,811.6 (US sheet separates GA/BTA, Canadian sheet combines)
  - `14:49` Review computed raw ratios/graphs; share sheet view-only and submit link
- **Checks / tie-outs:** Unit consistency (thousands vs millions) set once in template; Read every hand-keyed number back aloud / double check (typo risk because PDF text not copyable); Recompute total assets and compare with report total (rounding tolerance); Same line item wording as template label; governmental vs business-type columns; MD&A capital assets net should equal Note 6 total net of depreciation
- **Judgment calls:** Which ACFR line maps to each template field (e.g., 'current and other assets' as financial assets); Whether to combine governmental + business-type activities; When the report does not subtotal, compute it yourself
- **Why useful:** Closest real screen-recording of ACFR -> spreadsheet extraction: exact line items, prior-year comparatives entered together, manual keying pain, unit choice. Roughly 15 min per fiscal year of inputs; the template expects a 10-year series, so a full task is ~2-3 h of extraction plus interpretation (Part 6).

### [Let's Interpret The Graphs (Part 6) | Finance Decoder Tutorial](https://www.youtube.com/watch?v=me1fyWbfu9M)

- **Channel:** Strong Towns Library · **Duration:** 32:18 · **Uploaded:** 2025-08-23 · **Views:** 191
- **Fit:** B · **Role:** primary (pair with yAbiyx0cgM8) · **Transcript read:** yes · **Maps to:** #1 municipal ACFR PDFs (same ratios computable from any ACFR government-wide statements)
- **Persona:** Municipal finance writer (Michel Durand-Wood, 'You'll Pay for This') interpreting the decoder ratios with a council-oriented user
- **Inputs:** Completed Finance Decoder sheet for City of Delta, BC (2012-2024 entered from annual financial reports; Canadian PSAB statements)
- **Output / deliverable:** Ratio-by-ratio interpretation narrative (trend, threshold, plausible causes) used to brief council/community
- **Steps:**
  - `00:02` Fill years working backward from the most recent report so restated comparatives (2022 restatement) are used
  - `01:10` Net financial position: want positive and rising; no universal target, compare to own history
  - `03:21` Financial assets / total liabilities (2.2x, down from 2.4-2.6x a decade ago): improving but slowing
  - `08:16` Explain depreciation as the forcing function for setting money aside; pair with net-book-value ratio
  - `12:38` Total assets / total liabilities: below 1 = insolvent (Houston, NYC, Detroit cited); Delta ~8 but falling = getting poorer
  - `17:29` Net debt / total revenue: net debt = negative net financial position (not borrowing); years of revenue to close the gap
  - `21:16` Interest / total revenue (flexibility): 2-3% manageable, rising or 4-5% is a warning; spreadsheet shows 0 due to whole-number format
  - `23:57` Net book value / cost of tangible capital assets (~60-65%): falling = consuming infrastructure; growth, developer-contributed assets and inflation push it up
  - `27:43` Government transfers / total revenue (vulnerability): Delta 2-6% vs 20-25% elsewhere; Detroit example
  - `31:29` Wrap-up: read the 10-year trend line, not single points
- **Checks / tie-outs:** Use restated prior-year figures; Gaps in years create false dips; Number formatting can hide sub-1% ratios; Ratio must be >1 for solvency
- **Judgment calls:** Trend vs level; own-history comparison over peers ('cleanest shirt in the laundry'); Context adjustments for growth/inflation in asset-consumption ratio; Whether high intergovernmental dependence is strategy or risk
- **Why useful:** Shows the interpretation layer and concrete thresholds analysts actually apply to ACFR-derived ratios; pairs with Part 5 to form a full doc->sheet->conclusion chain.

### [How to Read Your Government's CAFR](https://www.youtube.com/watch?v=Fh4JZCB-Aus)

- **Channel:** Truth in Accounting · **Duration:** 17:21 · **Uploaded:** 2019-03-13 · **Views:** 10,938
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 municipal ACFR PDFs
- **Persona:** Government-finance watchdog analyst (Truth in Accounting)
- **Inputs:** City of Los Angeles CAFR for FY ended June 30, 2017 (PDF; page references given)
- **Output / deliverable:** Extraction recipe for TIA's 'money needed to pay bills' / taxpayer-burden metric published on State Data Lab (deliverable shown at the end, not built on screen)
- **Steps:**
  - `00:36` Why CAFR over budget (budgets overstate revenue); what CAFR shows
  - `02:53` Letter of transmittal (PDF p.9): who signs, date
  - `03:33` Independent auditor's report (PDF p.27): outside firm vs elected government auditor; unmodified vs modified/adverse opinion
  - `04:22` MD&A (PDF p.31) is unaudited and management-friendly
  - `05:18` Government-wide statements: primary government vs component units
  - `06:15` Statement of net position: assets (~$63B), deferred outflows, liabilities; net pension liability $10.3B (may only be in long-term liabilities note, PDF p.160); OPEB
  - `08:24` Deferred inflows; compute net position
  - `09:47` Unrestricted net position = 'magic number'; negative for LA => costs pushed to future taxpayers
  - `10:51` Statement of activities: functional expenses vs program revenues, general revenues, change in net position
  - `12:12` Governmental funds balance sheet (modified accrual) - TIA ignores for burden analysis
  - `12:29` Notes index (PDF p.83); pension note (PDF p.202)
  - `13:06` RSI schedule of changes in NPL (PDF p.258/261): TPL, fiduciary net position, contributions, investment income; funded ratio 67.77%; OPEB UAAL
  - `15:10` Statistical section (PDF p.383)
  - `16:07` State Data Lab: per-taxpayer burden, prior years, comparisons
- **Checks / tie-outs:** Auditor independence and opinion type; Find NPL in notes when not on face; Funded ratio from RSI vs plan report; Component units included or not
- **Judgment calls:** TIA treats most pension-related deferred inflows/outflows as invalid and backs them out; Unrestricted net position as headline solvency indicator; Discount MD&A narrative
- **Why useful:** Real city document with PDF page numbers for each extraction; defines a reproducible headline metric (unrestricted net position, NPL, funded ratio) that a benchmark task could ask for.

### [Worksession re: Bond Ratings - December 3, 2021](https://www.youtube.com/watch?v=_Im0iXY2SgA)

- **Channel:** Municipality of Anchorage · **Duration:** 1:20:59 · **Uploaded:** 2021-12-04 · **Views:** 100
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 municipal ACFR / official statement PDFs (Anchorage)
- **Persona:** Issuer-side debt manager (Anchorage public finance & investments manager) and municipal advisor (Masterson Advisors) briefing the Assembly on the rating process
- **Inputs:** 17-page rating-agency presentation (Nov 2021) for GO bond sale; S&P local government criteria (2013 framework) and S&P/Fitch reports; Anchorage CAFR 12/31/2020 general fund fund balance; Q3 2021 bed-tax actuals, 2022 budget
- **Output / deliverable:** Rating outcome (S&P AAA -> AA+, negative outlook; Fitch AA+) and Assembly briefing on causes and recovery plan; GO bonds priced at 2.15% all-in
- **Steps:**
  - `02:12` Context: 10% unrestricted GF fund-balance policy (+2-3% emergency) breached after earthquake/COVID
  - `09:29` S&P criteria: institutional framework, economy, management (20%), budgetary performance, budgetary flexibility, liquidity, debt & contingent liabilities (from CAFR)
  - `16:49` Management score hinges on adherence to written fund-balance policy; missed 2019, 2020, forecast 2021
  - `22:04` One or two misses need not trigger downgrade if a credible recovery plan is shown
  - `28:37` Rating history AA- (2005) -> AA -> AA+ -> AAA; up is slow, down is fast
  - `31:23` 90-day GO sale schedule: notify agencies, answer questions, presentation, rating before pricing
  - `33:01` July 2020 forecast of $80M fund balance vs actual -$40M in 2020 CAFR: ~$92M police/fire payroll moved to CARES grant fund, ~$70M respent awaiting FEMA reimbursement
  - `37:25` Fund balance as % of expenditures vs policy line (now -4%); multi-year recovery forecast 2022-24
  - `39:40` Revenue forecasts (bed tax) and a slide typo questioned by members
  - `49:36` Cost of a downgrade hard to quantify (spread depends on market, investor appetite)
  - `51:16` S&P downgrade: management factor very strong -> strong; failure to meet policy 3rd year
  - `62:00` Negative unassigned GF balance means borrowing other funds' pooled cash
- **Checks / tie-outs:** Fund balance % of current-year expenditures vs policy; Forecast vs actual reconciliation (presentation vs CAFR); Q3 actual vs full-year budget revenue sanity; Disclosure accuracy (SEC liability for OS misstatements)
- **Judgment calls:** Whether to assume timing of FEMA reimbursement in forecasts; Conservatism of revenue projections; Policy exceptions vs credibility with agencies; Use of ARPA to rebuild reserves (Fitch peer comment)
- **Why useful:** Only video found that shows how rating criteria map onto specific ACFR numbers and why a single ratio (fund balance policy) drove a downgrade; rich source of judgment calls and checks for a credit-memo task.

### [Reading an Official Statement | Airport Debt and Credit, Part 6](https://www.youtube.com/watch?v=UE8RKZol3VA)

- **Channel:** Dafang Wu · **Duration:** 7:50 · **Uploaded:** 2026-09-27 · **Views:** 0
- **Fit:** C · **Role:** supplementary · **Transcript read:** yes · **Maps to:** #1 official statement / ACFR PDFs
- **Persona:** Airport finance consultant (DWU Consulting) - revenue-bond analyst reading order
- **Inputs:** Tampa International Airport 2024 preliminary official statement (444 pp.) and airport ACFR (illustrative references)
- **Output / deliverable:** Reading checklist for revenue-bond credit review (no workbook)
- **Steps:**
  - `00:29` Three rule books (GAAP, rates & charges, bond trust) define revenues/expenses/coverage differently
  - `01:09` Illustration: operating income $10M under GAAP vs net revenues $40M under bond documents (depreciation excluded)
  - `01:43` ACFR = audited past; OS = legal terms + forecasts; ask whether airport did what last OS said
  - `02:37` ACFR order: auditor opinion (modified, going concern, restatement) -> MD&A vs numbers -> revenues/expenses -> notes (debt, pensions, leases, contingencies) -> statistical section
  - `03:51` OS order: rate covenant first (Tampa POS p.13: 125% of Bond Service Requirement) -> defined terms (App. C) -> pledge & flow of funds -> consultant report -> airline agreement / rate resolution (App. E) -> additional bonds test
  - `05:30` Traps: OS date vs fiscal year of data; coverage basis differs; days cash on hand undefined
- **Checks / tie-outs:** Fiscal year printed on every table; Coverage basis (bond-document vs rate-setting vs analyst); Days-cash-on-hand basis
- **Judgment calls:** Treat consultant forecast as second-hand; Newest OS supersedes older indenture summary
- **Why useful:** Short (<10 min) but encodes the practitioner reading order and definitional traps that a revenue-bond coverage task must test.

#### Anatomy synthesized across videos

**Synthesized anatomy (common sequence across the videos)**
1. **Assemble the document set.** Get the latest ACFR and prior ACFRs, working backward from the most recent so that restated comparatives are used. Add the official statement for the bond and any rating reports. Sources: Strong Towns P6, Dafang Wu.
2. **Triage document quality.** Check the auditor's opinion (modified, going concern, restatement; outside firm or elected auditor). Note whether the government holds the GFOA certificate. Treat the MD&A as unaudited management narrative. Sources: TIA, Wu.
3. **Extract government-wide figures.** From the MD&A condensed tables, statement of net position and statement of activities, take assets, deferred outflows and inflows, liabilities, net position (especially unrestricted), revenues (operating and capital grants), and interest on debt. From the capital-asset note, take cost and accumulated depreciation. Units are fixed once and prior-year columns are entered at the same time. Sources: Strong Towns P5, TIA.
4. **Extract long-term liabilities from notes and RSI.** Net pension liability (sometimes only in the notes), funded ratio from the RSI schedule of changes, OPEB, and the debt schedule. Sources: TIA, Wu.
5. **General-fund lens.** Compute unrestricted (unassigned) general fund balance as a % of current-year expenditures and compare it with the government's written policy. This drives the rating agency's management and financial factors. Source: Anchorage.
6. **Revenue bonds.** Start with the rate covenant and the defined terms in the official statement. Compute coverage on the bond-document basis, which is not the GAAP basis. Check the additional-bonds test and the basis behind days cash on hand. Source: Wu.
7. **Build a multi-year ratio series (10 years) and read trends against thresholds.** Total assets / total liabilities below 1 means insolvent. Interest / revenue of 2-3% is manageable. Net book value / cost of capital assets around 60-65%. Track dependence on intergovernmental transfers and whether fund balance meets policy. Sources: Strong Towns P6, Anchorage.
8. **Conclude** in rating-factor form (S&P's seven factors), with a reconciliation of forecast to actual and a recovery plan. Source: Anchorage.

*Human time implied:* about 15 minutes of hand-keying per fiscal year (about 15 inputs), so 2-3 hours for a 10-year series. A GO bond sale and rating cycle runs 60-90 days.

**Gaps:** No video shows a buy-side or rating-agency muni analyst building a credit model in Excel from an ACFR and writing a credit memo. There is no on-screen calculation of debt per capita, overlapping debt, debt service as % of spending, or revenue-bond coverage. The closest pieces are the Strong Towns pair (extraction and interpretation), Anchorage (rating criteria) and Wu (reading order). A benchmark task here has to be designed from these parts rather than copied from one video.


---

## W2. Government fund accounting: GASB 34 conversion, fund balance, year-end close, budget-to-actual


### [Comprehensive Example: Preparing Government Wide Financial Statements | CPA exam FAR](https://www.youtube.com/watch?v=qRHDkeXv8Sk)

- **Channel:** Farhat Lectures. The # 1 CPA & Accounting Courses · **Duration:** 50:40 · **Uploaded:** 2017-08-02 · **Views:** 9,966
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 ACFR PDFs (reconciliation schedules give answer key) and #2 ledgers/trial balances
- **Persona:** CPA instructor demonstrating the GASB 34 conversion worksheet used by government preparers/auditors
- **Inputs:** Fund-basis statements for fictional Jefferson County FY2017 (governmental funds balance sheet and SRECFB; enterprise and internal service fund statements); Facts: prior capital assets $7.89M net, depreciation $316K, capital outlay $651,900, $700K 6% bonds + $22,800 premium, $22K principal, $1,800 premium amortization, unavailable property tax $22,600 (prior $19,500), transfers $65,800, ISF profit $5,660
- **Output / deliverable:** Government-wide statement of activities and statement of net position (governmental activities) in Excel
- **Steps:**
  - `00:32` Worksheet: fund totals -> adjusting entries -> government-wide column
  - `02:41` Re-establish prior-year capital assets (Dr capital assets / Cr beginning net position)
  - `05:29` Book depreciation $316K
  - `07:42` Remove capital outlay expenditure $651,900 and capitalize
  - `10:15` Replace bond proceeds/premium OFS with bonds payable $700K + premium $22,800
  - `15:00` Reclassify principal payment $22K to reduce bonds payable (678K)
  - `17:46` Accrue interest 678K x 6% x 3/12 = $10,170
  - `20:32` Amortize premium $1,800 against interest expense
  - `22:47` Recognize unavailable property tax $22,600; reverse prior-year $19,500 via beginning net position
  - `26:15` Eliminate interfund transfers $65,800
  - `28:26` Fold in internal service fund; eliminate internal profit $5,660 against expenses; add ISF interest $600
  - `39:14` Compile statement of activities (change in net position $31,705)
  - `42:33` Compile statement of net position; NIICA = capital assets net - related debt & premium; restricted from fund statements; unrestricted residual
  - `48:10` Check assets = liabilities + net position; fix a mislinked inventory cell
- **Checks / tie-outs:** Each entry balances; Capital outlay and OFS lines zero out after adjustment; A = L + NP on final statement; Totals flow from worksheet links
- **Judgment calls:** Which debt is capital-related for NIICA; ISF profit elimination allocation; Restricted vs unrestricted classification
- **Why useful:** Only screen-share of the fund->government-wide conversion workbook; every adjustment type a city preparer makes, with numbers; directly templatable as a benchmark task (fund statements in, government-wide out).

### [Annual Comprehensive Financial Report (ACFR) Preparation Guide](https://www.youtube.com/watch?v=wW3hW_sqRP8)

- **Channel:** Cherry Bekaert · **Duration:** 58:38 · **Uploaded:** 2023-10-25 · **Views:** 1,331
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 ACFR PDFs; #2 ledgers (trial balance import)
- **Persona:** Government accounting advisory MD (ACFR writing) and audit partner / former GASB practice fellow (Cherry Bekaert)
- **Inputs:** Prior-year issued ACFR with account mapping; Current-year preliminary and final trial balance; GFOA general-purpose checklist, GAAFR Appendix D, state templates; Worksheets: NIICA calc, major fund test, GASB 34 conversion, GASB 54 classification
- **Output / deliverable:** Issued ACFR (introductory, financial, statistical sections) submitted for GFOA certificate
- **Steps:**
  - `04:29` ACFR anatomy and audiences (citizens, investors/creditors, oversight bodies)
  - `08:58` GASB Concept Statement 7: keep only essential note disclosures; prune legacy schedules
  - `29:07` Common MD&A errors: amounts not tied after late adjustments; no reasons for changes
  - `32:32` Statement errors: NIICA components, nonspendable inventories/prepaids, only GF positive unassigned, no negative restricted/committed/assigned, annual major-fund test
  - `34:46` Notes/RSI: encumbrances by fund, aggregate pension/OPEB schedule tying to face, covered payroll vs covered-employee payroll, contribution timing vs measurement date
  - `37:03` OSI: budgetary comparisons for non-major funds with legally adopted budgets; statistical debt schedules
  - `38:41` Tools and templates
  - `46:54` Four phases: Build (start from issued prior ACFR, verify links, remove topside plugs) -> Roll forward (map new accounts, roll fund balance, roll columns, assign owners) -> Draft (import final TB, re-run major fund test, back-to-front, MD&A analysis) -> QC (checklist, check figures to zero, side-by-side analytic review vs prior year, tie notes to face, auditor changes)
  - `45:49` Poll: 39% take >8 weeks start to finish
- **Checks / tie-outs:** MD&A amounts tie to statements; NIICA calculation; Major fund thresholds re-tested yearly; No negative restricted/committed/assigned fund balance; Pension/OPEB aggregate ties to face; Check figures between statements zero out; Prior-year issued ACFR ties to mapping (no lingering plugs)
- **Judgment calls:** Which disclosures are 'essential'; Fund balance classification rationale; Level of MD&A analysis
- **Why useful:** Practitioner checklist of the ACFR build and its most common errors; ready-made list of automated checks for a benchmark grader; gives human time (5-8+ weeks).

### [Your Guide to Government Audit Preparation & Year-End Close](https://www.youtube.com/watch?v=h_BmT8Zck_0)

- **Channel:** Forvis Mazars US · **Duration:** 52:33 · **Uploaded:** 2024-12-06 · **Views:** 196
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #2 state/city ledgers & checkbooks; #1 ACFR PDFs
- **Persona:** Former city controller/finance director and audit senior manager (Forvis Mazars)
- **Inputs:** General ledger / trial balance; Prior-year issued report and auditor adjusting entries; Pension/OPEB reporting packages and census data; Debt schedules, capital project status, leases/SBITAs; Grant expenditures and grantor reports (SEFA); Adopted/amended budget
- **Output / deliverable:** Closed books, PBC package, draft SEFA and ACFR ready for audit fieldwork
- **Steps:**
  - `05:43` Start after prior audit: exit meeting, review PBC list
  - `08:38` Through the year: monthly balance-sheet reconciliations, trend checks, vendor invoice timeliness, monitor potential major programs, align p-card cycle to month-end, log bank accounts
  - `12:36` Capital assets/CIP and lease/SBITA quarterly meetings with departments
  - `14:48` Agree TB beginning fund balance/net position to prior issued report; obtain auditor post-TB entries
  - `16:26` Interim: pension/OPEB packages, census data, contribution reports; debt roll-forward; arbitrage
  - `22:01` Year-end: countdown emails, p-card freeze, kickoff, assign close tasks with due dates
  - `26:27` Post-FYE: confirmations, draft SEFA, last-day utility billing/court reports
  - `29:50` Reconcile SEFA quarterly to grantor reports; interim compliance testing
  - `39:09` Budget-to-actual: match budget groupings to prior ACFR, track amendments, decide which funds need budgetary comparison
  - `40:46` Statistical section sources documented
  - `44:37` Search for unrecorded liabilities; retainage; reporting tool with check figures
- **Checks / tie-outs:** Beginning balances agree to prior issued report; SEFA reconciled to GL and grantor reports; Search for unrecorded liabilities; Budget groupings consistent with ACFR; Check figures across statements
- **Judgment calls:** Estimates (trend vs historical) balancing timeliness vs reliability; Which items to outsource; Single-audit applicability
- **Why useful:** Concrete close calendar and tie-outs from someone who ran a city close; includes budget-to-actual step, which no dedicated video covers.

### [Fund Balance Analysis](https://www.youtube.com/watch?v=0qoQGoaSSck)

- **Channel:** Lake Superior State University · **Duration:** 12:25 · **Uploaded:** 2014-11-04 · **Views:** 1,964
- **Fit:** C · **Role:** supplementary · **Transcript read:** yes · **Maps to:** #1 ACFR PDFs (fund balance tables)
- **Persona:** Charter-school office finance specialist (LSSU) teaching academy boards
- **Inputs:** Example audited statements of a Michigan charter academy (SRECFB and governmental balance sheet)
- **Output / deliverable:** Board-level understanding of fund balance level and classification
- **Steps:**
  - `00:46` Fund balance = beginning + net change; governmental funds only
  - `03:32` Tie ending fund balance on SRECFB to balance sheet
  - `04:38` GASB 54 five classes; nonspendable, restricted, committed (formal action before FYE), assigned, unassigned
  - `08:37` Only GF reports positive unassigned; spending-order default
  - `09:41` How much is enough: 15% of GF expenditures (Michigan school business officials)
- **Checks / tie-outs:** SRECFB ending fund balance = balance sheet fund balance; Only GF positive unassigned
- **Judgment calls:** Target fund balance level
- **Why useful:** Gives the tie-out and the % of expenditures benchmark used in fund-balance analysis.

#### Anatomy synthesized across videos

**Synthesized anatomy**
1. **Roll forward from the prior year.** Agree beginning fund balance and net position in the trial balance to the prior issued ACFR, and post the auditor's late entries. Source: Forvis, Cherry Bekaert.
2. **Reconcile through the year and at cutoff.** Monthly balance-sheet reconciliations; accruals and the search for unrecorded liabilities; cash and investment confirmations; capital assets and CIP roll-forward (retainage); debt roll-forward and arbitrage; leases and SBITAs; pension and OPEB entries from actuarial packages. Source: Forvis.
3. **Import the final trial balance.** Map new accounts and rerun the major-fund test. Source: Cherry Bekaert.
4. **Draft back to front.** Combining schedules, then fund statements, then a **GASB 34 conversion worksheet** with these entries: capital assets and depreciation, removal of capital outlay, bond proceeds and principal reclassified, accrued interest, premium amortization, availability-based deferred inflows, interfund transfers eliminated, internal service fund folded in. Source: Farhat.
5. **Classify equity.** Net position: NIICA, restricted, unrestricted. Fund balance under GASB 54: nonspendable, restricted, committed, assigned, unassigned (only the general fund may show a positive unassigned balance). Sources: Farhat, LSSU, Cherry Bekaert.
6. **Budgetary comparison** (original, final, actual, variance) for the general fund and major special revenue funds; non-major funds go in other supplementary information. Budget groupings must match the ACFR. Sources: Forvis, Cherry Bekaert.
7. **Notes, RSI, statistical section, MD&A** (with reasons for changes).
8. **QC.** Check figures between statements zero out; MD&A ties to the statements; side-by-side analytical review against the prior year; GFOA checklist.

*Human time:* 39% of webinar respondents need more than 8 weeks for the ACFR and 25% need 5-8 weeks. The GFOA target is issuance within 6 months of fiscal year-end.

**Gaps:** No screen-share of a real city's **budget-to-actual variance analysis** in Excel; the search surfaced only corporate FP&A templates and CPA-exam encumbrance lectures. No real trial balance to ACFR walkthrough; Farhat uses a fictional county. Nothing uses **state or city checkbook/ledger exports (#2)** directly.


---

## W3. Public pension actuarial valuation / net pension liability (GASB 67/68)


### [CalPERS GASB 68 Employer Tool Instructions – 2017](https://www.youtube.com/watch?v=lrorAMC4JJs)

- **Channel:** CalPERS · **Duration:** 21:16 · **Uploaded:** 2017-10-02 · **Views:** 2,692
- **Fit:** A · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 ACFR PDFs (pension notes/RSI as answer key); CalPERS reports are public PDFs
- **Persona:** Employer finance staff (city/district accountant) preparing GASB 68 entries; presented by CalPERS Financial Reporting & Accounting Services
- **Inputs:** CalPERS GASB 68 accounting valuation reports (miscellaneous and safety risk pools) for 6/30/2015 and 6/30/2016 measurement dates; CalPERS public agency schedules of employer allocations and collective pension amounts (allocation factors by rate plan); Employer's own employer-specific deferral calculations (2014, 2015); Prior-year (6/30/2016) note disclosure: deferral balances and NPL; Employer contribution records FY2015-16 and FY2016-17; CalPERS GASB 68 Employer Tool (Excel)
- **Output / deliverable:** Current-period GASB 68 journal entries (change in deferred outflows/inflows, NPL, pension expense) and note-disclosure tables for the FY2017 financial statements
- **Steps:**
  - `00:33` Scope: cost-sharing plans, 6/30 fiscal year; confirm approach with external auditors
  - `02:12` FY2017 reporting uses 6/30/2016 measurement-date reports plus 6/30/2015 history
  - `02:44` Separate plan-specific deferrals (experience, assumptions, investment earnings) from employer-specific (contributions vs proportionate share, change in proportion, contributions after measurement date)
  - `04:22` Workbook: only input and output tabs are edited; calc tabs protected
  - `05:27` 2014 tables: rate-plan type; employer-specific deferrals from own records (outflows +, inflows -)
  - `09:51` 2015 tables by rate plan ID: hand-key three allocation factors (TPL, FNP, deferrals/expense) from allocation schedule PDF (copy blocked)
  - `13:17` Enter 2015 unamortized employer-specific deferrals
  - `14:29` 2016 tables: aggregated allocation factors by risk pool
  - `16:07` Contributions 7/1/2015-6/30/2016 by risk pool
  - `17:12` Ending 6/30/2016 deferral balances and NPL from prior-year notes
  - `18:17` 2017 tables: contributions subsequent to measurement date
  - `19:21` Output tab: journal entries and note/RSI tables
- **Checks / tie-outs:** Input-status flags turn from 'incomplete' to 'OK'; Sign conventions for outflows/inflows; Prior-year ending balances tie to prior notes; Contributions subsequent to measurement date reconcile to payment records; Auditor review of tool output
- **Judgment calls:** Allocation of employer-specific deferrals among rate plans; Adjustments for non-June fiscal years; Auditor interpretation differences
- **Why useful:** A true PDF -> Excel -> journal-entry/note chain with exact source documents and inputs; best template for a GASB 68 benchmark task.

### [August Webinar   Understanding CalPERS Actuarial Valuation](https://www.youtube.com/watch?v=NU6EniOwjm0)

- **Channel:** GovInvest for Government · **Duration:** 1:00:29 · **Uploaded:** 2020-08-21 · **Views:** 257
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #1 (ACFR pension RSI); CalPERS valuation PDFs (public)
- **Persona:** Pension analytics consultants (GovInvest) guiding CA local-agency finance staff through their CalPERS valuation report
- **Inputs:** CalPERS June 30, 2019 actuarial valuation report for a sample agent-multiple-employer plan and a risk-pool plan (page-referenced)
- **Output / deliverable:** Interpretation of contribution requirements and funded status for FY2021-22 budgeting; expectations for 2020 valuation
- **Steps:**
  - `02:32` Expect stability unless workforce change, additional discretionary payments, or fresh starts
  - `04:45` Funded status summary p.6 (65.8% -> 66.1%)
  - `05:29` Contribution rate comparison p.4; two-year lag (6/30/2019 valuation sets FY2021-22 rates); normal cost 9.77% -> 9.73%; UAL payment $13M -> $14M
  - `09:36` Year events: no assumption/method changes; 6.7% return vs 7% assumed = small asset loss
  - `10:55` UAL reconciliation p.15: $284M start, payments, interest, expected vs actual, gains/losses
  - `19:35` New amortization policy: 20-yr level dollar, 5-yr ramp only for investment gains/losses
  - `21:42` Amortization bases schedule p.16 / p.11
  - `23:29` Normal cost reconciliation and PEPRA shift p.19
  - `26:22` Effect of additional discretionary payments on bases (p.5 new section)
  - `34:50` Contribution projections now include future PEPRA hires p.25
  - `36:57` Sensitivity (discount rate +/-1%, inflation-linked), maturity and volatility ratios, hypothetical termination liability
  - `50:27` Outlook: 4.7% FY2020 return will raise UAL
- **Checks / tie-outs:** UAL roll-forward reconciles; ADP reflected in base eliminations; Two-year rate lag applied to the right fiscal year; Normal cost split employer vs employee
- **Judgment calls:** Whether results are 'stable' for budgeting; Risk read from support and volatility ratios; ADP/fresh-start strategy
- **Why useful:** Page-by-page reading of a real valuation report with the reconciliations an analyst checks; provides the extraction targets (funded %, normal cost, UAL payment, sensitivities).

### [Proactively Managing Your Pension Plan’s Unfunded Liability](https://www.youtube.com/watch?v=jhPxGjreVrI)

- **Channel:** CalPERS · **Duration:** 58:29 · **Uploaded:** 2018-06-05 · **Views:** 2,987
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** CalPERS valuation PDFs (public); #1 ACFR pension notes/RSI
- **Persona:** CalPERS actuarial office (actuaries Julian Robinson, Kurt Schneider; Deputy Chief Actuary Randy Dziubek) advising public-agency employers on paying down UAL
- **Inputs:** Employer's annual CalPERS actuarial valuation report (funded status table, page 4 required contribution, amortization-bases schedule); Agency budget capacity
- **Output / deliverable:** Paydown strategy comparison: ADP to long vs short base, recurring ADPs to a level $9M target, full/partial/soft fresh start, Section 115 trust; interest-savings figures
- **Steps:**
  - `05:52` System context: 71% funded; discount rate phasing to 7%; amortization period shortened to 20 years prospectively
  - `09:42` Valuation mechanics: entry-age normal; normal cost vs UAL amortization
  - `13:19` Read funded status table: PVB, accrued liability, assets, UAL ($79M example), funded ratio
  - `14:32` Page 4 required contribution: normal cost % of pay + UAL dollar payment ($6M); prepaying annually saves ~$522K vs monthly
  - `15:47` Project future UAL payments from amortization layers (rising as new layers phase in, falling as old layers drop off)
  - `19:06` ADPs: State of California $6B ADP example ($177.3M lower next-year contribution, ~$6B interest saved over 20 yrs)
  - `22:23` Single base example: $1M base on 30-yr schedule shows negative amortization; $100K ADP to long base saves ~$167K interest; to 10-yr base saves ~$40K but larger near-term payment relief
  - `27:51` Full schedule (17 bases): one $4M ADP vs recurring ADPs to hold total at $9M/yr -> total payments $209M vs $219M (~$10M interest saved)
  - `32:27` Fresh starts (irrevocable): 20-yr saves ~$15.5M; 15-yr saves ~$48M but payment $6.3M -> $9.3M; partial/soft fresh starts
  - `38:06` IRS Section 115 trust as rate-stabilization reserve outside the plan
  - `41:38` Next steps: talk to assigned actuary; Q&A on funded-ratio drivers (investment return dominates)
- **Checks / tie-outs:** Funded ratio and UAL from report match schedule totals; Total payments under each scenario pay off same UAL; Interest savings vs budget capacity
- **Judgment calls:** Long-term savings vs near-term budget relief (which base to pay); Irrevocability of fresh start; Trust vs ADP for flexibility
- **Why useful:** The decision-memo end of the pension workflow: scenario table of payment streams and interest savings from the valuation's amortization schedule, ready to turn into an Excel task.

#### Anatomy synthesized across videos

**Synthesized anatomy**
1. **Collect the documents.** The plan's funding valuation; the GASB 67/68 accounting valuation and the employer allocation schedule; the employer's contribution records; prior-year notes. Sources: CalPERS tool, GovInvest.
2. **Extract** funded status, total pension liability / fiduciary net position / NPL, normal cost %, UAL payment, discount rate and ±1% sensitivity, and the amortization bases. Source: GovInvest.
3. **Reconcile year over year.** Expected vs actual UAL; asset gain or loss (6.7% actual vs 7% assumed); assumption, method and demographic changes; normal-cost drift (PEPRA). Source: GovInvest.
4. **Handle timing.** The measurement date differs from the fiscal year-end; rates lag two years; contributions made after the measurement date are deferred outflows. Sources: CalPERS tool, GovInvest.
5. **Employer accounting.** Proportionate share from the allocation factors; employer-specific deferrals (change in proportion, contributions vs proportionate share); journal entries and note/RSI tables. Source: CalPERS tool.
6. **Decision analysis.** Extra discretionary payments to long vs short bases, recurring payments to a level target, fresh starts, Section 115 trust, discount-rate sensitivity, with total payments and interest saved for each. Source: CalPERS UAL.
7. **Output:** journal entries and notes for the ACFR, plus a budget forecast or paydown memo.

**Gaps:** No independent analyst (Pew, Reason or rating-agency style) builds a state-plan stress test or contribution-adequacy model in Excel on screen. There is no plan-side GASB 67 report preparation. OPEB analogues exist only as accounting webinars (Maze, Cherry Bekaert), which were not read.


---

## W4. Nonprofit financial analysis from Form 990 / audited statements (grant due diligence, 990-PF)


### [How to Use ProPublica's Nonprofit Explorer News App](https://www.youtube.com/watch?v=4CJHqj8bxAE)

- **Channel:** ProPublica · **Duration:** 57:06 · **Uploaded:** 2023-11-30 · **Views:** 2,500
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML
- **Persona:** Investigative journalists (ProPublica news-apps team; NYT nonprofit reporter)
- **Inputs:** Form 990 e-filings (AMNH FY ended June 2022; Core Services Group 2020 filing) via Nonprofit Explorer; Schedules J, L, O, I, R; State corporate/charity registries; IRS Form 1023 by request
- **Output / deliverable:** Verified story leads / investigation (NYT 2021 shelter-operator story reproduced from 990s); reporter's multi-year spreadsheet of finances and people
- **Steps:**
  - `02:18` What a 990 contains: finances, compensation, grants made, contractors, conflicts; Schedule B donors redacted
  - `09:35` People search: AMNH president ~$1M/yr across years
  - `11:18` Form version year vs tax period (FY July-June)
  - `15:10` Schedule J: $10M other reportable comp -> supplemental info explains deferred comp at retirement; read Schedule O/supplemental before reporting
  - `17:27` Data caveats: typos, amended returns
  - `18:37` Org page: EIN, multi-year revenue/expenses/assets/liabilities, filing lag up to a year
  - `26:31` Find grants received via Schedule I full-text EIN search; 990-PF requires name search
  - `30:09` Case study: compare reported comp to story, independent contractors sharing an address, Schedule L transactions/loans, related entities not disclosed; check state registries
  - `39:43` Reporter workflow: collect all 990s -> spreadsheet tracking finances and people over time + related orgs -> question list -> Form 1023 request -> state AG charity filings
  - `49:59` Donor checks: program share, executive comp concentration; overhead ratio needs context
- **Checks / tie-outs:** Tax period vs form year; Amended return supersedes; Supplemental explanations for outliers; Related-party and contractor cross-check in state registries; Multi-year consistency
- **Judgment calls:** What counts as a red flag (closed funding loops, contractor at officer's address); Avoid over-reading coincidences; Overhead % depends on mission
- **Why useful:** Shows how professionals actually triage 990s and build a multi-year tracking sheet; direct analog for a 990-XML-based due-diligence task.

### [Comprehensive 990 financial analyses made easy: a demo for nonprofit advisers 20140603 1900 1 1](https://www.youtube.com/watch?v=PDvt7L8U1Vg)

- **Channel:** GuideStar by Candid · **Duration:** 30:20 · **Uploaded:** 2014-06-05 · **Views:** 627
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML
- **Persona:** Nonprofit Finance Fund advisory manager demoing GuideStar Financial SCAN (used by funders for grant due diligence)
- **Inputs:** Five years of Form 990 data (regular 990 only) for Boys & Girls Club of Metro Denver and peers
- **Output / deliverable:** Financial SCAN report: 5-year dashboard, 13 graphs with commentary, peer comparison (exportable to Excel)
- **Steps:**
  - `02:12` Look beyond overhead to vital signs: profitability, liquidity, balance-sheet composition
  - `08:20` Data: regular Form 990 only (not EZ/PF), 5-year view, peer comparison
  - `11:41` Report: org dashboard, graphs + text (expenses, revenue, profitability, balance sheet, liquidity), peer dashboard
  - `13:20` Uses: funder due diligence starting point, budgeting, strategic planning
  - `18:48` Demo: revenue-mix trend (contributed share falling, government grants rising)
  - `21:35` Profitability = change in unrestricted net assets before/after depreciation (990 revenue commingles restricted)
  - `22:08` Balance sheet: liabilities/assets, % of land-building-equipment depreciated, net assets by restriction; liquidity: months of cash, cash & investments, estimated unrestricted liquid net assets
  - `23:47` Peers: 5 named peers + group median of 26 via NTEE codes and $5-10M revenue band
- **Checks / tie-outs:** Restricted vs unrestricted separation; Multi-year consistency; Peer group definition
- **Judgment calls:** Peer selection (NTEE, size, geography); Interpreting revenue-mix shifts
- **Why useful:** Enumerates the exact 990-derived ratios funders use, with a peer-median design; a benchmark can replicate the dashboard from 990 XML.

### [Understanding Audited Financial Statements](https://www.youtube.com/watch?v=_VimoYczo38)

- **Channel:** Wallace Foundation · **Duration:** 31:04 · **Uploaded:** 2023-03-28 · **Views:** 4,268
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML (Part VIII-X carry the same lines); audited FS PDFs not in our sources
- **Persona:** Nonprofit finance consultant (BDO FMA, Wallace Foundation 'Strong Nonprofits' toolkit) for staff, boards and funders
- **Inputs:** Hypothetical nonprofit audited financial statements (SoFP, SoA, SFE, cash flows, notes)
- **Output / deliverable:** Health read-out: reserves (LUNA), true operating result, cost drivers, operating cash flow
- **Steps:**
  - `01:05` Order of GAAP statements in an audit
  - `05:06` Balance sheet: cash vs expenses; liabilities; net assets with/without donor restrictions; board-designated
  - `10:54` Reserves = LUNA: net assets without donor restrictions ($577K) minus net PP&E ($625K) = -$48K => borrowed from restricted funds
  - `15:07` Statement of activities: operating result = change in net assets without donor restrictions (-$111K) vs misleading total (+$1K); releases net to zero
  - `21:40` Statement of functional expenses: program/admin/fundraising; cost drivers; allocation methodology
  - `26:14` Cash flows: net cash from operations (includes restricted)
  - `28:41` Notes: debt terms, restrictions, subsequent events, concentrations
- **Checks / tie-outs:** Releases from restriction sum to zero; Use unrestricted column for operating result; Subtract fixed assets (net of related debt) for liquidity
- **Judgment calls:** Reserve adequacy; Which column defines performance
- **Why useful:** Defines the core grant-due-diligence metrics (LUNA, unrestricted surplus) with worked numbers.

### [How to Read & Understand Form 990 || CalTech Example || Colleges as NonProfits](https://www.youtube.com/watch?v=uPOeEVpBbWs)

- **Channel:** Tax, Life & Finances · **Duration:** 13:40 · **Uploaded:** 2024-08-27 · **Views:** 1,110
- **Fit:** B · **Role:** supplementary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML
- **Persona:** Tax/finance educator walking through a real university 990
- **Inputs:** California Institute of Technology Form 990 for FY ended Sept 2022 (plus 990-T)
- **Output / deliverable:** Annotated reading of key 990 parts and schedules (no workbook)
- **Steps:**
  - `00:00` Header: tax period, EIN, gross receipts (~$4B)
  - `01:42` Part I summary; Schedule O cross-references
  - `04:29` 990-T unrelated business income
  - `05:50` Part VIII revenue; Part IX expenses incl. compensation and fundraising allocation
  - `09:45` Part X balance sheet (~$4B investments, $239M pledges); net assets with/without restrictions
  - `11:14` Part VII compensation; Schedule B confidential
  - `12:00` Schedule D endowment ($3.4B, $99M gifts, ~-$0.5B investment loss, 5-year history)
  - `12:42` Schedules L, R, M (non-cash gifts of securities)
- **Checks / tie-outs:** Part I totals cross-reference Parts VIII-X; Schedule O explanations for unusual lines
- **Judgment calls:** Significance of large net income for tax-exempt status
- **Why useful:** Real 990 with endowment Schedule D fields, useful for endowment-spending variants (captions are garbled, so detail is partial).

### [Decoding IRS Form 990-PF Part 1: Reading Foundation Filings](https://www.youtube.com/watch?v=7k8TOimybvA)

- **Channel:** Angel Reyes DrPH (c), MCHES, PMP, ACP · **Duration:** 19:30 · **Uploaded:** 2026-05-12 · **Views:** 10
- **Fit:** C · **Role:** supplementary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML (990-PF)
- **Persona:** Grant-seeking course instructor (prospect research on private foundations)
- **Inputs:** Form 990-PF filings via ProPublica / Candid / IRS TEOS (multi-year)
- **Output / deliverable:** Foundation prospect profile (capacity, payout, governance, type) - template recommended
- **Steps:**
  - `02:43` Access 990-PFs (ProPublica, Candid, IRS TEOS, foundation websites)
  - `03:50` Key parts: I (summary), II (balance sheet), VII-A (officers), XV (grants paid)
  - `05:05` Assets (FMV vs book) and 5% payout -> estimated giving capacity
  - `06:23` Review 3-5 years for asset and giving trajectory
  - `08:35` Board composition (family/corporate)
  - `09:36` Qualifying distributions vs minimum payout; admin expense ratio; excise tax/penalties
- **Checks / tie-outs:** Multi-year, not single-year; FMV vs book value; Payout vs 5% minimum
- **Judgment calls:** Foundation type (pass-through vs endowed; operating vs grantmaking); Capacity for new grantees
- **Why useful:** Codifies the 990-PF extraction template (capacity, payout, trend) for a foundation-analysis task.

### [What Grantee Financial Statements Are Really Telling You (And What Program Officers Miss)](https://www.youtube.com/watch?v=bliBDH9pnSw)

- **Channel:** Nonprofit Finance at Scale | Rose Adem · **Duration:** 22:40 · **Uploaded:** 2026-05-12 · **Views:** 9
- **Fit:** C · **Role:** supplementary · **Transcript read:** yes · **Maps to:** #7 IRS 990 XML (Part VIII revenue sources, Part X, Schedule D/L partially)
- **Persona:** Nonprofit finance practitioner (20 years inside nonprofit finance functions) teaching program officers grant due diligence
- **Inputs:** Grantee audited financial statements (balance sheet, statement of activities, functional expenses, notes) - no specific entity
- **Output / deliverable:** Portfolio-lens due diligence read-out (beyond the checklist) feeding a grant recommendation
- **Steps:**
  - `00:00` Standard checklist (clean opinion, program ratio, operating reserve, current ratio) passed, yet grantee missed first report
  - `03:16` Question is capacity to deliver this grant, not generic health
  - `05:26` Balance sheet: net-asset composition by restriction; current ratio composition (receivables from one government contract are fragile)
  - `08:46` Trend of net assets without donor restrictions over 3-5 years (2-5%/yr erosion is a signal)
  - `09:50` Deferred revenue vs delivery capacity
  - `11:31` Revenue concentration: one funder >25-30% or one government contract >40% = risk; restricted vs unrestricted mix over time; in-kind used to flatter functional ratios
  - `14:52` Notes: functional allocation methodology, liquidity note, revenue recognition (conditions met vs cash), related-party transactions
  - `18:45` Look for pattern consistency across statements; finance-team conversation as data point
- **Checks / tie-outs:** Net assets split by restriction; Receivable collectability vs liabilities timing; Multi-year unrestricted trend; Concentration thresholds
- **Judgment calls:** Thin reserves + strong systems vs strong reserves + weak systems; Internal inconsistency as a flag
- **Why useful:** Only video found from the funder/program-officer seat; supplies concrete concentration and trend thresholds for a grant due-diligence memo.

#### Anatomy synthesized across videos

**Synthesized anatomy**
1. **Pull 3-5 years of 990s** (ProPublica, Candid, IRS TEOS) plus audited statements. Check the tax period against the form year and use amended returns where filed. Sources: ProPublica, 990-PF lesson.
2. **Build a tracking sheet.** Revenue mix (Part VIII: contributions, government grants, program revenue); functional expenses (Part IX); balance sheet (Part X); compensation (Part VII, Schedule J); related parties (Schedules L and R); grants made (Schedule I, or 990-PF Part XV); endowment (Schedule D). Sources: ProPublica, Caltech.
3. **Compute vital signs.** Change in unrestricted net assets before and after depreciation (not the total, which mixes in restricted gifts); LUNA or estimated unrestricted liquid net assets; months of cash; liabilities/assets; % of buildings and equipment depreciated; revenue concentration (one funder above 25-30%, or one government contract above 40%); for 990-PF, payout against 5% of average fair market value. Sources: Financial SCAN, Wallace, grantee DD, 990-PF.
4. **Benchmark against peers**: NTEE code plus revenue band medians. Source: Financial SCAN.
5. **Explain outliers before concluding.** Read Schedule O and the supplemental information (for example, $10M "other compensation" turned out to be deferred compensation paid at retirement), plus notes on liquidity, allocation methodology and revenue recognition. Sources: ProPublica, grantee DD.
6. **Deliverable**: due-diligence recommendation, investigative story, or foundation prospect profile.

**Gaps:** No video shows a grantmaker analyst building a 990-to-Excel model end to end on screen. Financial SCAN is a paid tool doing it, and ProPublica's spreadsheet is described rather than shown. **Endowment spending policy** calculations (for example, a percentage of a trailing 12-quarter average) appear only in investment-consultant talks, which were not read. Some 990-PF grant analysis (Part XV medians) is covered in the course's next lesson, which was not fetched.


---

## W5. Single audit / government audit fieldwork (SEFA, major programs, sampling, tie-outs)


### [Single Audit Major Program Determination](https://www.youtube.com/watch?v=Una0wGzoO9Q)

- **Channel:** CPA Hall Talk · **Duration:** 13:18 · **Uploaded:** 2020-06-14 · **Views:** 1,744
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** SEFA data (Federal Audit Clearinghouse) - not among listed sources; ACFR single-audit sections in #1 sometimes include SEFA
- **Persona:** CPA audit partner / governmental audit trainer (Charles Hall, CPA Hall Talk)
- **Inputs:** List of federal programs and expenditures (from prior SEFA rolled forward; 6 programs, $3.55M total) in Excel; Prior audit history and risk factors per program
- **Output / deliverable:** Major program determination workpaper (programs 1 and 2 selected) feeding the compliance test plan
- **Steps:**
  - `01:02` Build complete program list from SEFA (roll prior SEFA forward); total federal expenditures $3.55M
  - `02:09` Step 1: Type A threshold $750K (total < $25M); classify each program; clusters count as one program
  - `03:52` Step 2: risk-assess Type A; one not audited as major in last 2 years -> high risk; two low-risk Type A
  - `04:59` Step 3: assess high-risk Type B = at least 1/4 of low-risk Type A count (2 x 25% -> 1); skip Type B below 25% of Type A threshold ($187,500); stop once found
  - `09:37` Step 4: majors total $1.4M vs 20% coverage for low-risk auditee ($710K); add programs if short
  - `12:24` Test compliance and internal control for each major program
- **Checks / tie-outs:** Program list complete vs SEFA; Clusters aggregated; Coverage percentage met (20% low-risk / 40% otherwise)
- **Judgment calls:** Type A risk factors (prior findings, recent major-program audit); Type B high-risk factors (new program, multiple control systems); Avoid over-assessing extra Type B
- **Why useful:** Excel worked example of the rule-based step that drives single-audit scope; fully gradable (deterministic thresholds). Note: thresholds shown are pre-2024 Uniform Guidance; 2024 revision raised the single-audit and Type A floors, so tasks must fix the regime by fiscal year.

### [Materiality: Opinion Units in Audit Planning | Harshwal & Company LLP Training](https://www.youtube.com/watch?v=5GD4WGr5NXQ)

- **Channel:** Harshwal Training Videos · **Duration:** 17:42 · **Uploaded:** 2023-12-19 · **Views:** 25
- **Fit:** B · **Role:** primary · **Transcript read:** yes · **Maps to:** #2 state/city ledgers & checkbooks (disbursement populations)
- **Persona:** Government audit firm trainer (Harshwal & Company) - fieldwork procedure in Excel
- **Inputs:** Population of post-year-end cash disbursements (330 items) with expense account codes carrying fund number; Opinion units and tolerable misstatement per fund
- **Output / deliverable:** Search-for-unrecorded-liabilities selection workpaper by opinion unit
- **Steps:**
  - `01:14` AU-C 320.A5: set materiality per opinion unit (governmental activities, business-type, each major fund, aggregate remaining fund info)
  - `02:24` Apply to search for unrecorded liabilities; population of 330 disbursements
  - `03:31` List funds with tolerable misstatement; set scope at 1/3 TM (judgment)
  - `04:41` Map each payment to fund via expense account prefix
  - `06:23` Sort by amount; drop everything below lowest scope ($1,900) -> 45 lines
  - `06:58` Sort by fund then amount; select items above each fund's scope
  - `09:18` Evaluate proposed adjustments at opinion-unit materiality
  - `10:57` Which materiality applies depends on where item is reported (major enterprise fund $76K; combined golf funds $182K; non-major aggregate $93K; GF capital assets -> governmental activities $2.4M)
- **Checks / tie-outs:** Every disbursement mapped to a fund; Scope applied per opinion unit; Non-major funds aggregated correctly; non-major presented as major treated as own unit
- **Judgment calls:** Scope fraction of tolerable misstatement; Use lowest materiality vs per-unit when units similar
- **Why useful:** Concrete ledger-population -> filtered selection workflow that maps directly onto city checkbook data; deterministic enough to grade.

### [Single Audit Process](https://www.youtube.com/watch?v=hxoSq_NJ84w)

- **Channel:** County of San Mateo · **Duration:** 52:42 · **Uploaded:** 2022-04-06 · **Views:** 250
- **Fit:** C · **Role:** primary · **Transcript read:** yes · **Maps to:** SEFA / grant ledgers (#2 partially)
- **Persona:** County deputy controller (San Mateo County) training subrecipient community organizations
- **Inputs:** Subaward agreements (programs, amounts, performance periods); Sample SEFA layout; Uniform Guidance compliance requirements
- **Output / deliverable:** Determination of single-audit applicability; awareness of common findings
- **Steps:**
  - `01:44` Single audit definition and $750K threshold
  - `06:04` Objectives: internal control and compliance opinion
  - `07:42` Compliance areas; matching, earmarking, level of effort, cash management examples
  - `13:13` Recipient vs subrecipient vs contractor; required subaward data elements (FAIN, period, indirect rate)
  - `22:19` SEFA contents: agency, program, ALN/CFDA, pass-through entity and ID, grant #, expenditures, subrecipient amounts, clusters, loans
  - `24:43` Exercise: three subawards with different performance periods; fiscal vs calendar year determines whether >$750K expended
  - `41:58` Common findings: unapproved indirect costs, unapproved timesheets, undocumented time allocation, costs outside period, wrong program, budget not actual, SEFA not reconciled, unsupported JEs, late reports
  - `47:48` Delinquent single audit consequences; extensions
- **Checks / tie-outs:** Expenditures (not awards) within fiscal year drive threshold; SEFA reconciled to GL; Costs within period of performance
- **Judgment calls:** Subrecipient vs contractor classification
- **Why useful:** Gives SEFA column spec and the threshold test with worked numbers, plus a list of findings an audit task could plant.

### [Single Audit Requirements & Best Practices](https://www.youtube.com/watch?v=_PrB3bUnrE8)

- **Channel:** SEK, CPAs & Advisors · **Duration:** 30:43 · **Uploaded:** 2022-08-29 · **Views:** 1,884
- **Fit:** C · **Role:** supplementary · **Transcript read:** yes · **Maps to:** none directly (grant ledgers resemble #2)
- **Persona:** CPA firm member and audit manager (SEK CPAs) briefing municipalities/school districts/nonprofits
- **Inputs:** Grant agreements, ALN (CFDA) numbers, OMB Compliance Supplement (Part 2 matrix, Part 3 requirements); Federal expenditure tracking by basis of accounting
- **Output / deliverable:** Readiness checklist for single audit (no workbook)
- **Steps:**
  - `00:18` Threshold: >$750K federal expenditures in fiscal year (basis of accounting); ARPA alternative engagement
  - `02:31` Single audit tests compliance AND internal controls; one sample can serve both (take larger size, e.g., 25 vs 17)
  - `04:42` Low-risk auditee criteria and major-program determination ($750K Type A when <$25M)
  - `07:57` Compliance Supplement: 12 requirement types, at most 6 per major program; matrix changes yearly
  - `11:46` Activities allowed, allowable costs (necessary, reasonable, consistent, documented)
  - `15:01` Cash management (interest >$500 remitted), period of performance (liquidate within 120 days)
  - `18:20` Procurement thresholds (micro-purchase $10K, small purchase $250K, sealed bids above), written policy, suspension & debarment
  - `22:08` Reporting: federal financial reports and special reports tied to support, timeliness
  - `25:23` Read grant agreements; ALN prefix identifies agency (84.010 = Title I); pass-through vs vendor payments (vendor payments do not count toward threshold)
  - `28:39` SEFA content: program, amounts received/expended, pass-through to subrecipients
- **Checks / tie-outs:** Expenditures by fiscal year vs threshold; Sample covers both compliance and control attributes; Procurement method vs threshold; Debarment check
- **Judgment calls:** Subrecipient vs contractor/vendor status; Which compliance requirements are direct and material
- **Why useful:** Lists the compliance attributes and thresholds that a sampling/tie-out task would test; complements the major-program workpaper video.

### [Linking the Financial Statements to Audit Workpapers - Audit Review](https://www.youtube.com/watch?v=ZTgdYJF1rNY)

- **Channel:** Harshwal Training Videos · **Duration:** 11:37 · **Uploaded:** 2023-11-25 · **Views:** 155
- **Fit:** B · **Role:** candidate · **Transcript read:** NO (captions unavailable) · **Maps to:** #1 ACFR PDFs (statement-to-workpaper tie-out)
- **Persona:** Government audit firm trainer (Harshwal & Company) - audit review stage
- **Inputs:** (not verified - captions unavailable)
- **Output / deliverable:** (not verified)
- **Why useful:** Title/description indicate a tie-out of financial statements to audit workpapers, the exact check missing elsewhere; captions could not be downloaded, so content and fit are unverified - watch before use.

#### Anatomy synthesized across videos

**Synthesized anatomy**
1. **SEFA.** Draft it early from the general ledger with these columns: agency, program, ALN, pass-through ID, expenditures, amounts to subrecipients, clusters, loans. Reconcile it quarterly to the GL and to grantor reports. Sources: Forvis, San Mateo, SEK.
2. **Applicability.** Compare federal *expenditures* in the fiscal year (not awards; vendor payments don't count) with the threshold. Sources: San Mateo, SEK.
3. **Major-program determination.** Type A/B threshold; risk-assess Type A programs; find high-risk Type B programs (at least 1/4 of the low-risk Type A count; skip programs under 25% of the Type A threshold); check coverage of 20% (low-risk auditee) or 40%. Source: CPA Hall Talk.
4. **Compliance requirements** per major program come from the Compliance Supplement matrix (at most 6 direct and material). Source: SEK.
5. **Sampling and testing.** One sample can serve controls and compliance (use the larger size). Attributes: allowability, period of performance (120-day liquidation), cash management (interest above $500 returned), procurement thresholds and debarment checks, reporting tied to support. Sources: SEK, San Mateo.
6. **Financial-statement side.** Materiality for each opinion unit; filter post-year-end disbursements by fund and scope for the search for unrecorded liabilities; tie the statements to the workpapers. Source: Harshwal.
7. **Findings and reporting.** Findings and questioned costs; corrective action plan; submission within 9 months of fiscal year-end. Source: San Mateo.

*Note:* the videos use pre-2024 Uniform Guidance thresholds ($750K single-audit threshold, $750K Type A floor). The 2024 revision raised the single-audit threshold to $1M for fiscal years beginning on or after Oct 1, 2024, so tasks must fix the regime by fiscal year.

**Gaps:** No screen-share of an actual compliance test workpaper (a sample of payroll or vouchers with attribute columns) or of preparing a SEFA in Excel. The Harshwal statement-to-workpaper tie-out video (ZTgdYJF1rNY) has no captions and was not verified.


---

## Cross-cutting lessons for benchmark design

1. **Work starts from last year's document.** ACFR preparers, closers and auditors begin by tying beginning balances to the prior issued report and rolling the template forward. Strong Towns fills ratio series from the newest report backward to pick up restatements. Tasks should supply a prior-year artifact and grade the roll-forward.
2. **Manual PDF extraction is the norm and the main error source.** Both the Strong Towns ACFR and the CalPERS allocation schedules are explicitly "not copyable" and are keyed by hand. Practitioners guard against errors with unit settings, re-reading numbers, and recomputed totals checked against report totals. A benchmark should plant tie-out totals.
3. **Basis traps are the core judgment.** Several pairs of figures look alike but are measured differently:
   - GAAP vs bond-document vs rate-setting "revenues" and "coverage" (operating income $10M vs net revenues $40M)
   - fund (modified accrual) vs government-wide (accrual) statements
   - measurement date vs fiscal year-end (the two-year CalPERS rate lag)
   - 990 total vs without-donor-restriction columns
   - tax period vs form year
   - official statement date vs the fiscal year of its data
4. **Workflows mix deterministic steps (gradable) with judgment (rubric).** The deterministic ones are the GASB 34 conversion entries, NIICA, GASB 54 classes, the major-program four steps, the GASB 68 deferral mechanics, 990-PF payout and opinion-unit scope filtering. The judgment-heavy ones are the credit view (Anchorage downgrade logic), grant due diligence (concentration, pattern consistency) and pension paydown strategy.
5. **Deliverables are specific:**
   - rating presentation and recovery plan
   - government-wide statements and ACFR
   - GASB 68 journal entries and note tables
   - UAL paydown scenario table
   - due-diligence memo or investigative story with a multi-year 990 tracker
   - major-program and selection workpapers
6. **Thresholds practitioners cite** (useful for rubrics):
   - fund balance policy of 10% (+2-3%) of general fund expenditures (Anchorage); 15% for Michigan schools
   - interest / revenue of 2-3%
   - net book value / cost of capital assets around 60-65%
   - total assets / total liabilities above 1
   - single funder above 25-30% or one government contract above 40% of revenue
   - foundation payout of 5%
   - Type A $750K and 20% / 40% coverage (pre-2024 rules)
7. **Data-source fit.**
   - #1 ACFR PDFs anchor W1 and W2 and give answer keys for W3 (pension notes and RSI) and W2 (reconciliation schedules).
   - #7 990 XML maps directly to W4 (every Financial SCAN or ProPublica metric is computable from 990 XML Parts VIII-X and the schedules).
   - #2 ledgers/checkbooks fit W2 year-end close and W5 disbursement testing, but **no video uses public checkbook data**. That is the clearest gap where the benchmark would be original rather than mirrored.
