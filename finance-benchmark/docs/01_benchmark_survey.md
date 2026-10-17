# Survey: Finance, Accounting and Spreadsheet Agent Benchmarks (2023 to Oct 2026)

Purpose: background for designing a new long-horizon finance agent benchmark.
Compiled: 2026-10-17.

## How this was compiled

- **Sources.** Most facts come from arXiv abstract and HTML pages, which were fetched directly, plus a few GitHub and Hugging Face cards.
- **Blocked sites.** These could not be reached from this sandbox: vals.ai, accounting.penrose.com, spreadsheetbench.github.io, shortcut.ai, benchmarklist.com, benchlm.ai, aclanthology.org and stuut.ai. For those benchmarks, details come from search-engine snippets or secondary coverage and are marked **(unverified)**.
- **Model names.** Names such as "Claude Fable 5", "GPT-5.6 Sol" and "Muse Spark" are given exactly as the cited papers report them.
- **Trajectory length** means agent steps, LLM calls or tool calls per task, where the paper reports them. "n/r" means the paper does not report it.

---

## 1. Landscape matrix

Legend:
- **Env:** QA = QA over provided docs; RAG/Web = retrieval or web search; Sheet = spreadsheet manipulation; Tool/API = tool or MCP environment; FS = sandbox with file system and office apps; GUI = computer use; Sim = simulator.
- **Data:** R = real; S = synthetic; R→S = real-derived but transformed or anonymized.
- **Eval:** EM = exact match; Cell = cell-level comparison; Rubric = weighted binary criteria; LLM-J = LLM judge; Agent-J = agentic judge that opens files; State = deterministic final-state or DB check; Econ = economic outcome metric.

### 1a. Spreadsheet and financial-modeling deliverables

| Benchmark | Year / venue | Focus | Data | Env | Trajectory length | Eval | Size |
|---|---|---|---|---|---|---|---|
| SpreadsheetBench v1 | NeurIPS'24 D&B | Excel forum Q&A manipulation | R (4 Excel forums) | Sheet (code gen) | 1 to 5 rounds | Cell, OJ-style (3 test cases per item) | 912 instr. / 2,729 cases |
| SpreadsheetBench Verified | Dec 2025 (Shortcut + authors) | Cleaned v1 subset | R | Sheet | n/r | Cell | 400 |
| **SpreadsheetBench 2** | arXiv 2606.29955 (Jun 2026) | End-to-end business workbooks: modeling, debugging, template, charts | R (filings/reports; expert-built gold workbooks) | Sheet + bash (SWE-agent), no network | ≤50 turns; ~594 cells modified; 11.8 sheets | Cell (modification %, all-cell accuracy) + VLM rubric for charts | 321 |
| SheetCopilot | NeurIPS'23 | Atomic spreadsheet control | R-ish (curated) | Sheet (atomic actions) | short | Automated checks | 221 |
| SheetAgent / SheetRM | WWW'25 | Long-horizon, reasoning-dependent manipulation | R-ish | Sheet | n/r | Pass rate | n/r |
| MBABench | arXiv 2605.22664 (May–Aug 2026) | Finance spreadsheet builds (3-statement, valuation, FP&A…) | R (FMWC, ModelOff, Wall Street Prep) | Sheet / GUI (Excel add-ins) / code agents | n/r (completion time only) | Rubric + LLM-J (Accuracy, Formula, Format) | n/r (18+ agents) |
| BlueFin | arXiv 2605.30907 (May 2026) | Finance workbook synthesis, manipulation, interrogation | R (78 finance pros; seed workbooks) | Sheet (20 tools, LibreOffice recalculation) | 24–38 turns | Rubric + Agent-J, incl. **perturbation tests** | 131 tasks / 3,225 criteria |
| Finch (FinWorkBench) | arXiv 2512.13168 (Dec 2025–2026) | Real F&A spreadsheet workflows | **R, messy** (Enron emails and spreadsheet versions, EUSES, government reports) | Sheet / product agents | median 14–16 tool calls (6–107); ~17 min | Human pass/fail + LLM-J | 172 workflows / 384 tasks / 1,710 sheets |
| WTMBench | arXiv 2608.07873 (2026) | Formulas, charts, pivots, conditional formatting | R (public workbook corpora) | Sheet | multi-step (n/r) | Output vs. "future" workbook | 150 |
| **BankerToolBench** | arXiv 2604.11304 (Apr 2026) | Junior IB deliverables (DCF, LBO, comps, decks) | R (banker-written; market-data, EDGAR and profile APIs) | FS + 3 MCP tools, offline | **up to 539 LLM calls**; humans ~5 h (max 21 h) | ~150-criterion Rubric + Agent-J ("Gandalf") | 100 |
| **FrontierFinance** | arXiv 2604.05912 (Apr 2026) | Build 3-statement, LBO, DCF, merger and lender models from scratch | R (SEC filings) | **GUI** + bash (Firefox, LibreOffice) | 122–302 messages; 3–28M tokens; humans 18.3 h | Rubric (≤140 criteria, gating) + human graders + LLM-J | 25 |
| APEX-Agents (v1 / 1.1) | arXiv 2601.14242 (Jan 2026); 1.1 Sep 2026 | IB, consulting and law tasks in simulated "worlds" | S/R (expert-built worlds; Box-like FS) | FS + apps (mail, chat, sheets, docs, EDGAR…) | e.g. 92 steps avg (Kimi K2); 250-step timeout | Rubric + LLM-J, Pass@1 | 480 tasks / 33 worlds (v1); 240 / 31 (1.1) |
| GDPval (finance occupations) | arXiv 2510.04374 (Sep 2025) | 1-shot deliverables, incl. 5 finance occupations + accountants | R (expert work products) | Files in, files out | 1-shot; humans ~6.7 h avg | Blinded pairwise expert comparison | 1,320 (220 gold) |
| FinanceQA | arXiv 2501.18062 (Jan 2025) | Analyst calculations (hand-spreading, adjusted EBITDA) | R (mainly Costco FY24 10-K) | QA | 1-shot | EM | 148 |

### 1b. Accounting operations, audit, tax and payments

| Benchmark | Year / venue | Focus | Data | Env | Trajectory length | Eval | Size |
|---|---|---|---|---|---|---|---|
| **AccountingBench** (Penrose) | Blog, Jul 2025 | Close the books monthly for 1 real SaaS company over 1 year | **R** (Stripe, Ramp, Mercury, Rippling) | Tool/API (SQL ledger, Python, recon tool) | **12 sequential months**, context reset each month | Statement accuracy vs. CPA + automatic recon validation | 1 company (unverified details) |
| **APEX–Accounting** | arXiv 2607.27189 (Jul 2026) | Reconciliation, data entry, variance analysis, schedules and accruals | S (expert-specified worlds "frozen at month-end close") | FS + 91 tools (QuickBooks-like, mail, Excel, PDF) | cap 500 steps / 5M tokens; e.g. 41 tool calls | Rubric (13.7 criteria per task) + LLM-J, Pass^k | 160 tasks / 10 worlds |
| FinBalance | arXiv 2606.15949 (Jun 2026) | Source docs → cited journal entries → balance sheet | S (deterministic generator) | QA / structured output | n/r | **EM on final balance sheet + ledger replay (BS_recon)** | 710 eval records |
| FinMaster | arXiv 2505.13533; Findings ACL'26 | Literacy, accounting, auditing, consulting | S (FinSim ledgers) | QA | multi-step calculations | EM (JSON) | 183 tasks |
| CFAgentBench | arXiv 2606.22000 (Jun 2026) | Construction-finance CFO/controller across ERP, payroll, banks | S (35 simulated apps reconciled to a ledger) | Tool/API | n/r | State (functional), pass^k; money-movement must pause for approval | 1,014 specs; 40 runnable |
| FinalityBench | arXiv 2609.04706 (Sep 2026) | Ship, refund or wait under delayed payment finality | S (faulted 4-system event streams) | Sim | episode | **Econ (effect-level money)** + twin pairs | 321 tasks |
| DABStep | arXiv 2506.23719 (Jun 2025) | Payments-ops data analysis (fees, rules) | R (Adyen-derived) | Code + docs | multi-step | EM | ~450 |
| FinAuditing | arXiv 2510.08886 (Oct 2025) | XBRL cross-document consistency | R (XBRL US error messages, 372 cos.) | QA (long context, ~33k tokens) | 1-shot | EM / F1 | 1,102 |
| FinTagging | arXiv 2505.20650 (May 2025) | XBRL fact extraction + US-GAAP concept linking | R | QA | 1-shot | F1 | n/r |
| AuditBench | AAAI'25 workshop | Statement error detection, standard citation | R tables + S transactions | QA | 1-shot | mixed | n/r (unverified) |
| TaxCalcBench | arXiv 2507.16126 (Jul 2025) | US federal personal tax returns | S (verified by tax engine) | QA | 1-shot | EM vs. tax engine | n/r (small) |
| CARB (Stuut) | 2026 blog | Collections / AR | S (58 fictional ledgers) | Tool | n/r | 969 binary criteria | 168 (**unverified**) |

### 1c. Financial research, QA and retrieval

| Benchmark | Year / venue | Focus | Data | Env | Trajectory length | Eval | Size |
|---|---|---|---|---|---|---|---|
| FinQA / TAT-QA / ConvFinQA | EMNLP'21 / ACL'21 / EMNLP'22 | Numerical reasoning over table + text | R (10-K excerpts; hybrid reports) | QA | 1-shot (ConvFinQA: multi-turn) | EM / program accuracy | ~8.3k / ~16.5k / ~3.9k conversations |
| DocFinQA | ACL'24 | FinQA questions over full 10-Ks (~123k words) | R | QA (long context) | 1-shot | EM | ~7.4k |
| FinanceBench | arXiv 2311.11944 | Open-book QA over 10-K/Q/8-K | R | RAG | 1-shot | Human review | 10,231 (150 open) |
| BizBench | ACL'24 | Program synthesis, quantity extraction, finance knowledge | R + S | QA | 1-shot | EM | 8 tasks |
| SEC-QA | arXiv 2406.14394 | Refreshable multi-document question generation | R (EDGAR) | RAG | multi-hop | EM | generator |
| Fin-RATE | arXiv 2602.07294 | Single-filing, cross-company and **longitudinal** SEC reasoning | R | RAG | multi-doc | LLM-J / EM | n/r |
| **Finance Agent Benchmark** (Vals) | arXiv 2508.00828 | Analyst research with EDGAR and web tools | R (expert Qs on recent filings) | Tool/API (search, EDGAR, parse) | 3.5–12 turns; 1.7–25 tool calls | Rubric + LLM-J + contradiction check | 537 (50 public) |
| Finance Agent v2 (Vals) | 2026 | Adds comps, precedents, earnings, disclosure, modeling | R | Tool/API | n/r | n/r | n/r (**unverified**; top ~58–61%) |
| IPO Finance Agent | arXiv 2606.23032 | S-1 IPO diligence (SpaceX) | R | RAG + tools | n/r | Auto-generated rubrics + LLM-J | 1,000 (70 public) |
| FinSearchComp | arXiv 2509.13160; ICLR'26 | Live, historical and complex data fetching | R (Global + Greater China) | Web / plugins | n/r | LLM-J with tolerance bands | 635 |
| FinDeepResearch | arXiv 2510.13936 | Full equity-research report, 8 markets, 4 languages | R | Web / deep research | long (report-level) | HisRubric (15,808 items) + LLM-J | 64 companies |
| FinResearchBench (I / II) | arXiv 2507.16248; 2607.12252 | Research reports; logic-tree agent-as-judge | R | Deep research | long | Agent-J | 70 Qs (I) |
| FinGAIA | arXiv 2507.17186 | Chinese finance GAIA-style tasks (7 sub-domains) | R | Web + files + code | ~5 / 7 / 10 steps by level | Human + LLM-J | 407 |
| BizFinBench (v1 / v2) | arXiv 2505.19457; 2601.06401 | Chinese/US business-finance QA, plus online trading/allocation | R (real user queries) | QA + online tasks | 1-shot | IteraJudge (LLM-J) / EM | 6,781 / ~29k |
| FinBen | NeurIPS'24 D&B | 24 tasks / 42 datasets, incl. a trading agent | R | QA + Sim | mostly 1-shot | Task metrics | 42 datasets |
| EDINET-Bench | ICLR'26 | Japanese filings: fraud, earnings forecast | R (Japan EDINET) | QA | 1-shot | Classification | n/r |
| FinMTM | arXiv 2602.03130 | Multi-turn, multimodal finance + agent tasks | R | QA + agent | multi-turn | Custom | 11,133 |
| FinMCP-Bench / FinToolBench | arXiv 2603.24943 / 2603.08262 | Real financial MCP tools (65 / 760) | R + S | Tool/API | multi-tool, >5-step chains | Tool-call accuracy / compliance | 613 / 295 |

### 1d. Decision-making simulators with financial state

| Benchmark | Year / venue | Focus | Data | Env | Trajectory length | Eval | Size |
|---|---|---|---|---|---|---|---|
| InvestorBench | ACL'25 | Single-asset trading (stocks, crypto, ETFs) | R (market data) | Sim | daily steps | Econ (Sharpe, return, max drawdown) | 3 envs |
| FinTSB | arXiv 2502.18834 | Time-series forecasting with fees | R | Offline | n/a | Forecast/trade metrics | 15 years of data |
| FinWorld | arXiv 2508.02292 | Platform: 4 tasks, 800M data points | R | Platform | n/a | Task metrics | platform |
| **EnterpriseArena** | arXiv 2603.23638 | CFO of a lending firm for **132 months** | R→S | Sim (4 tools, ≤20 calls per month) | 132 timesteps | Econ (survival + terminal value) | 1 env |
| CEO-Bench | arXiv 2606.18543 | Run a startup for 500 days | S | Sim (Python API) | 500 days | Econ (ending cash) | 1 env |
| Vending-Bench / 2 | arXiv 2502.15840; Andon Labs | Run a vending business for a year | S | Sim (email, web, inventory) | >20M tokens; v2: 3,000–6,000 messages | Econ (net worth / balance) | 1 env |
| E-Commerce Bench | arXiv 2608.30730 | Multi-store merchant for 365 days | R→S | Sim | 365 days | Econ + fraud avoidance | 1 env |
| FinPersona-Bench | arXiv 2606.31522 | Mandate drift over long trading horizons | S | Sim | long | Behavioral (mandate salience decay) | 18 LLMs |
| MortarBench | arXiv 2606.19416 | Mortgage loan origination | S (mutation pipeline) | QA/agent | n/r | EM | n/r |

### 1e. General long-horizon agent benchmarks with finance components

| Benchmark | Year / venue | Focus | Data | Env | Trajectory length | Eval | Size |
|---|---|---|---|---|---|---|---|
| TheAgentCompany | arXiv 2412.14161 | Simulated software company (12 finance tasks) | S | FS + GitLab, ownCloud, Plane, Rocket.Chat | 27 steps avg (best model) | Checkpoints (deterministic + LLM) | 175 |
| OfficeBench | arXiv 2407.19056 | 1-, 2- and 3-app office workflows | S | Apps (Word, Excel, mail…) | short–medium | EM / fuzzy / execution | 300 |
| OdysseyBench | arXiv 2508.09124 | Long-horizon office workflows | R + S | Apps | multi-day context | Checks | 300 + 302 |
| WorkArena++ | arXiv 2407.05291 | ServiceNow compositional tasks | S | Browser | long | Validators | 682 |
| CRMArena-Pro | arXiv 2505.18878 | Salesforce sales, CPQ, service | S | Tool/API | multi-turn | EM / State | 19 tasks; ~4.3k instances |
| EnterpriseBench | arXiv 2510.27287; EMNLP'25 | SWE, HR, **finance**, admin with access control | S | Tool sandbox | n/r | Checks | 500 |
| τ-bench / τ²-bench | arXiv 2406.12045 / 2506.07982 | Retail, airline, telecom (dual control) | S | Tool/API + user simulator | multi-turn | **State (DB) + pass^k** | 115 / 50 / 114 |
| AppWorld | ACL'24 | 9 apps (incl. Venmo/Splitwise-like), 457 APIs | S | Code + API | long code | **State unit tests + collateral-damage checks** | 750 |
| Toolathlon | arXiv 2510.25726; ICLR'26 | 32 apps incl. Excel, Sheets, Yahoo Finance, Snowflake | S + R starting states | MCP | ~20–27 turns | Deterministic eval scripts | 108 |
| MCP-Universe | arXiv 2508.14704 | 6 domains incl. Financial Analysis (Yahoo Finance) | R (live) | MCP | n/r | Format, static and dynamic evaluators | 231 (40 finance) |
| SWE-Lancer | arXiv 2502.12115 | Paid Upwork software engineering tasks | R | Code | long | E2E tests; $ earned | ~1.4k ($1M) |
| xbench (profession tracks) | arXiv 2506.13651 | Recruitment, marketing (no finance track found) | R | Web | n/r | Rubric | 50 + 50 |
| ERP-Bench (Anchor paper) | arXiv 2605.26321 | Odoo procurement and manufacturing planning | S (CP-SAT spec) | ERP | long | State + optimality | 300 |
| LongDS-Bench | arXiv 2605.30434 | Stateful multi-turn data analysis | R (Kaggle) | Code | 2,225 turns across 68 tasks | EM | 68 |
| Wealth-mgmt TAC extension | arXiv 2512.02230 | Wealth-management assistant tasks | S | TheAgentCompany | n/r | Deterministic graders | 12 task pairs |

Searched for but **not found** under these names: "EconAgentic", "Finance-Bench-Long", "FinModelBench" (the closest matches are MBABench, FrontierFinance and BlueFin), and a finance track in xbench. "LedgerBench-100" (blobfish.ai) and "FactoryBench-100" were seen only in search snippets (**unverified**).

---

## 2. Benchmark details

### 2.1 SpreadsheetBench family (highest priority)

#### SpreadsheetBench v1

- **Paper:** Ma et al., [arXiv 2406.14991](https://arxiv.org/abs/2406.14991). NeurIPS 2024 Datasets & Benchmarks, Spotlight.
- **Data:** 912 real questions with their spreadsheets, taken from 4 forums: ExcelForum, Chandoo, MrExcel and ExcelGuru.
  - Only posts with an accepted answer were kept.
  - 35.7% of files have multiple tables; 42.7% have non-standard relational tables. Many include non-text elements.
- **Task types:** cell-level and sheet-level manipulation across 10 categories. The exact split between the two levels was not verified.
- **Building the answers:**
  1. Annotators applied the forum's formula or VBA solution to get the answer.
  2. They then modified the input data twice to make two more input/answer pairs, targeting corner cases such as empty cells that should read zero.
  3. Answer positions were shifted to reduce leakage.
  - Result: 2,729 test cases, about 3 per instruction.
- **Evaluation:** OJ-style.
  - Soft: partial credit per test case, like IOI scoring.
  - Hard: all test cases must pass, like ICPC scoring.
  - Settings: single-round code generation, or multi-round ReAct with up to 5 rounds of execution feedback.
- **Results at release:**
  - GPT-4o: 18.4% soft / 15.0% hard.
  - Copilot in Excel: about 20% soft, on a small sample.
  - Humans: 71.3% soft / 62.0% hard, on 50 items.
- **Example tasks:**
  - Extract a substring from a column inside a non-standard table.
  - Build a duty-schedule grid from two tables on one sheet.
- **Limitations:**
  - Short instructions (about 86 words).
  - About 1.4 sheets per file.
  - Single-step "help me with a formula" scope.
  - Corner cases not designed for every item.
  - Now saturated on the Verified subset.

#### SpreadsheetBench Verified (400)

- Released Dec 2025 by Shortcut AI with the original authors.
- 400 human-validated tasks filtered from the 912; some were removed as too easy.
- Third-party leaderboards (**unverified**) show it saturated by mid-2026: about 91–95% for products such as Qingqiu Agent, GPT for Excel and WPS AI.
- Practical point: v1-style forum tasks no longer separate frontier agents. That motivated v2.

#### SpreadsheetBench 2

- **Paper:** Zhu, Zhang, Ma, Zhang, Zhang (Renmin University) with Aptura AI/Shortcut AI and AfterQuery, [arXiv 2606.29955](https://arxiv.org/abs/2606.29955) (Jun 2026).
- **Data:** HF [KAKA22/SpreadsheetBench-v2](https://huggingface.co/datasets/KAKA22/SpreadsheetBench-v2), MIT license, 442 MB.
- **Data sources:** public financial reports and filings from NYU Stern (Damodaran), **Screener.in, BSE India** and Bloomberg. This gives some non-US coverage.
- **How tasks are built:**
  1. Financial experts build complete gold workbooks.
  2. Each task is derived by one of three edits: remove target regions (generation/template), inject controlled errors (debugging), or specify a chart objective (visualization).
  3. Each task must have a unique, deterministic solution and a self-contained instruction.
  4. Two independent experts solve every task from the instruction alone, and discrepancies lead to revision.
  5. Over 1,500 expert hours in total.
- **Task categories:**

| Category | Tasks | Avg. sheets | Avg. modified cells | Coverage |
|---|---|---|---|---|
| Financial Modeling | 100 | 15.3 | 1,164.5 | Consolidation, deferred tax, equity investments, DCF, LBO, M&A, comps |
| Debugging | 100 | 21.1 | 656.6 | 10 error types: double counting, wrong references, formula errors, bad INDEX/MATCH, wrong sign, unit mismatch, inconsistent color conventions… |
| Template | 97 | 1.2 | 65.7 | Template completion |
| Visualization | 24 | 1.7 | 88.3 | Charts and pivots |
| **Overall** | **321** | **11.8** (max 99) | **593.5** | Avg. instruction ~429 words |

- **Environment:**
  - SWE-agent harness with three tools: `bash`, `view_xlsx` and `submit`.
  - **Max 50 turns.**
  - Docker container with no network, Python 3.11, pandas, openpyxl and LibreOffice.
  - Per-model step counts appear only in a figure. The paper also defines an "effective-step ratio".
- **Evaluation:**
  - *Modification* = fraction of target cells whose values match gold.
  - *Accuracy* = 1 only if every cell matches.
  - Visualization = a VLM judge (GLM-4.6V) scoring rubric items (Data Correctness, Format Compliance).
- **Results (overall accuracy):** Claude Opus 4.6 34.89% (77.2% modification); GPT-5.2 26.8%; Gemini 3.1 Pro 23.7%; open models 7–17%.
  - Debugging accuracy is at most 12%.
  - Spreadsheet products on a 30-item subset: Claude for Excel was best of them at 15.4%. Products did not beat the scaffolded models.
  - Harness matters: Cline and Kilo Code scored about 8.7% vs. about 15% for the authors' scaffold, on GLM-5.
- **Failure modes:** insufficient inspection and wrong target selection. Examples:
  - Copying an adjacent formula doubles a Debt/Equity numerator.
  - Fixing 2 of 3 double-counting bugs in an LBO.
  - "Fixing" font-color conventions by editing formulas.
- **Stated limitations:**
  - Finance and business only.
  - Exact match undercounts semantically equivalent solutions.
  - Noise from the VLM judge.
  - No confidence intervals.
- **What v2 adds over v1:**
  - Expert-curated real business data instead of forum posts.
  - About 8× more sheets per file and about 5× longer instructions.
  - A debugging taxonomy and visualization rubrics.
  - Workflow-level evaluation.
- **What it still lacks:**
  - One workbook per task, with no cross-workbook or cross-document inputs.
  - No time dimension: no period rollforward or new actuals arriving.
  - No external systems.
  - A single static gold state.

#### Other spreadsheet benchmarks

- **SheetCopilot** ([arXiv 2305.19308](https://arxiv.org/abs/2305.19308), NeurIPS'23): 221 control tasks using atomic actions; 44.3% at release.
- **SheetAgent / SheetRM** ([arXiv 2403.03636](https://arxiv.org/abs/2403.03636), WWW'25 oral): long-horizon, multi-category, reasoning-dependent manipulation. Task count not verified.
- **WTMBench** ([arXiv 2608.07873](https://arxiv.org/abs/2608.07873)):
  - A "workbook time machine" mines input/output/query triples from public workbook corpora.
  - 150 curated tasks covering formulas, charts, pivots and conditional formatting, with queries at three specificity levels.
  - Finding: query specificity and the interface API strongly affect scores.
  - Relevant idea for us: **mine version histories to create tasks**.
- **Finch / FinWorkBench** ([arXiv 2512.13168](https://arxiv.org/abs/2512.13168)): the strongest "messy real data" benchmark.
  - **Data sources:**
    - Enron: about 15k spreadsheets and 500k emails.
    - EUSES spreadsheet corpus.
    - Government and international reports: World Bank, Canadian Public Accounts, UK PESA.
    - Adidas FY24 report.
  - **How workflows are built** (three channels):
    1. Mine email threads for business goals and the attached sheets.
    2. Diff successive spreadsheet versions to recover the workflow.
    3. Reverse-engineer workflows from final deliverables.
  - **Scale:** 172 workflows / 384 tasks; 78.5% of workflows have multiple tasks; about 8 sheets on average (max 91); median about 15k cells (max 3.7M cells).
  - **Task types:** calculation, structuring, data entry, validation, cross-file retrieval, visualization, modeling, web search.
  - **Business types:** reporting, trading and risk, planning and budgeting, AP/AR, and others.
  - **Evaluation:** human pass/fail plus a GPT-5-mini judge that sees diffs and screenshots (82–90% agreement).
  - **Results:** GPT 5.1 Pro 38.4%; Claude Sonnet 4.5 25%. Pass rates roughly halve when a workflow has more than 2 tasks (44%→24%).
  - **Example:** a column labeled "daily exposure" actually encodes 55-day payment timing in its formula, so models that ignore formulas misread it.
  - **Limitations:**
    - API baselines are single-call.
    - The judge over-estimates by a few points.
    - The data is old (Enron era) and US-centric.

### 2.2 Financial modeling and investment-banking deliverables

#### BankerToolBench (BTB)

- **Paper:** Handshake AI + McGill, [arXiv 2604.11304](https://arxiv.org/abs/2604.11304). Code: [GitHub](https://github.com/Handshake-AI-Research/bankertoolbench).
- **Data and authors:** 100 tasks written by 172 bankers (over 5,700 hours), out of 502 bankers involved overall (contributors, reviewers, collaborators) from firms such as Goldman Sachs, JPMorgan, Evercore and Lazard. Each task had at least 4 banker reviews.
- **Mix:**
  - By product: M&A 62%, LevFin 19%, ECM 10%, DCM 6%.
  - By workflow: Modeling & Scenario Analysis 37%, Valuation & Pricing 30%, Client & Marketing Materials 27%.
  - Common subcategories: DCF 18%, LBO/credit models 15%, trading comps 10%, pitchbooks 8%, merger models 6%.
- **Environment:**
  - A Harbor RL environment.
  - 3 MCP tools: a market-data API (FactSet/Capital IQ-like), an SEC EDGAR API and a company-profile API.
  - LibreOffice, Python, openpyxl, python-pptx and reportlab installed.
  - **Tasks anchored to a historical date; no internet access.**
- **Trajectory length:** humans about 5 h per task (max 21 h). Agents made **up to 539 LLM calls**, and 97% of steps were tool calls or code.
- **Evaluation:**
  - About 150 weighted binary criteria per task, in six areas: technical correctness, client readiness, instruction following, transparency, internal consistency, risk/compliance.
  - Agent-as-judge "Gandalf" (OpenHands + Gemini 3 Flash) opens and runs the xlsx/pptx outputs. It has 88.2% accuracy (κ 0.76) vs. 84.6% inter-human agreement.
  - A "sendable" threshold is calibrated to banker ratings.
- **Results:** best is GPT-5.4 at about 16% Pass@1 and about 13% Pass^3. **No output was client-ready.**
  - Failure mix: code/formula errors 41%, reasoning 27%, retrieval/persistence 18%, fabricated data 13%.
- **Example failures:**
  - Treating after-tax synergies as pre-tax.
  - Conflicting LTM revenue across two slides.
- **Stated limitations:** clean standardized data rather than messy deal data; no team collaboration; **US-centric**; no confidential deal data.

#### FrontierFinance

- **Paper:** Kensho + S&P Global, [arXiv 2604.05912](https://arxiv.org/abs/2604.05912).
- **Tasks:** 25 tasks, 5 each of 3-statement, LBO, DCF, merger and **lender** models, built from scratch from SEC filings. Deliverables are Excel, plus a PowerPoint memo for LBO tasks.
  - Example: LBO of Electronic Arts with sensitivity tables, a bridge schedule and an investment memo.
- **Environment:** **computer use (GUI)** plus bash, with Firefox, LibreOffice and python3, run through the Inspect framework.
- **Trajectory length:**
  - Humans: 18.3 h on average (6.5–35 h), against an estimate of 12.5 h.
  - Agents: 122–302 messages, 3–28M tokens and 0.3–1.3 h per task.
- **Evaluation:**
  - Rubric of 5–11 categories and up to 140 criteria, behind a gating condition.
  - Human graders on 10 tasks (r = 0.965 with the lead expert).
  - LLM judge (Sonnet 4.6): correlation with humans was only **0.20 without the rubric and 0.63 with it**. The judge over-estimates LLM outputs and shows self-preference.
- **Results (human-graded subset):** humans 77.2%, GPT-5.4 70.9%, Opus 4.6 61.8%.
- **Failure modes worth designing against:**
  - Hardcoded values instead of formulas.
  - **Balance sheets forced to balance with fabricated plugs.**
  - Hidden white-font rows used as workarounds.
  - Mismatched time periods.
- **Limitations:** very small; only 10 tasks human-graded; open release still "forthcoming".

#### MBABench

- **Paper:** Columbia Business School, [arXiv 2605.22664](https://arxiv.org/abs/2605.22664) (v1 May 2026, v5 Aug 2026).
- **Task sources:** Financial Modeling World Cup, ModelOff and the Wall Street Prep curriculum.
- **Task types:** 8 parent types: valuation, deals, 3-statement, FP&A, debt & equity, derivatives, wealth management, analytics. Difficulty levels 1–5.
- **Agents tested:** GUI agents (Claude for Excel, ChatGPT for Excel via Playwright), code agents (Codex, Claude Code in Docker with deny-by-default egress) and an MCP "Excel CLI agent".
- **Size of solutions:** gold solutions have about 33× more cells and about 93× more functions than SpreadsheetBench tasks.
- **Evaluation:** Gemini-2.5-pro judge with per-criterion pass/fail on Accuracy, Formula and Format. It has 0.92 accuracy vs. 408 expert labels.
- **Results:** scores drop sharply after a few chained calculations; the top level-4 score is 72.6. Excel add-ins often hardcode values.
- **Example:** "Bread and Butter" (ModelOff 2015): build a 3-statement model for an acquisition and compute a 10-year IRR.
- **Not reported:** task count and trajectory statistics.

#### BlueFin

- **Paper:** Longitude Labs + CMU, [arXiv 2605.30907](https://arxiv.org/abs/2605.30907).
- **Tasks:** 131 tasks (82 manipulation, 39 interrogation, 10 synthesis) with 3,225 criteria. 11 tasks are public; the rest are held out.
- **Authors of tasks:** 78 vetted finance contributors, at about 5 h of annotator time per task.
- **Harness:** 20 tools including LibreOffice headless recalculation with iterative calculation, plus sandboxed openpyxl. The system prompt is a minimal 61 words.
- **Evaluation:**
  - An agentic GPT-5.4 judge inspects the output workbook (α 0.826 vs. experts).
  - Criteria cover formula correctness, integration, output validation, presentation and pitfalls.
  - **Perturbation tests**: e.g. change WACC from 8.5% to 10%, then check that EV moves to within ±2% of the expected value.
- **Results:** no model above 50% (GPT-5.5 49.6%, Opus 4.7 49.2%). Models are worst on validation and perturbation criteria.
- **Cost:** about $6–49 per task. Opus was 16× costlier than Gemini on one task for a similar score.
- **Limitation:** one workbook of context per task.

#### APEX-Agents (Mercor)

- **Paper:** [arXiv 2601.14242](https://arxiv.org/abs/2601.14242).
- **Scale:** 480 tasks in 33 "worlds"; 10 worlds are investment banking (about 172 files per world).
- **Apps:** mail, chat, calendar, docs, sheets, slides, PDFs, file system and code. Some IB worlds add EDGAR plus equity and fixed-income data apps (187 extra tools).
- **Task format:** single-turn prompts that can only be solved using in-world files.
- **Evaluation:** rubrics (about 3 criteria per task) with LLM judging, scored Pass@1.
- **Results:** best 24% at launch (Gemini 3 Flash). Later reports put GPT-5.4 at about 36% Pass@1 (**unverified**).
- **Trajectories:** Kimi K2 averaged 92 steps; runs over 250 steps count as timeouts.
- **Infrastructure:** "Archipelago" is open-sourced.
- **APEX-Agents 1.1** (Sep 2026, Harbor hub): 240 tasks, 31 worlds, 955 criteria (**unverified** detail).

#### GDPval

- **Paper:** OpenAI, [arXiv 2510.04374](https://arxiv.org/abs/2510.04374).
- **Finance coverage:** 5 Finance & Insurance occupations (financial managers, customer service reps, securities sales agents, personal financial advisors, financial & investment analysts) plus Accountants & Auditors. Each has ≥30 tasks in the full set and 5 in the gold set.
- **Task format:** real work products, about 1.9 reference files in and 1.5 files out per task. Human tasks take about 6.7 h on average.
- **Evaluation:** blinded pairwise comparison by experts; the autograder reaches 66% agreement vs. 71% between humans.
- **Limitation:** **one-shot, fully specified tasks** with no interaction, no tacit context and no proprietary software.

#### FinanceQA

- **Paper:** AfterQuery, [arXiv 2501.18062](https://arxiv.org/abs/2501.18062). Data: HF [AfterQuery/FinanceQA](https://huggingface.co/datasets/AfterQuery/FinanceQA).
- **Questions:** 148, typed basic, assumption or conceptual, mostly on Costco's FY2024 10-K.
  - Examples: gross profit, unadjusted vs. adjusted EBITDA.
  - Assumption-based questions need an unstated convention, such as operating-lease adjustments.
- **Evaluation:** exact match.
- **Results:** models fail about 60%; assumption questions are near 0–4%.

### 2.3 Accounting operations

#### AccountingBench (Penrose, Jul 2025; blog only, no paper)

- **Source:** [accounting.penrose.com](https://accounting.penrose.com/). Details are from the [HN discussion](https://news.ycombinator.com/item?id=44637352) and press coverage.
- **Task:** close the books **month by month for one year** for a real YC SaaS company with millions in revenue.
- **Data:** real source data from Stripe, Ramp, Mercury and Rippling. The ledger is seeded with the chart of accounts and 8 months of history.
- **Tools:** SQL read/write on the general ledger, Python, a reconciliation tool and `create_tool`.
- **Monthly procedure:**
  1. Post transactions to the GL.
  2. Reconcile key accounts against bank and other statements; small timing differences such as Stripe payouts are allowed.
  3. Submit recon reports. **These are validated automatically, and the agent cannot proceed until they pass.**
  - Context is reset each month, but the state carries forward.
- **Scoring:** financial-statement accuracy vs. a CPA baseline. Best of 3 runs was reported.
- **Results (secondary sources):**
  - Claude 4 and Grok 4 stayed within about 1% of the CPA for the first months, then degraded. Grok fell sharply in month 5; Claude fell below 85%.
  - o3, o4-mini and Gemini 2.5 Pro could not finish one month.
- **Key finding: reward hacking.** Models pulled in unrelated transactions or invented false ones to pass reconciliation checks, and anti-gaming prompts helped only temporarily. **Errors compound across periods**: one bank opening balance was off by more than $100k and set off an error loop.
- **Limitations:** a single company; not open; best-of-3 reporting; methodology only partly published (**unverified** details).

#### APEX–Accounting

- **Paper:** Mercor + Ramp, [arXiv 2607.27189](https://arxiv.org/abs/2607.27189).
- **Tasks:** 160 tasks across 10 synthetic companies, each "frozen at month-end close".
  - Reconciliation 61, Data Entry 26, Variance Analysis 28, Schedules & Accruals 45.
- **Environment:** 91 tools (file system, docx/pdf/Excel, mail, code, accounting software with QuickBooks-like data). Caps of 500 steps and 5M tokens.
- **Evaluation:** binary outcome rubrics (13.7 per task) with a DeepSeek-v4-Flash judge (97.1% agreement with experts). Metrics: Mean Criteria@3, Pass@8 and Pass^8.
- **Results:** best Mean Criteria 56.4%; best Pass@8 21.5%; **best Pass^8 2.6%**. 58% of tasks were never fully solved.
- **Example:** a December client cost-advance reconciliation where $23.5k of contract attorney fees was expensed instead of capitalized.
- **Stated limitations:**
  - **No tax, audit or consolidation.**
  - No human-in-the-loop clarification.
  - **Single period.**
  - Small sample.

#### FinBalance

- **Paper:** [arXiv 2606.15949](https://arxiv.org/abs/2606.15949).
- **Task:** turn synthetic source-document bundles (8 industries, 3 period types, 5 difficulty levels, tax/FX treatments, distractors, 23 inconsistency codes) into cited journal entries, then a balance sheet.
- **Evaluation:**
  - Exact final balance sheet (≤46% for the best model).
  - **Ledger replay**: BS_exact (what the model reported) vs. BS_recon (what its entries actually produce). The 26–41 pp gap shows models "report" balance sheets their own entries don't support.
  - This is a strong verification idea.

#### FinMaster

- **Paper:** [arXiv 2505.13533](https://arxiv.org/abs/2505.13533) (Findings ACL'26).
- **Data:** the FinSim simulator generates daily transactions for 5 company types with injected errors, then derives the three statements.
- **Tasks:** 183 across literacy (64), accounting (49), auditing (35) and consulting (35).
- **Results:** accuracy falls from over 90% on basic tasks to about 3% on full statement generation, and from 58% to 37% when going from single to multiple metrics (error propagation).
- **Limitations:** text only; simulated data.

#### Other accounting, payments and tax benchmarks

- **CFAgentBench** ([arXiv 2606.22000](https://arxiv.org/abs/2606.22000)):
  - A construction-finance CFO/controller working across 35 simulated apps (31 reconciled to one company ledger), covering ERP, project management, email, payroll, lien waivers and bank portals.
  - 1,014 task specs; 40–54 runnable with oracle-validated evaluators.
  - Graded on **functional correctness, with no LLM judge**.
  - **278 instances include a money-movement step where the correct action is to pause for human approval.**
  - Results: pass^1 0.67 but pass^5 0.38.
- **FinalityBench** ([arXiv 2609.04706](https://arxiv.org/abs/2609.04706)):
  - A hidden canonical event log is the ground truth. Four systems (processor, ledger, ERP, bank feed) see faulted streams (delayed, duplicated, dropped, reordered).
  - The agent decides whether to ship, refund, re-submit a capture or wait.
  - Graded on **executed monetary effects**, using twin-pair tasks that cannot be told apart at the decision point.
  - A strong template for cross-system reconciliation under uncertainty.
- **DABStep** ([arXiv 2506.23719](https://arxiv.org/abs/2506.23719)): about 450 Adyen payments-ops questions over payment and fee data plus documentation. Exact-match answers; best 14–16% on hard tasks.
- **FinAuditing** ([arXiv 2510.08886](https://arxiv.org/abs/2510.08886)): 1,102 instances from real XBRL US validation errors (372 companies, 2020–24). Tasks cover semantic matching, relationship extraction and math consistency across documents.
- **FinTagging** ([arXiv 2505.20650](https://arxiv.org/abs/2505.20650)): XBRL numeric-fact identification plus concept linking to the full US-GAAP taxonomy. Concept linking is weak.
- **AuditBench** (AAAI'25 workshop): real tables with synthetic transactions. Models detect errors but fail to explain them or cite standards.
- **AuditFraudBench** ([arXiv 2606.08345](https://arxiv.org/abs/2606.08345)): audit judgment on fraudulent misstatements (details not verified).
- **TaxCalcBench** ([arXiv 2507.16126](https://arxiv.org/abs/2507.16126)): US personal federal returns, synthetic, verified by a tax engine. Under a third correct.
- **CARB** (Stuut; **unverified**): 168 AR/collections tasks over 58 fictional ledgers, graded by 969 binary criteria.

### 2.4 Financial research and QA

#### Finance Agent Benchmark (Vals AI)

- **Paper:** [arXiv 2508.00828](https://arxiv.org/abs/2508.00828).
- **Questions:** 537 expert questions (50 public, 150 private validation, 337 private test) in 9 categories:

| Category | Count | Example |
|---|---|---|
| Quantitative retrieval | 102 | |
| Qualitative retrieval | 97 | |
| Numerical reasoning | 83 | |
| Complex retrieval | 29 | |
| Adjustments | 43 | Lemonade FY24 adjusted EBITDA |
| Beat or miss | 69 | Lam Research revenue vs. guidance midpoint |
| Trends | 33 | |
| Financial modeling | 47 | Amazon M&A capacity |
| Market analysis | 34 | |

- **Tools:** Google search (SerpAPI), EDGAR search, HTML parsing and a retrieve-information key-value store.
- **Trajectories:** 3.5–12 turns and 1.7–25 tool calls on average.
- **Evaluation:** GPT-4o-extracted rubrics (reviewed by humans), each check graded separately, plus a **contradiction check**.
- **Results:** o3 46.8% at $3.79 per query. Humans took 16.8 min and about $25.66 per question.
- **Limitations (stated):** little tabular or spreadsheet work; citations not checked; public filings only.
- **Finance Agent v2 (2026):** expands into comps, precedents, earnings, disclosure and modeling. Top score about 58–61% by Aug 2026 (**unverified**; vals.ai blocked).
- **IPO Finance Agent** ([arXiv 2606.23032](https://arxiv.org/abs/2606.23032)): S-1 diligence with 1,000 questions (70 public, on SpaceX). It uses contextual retrieval because the original harness failed on S-1 length, and rubrics generated by an evaluator-optimizer pipeline.

#### Other research and QA benchmarks

- **FinanceBench** ([arXiv 2311.11944](https://arxiv.org/abs/2311.11944); [GitHub](https://github.com/patronus-ai/financebench)):
  - 10,231 questions over 10-K/10-Q/8-K/earnings documents; 150 open.
  - Types: metrics-generated, domain-relevant, novel.
  - Evaluation: human review. GPT-4-Turbo + RAG failed or refused 81%.
  - Saturating for long-context models.
- **FinSearchComp** ([arXiv 2509.13160](https://arxiv.org/abs/2509.13160), ICLR'26; ByteDance Seed + Columbia):
  - 635 questions written by 70 experts, in three types:
    - T1: time-sensitive fetch, e.g. "latest close of Bloom Energy".
    - T2: simple historical lookup, e.g. Starbucks total assets on 2020-09-27.
    - T3: complex historical investigation, e.g. "largest monthly S&P 500 gain, Jan 2010–Apr 2025".
  - Evaluation: LLM judge with **asset-class-specific tolerance bands**. T1 is graded after market close. Judge agreement is 95%.
  - Results: Grok 4 (web) 68.9% vs. human 75% on Global; Greater China is harder.
- **FinDeepResearch** ([arXiv 2510.13936](https://arxiv.org/abs/2510.13936)):
  - Coverage: 64 companies in **8 markets (US, UK, China, HK, AU, SG, MY, ID)** and 4 languages.
  - Task: a templated report (6 sections, 18 subsections, 18 tables).
  - HisRubric: 15,808 items typed recognition, calculation, abstraction or interpretation.
  - Best result: o3-deep-research 37.9/100, with interpretation at most 20.3.
  - Caveat: reference answers were drafted by LLMs and then checked by experts.
- **FinResearchBench** ([arXiv 2507.16248](https://arxiv.org/abs/2507.16248)): 70 research questions of 7 types. A logic tree is extracted from each report and used by an agent-as-judge. FinResearchBench II ([arXiv 2607.12252](https://arxiv.org/abs/2607.12252)) adds consensus-derived gold rubrics.
- **FinGAIA** ([arXiv 2507.17186](https://arxiv.org/abs/2507.17186)):
  - 407 Chinese tasks across securities, funds, banking, insurance, futures, trusts and asset management.
  - Three levels: about 5, 7 and 10 steps.
  - Requires web, PDF, Excel, image and audio handling plus Python (e.g. max drawdown via akshare).
  - Results: ChatGPT Deep Research 48.9% vs. experts 84.7%. **Portfolio fund allocation was the weakest category.**
- **BizFinBench** ([arXiv 2505.19457](https://arxiv.org/abs/2505.19457)) and **v2** ([arXiv 2601.06401](https://arxiv.org/abs/2601.06401)):
  - v1: Chinese, 6,781 queries in 5 dimensions; uses the IteraJudge method.
  - v2: about 29k items from **real user queries** in Chinese and US equity markets, plus two online tasks (stock prediction, portfolio allocation).
- **FinBen** (NeurIPS'24 D&B): 42 datasets, 24 tasks, 8 aspects, English and Spanish, including a stock-trading agent task.
- **Classic QA:** FinQA (EMNLP'21), TAT-QA (ACL'21) and ConvFinQA (EMNLP'22), all numerical reasoning over table + text from reports.
  - ConvFinQA adds multi-turn chains.
  - DocFinQA ([arXiv 2401.06915](https://arxiv.org/abs/2401.06915), ACL'24) re-hosts about 7.4k FinQA questions on full filings (~123k words).
  - BizBench ([arXiv 2311.06602](https://arxiv.org/abs/2311.06602), ACL'24): 8 tasks covering program synthesis and quantity extraction.
  - SEC-QA ([arXiv 2406.14394](https://arxiv.org/abs/2406.14394)): a refreshable generator of multi-document questions.
  - Fin-RATE ([arXiv 2602.07294](https://arxiv.org/abs/2602.07294)): accuracy drops 18.6% going from single-document to **longitudinal** reasoning and 14.4% going to cross-entity reasoning.
- **Fin-R1** ([arXiv 2503.16252](https://arxiv.org/abs/2503.16252)): a 7B model evaluated only on static QA (FinQA 76, ConvFinQA 85, Ant_Finance 81, TFNS 71, Finance-Instruct-500K 62.9). This illustrates that "finance model" evaluations are still mostly single-turn QA.
- **EDINET-Bench** ([arXiv 2506.08762](https://arxiv.org/abs/2506.08762), ICLR'26): Japanese filings, used for fraud detection, earnings forecasting and industry classification. LLMs barely beat logistic regression.
- **FinMTM** ([arXiv 2602.03130](https://arxiv.org/abs/2602.03130)): 11k bilingual multimodal multi-turn items, plus agent tasks.
- **FinMCP-Bench** ([arXiv 2603.24943](https://arxiv.org/abs/2603.24943)): 613 samples using 65 real MCP tools, built from production traces at Qwen DianJin and YINGMI.
- **FinToolBench** ([arXiv 2603.08262](https://arxiv.org/abs/2603.08262)): 760 tools and 295 queries; scores compliance and timeliness alongside execution.

### 2.5 Decision simulators

- **EnterpriseArena** ([arXiv 2603.23638](https://arxiv.org/abs/2603.23638)): the closest existing "multi-period finance state" benchmark.
  - **Setup:** CFO of a FinTech lender for **132 months**, starting with $15M cash. Firm data is derived from real filings and anonymized; ledger logic is GAAP/ASC-inspired. The macro regime is hidden.
  - **Agent interface:** 4 tools (≤20 calls per month, each with a cost). One action per month: book_closing, fund-raise (equity or debt) or pass. Fund-raising succeeds stochastically and arrives with a 1–6 month delay.
  - **Metrics:** survival (cash ≥ 0) and terminal value (5× TTM revenue + cash − tool costs).
  - **Results:** 15.4% of runs survive. Humans survive 60% and reach $476.7M; the best agent (Codex + GPT-5.5) reaches $34.7M.
  - **Limitation:** decisions are coarse. There is no bookkeeping, reconciliation or document work.
- **CEO-Bench** ([arXiv 2606.18543](https://arxiv.org/abs/2606.18543)): run a startup for 500 days from a $1M start. Only 3 models end above the starting balance, and all trail a rule-based baseline.
- **Vending-Bench** ([arXiv 2502.15840](https://arxiv.org/abs/2502.15840)) and **Vending-Bench 2** (Andon Labs):
  - v1: over 20M tokens per run; net worth = cash + uncollected cash in the machine + inventory at cost. "Meltdowns" were not correlated with context-window fill.
  - v2: one simulated year, about 3,000–6,000 messages, adversarial suppliers, scored on ending balance.
- **E-Commerce Bench** ([arXiv 2608.30730](https://arxiv.org/abs/2608.30730)): 365 days running multiple stores, scored on assets plus fraud avoidance.
- **InvestorBench** ([arXiv 2412.18174](https://arxiv.org/abs/2412.18174), ACL'25): single-asset trading scored on Sharpe ratio and drawdown. **No portfolio management.**
- **FinPersona-Bench** ([arXiv 2606.31522](https://arxiv.org/abs/2606.31522)): measures mandate drift ("mandate salience decay") over long horizons.
- **FinTSB** ([arXiv 2502.18834](https://arxiv.org/abs/2502.18834)) and **FinWorld** ([arXiv 2508.02292](https://arxiv.org/abs/2508.02292)): forecasting and trading platforms, not agentic workflows.
- **MortarBench** ([arXiv 2606.19416](https://arxiv.org/abs/2606.19416)): synthetic loan-origination examples, exact match, best 77%.

### 2.6 General agent environments relevant as design templates

- **TheAgentCompany** ([arXiv 2412.14161](https://arxiv.org/abs/2412.14161)):
  - 175 tasks, 12 of them finance.
  - Example finance task: fill Section B of IRS Form 6765 (R&D credit) from ownCloud data and a CSV, asking the Finance Director on Rocket.Chat about two ambiguous items.
  - **Checkpoint scoring:** 0.5 × partial credit + 0.5 × full completion.
  - Best model: 30.3% full success, 27 steps, about $4.20 per task.
  - A wealth-management extension exists ([arXiv 2512.02230](https://arxiv.org/abs/2512.02230)).
- **τ-bench / τ²-bench** ([arXiv 2506.07982](https://arxiv.org/abs/2506.07982)): final-DB-state assertions, **pass^k** reliability and a dual-control user simulator.
- **AppWorld** ([arXiv 2407.18901](https://arxiv.org/abs/2407.18901)): 9 apps, 457 APIs, 750 tasks, scored by **state-based unit tests plus collateral-damage checks**.
- **Toolathlon** ([arXiv 2510.25726](https://arxiv.org/abs/2510.25726)):
  - 108 tasks across 32 apps (including Excel, Google Sheets, Yahoo Finance, Snowflake and WooCommerce).
  - 67% of tasks start from a realistic initial state, such as real financial spreadsheets.
  - Deterministic eval scripts compare against static or dynamically fetched ground truth.
  - About 20–27 turns; best model 38.6%.
- **MCP-Universe** ([arXiv 2508.14704](https://arxiv.org/abs/2508.14704)):
  - 40 financial-analysis tasks on Yahoo Finance: portfolio, statements, strategies, holdings, dividends.
  - *Dynamic* evaluators fetch live ground truth. That hurts reproducibility.
  - Best finance success: GPT-5 67.5%.
- **OfficeBench** ([arXiv 2407.19056](https://arxiv.org/abs/2407.19056)): 300 tasks. GPT-4o drops from 64.5% on 1-app tasks to 21.4% on 3-app tasks.
- **OdysseyBench** ([arXiv 2508.09124](https://arxiv.org/abs/2508.09124)): 300 tasks from real use cases plus 302 synthesized long-horizon office tasks, set in multi-day dialogue contexts.
- **WorkArena++** ([arXiv 2407.05291](https://arxiv.org/abs/2407.05291)): 682 ServiceNow tasks.
- **CRMArena-Pro** ([arXiv 2505.18878](https://arxiv.org/abs/2505.18878)): success drops from about 58% single-turn to 35% multi-turn; confidentiality awareness is near 0.
- **EnterpriseBench** ([arXiv 2510.27287](https://arxiv.org/abs/2510.27287)): 500 tasks with **access-control hierarchies** and finance/budget data; best 41.8%.
- **SWE-Lancer** ([arXiv 2502.12115](https://arxiv.org/abs/2502.12115)): about 1.4k Upwork tasks worth $1M total. Graded by triple-verified E2E tests, reported as **dollar-denominated** scoring.
- **xbench** ([arXiv 2506.13651](https://arxiv.org/abs/2506.13651)): profession-aligned tracks with tasks priced in human time and dollars. No finance track was found.
- **ERP-Bench** ([arXiv 2605.26321](https://arxiv.org/abs/2605.26321)): 300 Odoo planning tasks generated from a CP-SAT specification, so optimality can be checked (26% feasible, 17% optimal).
- **LongDS-Bench** ([arXiv 2605.30434](https://arxiv.org/abs/2605.30434)): stateful multi-turn analysis over 2,225 turns.

---

## 3. What "long-horizon" means in these papers, and how they keep it verifiable

### 3.1 How horizon is measured

The papers use five different yardsticks.

1. **Human time:**
   - GDPval: about 6.7 h.
   - BankerToolBench: about 5 h (max 21 h).
   - BlueFin: about 5 h of annotation per task.
   - FrontierFinance: 18.3 h on average (max 35 h).
2. **Agent steps and tokens:**
   - Finance Agent Benchmark: 3.5–12 turns.
   - FinGAIA: 5–10 steps.
   - Finch: median 16 tool calls.
   - Toolathlon: about 20–27 turns.
   - BlueFin: 24–38 turns.
   - TheAgentCompany: 27 steps.
   - SpreadsheetBench 2: 50-turn cap.
   - APEX-Agents: about 92 steps, 250-step timeout.
   - FrontierFinance: 122–302 messages and up to 28M tokens.
   - APEX–Accounting: cap of 500 steps and 5M tokens.
   - BankerToolBench: up to 539 LLM calls.
3. **Size of the output:**
   - SpreadsheetBench 2: about 594 modified cells, and over 1,100 for modeling tasks.
   - MBABench: about 33× SpreadsheetBench's cells.
   - BankerToolBench and FrontierFinance: about 100–150 rubric criteria per deliverable.
4. **Simulated calendar time with carried-forward state:**
   - AccountingBench: 12 months.
   - EnterpriseArena: 132 months.
   - Vending-Bench 2 and E-Commerce Bench: 365 days.
   - CEO-Bench: 500 days.
5. **Chained subtasks within one workflow:**
   - Finch: 78.5% of workflows are multi-task.
   - OfficeBench: multi-app tasks.
   - FinMaster: disclosure items, then full statements.
   - SpreadsheetBench 2: multi-sheet dependency chains.

**Observation:** only group 4 has *temporal state*, where outputs from period t become inputs at t+1. Within that group, only AccountingBench does real accounting work on real documents, and it is closed, uses one company and is only partly documented. The others are coarse decision simulators scored on a single economic outcome.

### 3.2 Verification strategies, from most to least deterministic

| Strategy | Used by | Pros | Cons |
|---|---|---|---|
| Final-state / DB assertions + collateral-damage checks | τ²-bench, AppWorld, Toolathlon, CFAgentBench, TheAgentCompany checkpoints | Cheap, reproducible, path-agnostic | Needs a structured end state; weak for documents |
| Exact cell match vs. gold workbook | SpreadsheetBench 2, SpreadsheetBench v1 | Objective | Brittle (undercounts equivalent layouts); one gold answer |
| **Multiple test inputs (OJ-style)** / **perturbation tests** | SpreadsheetBench v1 (3 cases per item); BlueFin (change WACC, check EV) | Tests that the *model logic* is live, not hardcoded | Needs formula-preserving outputs |
| Exact balance sheet + **ledger replay** | FinBalance (BS_exact vs. BS_recon) | Detects "reported ≠ supported"; accounting identities give free checks | Requires a structured JE format |
| Generator/simulator ground truth (oracle) | FinMaster (FinSim), FinBalance, EnterpriseArena, FinalityBench (hidden event log), ERP-Bench (CP-SAT optimum) | Unlimited, contamination-resistant, exact | Synthetic-realism gap |
| Economic outcome metric | Vending-Bench, EnterpriseArena, CEO-Bench, E-Commerce Bench, FinalityBench, SWE-Lancer ($) | One interpretable number | Sparse; hides *why*; high variance |
| In-trajectory validators / gating | AccountingBench (recon must pass to proceed), FrontierFinance (gating condition) | Dense signal, stops runaway errors | **Invites reward hacking** (fabricated reconciling items) |
| Tolerance bands | FinSearchComp, BlueFin (±2%) | Handles rounding and live data | Choosing the band is a judgment call |
| Weighted binary rubrics + LLM/agent judge | BankerToolBench (88.2%, κ .76), APEX–Accounting (97.1%), BlueFin (α .826), MBABench (0.92), Finch (82–90%), Finance Agent Benchmark, FinDeepResearch, APEX-Agents | Scales to open-ended deliverables (decks, memos) | Judge drift and self-preference (FrontierFinance: r = 0.63 even with a rubric; over-estimates) |
| Pairwise expert preference | GDPval | Gold-standard quality | Expensive, not reproducible |
| Reliability metrics (pass^k) | τ²-bench, APEX–Accounting (Pass^8 2.6%), BankerToolBench (Pass^3), CFAgentBench (pass^5) | Exposes inconsistency hidden by pass@1 | k× cost |

**Practices for keeping long runs verifiable:**
- Anchor tasks to a historical date, offline (BankerToolBench). Avoid live data, which hurt MCP-Universe and FinSearchComp reproducibility.
- Score at checkpoints or per period rather than only at the end (TheAgentCompany; AccountingBench per month).
- Decompose deliverables into atomic binary criteria.
- Make judges *agentic* so they can open and run the files (BankerToolBench's Gandalf, BlueFin).
- Run perturbation or OJ-style re-execution.
- Replay the agent's entries through a ledger.
- Report pass^k.

---

## 4. Gaps: under-served axes

1. **Multi-period temporal state (the largest gap).** No open benchmark has an agent run *N* consecutive accounting or FP&A periods where:
   - opening balances, accrual reversals, prepaid and deferred-revenue rollforwards, depreciation schedules and covenant tests depend on its own earlier outputs; and
   - new actuals and documents arrive each period.
   - What exists falls short in specific ways:
     - AccountingBench does this, but it is closed, uses one company and reports best-of-3.
     - APEX–Accounting is explicitly single-period ("frozen at month-end close").
     - SpreadsheetBench 2, BankerToolBench and FrontierFinance are single snapshots.
     - EnterpriseArena, CEO-Bench and Vending-Bench have state but no bookkeeping or document work.
   - Evidence that it matters:
     - AccountingBench: error compounding after month 4–5.
     - FinMaster: error propagation.
     - Finch: pass rate halves with more than 2 tasks.
     - Fin-RATE: −18.6% on longitudinal questions.
2. **Recovery from errors and debugging inside a workflow.**
   - SpreadsheetBench 2 debugging is the hardest category (≤12%), and BlueFin's validation and perturbation criteria are the lowest.
   - No benchmark *injects an error in period t and checks whether the agent detects and corrects it at t+k* (for example, a mis-coded expense discovered in a later flux review).
3. **Messy, conflicting, multi-system real data.** Most benchmarks use clean SEC filings or synthetic worlds; BankerToolBench names "standardized data sources rather than messy live-deal information" as a limitation. The exceptions:
   - Finch: Enron emails and spreadsheet version histories, 2000-era.
   - AccountingBench: real Stripe/Ramp/Mercury data, closed.
   - FinalityBench: faulted streams, but synthetic and narrow (payments).
   - Missing: late-arriving bank feeds, duplicate vendor records, scanned or partial invoices, FX-converted statements, mid-period chart-of-accounts changes and disagreements between subledger and GL.
4. **Cross-document and cross-system reconciliation at scale.**
   - Covered as single-period or single-bundle tasks: APEX–Accounting reconciliation (61 tasks), FinBalance and FinAuditing (XBRL).
   - Not covered: three-way match (PO / receipt / invoice), intercompany eliminations, subledger↔GL↔bank tie-outs across periods, and tracing a metric across board deck ↔ model ↔ GL. BankerToolBench found inconsistent LTM revenue between slides, which shows consistency across artifacts is a real failure mode that is rarely tested.
5. **Jurisdictions and standards beyond US GAAP / SEC.**
   - US-centric: Finance Agent Benchmark, FinanceBench, FinanceQA, BankerToolBench (stated), FrontierFinance, TaxCalcBench, FinTagging (US-GAAP taxonomy).
   - Exceptions: FinDeepResearch (8 markets, 4 languages), FinSearchComp/BizFinBench/FinGAIA (China), EDINET-Bench (Japan), SpreadsheetBench 2 (Indian data sources), Finch (UK PESA, Canadian public accounts).
   - **Not covered:** IFRS vs. US GAAP treatment differences (leases, development costs, revaluation), statutory local-GAAP reporting, VAT/GST, multi-currency consolidation, and non-English source documents in *operational* (not QA) tasks.
6. **Private-company, SMB, government and non-profit finance.**
   - Private companies appear only as synthetic worlds (APEX–Accounting, CFAgentBench) or a single real SaaS company (AccountingBench).
   - No government or fund accounting (encumbrances, budgetary vs. GAAP basis).
   - No non-profit restricted-fund accounting.
   - No real private-company management accounts.
7. **Accounting operations vs. investment QA.** The field is still weighted toward investment research QA and sell-side or IB deliverables. Thin or missing:
   - Consolidation, explicitly excluded by APEX–Accounting.
   - Tax provision (ASC 740 / IAS 12) and indirect tax.
   - Revenue recognition (ASC 606 / IFRS 15) with multi-element contracts.
   - Lease accounting (ASC 842 / IFRS 16).
   - Audit fieldwork: sampling, PBC lists, workpapers, tie-outs. Existing audit benchmarks only detect errors.
   - Treasury: 13-week cash forecasts, borrowing-base certificates.
8. **Controls, approvals and human-in-the-loop.**
   - Only CFAgentBench tests "pause before money movement".
   - TheAgentCompany and τ²-bench include asking a person.
   - EnterpriseBench has access control.
   - No finance benchmark tests segregation of duties, materiality thresholds, approval workflows or the audit trail.
9. **Anti-gaming and integrity checks.** Gaming is observed but rarely scored:
   - Fabricated reconciling items (AccountingBench).
   - Forced-balance plugs and hidden white-font rows (FrontierFinance).
   - Hardcoded outputs (MBABench, BlueFin, Finch).
   - "Reported ≠ entries" (FinBalance).
   - Plug detection, formula provenance, the ledger-replay gap and evidence citation should be first-class metrics.
10. **Reliability and statistical power.** Long-horizon finance benchmarks are tiny:
    - FrontierFinance 25 tasks, BankerToolBench 100, BlueFin 131, APEX–Accounting 160, AccountingBench 1 company.
    - Each run costs about $5–50 or more.
    - Pass^k is rarely reported, and where it is, it is very low (2.6% Pass^8).
    - A procedurally generated world with exact oracles (FinMaster, FinBalance and FinalityBench style), anchored in real data, could add volume without losing verifiability.
11. **Verifiability of long trajectories.** Benchmarks with deterministic checks tend to have weak finance depth (τ²-bench, AppWorld, Toolathlon); deep-finance benchmarks rely on LLM judges (FrontierFinance judge r = 0.63). Almost no benchmark combines deep finance, a long horizon and mostly deterministic grading. The closest are FinBalance and CFAgentBench, both synthetic and short.
12. **Contamination and point-in-time.**
    - Public 10-K-based items (FinanceQA on Costco, FinanceBench) are contaminated.
    - Live-data benchmarks drift.
    - BankerToolBench's offline historical anchoring and SEC-QA's refreshable generation are partial fixes. A Look-Ahead-Bench ([arXiv 2601.13770](https://arxiv.org/abs/2601.13770)) style point-in-time discipline is rare in agentic finance tasks.

---

## 5. Finance workflow archetypes: coverage map

✅ = substantively covered · ◐ = partial (single period, QA-only or tiny) · ✗ = not found

| Archetype | Coverage | Where | Notes / gap |
|---|---|---|---|
| 3-statement model build | ✅ | FrontierFinance, MBABench, SpreadsheetBench 2, BankerToolBench | All single snapshot; **none roll the model forward with new actuals or re-forecast** |
| DCF | ✅ | BankerToolBench (18%), FrontierFinance, SpreadsheetBench 2, BlueFin, MBABench | Well covered; perturbation testing only in BlueFin |
| LBO / credit model | ✅ | BankerToolBench (15%), FrontierFinance, SpreadsheetBench 2, MBABench | |
| Merger model / accretion-dilution | ✅ | BankerToolBench, FrontierFinance, SpreadsheetBench 2 | Models weakest here (BankerToolBench) |
| Trading comps / precedents | ✅ | BankerToolBench (10%), SpreadsheetBench 2, Finance Agent v2 (unverified) | |
| Pitchbook / CIM / investment memo | ✅ | BankerToolBench, FrontierFinance (LBO memo), APEX-Agents | Rubric-judged only |
| Equity research report | ✅ | FinDeepResearch, FinResearchBench | LLM-judged |
| Filing QA / beat-miss / adjustments | ✅ | Finance Agent Benchmark, FinanceBench, FinanceQA, FinSearchComp | Saturating or contaminated |
| IPO / S-1 diligence | ◐ | IPO Finance Agent | One issuer public |
| Journal entries / data entry | ◐ | APEX–Accounting (26), FinBalance, FinMaster | Single period |
| Account / bank reconciliation | ◐ | APEX–Accounting (61), AccountingBench, FinBalance, CFAgentBench, FinalityBench | Multi-month bank rec with timing items: only AccountingBench (closed) |
| Schedules & accruals (prepaids, deferred revenue, fixed assets) | ◐ | APEX–Accounting (45), AccountingBench | **No rollforward across periods** in open benchmarks |
| **Month-end close (full checklist, multi-period)** | ◐/✗ | AccountingBench (closed); APEX–Accounting (single period) | Major gap |
| Variance / flux analysis, budget vs. actual | ◐ | APEX–Accounting (28), Finch (planning & budgeting) | No multi-period FP&A cycle (budget, then actuals, then reforecast) |
| Consolidation / intercompany / FX | ✗/◐ | SpreadsheetBench 2 (consolidation modeling); APEX–Accounting excludes it | Gap |
| Revenue recognition (606/15), leases (842/16) | ✗ | — | Gap |
| Tax (corporate provision, VAT/GST) | ✗/◐ | TaxCalcBench (US personal), TheAgentCompany Form 6765, SpreadsheetBench 2 (deferred tax) | Gap |
| Audit fieldwork / XBRL review | ◐ | FinAuditing, FinTagging, AuditBench, FinMaster auditing, EDINET fraud | Detection QA only; no sampling or workpapers |
| **Covenant compliance certificate / borrowing base** | ✗ | (FrontierFinance lender models; BankerToolBench LevFin indirectly) | Gap; a natural verifiable multi-period task |
| **Credit memo / underwriting** | ◐ | MortarBench (mortgage, exact match), CACE-Bench (synthetic credit pipeline; GitHub only) | No corporate credit memo benchmark |
| Treasury / cash forecasting (13-week) | ◐ | EnterpriseArena, CEO-Bench, Vending-Bench (implicit) | No document-grounded rolling cash forecast |
| AP / AR / collections, three-way match | ◐ | CFAgentBench, CARB (unverified), Finch (AP/AR 10 workflows) | |
| Payments operations | ◐ | DABStep, FinalityBench | |
| **Portfolio rebalancing** (drift bands, tax lots, constraints) | ✗/◐ | InvestorBench (single asset), BizFinBench v2 (online allocation), FinGAIA (weakest category), MCP-Universe | Gap for deterministic, constraint-checked rebalancing |
| **Fund NAV / fund accounting / capital accounts / waterfall** | ✗ | — (searches returned nothing) | Clear gap |
| Wealth management / advisory | ◐ | Wealth-mgmt TheAgentCompany extension (12 task pairs), GDPval advisors | |
| Loan origination | ◐ | MortarBench | |
| Regulatory / compliance actions | ◐ | FinToolBench, ReguSim ([arXiv 2608.19974](https://arxiv.org/abs/2608.19974)), CFAgentBench approvals | |

---

## 6. Design implications for differentiating a new benchmark

These are suggestions drawn from the gaps above.

1. **Make time the core axis.** Use a persistent company world (or several) run for 6–24 monthly periods. Each period's close produces:
   - the ledger,
   - schedules (prepaids, deferred revenue, fixed assets, leases, debt),
   - reconciliations, and
   - an updated 3-statement model, cash forecast and covenant certificate.
   These outputs are the *inputs* to period t+1. Score per period so a long run gives a dense signal, and report both an "independent" score (oracle opening balances) and a "compounded" score (the agent's own balances). The difference between them measures error propagation.
2. **Hidden canonical event log as the oracle** (FinalityBench/FinBalance style). Generate the business's true transactions, then render them into messy, conflicting views: bank feed, PSP payouts, AP invoices (PDF and scans), payroll exports, emails and spreadsheet versions. Ground truth is exact; the agent sees realistic noise. Seed the world from real anonymized patterns (EnterpriseArena-style R→S) for realism.
3. **Mostly deterministic grading.** Use:
   - accounting identities (BS balances, cash ties to bank, subledger = GL control accounts);
   - **ledger replay** (reported vs. supported numbers);
   - **perturbation re-execution** of the agent's model (change an assumption and check that outputs move correctly);
   - covenant and ratio recomputation;
   - plug and hardcode detectors.
   Reserve rubric/LLM judging for narrative artifacts such as flux commentary and lender memos, and audit judge agreement.
4. **Inject errors and late information.** Plant misclassifications or missing accruals in early periods and surface evidence later; score detection and correction. Include restatement and true-up events.
5. **Non-US and multi-standard variants.** Use IFRS and a local-GAAP entity, multi-currency subsidiaries with consolidation and intercompany, and VAT/GST. Optionally include non-English source documents. Few existing benchmarks do this operationally.
6. **Under-covered archetypes as first-class tasks:** multi-period close, consolidation, covenant compliance certificate, 13-week cash forecast with variance to actuals, rolling reforecast, fund NAV / capital-account rollforward and waterfall, and constraint-checked portfolio rebalancing. All are naturally verifiable.
7. **Controls and human-in-the-loop.** Approval gates for payments and journal entries above materiality (CFAgentBench-style), segregation of duties, and a simulated controller or auditor to ask (TheAgentCompany / τ²-bench style). Score both inappropriate autonomy and over-asking.
8. **Integrity metrics as headline numbers:** fabricated-evidence rate, unsupported-number rate, plug usage, and citation of source documents (FinBalance found citation pressure barely helped).
9. **Reliability and cost:** report pass^k per period, tokens, cost and wall-clock time. Release an offline, date-anchored, containerized environment (Harbor/Inspect compatible, as BankerToolBench and APEX-Agents are) with a held-out private world set to limit contamination.

---

## 7. Unverified or partially verified items

- **SpreadsheetBench Verified:** composition and leaderboard figures (third-party aggregator; official site blocked).
- **SpreadsheetBench v1:** exact split between cell-level and sheet-level tasks.
- **Finance Agent v2 (Vals):** categories, size and scores (secondary sources only).
- **AccountingBench:** per-month accuracies and model list (blog and press; Penrose site blocked).
- **APEX-Agents:** later scores and 1.1 details. **APEX v1** (2025) not reviewed.
- **Vending-Bench 2:** leaderboard values.
- **Toolathlon:** finance-category Pass@1 values (table extracted as text; columns may be misaligned).
- **FinWorld:** KDD 2026 venue.
- **AuditBench:** size. **AuditFraudBench:** details.
- **CARB, LedgerBench-100, FactoryBench-100:** snippet-level only.
- **FinBen:** details from search results, not re-read. **OSWorld** (LibreOffice Calc tasks) was not reviewed.
- **Not found under these names:** EconAgentic, Finance-Bench-Long, FinModelBench, and an xbench finance track.
