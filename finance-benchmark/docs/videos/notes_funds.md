# Funds, portfolios, wealth and asset owners: YouTube workflow evidence

This file is the cluster deliverable for the long-horizon finance benchmark. Every video listed had its metadata fetched with `yt_tool.py meta`. Picks were rated after their auto-caption transcripts were read in full; a few very long ones were read by segment.

**Fit key**

- **A**: the video covers the full chain from source documents to a workbook to a deliverable.
- **B**: it covers a substantial part of that chain.
- **C**: it is concept explanation only.

**Data-source tags**

- #5: SEC N-PORT and 13F.
- #6: India AMC monthly portfolios plus AMFI NAV and TER.
- #7: IRS 990-PF.
- Pension PE quarterly reports (WSIB-style).

**Caveats**

- The three strongest India videos have only Hindi/Hinglish auto-captions (`hi-orig`), with no English track.
- The pension meeting captions are noisy auto-captions.
- YouTube rate limits (HTTP 429 and its bot check) blocked a few transcripts. These are listed as metadata-only.

## Picks at a glance

| Workflow | Fit | Video | Channel | Length | Maps to |
|---|---|---|---|---|---|
| 1. | A | [Portfolio Rebalancing Calculator Tutorial - Measure Twice Planners](https://www.youtube.com/watch?v=G6KoHtjdGio) | Measure Twice Planners | 15:06 | none directly |
| 1. | B | [AdvisorClaw Series: Advisor-built tax rebalancer for Schwab & iRebal](https://www.youtube.com/watch?v=mxJuJ8KEdMc) | IDX | 15:29 | none |
| 1. | B | [How to Make a Portfolio Rebalancing Spreadsheet](https://www.youtube.com/watch?v=9qgSqXiK1nM) | The White Coat Investor | 10:36 | none |
| 2. | B | [YCharts + iRebal: Leveraging the NEW Integration for Enhanced Portfolio Management](https://www.youtube.com/watch?v=rNvlfiNIh5Y) | YCharts | 37:02 | #5 SEC N-PORT |
| 2. | C | [Portfolio Performance Attribution:  The  Brinson-Fachler Model](https://www.youtube.com/watch?v=TSWKwcv42QI) | Ric Thomas - Campus Macro | 10:08 | #5 SEC N-PORT |
| 2. | B | [How To Analyze A Mutual Fund - Simple Investment Analysis](https://www.youtube.com/watch?v=ROAGmAgoMAE) | Jay Fairbrother | 16:51 | #5 SEC N-PORT |
| 3a. | A | [How to Review a Client’s Mutual Fund Portfolio ? \| Live MFD Demo (FinApp)](https://www.youtube.com/watch?v=p_m2DCJi520) | FinApp by Pulselabs | 1:41:11 | #6 India AMC monthly portfolios + AMFI NAV/TER |
| 3a. | B | [How I Review My 2 Cr+ Mutual Fund Portfolio \| Find Hidden Mistakes with this Tool](https://www.youtube.com/watch?v=A6-4rZEcK-8) | Amit Upadhyaya | 18:04 | #6 India AMC monthly portfolios |
| 3a. | B | [Client Portfolio Review as Mutual Fund Distributor](https://www.youtube.com/watch?v=12U_M7zEL7I) | MentorShobhit | 16:08 | #6 India AMFI NAV |
| 3b. | B | [1.8- Financial Modeling- Fund Selection Case study Using Excel- Feb Live Class](https://www.youtube.com/watch?v=1zHh9I1IKkg) | Mentor Me Careers | 1:14:47 | #6 AMFI NAV history |
| 3b. | B | [Use this tool to compare mutual fund performance with benchmarks](https://www.youtube.com/watch?v=8oriyM8s-ew) | freefincal - Prudent DIY Investing (freefincal) | 10:24 | #6 AMFI NAV |
| 3b. | B | [How to extract a mutual fund portfolio to a spreadsheet](https://www.youtube.com/watch?v=7S0VFj05N9k) | freefincal - Prudent DIY Investing (freefincal) | 15:59 | #6 India AMC monthly portfolios |
| 4. | B | [PE Fund Performance Metrics: TVPI vs. MOIC vs. DPI and Gross vs. Net IRR](https://www.youtube.com/watch?v=bGhv_Kox5RA) | Mergers & Inquisitions / Breaking Into Wall Street | 17:51 | Pension PE quarterly reports |
| 4. | B | [PE Funds of Funds and Secondaries Case Studies: Full Prep Guide](https://www.youtube.com/watch?v=Md8aJNGavDo) | Mergers & Inquisitions / Breaking Into Wall Street | 17:20 | Pension PE quarterly reports |
| 4. | B | [Private Markes Pacing Model - Basic: Overview](https://www.youtube.com/watch?v=xtCXm7t8WZ0) | IRRModels | 10:31 | Pension PE quarterly reports |
| 5. | B | [TRS Investment Meeting - March 5, 2026](https://www.youtube.com/watch?v=j0kgLzFNwfI) | TRSNYC | 41:20 | Pension PE quarterly reports |
| 5. | B | [Firefighters Pension Board Mtg June 4, 2024](https://www.youtube.com/watch?v=vW5U27MSX8I) | City of Palatka Official Page | 1:33:27 | none directly |
| 5. | B | [06-17-2024 Fire Pension Investment Meeting](https://www.youtube.com/watch?v=AdkKohRnP4o) | NYC Investment Meetings | 1:21:44 | Pension PE quarterly reports |
| 5b. | B | [September 30, 2026, Investment Committee Meeting](https://www.youtube.com/watch?v=QDPTJXTwDKY) | Pension Review Board | 1:13:25 | Public pension filings |
| 6. | B | [Fund Accounting: NAV & HWM Calculation Process/Fund accounting end-to-end NAV calculation example](https://www.youtube.com/watch?v=JZPV88cTbZk) | GMT Academy-Learning First | 1:07:46 | none |
| 6. | B | [Cash Reconciliation](https://www.youtube.com/watch?v=HuMT8inUjJs) | The Fund Accountant | 20:43 | none |
| 6. | B | [Position and Income Reconciliation](https://www.youtube.com/watch?v=I5NuvmTP-E4) | The Fund Accountant | 14:43 | none |

## 1. Portfolio rebalancing (drift vs target, bands, trade list, tax-aware, model portfolios)

### Anatomy synthesized across the videos

**Inputs.** Custodian positions per account (a tax-lot file for taxable accounts), cash (often missing from lot exports and keyed by hand), a security-to-asset-class map (Morningstar categories feed the platforms), model or target weights at asset-class or ticker level, tolerance bands, client cash needs (withdrawals or contributions), and each account's tax type (taxable, IRA, Roth).

**Steps, in the order practitioners follow them.**
1. Aggregate holdings by account and asset class, and tie the totals to the custodian.
2. Compute current weights and compare them with the targets.
3. Flag drift outside the bands. Examples seen: the 5/25 rule (±5 points absolute or ±25% relative) and a 20% relative band.
4. Decide whether to trade at all. Frequently nothing is outside the bands and the answer is "no trades".
5. Choose the trade style: full rebalance, partial (out-of-band classes only), or buy-only deployment of cash.
6. Apply the tax overlay: harvest losses first, select lots, and compare tax-neutral, tax-efficient and back-to-target scenarios.
7. Layer in cash needs and asset location across accounts.
8. Round to whole shares and minimum lots, which leaves residual cash.
9. Export a custodian-format trade file or blotter and confirm post-trade weights.
10. Keep monitoring drift.

**Deliverable.** A per-account trade list in dollars or shares, plus a household allocation and tax-location summary.

**Recurring checks.** Targets sum to 100%. Account totals tie to the custodian. Pre-trade total equals post-trade total. Post-trade weights land inside the bands. A flag appears when the requested cash cannot be raised without selling.

**Time.** The spreadsheet versions run in minutes once set up; the planner runs it live in a client meeting. The RIA's tax tool was "built in three sessions".

### [A] Portfolio Rebalancing Calculator Tutorial - Measure Twice Planners

- **Link:** https://www.youtube.com/watch?v=G6KoHtjdGio
- **Channel / length / uploaded / views:** Measure Twice Planners / 15:06 / 2024-10-18 / 2,776
- **Persona:** Advice-only financial planner (Measure Twice Planners network member) whose DIY clients place their own trades; he runs the calculator live with them
- **Maps to:** none directly (client custodial positions); a benchmark task could synthesize multi-account household holdings
- **Transcript read:** yes

**Inputs**

- Current balance of each holding per account, keyed from the custodian (client screen-shares custodian login)
- Bank checking/savings cash outside investment accounts
- Desired allocation per ticker/asset category for each account (taxable, pre-tax, Roth)
- Desired cash remaining after trades (including planned withdrawals, e.g. $20k from taxable, $50k from pre-tax)
- Knowledge of which taxable positions carry unrealized capital losses (sold first)

**Steps (timestamps from the transcript)**

- `00:02` Purpose: run the calculator live while the client logs into the custodian so both see which trades to place; also handed to clients for future self-rebalancing
- `00:34` Enter checking/savings cash so household-level reports include cash held outside brokerage/retirement accounts
- `01:40` Taxable brokerage block: list tickers and asset categories (US large/mid/small, foreign developed, emerging, bonds, cash), incl. funds to be bought; enter desired allocation (80/20 example) until the red 'not 100%' warning clears
- `02:43` Enter current balance per holding; compare computed account total with the actual account; current allocation = balance / account total
- `03:15` Set desired post-trade cash (e.g. fully invest the $20k cash position)
- `03:47` 'Trades with sale' column = desired $ - current $ (sell US large/small, buy mid/foreign/EM/bonds); future allocation equals target
- `04:19` 'Trades without sale': allocate only available cash to underweight holdings pro rata (percentage-of-cash column) to avoid realizing gains; result moves closer to target (bonds 12% -> 19% vs 20% target) but not exact
- `05:21` Tie-out: current and future account totals must be equal
- `05:53` Withdrawal case ($20k cash need, no cash in account): with-sale variant oversells to raise cash and rebalance; buy-only variant flags in red that cash cannot be raised without selling
- `06:26` Practice note: first sell taxable positions with unrealized capital losses, then re-enter balances including freed-up cash before computing trades
- `09:09` Pre-tax and Roth blocks: same layout without the tax-avoidance columns (e.g. 60/40 with $50k withdrawal; Roth moved to 100% equity by selling bonds and deploying cash)
- `10:48` Add more accounts by copying a block and re-pointing absolute references (warns about broken fixed references)
- `13:03` Household roll-up: sum each asset category across accounts, current vs future (with and without sale); red highlight if roll-up totals disagree
- `14:09` Tax-location summary: dollars and % in taxable / pre-tax / tax-free (no change from trades because money does not move between accounts)

**Checks and tie-outs**

- Target allocation per account must sum to 100% (red warning otherwise)
- Computed account total should match the custodian's account value
- Current total = future total per account (trades are self-financing apart from requested cash)
- Red flag when requested cash cannot be raised in the buy-only variant
- Household roll-up totals must agree across current/future views (red highlight on mismatch)

**Judgment calls**

- Full rebalance (realize gains) vs buy-only cash deployment in taxable accounts
- Harvest unrealized losses before rebalancing
- How much cash to hold or withdraw and from which account (tax location)
- Fund/ticker chosen per asset category (presented as examples, not advice)

**Output:** Per-account dollar trade list in two variants (full rebalance 'trades with sale' and buy-only 'trades without sale'), plus household-level asset-allocation (detailed and US/foreign/bonds/cash) and tax-location (taxable/pre-tax/tax-free) summary, current vs post-trade

**Why useful:** Clearest end-to-end advisor rebalancing workbook found: multi-account household, explicit target/current/trade/future columns, tax-aware buy-only variant, withdrawals, and built-in tie-out checks. Good template for a 'rebalance trade list' deliverable.

### [B] AdvisorClaw Series: Advisor-built tax rebalancer for Schwab & iRebal

- **Link:** https://www.youtube.com/watch?v=mxJuJ8KEdMc
- **Channel / length / uploaded / views:** IDX / 15:29 / 2026-09-08 / 50
- **Persona:** RIA portfolio manager (quant, ~10 years running rebalancers) doing tax-sensitive rebalancing of inherited low-basis accounts
- **Maps to:** none (custodian tax-lot exports); synthetic lot files would be needed
- **Transcript read:** yes

**Inputs**

- Tax-lot file downloaded from Schwab (or multi-account export from portfolio-reporting software)
- Cash position keyed by hand (lot downloads usually omit cash)
- CSV mapping each symbol to asset class / category
- Model targets at asset-class / category level
- Schwab trade-file specification and account number

**Steps (timestamps from the transcript)**

- `02:50` Context: accounts from an acquired advisor have very low cost basis; goal is to hit asset-class/category targets tax-sensitively; iRebal's tax settings were not granular enough
- `03:57` Download lot file from Schwab or portfolio reporting; drag into tool; column mapping tolerates different custodians
- `04:30` Key in the cash position missing from the lot file
- `05:02` Parse holdings; attach asset class/category from a CSV (would be an API in production)
- `05:35` Pick a preset model or 'current'; edit asset-class targets
- `06:11` Calibrate: suggests trades; with 'current' as model everything fell in band, so no trades
- `07:16` Compare scenarios: tax-neutral (harvest losses to offset gains), tax-efficient (in between), back-to-target (full rebalance); sells chosen using lot-level tax consequences
- `07:49` Buys suggested only at asset-class level; next step is a rule for which symbol to buy (pro rata to existing holdings or priority order)
- `08:53` Export chosen scenario as Schwab trade file (account number required); import into iRebal blotter alongside IRA/other trades; iRebal continues drift monitoring and alerts

**Checks and tie-outs**

- Drift-band test (no trades when in band)
- Tax-neutral constraint: realized gains offset by harvested losses
- Manual cash entry because lot files omit cash
- Builder/tester sub-agents ran tests on the tool

**Judgment calls**

- Which tax lots to sell; how much net gain to accept (tax-neutral vs back-to-target)
- Security selection for buys within an asset class
- Keeping an established rebalancer as the guardrail/monitoring layer

**Output:** Scenario trade list (tax-neutral / tax-efficient / back-to-target) exported as a Schwab-format trade file, then executed through the iRebal blotter with other trades

**Why useful:** Shows the real RIA data chain for tax-aware rebalancing (custodian lot file -> asset-class mapping -> model -> tax scenarios -> custodian trade file) and the known gaps (missing cash, buy-side selection). Partly a product demo.

### [B] How to Make a Portfolio Rebalancing Spreadsheet

- **Link:** https://www.youtube.com/watch?v=9qgSqXiK1nM
- **Channel / length / uploaded / views:** The White Coat Investor / 10:36 / 2019-11-04 / 27,697
- **Persona:** DIY physician investor / personal-finance educator (White Coat Investor)
- **Maps to:** none
- **Transcript read:** yes

**Inputs**

- Balances per asset class summed by hand across all investment accounts (401k etc.)
- Target asset allocation (US 30 / intl 25 / bonds 25 / real estate 15 / gold 5)

**Steps (timestamps from the transcript)**

- `01:04` Lay out columns: asset class, desired %, current $, current %, desired $, difference
- `01:38` Enter five asset classes and target %; check targets sum to 100%
- `02:46` Go through each account and sum dollars per asset class (total $268,431)
- `03:53` Current % = class $ / total (absolute reference)
- `05:38` Desired $ = target % x total; difference = desired - current (e.g. -$6,702 US stocks, +$6,200 intl, +$8,200 bonds, -$5,700 RE, -$2,000 gold)
- `07:18` Conditional formatting bands using the 5/25 rule: +/-5 points for large classes (25-35%, 20-30%), +/-25% relative for small ones (11.25-18.75% for 15%, 3.75-6.25% for 5%)
- `10:05` Conclusion: all classes inside bands, so no rebalance needed this time

**Checks and tie-outs**

- Targets sum to 100%
- Band test per asset class (green/red)

**Judgment calls**

- Band width choice (5/25 rule)
- Whether to act when inside bands

**Output:** Per-asset-class dollar moves to restore targets plus a band test showing whether rebalancing is needed

**Why useful:** Minimal canonical drift-vs-target + tolerance-band spreadsheet; good baseline spec for a benchmark task's first stage.

### Gaps

No video works a real multi-account household with tax lots in Excel from actual statements end to end. Platform videos (Orion Eclipse, Fidelity Wealthscape) cover setup rather than decisions. None gives the cost of rebalancing a whole book of business. Model-portfolio maintenance across many accounts (household or sleeve level) only appears in vendor demos.

### Runners-up (metadata verified)

- Ox0sqEG_HnU - Risk Parity Chronicles, simple rebalancing spreadsheet: complete vs partial rebalance, 20% relative band, rounding down to whole shares leaves cash (transcript read, B)
- 9eGC6YoTHfM - Orion WealthTech, Eclipse Trading Series: Foundations and Setup. Security classification tiers and account tax-type flags drive tax-aware trading (transcript read, C)
- 64a2SsGvh0E - kite withyou, live rebalancing with an Excel sheet. Crypto, but shows bid/ask and minimum-order effects on post-trade weights (transcript read, C)
- qMn-cCqsrBw - Orion WealthTech, Eclipse Trading Series: Trade Tools. Process: review accounts -> trade creation (global trades, trade-to-target per account, cash needs per portfolio, tax-loss harvesting, quick trade, liquidate) -> trade review -> submission to custodians (transcript read, C)
- 2g_MiWVuJ3I - NEDL, tolerance-band simulation in Excel (metadata only)
- c3rUFtiCflQ - Fidelity Institutional, Wealthscape modeling and rebalancing demo (metadata only)

## 2. Fund/ETF due diligence & manager selection (holdings, attribution, fees, replacement decision)

### Anatomy synthesized across the videos

**Inputs.** Fund NAV or returns, the benchmark and category peer set, holdings (sector, style and market cap), expense ratio, turnover, manager tenure and changes, and the model or menu in which the fund sits.

**Steps.**
1. Classify what the fund is: style box, index or active, US or foreign.
2. Measure return vs benchmark and vs category rank over several windows.
3. Compute risk statistics (beta, alpha, R², Sharpe, capture ratios).
4. Run attribution (Brinson allocation, selection and interaction) and identify detractors.
5. Compare costs. Expense ratio and turnover are converted to dollars per $10k, and the question is whether the fee is earned.
6. If a fund fails, screen its category for replacements.
7. Re-optimize the model with weight constraints.
8. Produce the proposal or monitoring report and push the model to the rebalancer.

**Rules seen.** Watch-list criteria are set in the IPS: an fi360 score in the top 25%, plus separate passive criteria (tracking error, information ratio, expense ratio) and separate criteria for target-date funds and money-market funds. One period of attribution is never enough to act on. A manager change is an explicit trigger.

**Deliverable.** A monitoring or proposal report, or a model change.

### [B] YCharts + iRebal: Leveraging the NEW Integration for Enhanced Portfolio Management

- **Link:** https://www.youtube.com/watch?v=rNvlfiNIh5Y
- **Channel / length / uploaded / views:** YCharts / 37:02 / 2024-05-09 / 1,280
- **Persona:** RIA / wealth advisor maintaining model portfolios (webinar by YCharts customer-success manager with Schwab iRebal integration consultant)
- **Maps to:** #5 SEC N-PORT (fund holdings/returns could substitute for vendor data) - indirect
- **Transcript read:** yes

**Inputs**

- Model portfolio held in Schwab iRebal (holdings + target weights)
- YCharts fund data (returns, category rankings, attribution)
- Prospect's current holdings (for proposal comparison)

**Steps (timestamps from the transcript)**

- `07:44` Activate the Schwab/iRebal integration in YCharts
- `09:51` Import the iRebal model: holdings and target weights; set benchmark and rebalance frequency
- `14:19` Generate comparison report: proposed model vs prospect's current holdings (and benchmark); customize modules (e.g. swap beta for weighted-average P/E)
- `20:56` Attribution tab: identify which holdings detracted from model performance
- `23:06` From the detractor, 'find funds ranked in category' -> screen category peers on 1/3/5-year scores; pick replacement
- `24:42` Replace the fund in the model
- `27:35` Portfolio optimizer over the longest common history; choose a frontier point with higher return at same standard deviation; constrain weights (min 5%, max 60%)
- `32:14` Export optimized result as a model portfolio and push to iRebal

**Checks and tie-outs**

- Use the longest available common history for optimizer statistics
- Min/max weight constraints to avoid corner solutions

**Judgment calls**

- Which detractor to replace and with which category peer
- Whether the optimizer's reweighting is acceptable
- What to show the client in the proposal report

**Output:** Updated model (underperforming fund replaced, weights optimized) pushed back to iRebal for implementation, plus a client-facing comparison/proposal report (proposed model vs current holdings vs benchmark)

**Why useful:** Shows the practical wealth-management variant of fund due diligence: attribution -> find laggard -> category screen -> replace -> reweight -> push to rebalancer -> client proposal. Vendor demo, so analysis depth is shallow.

### [C] Portfolio Performance Attribution:  The  Brinson-Fachler Model

- **Link:** https://www.youtube.com/watch?v=TSWKwcv42QI
- **Channel / length / uploaded / views:** Ric Thomas - Campus Macro / 10:08 / 2021-12-22 / 22,878
- **Persona:** Institutional investment professional / educator explaining performance attribution
- **Maps to:** #5 SEC N-PORT (holdings-based sector weights for a fund vs index) - possible input
- **Transcript read:** yes

**Inputs**

- Portfolio and benchmark sector weights (three sectors) for one month
- Portfolio and benchmark sector returns

**Steps (timestamps from the transcript)**

- `00:32` Compute portfolio return (3.6%) and benchmark return (1.8%) as weight x return sums; excess return 1.8%
- `01:38` Allocation effect per sector = (wp - wb) x (rb_sector - rb_total): consumers +7 bp, financials +63 bp, technology +31 bp; total 101 bp
- `04:21` Selection effect = wb x (rp_sector - rb_sector): +38 bp, -132 bp, +111 bp; total +17 bp
- `06:28` Interaction effect = (wp - wb) x (rp_sector - rb_sector): consumers +12 bp, technology +15 bp, financials the remainder (about +33 bp, large underweight where selection was bad); total ~60 bp
- `08:38` Summary table by sector and effect; sums to ~178-180 bp = excess return
- `09:14` Interpretation: better allocators than stock pickers; poor selection in financials; one month too short to act on

**Checks and tie-outs**

- Sum of allocation + selection + interaction must reconcile to total excess return (rounding)

**Judgment calls**

- Do not draw manager-quality conclusions from one period

**Output:** Brinson-Fachler attribution table: allocation, selection and interaction effects by sector that sum to the 1.8% excess return, with a verbal interpretation

**Why useful:** Precise computational spec and tie-out for the attribution step inside a due-diligence memo; concept-level only (no real fund data).

### [B] How To Analyze A Mutual Fund - Simple Investment Analysis

- **Link:** https://www.youtube.com/watch?v=ROAGmAgoMAE
- **Channel / length / uploaded / views:** Jay Fairbrother / 16:51 / 2020-12-15 / 8,934
- **Persona:** Investor-educator (20+ years investing/finance experience) doing a second-opinion review of a fund an advisor recommended to a near-retiree
- **Maps to:** #5 SEC N-PORT (holdings incl. affiliated-fund positions allow fund-of-funds look-through; expense data from prospectus)
- **Transcript read:** yes

**Inputs**

- Fund websites / fact sheets for JPMorgan Investor Balanced (OGIAX) and Vanguard Balanced Index Admiral (VBIAX): objective, expense ratio, holdings
- Underlying funds' fact sheets for the fund-of-funds holdings (JPM Core Bond R6, Core Plus Bond R6)
- Client context: near retirement, already paying an advisor ~1%

**Steps (timestamps from the transcript)**

- `01:06` Context: viewer near retirement; advisor wants to sell stocks and move money into one balanced fund; fact sheet raised red flags
- `02:43` Check objective/mix: 50/50 stocks vs fixed income - suitable risk level for a near-retiree
- `03:50` Skip past performance; check fees first: 1.01% gross / ~0.9% net expense ratio; plus ~1% advisor fee -> ~2% all-in
- `05:30` Holdings: 28 holdings, $4.83bn assets; top holdings are JPM Core Bond R6 (21.6%), Core Plus Bond R6 (9.6%), US Equity R6 (8.8%) - a fund of funds
- `07:10` Look through to underlying funds' own expense ratios (0.34%, 0.40%) - layered costs, plus their turnover/distribution/tax effects
- `10:30` Comparator: Vanguard Balanced Index (60/40 target) - note different mix despite similar name
- `11:37` Fees 0.07% vs 1.01%
- `12:43` Holdings: ~3,300 individual stocks and ~7,721 individual bonds held directly (no second fee layer)
- `15:28` Conclusion: Vanguard fund clearly better; would decline the advisor's recommendation

**Checks and tie-outs**

- Compare stated target mix (50/50 vs 60/40), not just fund names
- Look-through of fund-of-funds holdings to underlying expense ratios
- Total cost including advisory fee

**Judgment calls**

- Ignore past performance vs fees as the primary screen
- Whether the mix suits the client's horizon
- Recommend/decline

**Output:** Verdict to the client: reject the advisor's fund (all-in ~2% cost, layered fund-of-funds fees) in favour of the low-cost balanced index fund

**Why useful:** A concrete holdings-and-fee due-diligence chain ending in a recommendation; the fund-of-funds look-through is directly reproducible from N-PORT filings. Retail framing rather than institutional.

### Gaps

No video shows a consultant or OCIO analyst writing a full manager-research IC memo, or doing holdings-based style-drift or active-share analysis on actual N-PORT or 13F filings. The best material is a vendor demo plus calculation tutorials. 401(k) fund monitoring with a watch list is a promising real workflow, but the only video found (fi360) is a product interview.

### Runners-up (metadata verified)

- -JsLKLm1afk - Retireholics, Fi360 Toolkit: Fiduciary Software for 401(k) Advisors. IPS-driven watch list (fi360 score, top 25%), separate passive criteria, quarterly monitoring reports for 40,000 plans; manual Excel upload of plan funds and balances was the slowest step (transcript read, C)
- cCNxKbYZZf0 - Ronald Moy, Ph.D., CFA, CFP, Morningstar Mutual Fund Analysis. Index vs active fund on expense ratio, turnover (496%), beta 1.48 and cost per $10k ($16 vs $334 over 3 years) (transcript read, C)
- MGDe3RUvfao - Rob Berger, How to Evaluate a Mutual Fund: style box, expense ratio, turnover, holdings via Fidelity and Morningstar (transcript read, C)
- fWI52Iy5lpU - Phenix Capital, impact fund-of-funds manager selection case study. 6-dimension, 22-item scorecard scored 1-4 over 3-24 months of diligence (transcript read, C)
- MForYyl9WiU - Chandra Bhatnagar, Portfolio Performance Attribution, asset-allocation vs selection derivation (transcript read, C)

## 3a. India MF client portfolio review (CAS -> allocation/benchmark/category review -> exit/switch recommendation)

### Anatomy synthesized across the videos

**Inputs.** The client's detailed CAS from CAMS or KFintech. Practitioners stress transaction-level data, not the NSDL/CDSL summary. Also the risk profile (capacity, tolerance and required risk), the agreed target allocation, a blended or category benchmark, and category rank or quartile data.

**Steps.**
1. Aggregate all folios and compute XIRR.
2. Compare the portfolio with a blended benchmark and with headline indices over several windows.
3. Check asset allocation vs target (equity/debt/gold/cash) and market-cap mix vs band. One example: mid plus small cap at 55% ±5.
4. Review each scheme vs its benchmark and category quartile. Keep a scheme if it sits in the top or upper-middle quartile in 2-3 of the last 3-4 years; minimum one-year track record.
5. Flag drags: inline or underperforming schemes, manager changes, regular plans paying commission.
6. Check look-through sector concentration (financials above ~30%) and overlap with direct equity.
7. Recommend exits or switches with the capital-gains impact.
8. Rebalance by booking profit in the overweight asset class.
9. Present a PDF to the client.

**Deliverable.** A client review report with an action list (exit, switch, rebalance).

### [A] How to Review a Client’s Mutual Fund Portfolio ? | Live MFD Demo (FinApp)

- **Link:** https://www.youtube.com/watch?v=p_m2DCJi520
- **Channel / length / uploaded / views:** FinApp by Pulselabs / 1:41:11 / 2026-10-10 / 110
- **Persona:** Mutual fund distributors (MFDs) in a live training session run by a fintech (FinApp) - client portfolio review and rebalancing on a CAS
- **Maps to:** #6 India AMC monthly portfolios + AMFI NAV/TER (scheme returns, category ranks, holdings for overlap/correlation); client CAS would need to be synthesized
- **Transcript read:** yes

**Inputs**

- Detailed CAS (consolidated account statement) PDF from CAMS/KFintech - explicitly not the NSDL/CDSL summary CAS
- Client risk-profile questionnaire (risk capacity, risk tolerance, risk required)
- Scheme ranking data (in-house 21-factor score; 1/3/5-year windows; CAGR, rolling and quarterly absolute returns)
- Scheme vs benchmark returns
- RTA mailback files for distributor's existing clients (bulk alternative to CAS upload)

**Steps (timestamps from the transcript)**

- `03:59` Framing: fintechs offer free portfolio reviews to MFD clients; asks how many MFDs genuinely sit with HNI clients to review rather than just sending statements
- `25:06` Run client risk profiler: separate risk capacity, risk tolerance and risk required to reach goals
- `26:16` Suitability report: does the portfolio match the risk profile? if unsuitable, drill into asset allocation, fund category and scheme-level suitability
- `29:39` Upload detailed CAS (from CAMS/KFintech, not NSDL/CDSL); parsing takes ~7-10 minutes when there are many transactions
- `32:00` Review totals invested and current value; portfolio risk profile vs client risk profile
- `33:41` Folio-wise analysis of all 28 schemes; 'blood test report' framing - out-of-range items highlighted for discussion
- `37:04` Scheme ranking is a combination of 21 factors (returns plus risk etc.); keep only schemes in first quartile (top 25%) of category
- `38:50` Scheme vs benchmark: e.g. 10.5% vs 12.42% and rank 6 of 6 -> underperformed on both tests -> exit candidate
- `40:27` Impact rating (minimal / high positive / high negative) driven by the scheme's weight in the portfolio
- `42:41` Debt/liquid funds are not ranked the same way (strategic holdings)
- `43:13` Time-window choice: recent investors (<3 years) need shorter ranking windows
- `47:04` Portfolio optimize: full rebalancing (hard) or targeted switches; pick replacement by category or favourite schemes (e.g. move a pure-equity thematic holding to hybrid)
- `48:45` Submit -> old vs new portfolio analysis: holdings, correlation, transactions and short-term capital gains
- `49:55` Generate PDF and share with the client

**Checks and tie-outs**

- Use the detailed CAS (transaction-level) rather than the summary CAS
- Benchmark comparison and category rank must both fail before recommending exit
- Short-term capital gains / tax shown before switching
- Ranking window must fit the client's holding period

**Judgment calls**

- Suitability vs client's stated and required risk
- Exit vs hold for an underperformer, weighted by its portfolio impact
- Replacement scheme choice (advisor's preferred list)
- How to present findings to the client (doctor/blood-report analogy)

**Output:** Client-shareable PDF portfolio review: suitability verdict at asset-allocation, category and scheme level; folio-wise scorecard with highlighted problem schemes; proposed switches with old-vs-new portfolio comparison (holdings, correlation, short-term gains/tax impact, a cost/risk metric 3.44 -> 2.80)

**Why useful:** The most complete source-doc -> analysis -> client deliverable chain found for India; shows the practitioner's real inputs (detailed CAS), decision rules (quartile + benchmark), and the deliverable (PDF review with switch plan). Captions are Hindi/Hinglish auto-captions only (hi-orig); no English track.

### [B] How I Review My 2 Cr+ Mutual Fund Portfolio | Find Hidden Mistakes with this Tool

- **Link:** https://www.youtube.com/watch?v=A6-4rZEcK-8
- **Channel / length / uploaded / views:** Amit Upadhyaya / 18:04 / 2025-08-14 / 177,827
- **Persona:** Experienced individual investor / finance YouTuber reviewing his own Rs 2.08 crore MF portfolio (method intended for any investor or advisor)
- **Maps to:** #6 India AMC monthly portfolios (sector/market-cap look-through) + AMFI NAV/TER (returns, regular vs direct cost)
- **Transcript read:** yes

**Inputs**

- All MF holdings aggregated (SoA and demat) in the INDmoney app via phone-number sync (CAS-equivalent)
- Blended benchmark built from portfolio constituents; Nifty 50 / Midcap / Smallcap indices
- Fund-level performance vs benchmark and category; sector exposure

**Steps (timestamps from the transcript)**

- `03:04` Four questions: are returns beating benchmark? is asset and market-cap allocation right? which fund drags the portfolio? hidden sector risks?
- `05:17` Aggregate portfolio: Rs 60 lakh invested -> Rs 2.08 crore; app flags regular-plan funds
- `06:05` Portfolio XIRR since inception 16.89% vs blended benchmark 15.23%; vs Nifty 50 11.79%; slightly below Nifty Midcap; in line with Smallcap; repeat for 3y/1y/3m/1m
- `07:45` Asset allocation: 90-93% equity - acceptable because debt and gold are held outside MFs
- `09:22` Market-cap split: 37% large, 34% mid, 20% small; mid+small target 55% (moderate profile); rebalance toward large cap if it drifts >5 points (e.g. to 60%)
- `11:03` Fund-level: classify outperform / inline / underperform vs benchmark; none underperform, but an 'inline' Bandhan flexi-cap (14-15% vs portfolio 17% CAGR) drags returns after a fund-manager change
- `13:18` It is a regular plan paying ~Rs 44,000 commission; consistently in lower part of its category over 6m/1y/3y -> decision: exit and switch to a better flexi-cap
- `14:33` Sector exposure: financial services ~31% (>30% caution); HDFC Bank/ICICI Bank top weights - avoid adding the same stocks directly or via the replacement fund
- `16:08` Summarize answers to the four questions and the action plan

**Checks and tie-outs**

- Compare against a blended benchmark and several indices over multiple windows
- Fund return vs overall portfolio CAGR (does it drag?)
- Look-through sector concentration incl. direct equity holdings

**Judgment calls**

- Tolerance band for market-cap drift (5 points)
- Exit trigger: inline/underperforming + manager change + regular-plan commission
- Sector concentration threshold (~30%)

**Output:** Four-question portfolio verdict and action plan: portfolio beats blended benchmark; equity-heavy by design; market-cap mix within band; exit one underperforming regular-plan flexi-cap fund and switch; watch financial-services concentration

**Why useful:** Very clear decision rules a benchmark grader could check (blended-benchmark test, 55% +/-5 band, exit criteria, sector cap). App-driven rather than spreadsheet. Hindi auto-captions only.

### [B] Client Portfolio Review as Mutual Fund Distributor

- **Link:** https://www.youtube.com/watch?v=12U_M7zEL7I
- **Channel / length / uploaded / views:** MentorShobhit / 16:08 / 2024-12-15 / 1,183
- **Persona:** Trainer of mutual fund distributors (MentorShobhit) teaching the client portfolio-review routine
- **Maps to:** #6 India AMFI NAV (category quartile ranks computable from NAV history)
- **Transcript read:** yes

**Inputs**

- Client risk profile (aggressive/moderate/conservative) and agreed target allocation (e.g. 60 equity / 20 debt / 10 gold / 10 cash)
- Client's current allocation
- Quartile rankings by category from AdvisorKhoj (calendar-year quartiles)
- Client goal/life-event changes

**Steps (timestamps from the transcript)**

- `00:00` Purpose of review: performance check, keep/exit schemes, strengthen relationship, cross-sell/up-sell
- `04:30` Maintain risk-reward: asset allocation drives ~90% of returns
- `07:52` Start from risk profiling; set target allocation (example 60/20/10/10)
- `09:32` Compare current (55/25/10/10) to target; rebalance by booking profit in debt and moving it to equity ('asset re-allocation')
- `11:15` Scheme review: each scheme should be in its category's top quartile; judge only after at least one year
- `13:38` Use AdvisorKhoj quartile ranking page; sort by category
- `14:14` Keep a fund if top/upper-middle quartile in at least 2-3 of the last 3-4 years (e.g. JM Flexicap, HDFC Flexicap); otherwise consider replacement

**Checks and tie-outs**

- Target allocation sums to 100%
- Minimum one-year evaluation period
- Quartile consistency across years

**Judgment calls**

- Rebalance trades vs tax/exit load
- How many years of quartile slippage justify replacement
- Goal or family changes that alter the target

**Output:** Review conclusions: asset re-allocation trades (book profit in overweight debt, add to equity) and keep/replace decision per scheme based on quartile consistency

**Why useful:** Gives the MFD's standard operating rules (allocation drift, quartile consistency). Hindi auto-captions only.

### Gaps

The practitioner reviews are app-driven (INDmoney, FinApp, AdvisorKhoj) rather than spreadsheet-driven. All three best videos have only Hindi auto-captions. No video works directly from the AMC monthly portfolio Excel disclosures for overlap or look-through. Regular-to-direct switch economics (TER differences from AMFI) are discussed but never computed.

### Runners-up (metadata verified)

- C37brsKcJQ8 - SUBRAMONEY (P V Subramanyam), How to do a Client Portfolio Review? Transcript fetched, but the only caption track is a garbled Hindi auto-caption of English speech, so it was unusable (not rated)
- fs4ifurrXEw - Asset Wave, 5-point checklist to find bad mutual funds (metadata only; captions not yet available)
- WxoNEtQSxd4 - CA Rachana Ranade, portfolio overlap with AdvisorKhoj and theFundoo (metadata only)
- bn4e3CdDIxo - ET Money, how to reduce the number of funds (metadata only)

## 3b. India MF scheme analysis from AMC/AMFI data (holdings extraction, overlap, rolling returns vs benchmark, factsheet reading)

### Anatomy synthesized across the videos

**Inputs.** AMFI NAV history (growth option; regular plans give longer history), benchmark TRI series, and scheme holdings (aggregator pages or AMC monthly portfolio files).

**Steps.**
1. Extract holdings or NAV into the sheet (IMPORTHTML, macros, lookups) and handle missing dates.
2. Normalize NAV and compute rolling returns and rolling risk vs the benchmark.
3. Compute an outperformance-consistency statistic (share of windows beating the index).
4. Build SIP or lumpsum cash flows and compute XIRR per scheme and for the portfolio.
5. Run allocation sensitivity with a data table.
6. Compare holdings across funds for overlap.

**Deliverable.** Charts and statistics feeding a fund review or recommendation.

### [B] 1.8- Financial Modeling- Fund Selection Case study Using Excel- Feb Live Class

- **Link:** https://www.youtube.com/watch?v=1zHh9I1IKkg
- **Channel / length / uploaded / views:** Mentor Me Careers / 1:14:47 / 2021-04-24 / 338
- **Persona:** Financial-modeling instructor (Mentor Me Careers) running a live Excel case for finance trainees: fund selection on real NAV data
- **Maps to:** #6 AMFI NAV history (scheme NAVs) + NSE index data
- **Transcript read:** yes

**Inputs**

- ~3 years of daily NAVs for Franklin India Prima Plus (equity) and SBI Magnum Gilt (debt) - real data, with missing days
- SIP plan: Rs 15,000/month split 50/50; redemption date 14-Oct-2016
- Nifty index data for the second part (does the fund beat Nifty?)

**Steps (timestamps from the transcript)**

- `00:47` Task: using the NAV database, compute returns for each fund and the combined portfolio to the redemption date; fund selection should be data-based, not brand-based
- `02:31` Daily NAV sheet is given; first build a monthly date series for SIP dates
- `08:13` NAVs are not available for every date - lookup must handle gaps
- `19:33` Layout: a cash-flow column (monthly -7,500 investments, redemption value at end) and a portfolio-value line
- `28:46` VLOOKUP each SIP date into the NAV table (exact match, absolute ranges)
- `29:53` Monthly % change in NAV; portfolio value = prior value x (1 + change) + new instalment
- `36:01` Put the redemption value on 14-Oct as the final positive cash flow
- `37:26` Use XIRR (dates) rather than IRR; equity fund ~20.27%
- `39:57` Debug #NUM!: investments must be negative cash flows
- `57:31` Repeat for SBI Magnum Gilt (~12.8%)
- `58:40` Portfolio-level XIRR from combined cash flows (~17%); interpretation: debt half cost little return
- `61:29` What-if data table: portfolio XIRR across allocation splits (e.g. 90% equity ~20%)
- `69:26` Next session: risk measures (dispersion, standard deviation, limits of Sharpe/mean-based metrics) on the same data

**Checks and tie-outs**

- All inputs linked (no hard-coding) so data tables recalculate
- Sign convention for XIRR
- Duplicate/missing dates in the NAV series

**Judgment calls**

- Allocation split between equity and debt
- Whether XIRR alone is a sufficient selection criterion (risk to follow)

**Output:** Workbook with per-fund SIP schedules, XIRR per fund (~20.3% equity, ~12.8% gilt), portfolio-level XIRR (~17%), and a data table of portfolio XIRR vs equity/debt allocation (90% equity -> ~20%)

**Why useful:** A complete, real-data NAV -> SIP cash-flow -> XIRR -> allocation sensitivity workbook build, exactly the computational core of an India fund-comparison task.

### [B] Use this tool to compare mutual fund performance with benchmarks

- **Link:** https://www.youtube.com/watch?v=8oriyM8s-ew
- **Channel / length / uploaded / views:** freefincal - Prudent DIY Investing (freefincal) / 10:24 / 2019-04-25 / 4,322
- **Persona:** Independent India MF analyst / blogger (freefincal, M. Pattabiraman) - the tool he uses for his published fund reviews
- **Maps to:** #6 AMFI NAV (+ NSE TRI benchmark)
- **Transcript read:** yes

**Inputs**

- AMFI NAV history for the chosen scheme (growth option; regular plan for longer history; data from 3 Apr 2006)
- Benchmark index data (total-return index, e.g. Nifty 100 TRI)
- Rolling window length in days (e.g. 3 or 5 years) and start date

**Steps (timestamps from the transcript)**

- `01:38` Input sheet: follow steps 1-7, fill only green cells
- `03:17` Pick scheme by name; always choose growth option (dividend option distorts returns); regular vs direct plan choice
- `03:51` Pick benchmark index (about 60 available)
- `04:23` Download NAV and index data via macros
- `04:56` Set rolling window (days) and start date (default oldest AMFI date)
- `05:32` Review normalized growth (fund vs Nifty 100 TRI) and 5-year rolling returns
- `06:38` Review rolling risk: fund's rolling volatility should be below the index's
- `07:11` Analysis sheet: count of windows where fund outperformed index (1658/1987)
- `09:20` Workflow tip: run one fund at a time, screenshot results, repeat for the next fund

**Checks and tie-outs**

- Use growth option only
- Window end-date convention (date = end of rolling period)
- Two calculation methods give the same outperformance count

**Judgment calls**

- Which benchmark to use
- Window length
- Return consistency vs risk trade-off

**Output:** Normalized NAV vs index chart, rolling-return and rolling-risk charts, and consistency statistic (fund beat index in 1,658 of 1,987 windows, ~83%) used in his fund reviews

**Why useful:** Exactly the benchmark-comparison step of Indian scheme due diligence, driven by AMFI NAV data we can source.

### [B] How to extract a mutual fund portfolio to a spreadsheet

- **Link:** https://www.youtube.com/watch?v=7S0VFj05N9k
- **Channel / length / uploaded / views:** freefincal - Prudent DIY Investing (freefincal) / 15:59 / 2019-05-08 / 21,477
- **Persona:** Independent India MF analyst / blogger (freefincal) building a free portfolio-overlap tool
- **Maps to:** #6 India AMC monthly portfolios (here via Moneycontrol rather than the AMC Excel disclosure)
- **Transcript read:** yes

**Inputs**

- Scheme portfolio pages on Moneycontrol (full holdings table) identified by scheme code
- Scheme-code list scraped with a link-extractor browser extension

**Steps (timestamps from the transcript)**

- `04:32` Moneycontrol portfolio page has summary (market-cap split), top-10 and full-holdings tables
- `06:14` Google Sheets IMPORTHTML(url, "table", n) pulls the full-holdings table (table 5 by trial)
- `07:53` Repeat for each fund; compare common stocks with simple formulas
- `08:26` Excel route: recorded web-query macro, edited URL; Excel 2007/IE script errors forced workarounds
- `11:14` To make a general tool, build scheme-code list: extract all links from the AMC listing page, open as CSV, split URL by '/' to get codes

**Checks and tie-outs**

- Correct table index for full holdings
- Growth vs dividend plans share one portfolio

**Judgment calls**

- Data source choice (aggregator page vs AMC disclosure)
- Which funds to compare

**Output:** Full scheme holdings in a spreadsheet (one sheet per fund) ready for overlap comparison of up to five funds

**Why useful:** Shows the extraction step analysts actually do before overlap analysis and how brittle web sources are; our AMC monthly-portfolio files would replace the scraping.

### Gaps

Nobody downloads the AMC's own monthly portfolio Excel or AMFI TER files on camera. Overlap is shown only through third-party tools. Factsheet-reading videos (AMC CIO, PPFAS) explain fields but were not transcribed here.

### Runners-up (metadata verified)

- d9OU1LaymEA - Mutual Funds with Groww, How to Read a Mutual Fund Factsheet? ft. Shridatta Bhandwaldar (CIO Equities, Canara Robeco). Chapters cover rolling returns, top holdings, turnover, cash levels, TER and exit signals (metadata and chapters only; transcript blocked by YouTube's bot check)
- y_ZqDr_1yQM - PPFAS, How to Read a PPFAS Mutual Fund Factsheet (metadata only)

## 4. Private equity fund performance analysis for LPs (TVPI/DPI/IRR, fund evaluation, pacing)

### Anatomy synthesized across the videos

**Inputs.** Fund cash flows from capital account statements or quarterly reports: commitment, paid-in, distributions and NAV per fund. Also fee terms, the GP's deal-level track record (entry and exit, industry, size, realized or unrealized), and pacing assumptions (Takahashi-Alexander: fund life, bow, yield, growth).

**Steps.**
1. Establish fund age and strategy first.
2. Compute gross MOIC and IRR, then the fee and carry schedule (time-weighted fee allocation, MIN(0) guard on carry).
3. Compute net TVPI, DPI, RVPI and net IRR; check that RVPI = TVPI - DPI and that net is below gross.
4. Interpret against life-cycle stage. A DPI of 2x in year 6 of 10 is acceptable.
5. Challenge GP marks against public comps.
6. For new commitments, slice the track record by fund, industry, deal size and realized vs unrealized, and test concentration in single deals.
7. Make the yes/no commitment call with risk factors.
8. Run pacing: feed quarterly actuals into the T-A projection, re-forecast, and run variance vs the initial plan, by fund and by GP.

**Deliverable.** A performance table and memo, a commitment recommendation, and a pacing plan.

**Time.** AUXILIA estimates 5-6 hours to build 12 conventional net-IRR cash-flow models, versus about 10 minutes with the effective-hold formula.

### [B] PE Fund Performance Metrics: TVPI vs. MOIC vs. DPI and Gross vs. Net IRR

- **Link:** https://www.youtube.com/watch?v=bGhv_Kox5RA
- **Channel / length / uploaded / views:** Mergers & Inquisitions / Breaking Into Wall Street / 17:51 / 2026-01-21 / 5,581
- **Persona:** Financial-modeling trainer (Mergers & Inquisitions / BIWS) teaching PE fund performance analysis for funds-of-funds/secondaries roles
- **Maps to:** Pension PE quarterly reports (e.g. WSIB: commitment, paid-in, distributions, NAV, IRR, TVPI per fund)
- **Transcript read:** yes

**Inputs**

- Annual fund cash flows: invested capital per portfolio company, realizations, unrealized values
- Fund terms: 2% management fee on commitments in investment period then 1.5% on remaining cost; 20% carry

**Steps (timestamps from the transcript)**

- `00:32` Before metrics, establish fund life-cycle stage, strategy and valuation assumptions
- `01:40` Gross MOIC (~1.9x) = (realized + unrealized) / invested; gross IRR on gross cash flows
- `03:13` Management fees: 2% of commitments in investment period, then 1.5% of remaining cost basis (~$4.7bn) in year 6
- `04:17` Net value = gross value - realized and accrued carry; TVPI = net value / called capital (investments + fees)
- `05:25` Net IRR on net cash flows (always below gross); DPI = (realizations - distributed carry) / called capital
- `06:27` Interpretation: unknown valuation assumptions; DPI low but year 6 of 10; gross-net gap ~6-7 points normal; net IRR above long-run S&P but not by much
- `07:57` Allocate management fees to companies by time-weighted cost-basis share (~$62-63m to the exited company)
- `09:13` Carry per realized company = 20% x (realizations - investment - allocated fees), MIN(0,...) so losses do not create negative carry; accrued carry on unrealized pool, net of carry already paid
- `12:05` Build gross and net cash-flow rows; NAV = unrealized value - accrued carry; compute MOIC, IRR, TVPI, DPI, RVPI = TVPI - DPI
- `14:18` Complications: challenge GP marks (cut an 8-9x revenue multiple to 7-8x vs public comps), hurdle/catch-up waterfalls, recycling, clawbacks

**Checks and tie-outs**

- Net IRR < gross IRR once fees exist
- Carry sign/MIN(0) guard for losses
- RVPI = TVPI - DPI identity
- Sanity-check GP valuation multiples against public comps

**Judgment calls**

- Whether a low DPI is a red flag given fund age
- Haircutting GP marks
- Fee allocation method

**Output:** Excel schedule of gross MOIC/IRR, management fees, realized and accrued carry, net value, NAV, TVPI, DPI, RVPI, net IRR with interpretation (fund 'solid but not spectacular', DPI 2x acceptable in year 6 of 10)

**Why useful:** Gives the exact LP metric definitions, formulas and interpretive rules an LP analyst applies to quarterly PE program data.

### [B] PE Funds of Funds and Secondaries Case Studies: Full Prep Guide

- **Link:** https://www.youtube.com/watch?v=Md8aJNGavDo
- **Channel / length / uploaded / views:** Mergers & Inquisitions / Breaking Into Wall Street / 17:20 / 2025-12-10 / 4,838
- **Persona:** Financial-modeling trainer (M&I/BIWS) describing PE fund-of-funds and secondaries analyst case studies (pension/endowment/SWF allocators)
- **Maps to:** Pension PE quarterly reports (WSIB/CalPERS/CalSTRS fund-level data) - explicitly cited as the public data source for practice
- **Transcript read:** yes

**Inputs**

- GP track record: portfolio-company cash flows, entry/exit dates, deal size, industry, realized vs unrealized status across prior funds
- For LP-led secondaries: unrealized companies' financials, GP marks, business plans, bid price/discount and deferrals

**Steps (timestamps from the transcript)**

- `01:05` Why LPs do this: pensions/endowments/SWFs evaluate GPs' new funds; LPs sell stakes for liquidity/rebalancing
- `06:58` Primary fund case type 1: given cash flows, categorize and compute MOIC, IRR, net IRR, TVPI, DPI by company; recompute after an extra investment/distribution (XLOOKUP, SUMIFS, SUMPRODUCT, FILTER)
- `07:38` Case type 2: evaluate historical funds and make a yes/no recommendation on the new fund
- `08:10` Test consistency, stability and distribution of returns; avoid dependence on one sector, deal type or person; identify the GP's edge
- `09:13` Fund I/II IRRs 20-25%, MOIC 2.3-3.6x look good; Fund III too young to judge
- `09:46` Drill-down: strong in healthcare/consumer, weak in business services; deal size neutral; realized >> unrealized (less upside left); returns propped up by single 40%+ IRR deals -> list as risk factors
- `10:51` Other cuts: by team member, by sourcing (proprietary vs banker-led); real data is scarce - CalPERS/CalSTRS publish fund-level data
- `11:24` LP-led secondary: forecast unrealized companies, cut aggressive GP marks (car wash at 15x EBITDA -> 13.5x), deduct carry and fees, solve for price
- `13:01` Sensitize returns to exit timing and bid discount; recommend if ~20% net IRR and 2x TVPI are reachable

**Checks and tie-outs**

- Realized vs unrealized split
- Concentration of returns in a few deals
- GP marks vs public comps
- Sensitivity of net IRR/TVPI to exit timing and discount

**Judgment calls**

- Commit / do not commit to a new fund
- Which risk factors are disqualifying vs mitigable
- Price to bid for an LP stake

**Output:** Yes/no commitment recommendation on a new fund with risk factors; for secondaries, a price/bid-discount recommendation that meets ~20% net IRR / 2x TVPI targets with sensitivities

**Why useful:** Describes the LP analyst's due-diligence deliverable (commitment recommendation with risk factors) and the slicing they do; bridges W2 (manager selection) and W4.

### [B] Private Markes Pacing Model - Basic: Overview

- **Link:** https://www.youtube.com/watch?v=xtCXm7t8WZ0
- **Channel / length / uploaded / views:** IRRModels / 10:31 / 2025-04-14 / 656
- **Persona:** Private-markets modeler (IRRModels) presenting an LP commitment-pacing / cash-flow forecasting model
- **Maps to:** Pension PE quarterly reports (WSIB fund-level calls/distributions/NAV as the 'actuals' input)
- **Transcript read:** yes

**Inputs**

- Per-fund commitment and assumptions (fund life, Takahashi-Alexander 'bow', yield, growth) or manual call/distribution patterns
- Quarterly actuals per fund: capital calls, distributions, NAV
- GP/sponsor grouping

**Steps (timestamps from the transcript)**

- `00:00` Structure: green summary sheets, blue assumptions, one tab per fund, technical checks sheet
- `01:07` Fund tab: KPI summary, inputs, quarterly actuals input block (model is annual, actuals quarterly), standard pacing chart
- `01:39` Rolling forecast = actuals to date + re-projected future; initial projections retained for tracking; a transition block bridges actuals to projections
- `02:48` Choose call pacing (manual or curve) and distributions (manual or Takahashi-Alexander using fund life, bow, yield, growth)
- `03:55` Enter year-end actuals for 2025-2026; all actual cells must be populated (red warning); model re-forecasts when actual calls/distributions run faster
- `05:08` Charts: IRR to date and DPI; commitments, calls and total value
- `05:43` Projected/actual summary tabs: fund-by-fund overview, portfolio chart, cash flows by fund, grouping by sponsor to evaluate GPs
- `06:52` Variance analysis: initial projection vs actual calls, NAV, distributions, KPIs
- `08:03` Add a fund by duplicating a tab; checks sheet flags that the new fund is not mapped to a GP until rows are added

**Checks and tie-outs**

- All actuals populated
- Checks sheet: every fund mapped to a GP/summary
- Variance vs initial projection

**Judgment calls**

- Pacing-curve parameters (bow, yield, growth)
- How to blend actuals with projections
- GP grouping

**Output:** Portfolio-level projected and actual calls, distributions, NAV and KPIs (IRR to date, DPI, TVPI) by fund and by GP, plus variance analysis vs initial projections

**Why useful:** Commitment pacing is a recurring pension/endowment workflow; this shows the workbook anatomy (actuals + T-A projections + checks) a benchmark task could require.

### Gaps

No transcript shows a PME (Kaplan-Schoar or Long-Nickels) computed in a worked example. PitchBook's 4-minute explainer was not read. No video analyzes a real pension PE quarterly report such as WSIB's, although M&I points to CalPERS and CalSTRS fund-level disclosures as the practice data.

### Runners-up (metadata verified)

- e6YXKMN7_Hg - AUXILIA Mathematica, Private Equity Net Returns: The Effective Net IRR. Gross-to-net via fee and carry multipliers, effective hold = ln(MOIC)/ln(1+IRR), with explicit model-build time estimates (transcript read, B)
- JYnV96EFb-Q - M&I, Private Equity Fund Financial Statements: partners' capital split between LP and GP, unrealized and realized gains, carry (transcript read, B, also relevant to W6)
- JTTQd3jPvAk - PitchBook, Measuring fund performance: IRR vs PME (metadata only)

## 5. Pension / endowment asset allocation vs policy & quarterly performance review

### Anatomy synthesized across the videos

**Inputs.** The IPS with targets and min/max ranges, quarter-end market values by asset class and manager, net returns vs the policy benchmark, a public-market-equivalent mix (e.g. 65/35), peer universe ranks, lagged private-markets returns vs premium benchmarks (PE = public + 300 bp, real estate = ODCE + 100 bp), actuarial assumed return, capital-market assumptions from the last SAA study, and risk-model output.

**Steps.**
1. Market context.
2. Allocation vs targets and ranges, including look-through of equity exposure in infrastructure and real estate against the equity cap.
3. Total-plan return vs policy, PME, peers and the actuarial bogey.
4. Explain the gaps: manager selection, deviation from targets, and the mismatch between private-market and public benchmarks.
5. Asset-class and manager excess returns.
6. Risk: expected range vs actual, ex-ante volatility, active risk, and a risk-allocation view. At NYC Fire, public plus private equity drove 81% of risk.
7. Private-markets liquidity: unfunded commitments vs NAV, a pacing plan with conservative distribution assumptions, and the cash needed for benefit payments.
8. Report the rebalancing trades executed. At NYC Fire, ~2.5% moved from US equity to non-US, TIPS were exited, and $220m was raised for benefits.
9. Recommendation. Usually "no changes"; the bar for changing allocation is high.
10. The board votes to accept the report.

**Oversight variant (Texas PRB).** Compare many systems' returns with their assumptions and with a passive benchmark chosen by target return. Group by fiscal year-end, flag stale reporters, compute the "drift benefit" from lowering return assumptions, and reconcile expense definitions.

### [B] TRS Investment Meeting - March 5, 2026

- **Link:** https://www.youtube.com/watch?v=j0kgLzFNwfI
- **Channel / length / uploaded / views:** TRSNYC / 41:20 / 2026-03-10 / 111
- **Persona:** Public pension investment staff/consultant presenting the quarterly performance & risk review to a board (NYC Teachers' Retirement System, Bureau of Asset Management + consultant)
- **Maps to:** Pension PE quarterly reports (WSIB-style) for the private-markets section; plan-level allocation data from pension ACFRs
- **Transcript read:** yes

**Inputs**

- Quarterly performance report (net of fees) by asset class and manager sleeve; DC 'passport funds' report and monthly flash
- Strategic asset allocation targets and long-run capital-market assumptions from the last SAA review (2023)
- Policy benchmark, a 65/35 public-market-equivalent portfolio, and peer universe (TUCS)
- Private-markets returns lagged one quarter, from consultants
- Risk model output (ex-ante volatility, active risk, rate/spread duration)

**Steps (timestamps from the transcript)**

- `01:49` DC passport funds: Q4 final report, 1-year returns by fund, active sleeves lagged (low-quality rally), total assets $23.6bn; then January and preliminary February benchmark proxy
- `08:32` Market update; weekly rebalancing committee reviews active weights and cash needs; bar for recommending allocation change is high - none recommended
- `24:35` Compare realized asset-class returns with the long-run expected returns from the 2023 SAA (e.g. 6.7% Russell 3000; ~7% portfolio expected return)
- `26:50` QC incident disclosed: slides posted the night before referenced a different pension system (similar colour coding); corrected deck reposted
- `27:23` Growth of $1,000 at the 7% actuarial bogey ($1,967 over 10 years) vs actual portfolio (~$2,300, ~8.5% annualized)
- `28:29` Portfolio composition vs strategic targets: ~45% public equity, ~1/3 fixed income, rest alternatives; kept within ~1% of targets, checked weekly
- `29:05` Total plan Q4 return 2.2% slightly below policy benchmark, below 65/35 public-market equivalent and below TUCS peers
- `30:12` Explain gaps: manager selection, deviations from targets, and mismatch between public-market policy benchmarks and private-market pricing; actual equity exposure vs 65%
- `31:17` Public-markets returns by strategy (3 months to 10 years, net); excess returns: US equity tracking, developed ex-US lagging due to active managers
- `33:28` Alternatives lagged a quarter; PE vs public+300 bp benchmark shows red because public markets rallied; real estate vs ODCE (+100 bp); infrastructure and alt credit ahead
- `35:39` Risk: expected quarterly gain/loss range per strategy vs actual Q4 result (within range); ex-ante volatility 9.5% vs 10% for 65/35; active risk 1.8% tightly bounded

**Checks and tie-outs**

- Actual weights within ~1% of strategic targets (weekly)
- Total plan vs policy benchmark, vs 65/35 PME, vs peer universe
- Realized returns vs SAA capital-market assumptions and actuarial 7% bogey
- Actual quarterly return inside model-expected range
- Deck QC: correct plan's data/branding

**Judgment calls**

- Whether market events justify changing allocation (high bar; no change)
- How to attribute underperformance (manager vs allocation vs benchmark mismatch)
- How to frame PE underperformance vs public+premium benchmark

**Output:** Board deck/oral review: allocation vs strategic targets, total-plan return vs policy/PME/peers with explanations, asset-class excess returns, private-markets returns vs premium benchmarks, risk summary; no allocation change recommended

**Why useful:** Real deliverable anatomy for 'allocation vs policy review': targets, ranges, benchmarks, PME comparison, lagged private-markets, risk, and an explicit no-action recommendation. Shows the output side; the workbook is not shown.

### [B] Firefighters Pension Board Mtg June 4, 2024

- **Link:** https://www.youtube.com/watch?v=vW5U27MSX8I
- **Channel / length / uploaded / views:** City of Palatka Official Page / 1:33:27 / 2024-06-04 / 13
- **Persona:** Small public pension (Palatka firefighters) - investment manager/trust officer and investment consultant presenting quarterly policy review to the board
- **Maps to:** none directly (small-plan quarterly reports); comparable to pension ACFR allocation tables
- **Transcript read:** yes

**Inputs**

- Investment policy statement with target and min/max range per asset class (incl. infrastructure, convertibles, high yield, cash)
- Quarter-end market values and fiscal-YTD returns by asset class and fund vs benchmarks
- Peer ranking universe; actuarial assumed return (7.4%)

**Steps (timestamps from the transcript)**

- `18:15` Fixed-income manager: return vs benchmark (6.27% vs 6%), duration vs index (5.95 vs 6.11, effective high-6s), sector positioning
- `35:53` Policy review: actual allocation vs policy targets and ranges for the total fund
- `36:25` Everything within range; international at low end; overweight cash (earning ~5%) to stay under the policy equity cap; convertibles slightly overweight; core bonds slightly underweight
- `37:30` Corrects two typos in the policy-range table (infrastructure range 3-8 not 3.8; convertibles 2-8 not 6-10) and re-confirms compliance
- `38:06` Fiscal-YTD performance by asset class (equities +21.3%, high yield +7.59%) and market commentary
- `43:09` Holdings: equities 68% excluding infrastructure/real estate held elsewhere, ~75% including them - 'about as high as we want to go'
- `44:52` Board asks if comfortable with allocation; answer: no changes, stay overweight equities given expected returns
- `49:08` Consultant: 65% of assets indexed; quarter +5% (~$500k), 28th percentile peer rank; 1-year 13.1% net slightly behind index due to laggards
- `50:51` 5-year 7.1% net vs recently reset 7.4% assumed return; 10-year 6.3% net; assets $7.2m -> $10.3m
- `53:43` Infrastructure manager ~40% in utilities; 'I don't recommend any changes at this time'; motion to accept report

**Checks and tie-outs**

- Each asset class within policy min/max range
- Total equity exposure vs policy cap, including look-through of infrastructure/real estate
- Policy-range table itself verified (typos corrected)
- Returns vs benchmarks, peer percentile, and vs actuarial assumed return

**Judgment calls**

- Using cash overweight to stay under the equity cap
- Tactical underweights (international, core bonds) within ranges
- Whether to recommend changes (none)

**Output:** Quarterly investment review presented to the board: allocation vs policy ranges (all in range), returns vs benchmarks and peers, look-through equity exposure, and recommendation of no changes; board motion to accept

**Why useful:** Shows a real small-plan allocation-vs-policy compliance check, including a tie-out error in the policy table and look-through exposure vs cap. Captions are auto-generated; meeting also includes unrelated actuarial items.

### [B] 06-17-2024 Fire Pension Investment Meeting

- **Link:** https://www.youtube.com/watch?v=AdkKohRnP4o
- **Channel / length / uploaded / views:** NYC Investment Meetings / 1:21:44 / 2024-07-18 / 4
- **Persona:** Public pension investment staff (NYC Comptroller's Bureau of Asset Management risk head and asset-class leads) with consultants presenting the quarterly review to the fire pension board
- **Maps to:** Pension PE quarterly reports (WSIB-style commitments/unfunded/NAV by fund) and pension ACFR allocation tables
- **Transcript read:** yes

**Inputs**

- Risk-model output: forecast total risk (10.5%), active risk (1.8%), risk allocation by asset class, forecast return ranges vs realized quarter
- Strategic asset allocation (old and new SAA; 45% public equity, 26% alternatives in the old SAA) and market values
- Net returns by strategy vs policy benchmark, 65/35 public mix, TUCS peers and the 7% actuarial assumption
- Private-markets exposure: invested NAV vs unfunded commitments (PE ~$2.9bn = ~$1.8bn invested + ~$1.1bn unfunded); consultant (StepStone) pacing plan; distribution rates
- Quarter's rebalancing trades and benefit-payment cash needs

**Steps (timestamps from the transcript)**

- `02:15` Agenda reordered: risk presentation by the head of risk before the consultant's market update
- `11:06` Forecast 12-month total risk 10.5% vs 10.6% for a 65/35 market blend and slightly lower for the diversified policy benchmark; active risk 1.8%, roughly unchanged
- `13:20` Two views of allocation: market-value SAA vs risk allocation - public plus private equity drive ~81% of total risk
- `14:26` Check realized quarterly returns against forecast ranges at total, asset-class and manager level - 'nothing unusual'
- `16:39` Active-risk decomposition: private assets dominate because their benchmarks are not comparable; public fixed income and equity contribute little
- `18:40` PE liquidity: distributions slowed from ~20% to ~10% of the portfolio per year; holding periods lengthening; public equity book is ~6x the PE book
- `21:25` Excess return vs forecast: PE's large negative quarter is a lag/benchmark artefact after a strong public market, not a loss
- `54:23` Performance table: 5-year plan return 7.9% vs 7% assumed rate, below some benchmarks (policy 65/35, TUCS) while private assets ramp up; growth-of-$1,000 vs 7% line
- `55:28` Net public-market returns by strategy for the quarter (US equity +10%, developed ex-US +4%, EM +3%, fixed income mixed)
- `72:12` Net private-manager returns by year and 10-year; PE 1-year excess return negative vs Russell 3000 (+29.3%)
- `73:18` New exhibit: invested vs unfunded commitments by private asset class; consultant pacing modelled conservatively because distributions slowed; unfunded/NAV ratio stable
- `77:48` Quarter's rebalancing: mostly transition to the new SAA (private markets via pacing plan); sold ~2.5% US equity into non-US, divested TIPS, +1% high yield, raised $220m cash for benefit payments

**Checks and tie-outs**

- Realized returns within forecast risk ranges (total, asset class, manager)
- Plan vs policy benchmark, 65/35 PME, TUCS peers and 7% assumption
- Unfunded commitments vs NAV and pacing vs slower distributions
- Cash raised to cover benefit payments

**Judgment calls**

- Interpreting PE underperformance vs public benchmarks in a strong market
- How conservatively to model distributions in the pacing plan
- Where to source rebalancing and benefit cash during an SAA transition

**Output:** Quarterly board review: risk and performance within expected ranges, plan vs policy/PME/peers/7% bogey, private-markets exposure and pacing commentary, and a log of rebalancing actions (shift ~2.5% from US equity to non-US, exit TIPS, +1% high yield, raise $220m for benefits)

**Why useful:** Covers the parts of the asset-owner review other videos skip: risk-based allocation view, private-markets unfunded/pacing liquidity, and the actual rebalancing trades and cash raise. Deliverable side only; auto-captions are noisy.

### Gaps

All three videos show the deliverable, not the analyst building the allocation-vs-policy workbook. Asset-owner rebalancing appears only as a summary of trades already executed (NYC Fire). How they were sized, which managers funded them, and the private-markets denominator effects are never worked through. No endowment or foundation example was found; IRS 990-PF-style foundation investment review has no YouTube analogue in this search.

### Runners-up (metadata verified)

- 1IjwTE58lt0 - City of Austin ERS, 2026 COAERS Member Summit State of the Pension Fund (metadata only)

## 5b. Pension oversight variant: cross-system review of returns vs actuarial assumptions, passive benchmarks and expenses (state regulator)

### Anatomy synthesized across the videos

**Oversight analyst workflow (Texas PRB).**
1. Collect each system's annual returns by fiscal year-end, its actuarial assumed return now and 10 years ago, its broad asset allocation, and investment expenses (SB 322 definition including carry and profit share, vs the audited figure).
2. Compare returns with the assumption.
3. Add a passive benchmark chosen by target return (60/40, 50/50 or 40/60).
4. Group systems by fiscal year-end so the comparisons are apples to apples, and flag lagging reporters.
5. Compute a "drift benefit" that separates real outperformance from lowered assumptions.
6. Show the expense ratio. High cost with low return is the red flag.

**Deliverable.** A single cross-system Investment Data Report for the board.

### [B] September 30, 2026, Investment Committee Meeting

- **Link:** https://www.youtube.com/watch?v=QDPTJXTwDKY
- **Channel / length / uploaded / views:** Pension Review Board / 1:13:25 / 2026-09-30 / 66
- **Persona:** Oversight analyst at the Texas Pension Review Board presenting the cross-system Investment Data Report redesign to the board's investment committee
- **Maps to:** Public pension filings (ACFR-type data, analogous to WSIB reports); IRS 990-PF style cross-entity comparison for foundations
- **Transcript read:** yes

**Inputs**

- Returns reported by Texas public retirement systems (annual, by fiscal year-end) and their actuarial assumed returns (current and 10 years ago)
- Asset-allocation data from audits/filings (often only broad classes)
- Investment expenses under SB 322 (incl. indirect fees, carried interest/profit share) vs audited investment expense
- Passive benchmark index series (60/40, 50/50, 40/60; 1976-2025 statistics)

**Steps (timestamps from the transcript)**

- `01:22` Update: most reporting systems now beat or are within 1% of their actuarial return assumption; only ~10 more than 1% below
- `03:51` Proposal: add benchmark context - option 1 passive blend incl. real estate/commodities, option 2 simple stock/bond blend, option 3 asset-class-weighted benchmark (needs detailed allocation data most systems do not report)
- `07:33` Committee debate: 60/40 vs 50/50 vs 40/60 depending on a plan's target return and maturity
- `13:59` Report redesign: consolidate columns (annual audit expense vs SB 322 expense), add benchmark columns
- `14:36` Group systems by fiscal year-end so 1/3/5/10-year returns are comparable; flag systems lagging in reporting (stale 2024 data next to 2025)
- `17:08` New 'drift benefit' metric: how much of apparent outperformance comes from lowering return assumptions over 10 years (e.g. from 7.8%)
- `20:51` Long-run benchmark stats pulled live: 60/40 10.13% annualized vs 50/50 9.59% (1976-2025) with drawdowns; committee picks 50/50
- `26:07` Expense ratio retained: high expenses with high returns acceptable, high expenses with low returns not
- `31:52` Takeaways: add benchmark and drift-benefit columns; keep a single report; present at December board
- `32:33` Member caveat: lowering the assumption while keeping the same allocation means the same risk now 'beats' a lower bar

**Checks and tie-outs**

- Comparable fiscal year-ends before comparing multi-year returns
- Stale/late reporting flagged
- Expense definitions reconciled (audit vs SB 322 incl. carry)
- Benchmark choice consistent with each system's target return

**Judgment calls**

- Which passive benchmark fairly represents a plan
- Whether outperformance vs assumption is real or from lowered assumptions
- Report concision vs completeness

**Output:** Redesigned Investment Data Report for the full board: per-system returns vs assumption and vs a passive benchmark chosen by target return, systems grouped by fiscal year-end with stale/lagging reporters flagged, a 'drift benefit' metric for lowered assumptions, and expense ratios

**Why useful:** Shows an oversight analyst's cross-sectional asset-owner review (returns vs assumptions vs passive benchmark, expenses, data staleness) - a natural benchmark task over many public filings. Captions are partly garbled.

### Gaps

Only one video. The analyst's dataset build is described, not shown. It is a good template for a multi-entity task over public filings (pension ACFRs, or IRS 990-PF for foundations).

## 6. Fund accounting: NAV calculation and custodian reconciliation (fund administrator)

### Anatomy synthesized across the videos

**Inputs.** Fund-accounting ledger (positions, cash by currency, accruals), custodian statements, investment-manager instructions, broker statements for derivatives, corporate-action and withholding-tax vendor data, capital-stock activity from the transfer agent, and a trial balance.

**Steps (daily or NAV cycle).**
1. Confirm that prior-day FA and custodian balances agree.
2. Reconcile positions by security, then income accruals before the pay date, then cash line by line by currency.
3. Classify each break: timing (contractual vs actual settlement), failed trade, missing IM instruction, FX rate or date, asset set up in a different currency, corporate action, withholding tax, cancelled dividend, late instruction after the NAV cut-off.
4. Comment and chase each break the same day; ageing breaks become backlog.
5. Value positions at fair value and book accruals and expenses.
6. Confirm the balance sheet ties. A missing cash line blocks the NAV.
7. Strike NAV = (assets - liabilities) / units.
8. Test the high-water mark before accruing an incentive fee.
9. Book capital-stock activity at the correct NAV.
10. Assemble the NAV pack for reviewer and fund-manager sign-off.

**Deliverable.** Reconciled books, NAV per unit, and the NAV package.

### [B] Fund Accounting: NAV & HWM Calculation Process/Fund accounting end-to-end NAV calculation example

- **Link:** https://www.youtube.com/watch?v=JZPV88cTbZk
- **Channel / length / uploaded / views:** GMT Academy-Learning First / 1:07:46 / 2023-03-15 / 10,249
- **Persona:** Fund-accounting trainer (GMT Academy) working a live NAV and high-water-mark example with trainees, then outlining the NAV package
- **Maps to:** none (synthetic trial balance); positions could be seeded from SEC N-PORT
- **Transcript read:** yes

**Inputs**

- Trial-balance-style list of fund assets and liabilities for an existing multi-class fund (equity at book and market value, T-bills, investment in a master fund 57,800, prepaid fees)
- Net loss for the period; units outstanding; base high-water-mark NAV

**Steps (timestamps from the transcript)**

- `00:01` Read the case: identify all asset types, compute total assets, then NAV per share; multi-class (A-D) existing fund
- `03:21` High-water mark defined on a base price; no incentive fee unless NAV exceeds it
- `04:59` Line 1: equity investment - choose market (fair) value over book value; record the change through P&L (FVTPL)
- `09:58` Add T-bill / government-security investments and subtotal the investment lines
- `11:38` Add investment in master fund (57,800) and prepaid fees as assets
- `13:37` Book the net loss (debit losses) and absorb it in shareholders' equity
- `18:47` List liabilities and outstanding unit capital
- `23:47` Assets and liabilities do not tie -> question the missing cash-at-bank component before striking NAV
- `27:10` Rule: do not compute NAV per share while the balance sheet is out of balance
- `32:22` NAV per unit = (total assets - total liabilities) / units outstanding
- `34:03` Quarterly HWM test: NAV (gross asset value 2,231.75) far below base -> no incentive fee, no crystallization
- `42:44` Allocate losses to existing unit holders
- `59:40` NAV package components: capital stock activity (subscriptions/redemptions), trade processing/settlement, corporate actions, income distribution, reconciliations, fund set-up

**Checks and tie-outs**

- Balance sheet must tie before NAV is struck (find missing cash)
- Fair value used for listed investments
- HWM comparison before accruing incentive fee

**Judgment calls**

- Book vs market value treatment
- Where to absorb the period loss
- Whether incentive fee crystallizes

**Output:** Total assets, total liabilities, NAV per unit, and incentive-fee/crystallization conclusion (NAV below HWM -> no incentive fee; losses allocated to unit holders)

**Why useful:** Only video found that walks a numeric NAV strike with a tie-out failure and HWM test; long, classroom-style and partly off-topic in the second half.

### [B] Cash Reconciliation

- **Link:** https://www.youtube.com/watch?v=HuMT8inUjJs
- **Channel / length / uploaded / views:** The Fund Accountant / 20:43 / 2022-09-10 / 43,655
- **Persona:** Fund accountant (The Fund Accountant channel) explaining daily cash reconciliation between fund accounting, custodian and investment manager
- **Maps to:** none (needs synthetic custodian vs ledger files); N-PORT holdings could seed positions
- **Transcript read:** yes

**Inputs**

- Fund-accounting cash ledger by currency (contractual settlement basis)
- Custodian cash statement by currency (actual settlement basis)
- Investment-manager instructions (trades, FX contracts, expenses); corporate-action and dividend data

**Steps (timestamps from the transcript)**

- `00:32` Define parties: fund accounting vs custody (internal or external), sometimes three-way with the investment manager
- `01:38` Why breaks arise: FA books on contractual dates (trade T+2, dividend pay date) while custody books only on actual cash movement
- `04:25` Research and comment every break the same day; un-researched breaks become aged backlog
- `06:04` Reconcile each currency balance separately (USD base plus GBP, AUD, INR...)
- `06:37` Dividend payment breaks: query custody after the team's waiting period (1-3 days)
- `07:42` Failed/late trade settlement breaks: confirm custody is chasing the broker
- `09:22` Currency-contract breaks: IM failed to instruct custody; ask IM or send instruction
- `10:29` FX-rate breaks: contract booked on different dates/rates; verify your own booking before blaming custody
- `14:20` Asset set up in different currency at FA vs custody -> offsetting breaks in two currencies; resolve by dummy FX or settlement-currency change per team practice
- `16:30` Corporate-action cash (reclaims, tenders): check receivable bucket before posting to avoid double counting
- `18:10` Expense payments instructed only to custody: reduce accrual and book payment when custody processes
- `18:56` Daily method: confirm prior-day balances agree, list today's settling items (trades, dividends, capital activity) and match line by line

**Checks and tie-outs**

- Prior-day FA vs custody cash agree before working today
- Line-by-line match of settling trades, income and capital activity
- Per-currency balance agreement
- Receivable bucket checked to avoid double-booking reclaims
- Break ageing / follow-up cadence

**Judgment calls**

- Who is wrong (FA or custody) on FX/booking breaks
- How long to wait before chasing
- Which resolution entry matches team practice

**Output:** Daily cash reconciliation by currency with every break researched, commented and followed up (chasers to custodian/IM) so the NAV can be struck on clean books

**Why useful:** Precise catalogue of break types and the daily matching procedure - directly convertible into a reconciliation task with planted breaks.

### [B] Position and Income Reconciliation

- **Link:** https://www.youtube.com/watch?v=I5NuvmTP-E4
- **Channel / length / uploaded / views:** The Fund Accountant / 14:43 / 2022-09-17 / 20,779
- **Persona:** Fund accountant (The Fund Accountant channel) explaining position and income reconciliation
- **Maps to:** none (synthetic); positions could be seeded from SEC N-PORT holdings
- **Transcript read:** yes

**Inputs**

- FA holdings by security/asset line; custodian holdings; IM instructions
- Broker statements for futures/options
- Dividend accruals (receivables) at FA and custody; ex-date trades; withholding-tax data from third-party vendors

**Steps (timestamps from the transcript)**

- `00:20` Position recon: holdings FA vs custody (or vs IM), same treatment for all parties
- `01:02` Trade breaks: missed cancellation, duplicate booking - show in positions before cash (T+2)
- `03:04` Corporate-action breaks (rights, spin-offs, mergers) from different dummy-line treatment
- `03:52` Asset-line set-up differences between FA and internal custody
- `05:28` Futures position breaks: request broker statement; late instructions after NAV cut-off booked next day and commented
- `08:04` Income recon at accrual stage (receivables) to pre-empt cash breaks
- `09:17` Ex-date trade breaks: entitlement on pre-trade vs post-trade shares; verify full amount at payment (e.g. $85 received vs $100 due)
- `10:55` Withholding-tax breaks: confirm taxability from external vendor; escalate to reviewer
- `12:09` Cancelled dividends: custody drops accrual; FA must verify with vendor and reverse, else it becomes a cash break

**Checks and tie-outs**

- Holdings agree by security
- Accruals agree before pay date
- Payment equals entitlement
- Withholding tax consistent with vendor data
- NAV cut-off for late instructions

**Judgment calls**

- Escalation to reviewer/senior on tax treatment
- Comment vs correct a justified break

**Output:** Position and income reconciliations with commented breaks (trade, corporate action, asset line, futures, ex-date, withholding tax, cancelled dividend) prior to NAV sign-off

**Why useful:** Completes the reconciliation rule set (positions + income) needed to design a NAV-pack task.

### Gaps

No video builds a full NAV pack in Excel from source files. The reconciliation videos are whiteboard explanations, and the NAV example is a classroom exercise. Price-variance and stale-price checks are absent, and so are fund-administrator tooling demos (e.g. Geneva or Investran). India mutual-fund NAV/TER accrual mechanics were not found.

### Runners-up (metadata verified)

- YgIaLTKIwNk - GMT Academy, capital-stock activity, NAV calculation and NAV package. Subscriptions and redemptions must be booked at the correct NAV, plus TA reconciliation (transcript read, C)
- SYOhQ6weFOY - Sushila Hariharan, Hedge funds: investor allocations vs unitisation (transcript read, C)
- OWSSOt9plYg - The Fund Accountant, How to calculate NAV (metadata only)

## Cross-cutting lessons for benchmark design

### 1. Practitioners tie out before they analyze

Every serious workflow starts by reconciling inputs to a source of truth:

- Account totals are matched to the custodian (rebalancing).
- The detailed CAS is used rather than the summary CAS (India reviews).
- Prior-day cash and positions must agree before today's breaks are worked (fund accounting).
- The balance sheet must tie before NAV is struck.
- Policy-range tables are corrected before compliance is asserted (pension).

Benchmark tasks should plant input inconsistencies (missing cash in a lot file, stale fiscal year-ends, a typo in the policy range) and grade whether the agent catches them.

### 2. Deliverables are decisions with thresholds, and "no action" is a common correct answer

The thresholds used are explicit:

- Rebalancing bands (5/25 rule, 20% relative band, mid+small cap at 55% ±5).
- Watch-list rules (top-quartile category rank in 2 of the last 3-4 years, fi360 top 25%).
- Exit triggers (fails both the benchmark and category-rank tests, manager change, regular-plan commission).
- PE commitment targets (about 20% net IRR and 2x TVPI).
- Pension allocations kept within about 1% of targets or within the policy min/max.

Several real reviews end in "no changes recommended". Grading should reward a correct no-trade or no-change conclusion, not only activity.

### 3. Cost and tax layers are where the expertise shows

- Practitioners compare a trade-everything variant with a buy-only variant (avoid realizing gains) and with tax-neutral loss harvesting.
- They look through fund-of-funds to the underlying expense ratios.
- They add the advisory fee to the fund's TER.
- They separate SB 322 investment expense, which includes carry, from audited expense.
- They compute a gross-to-net bridge (fees and carry) for PE.

Tasks should require these layers, not just headline returns.

### 4. Benchmarks and time windows are judgment calls the analyst must justify

Examples seen:

- Blended benchmark vs Nifty 50 for a multi-cap portfolio.
- Total-return index for rolling returns.
- Policy benchmark vs a 65/35 public-market equivalent vs a peer universe vs the 7% actuarial bogey.
- PE vs public + 300 bp, lagged one quarter.
- 60/40 vs 50/50 chosen by a plan's target return.
- Fund age (DPI of 2x in year 6 of 10 is fine).
- Ranking windows that suit the client's holding period.

A good task gives the agent several plausible benchmarks and grades the stated rationale.

### 5. The real input formats are messy exports

- Schwab tax-lot CSVs without cash.
- CAMS/KFintech CAS PDFs.
- AMFI NAV text files with missing dates.
- Moneycontrol HTML tables.
- Custodian and fund-accounting cash ledgers by currency.
- Quarterly PE actuals (calls, distributions, NAV) per fund.

Our sources map cleanly:

| Source | What it feeds |
|---|---|
| #6 AMFI NAV/TER plus AMC monthly portfolios | India scheme analysis and client reviews (holdings look-through, overlap, rolling returns, regular-vs-direct cost) |
| #5 N-PORT | Fund-of-funds and holdings look-through, attribution weights, and seed positions for NAV/reconciliation tasks |
| Pension PE quarterly reports (WSIB) | LP metrics, pacing actuals, and unfunded-vs-NAV liquidity |
| Pension filings and #7 990-PF | The cross-entity oversight variant (5b) |

### 6. Human time scale

These are minutes-to-hours tasks per client or fund, repeated across a book. Evidence:

- The rebalancing calculator is run live in a client meeting.
- Parsing a CAS takes 7-10 minutes, then the review is a meeting.
- The trainer says the NAV/SIP case "takes half an hour".
- AUXILIA estimates 5-6 hours to build 12 conventional net-IRR models.
- Reconciliation is daily and break-driven.
- Quarterly pension reviews are 40-90 minute board sessions backed by weeks of staff and consultant work.

A long-horizon task can chain them: holdings ingest, then tie-out, then analysis, then the decision memo or trade file.
