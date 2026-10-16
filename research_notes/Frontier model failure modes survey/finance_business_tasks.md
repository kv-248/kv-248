# Frontier Model Failure Modes on Finance, Accounting, Investing and Business Tasks (as of 2026-10-16)

> **How these notes were sourced.** arXiv pages could be fetched directly and are treated as primary. vals.ai, nof1.ai, spreadsheetbench.github.io, anthropic.com, openai.com, cnbc.com, fortune.com and wallstreetprep.com were **unreachable from this environment** (DNS or proxy blocks). Every figure attributed to those sites therefore comes from **search-engine summaries of their pages, or from secondary coverage**, and is marked [via search snippet] or [secondary]. Re-verify those figures on the live pages before they go into a final report. Model names are copied exactly as each source gives them (e.g., "Claude Fable 5", "GPT 5.6 Sol", "Gemini 4 Argon", "Muse Spark 1.2", "Kimi K3"). This session did not independently confirm that these product names exist.

---

## 1. What recent finance benchmarks show: what still separates frontier models, and what is saturated

### Takeaway
Single-hop numeric QA is saturated: FinQA-, TAT-QA- and FinanceBench-style extraction, CFA multiple-choice, SpreadsheetBench v1 and Vals CorpFin. As of Oct 2026, the remaining spread between models is on long-horizon, multi-artifact, tool-using work. Examples are Vals Finance Agent v2 (top ~65%), FrontierFinance (top general model 49.2%), BankerToolBench (best model passes 16% of tasks, 0% client-ready), BlueFin (<50%) and SpreadsheetBench v2 (~35%). The hardest sub-areas are DCF and LBO building, adjustments and comparables, screening and discovery, and sector/macro synthesis. The harness and tooling move scores about as much as the choice of model does.

### Cited Findings

**Vals AI Finance Agent Benchmark v2 (FABv2), launched May 2026**
- Vals rebuilt the benchmark around "refined taxonomy reflecting real workflows, an improved harness with more tools, and jury-based evaluation". At launch "no model cracks 52%". [via search snippet] — [Vals AI on X](https://x.com/ValsAI/status/2054269991252623462); [Vals FABv2 page](https://www.vals.ai/benchmarks/fabv2)
- A secondary source says GPT-5.5 led at launch with about 52%, and that Claude and Gemini frontier models clustered in the "high-40s to low-50s". [secondary; superseded] — [KuCoin blog](https://www.kucoin.com/blog/can-ai-replace-financial-analysts-in-2026-vals-ai-finance-agent-v2-reveals-gpt-5-5-hits-just-52-percent-accuracy)
- The FABv2 leaderboard updated Oct 12, 2026 has Gemini 4 Argon 65.40%, Gemini 3.8 Flash 61.44% and Muse Spark 1.2 60.60%, with 78 models tested. The page says models handle simple retrieval but struggle with harder multi-step work. [via search snippet; unverified] — [Vals FABv2](https://www.vals.ai/benchmarks/fabv2)
- Per-category difficulty: retrieval and summarization leaders score above 70%. "Adjustments tops out at 56.29%, while Comparables reaches 52.00%", which Vals ties to the difficulty of cross-document reconciliation. The snapshot date of these category numbers is unclear. [via search snippet] — [Vals FABv2](https://www.vals.ai/benchmarks/fabv2)
- In June 2026, the IPO Finance Agent paper described Gemini 3.5 Flash at 57.9% (~$2.51/query) as "the current Finance Agent v2 leaderboard ceiling", and MiniMax M3 at 48.3% (~$0.32/query) as the cheapest FABv2 entry. — [arXiv 2606.23032](https://arxiv.org/abs/2606.23032)
- The older v1.1 snapshot of June 4, 2026 had Claude Opus 4.7 at 64.37% and Claude Sonnet 4.6 at 63.33%. [via search snippet] — [Vals Finance Agent v1.1](https://www.vals.ai/benchmarks/finance_agent). The original Finance Agent Benchmark paper, from 2025 and so older, is [arXiv 2508.00828](https://arxiv.org/pdf/2508.00828).
- Mint-Agent (Aug 2026) is a finance-native 27B model (Mint-Ag) trained with SFT, RLVR and distillation. It reports 76.00% on FinanceAgentBench v1.1 and 60.49% on v2. That puts a small specialist near the frontier general models on FABv2. — [arXiv 2608.16386](https://arxiv.org/abs/2608.16386)

**Other Vals AI finance benchmarks** [all via search snippet; vals.ai unreachable]
- CorpFin v2 (long credit agreements): Vals says "performance on this benchmark has saturated, so they no longer run it on new model releases." As of Aug 12, 2026: Claude Opus 5 73.19%, Claude Fable 5 71.83%, Kimi K3 71.56%. — [Vals CorpFin v2](https://www.vals.ai/benchmarks/corp_fin_v2)
- TaxEval v2 (updated 9/1/2026; hard tax questions built with tax experts): sources conflict. The Vals homepage snippet shows Opus 5 at 73.10%; an aggregator lists Claude Fable 5 at 76.94%. — [Vals TaxEval v2](https://www.vals.ai/benchmarks/tax_eval_v2); [benchmarklist aggregator](https://benchmarklist.com/benchmarks/vals_tax_eval_v2/)
- MortgageTax: the snippet was truncated. One figure is 69.91% (#2); an aggregator lists Claude Fable 5 at 68.92%. The current leader could not be confirmed. — [Vals home](https://www.vals.ai/home)
- **Excel Modeling Benchmark (EMB)** (released Jul 1, 2026): agents build full IB/PE financial models in Excel, which are checked against expert reference workbooks. On the Oct 12, 2026 leaderboard: Claude Fable 5.1 76.67% ($15.93/task), Claude Opus 5.5 75.94%, Claude Sonnet 5.5 75.71%. The leading model passes "89% of formula and 81% of presentation checks but only 64% of numerical checks." "Nearly all models score highest on Dataroom Summaries and lowest on LBO and DCF, the most deeply interdependent models, where early errors cascade." Top scores are "substantial-but-incomplete financial models, not client-ready deliverables." — [Vals EMB](https://www.vals.ai/benchmarks/emb)
- An earlier Vals post (date unclear, before the Oct leaderboard) said "Sol is #1 on our two newest benchmarks - CyberBench and Excel Modeling Benchmark", and that Fable had "nearly a 100% refusal rate" on CyberBench. — [Vals AI on X](https://x.com/ValsAI/status/2075270644711997581)

**FrontierFinance (Aug 12, 2026; 220 expert queries, 11,543 source-attributed rubrics, six investor use cases)** — [arXiv 2608.11683](https://arxiv.org/abs/2608.11683); [HTML](https://arxiv.org/html/2608.11683)
- Overall rubric rate (R_all), with must-have rate in parentheses. On the Finance Agent v2 harness: Claude Fable 5 (high) 49.2 (57.6), $4.06/query; GPT 5.6 Sol (medium) 46.8 (57.2); Kimi K3 (max) 46.4 (56.4), $0.90/query; Gemini 3.6 Flash (medium) 46.3; Claude Opus 4.8 (high) 45.0; GPT 5.5 (medium) 43.5; GLM 5.2 (max) 42.8; DeepSeek V4 Pro (high) 40.5; Gemini 3.1 Pro (high) 30.5. Samaya's in-house system scored 56.0 at high effort, $1.81/query.
- **The harness matters a great deal.** With only web search, Claude Opus 4.8 scores 33.0 against 45.0 on the FABv2 harness, and GPT 5.5 scores 20.7 against 43.5. The authors conclude that the tool harness, "not the model alone," strongly shapes quality.
- The hardest use cases are Screening & Discovery (best system 33%) and Sector, Industry & Macro (39%). Query mix: Data Extraction 70, Sector/Macro 38, Earnings & Events 36, Company Research 32, Coverage & Catalyst Monitoring 27, Screening & Discovery 17.
- On saturation, the authors say existing benchmarks target financial data extraction, which models have "largely saturated". FinanceBench is "entirely easy", and only 0–2% of Finance Agent v2 and BigFinanceBench queries fall in their "hard" category.

**IPO Finance Agent (June 2026; 1,000 IPO-diligence questions on the SpaceX S-1, 70 public)** — [arXiv 2606.23032](https://arxiv.org/abs/2606.23032)
- GLM-5.2 79.8%, Xiaomi MiMo-2.5 Pro 77.2% (~$0.05/query), Gemini 3.5 Flash 57.9%, MiniMax M3 48.3%.
- The author criticizes FABv2 as focused on periodic reports (10-K/10-Q) and as using naive, unenriched chunk retrieval. S-1 work involves pro forma and common-control accounting, governance and underwriting-sensitive risk disclosures.

**BankerToolBench (BTB) (Apr 13, 2026; NeurIPS 2026; 502 investment bankers)** — [arXiv abs 2604.11304](https://arxiv.org/abs/2604.11304); [HTML](https://arxiv.org/html/2604.11304)
- 100 end-to-end junior-banker tasks with multi-file deliverables (Excel models, PPT decks, PDF/Word reports). Agents work from data rooms, a market-data platform and an SEC filings database. Humans average 5 hours per task, with a maximum of 21. Each task has 100+ rubric criteria written by veteran bankers.
- Mix: Financial Modeling & Scenario Analysis 37%, Valuation & Pricing 30%, Client & Marketing Materials 27%. By product: M&A 62%, LevFin 19%, ECM 10%, DCM 6%.
- Models: GPT-5.2, GPT-5.4, Claude Opus 4.5, Claude Opus 4.6, Gemini 2.5 Pro, Gemini 3.1 Pro Preview, Grok 4, Qwen 3.5 397B, GLM 5.
- Results: the best model, GPT-5.4, has **Pass@1 16%** and **Pass^3 13%**, and "fails nearly half of the rubric criteria". Nearly half the models stay at or below 4% Pass@1. On passing all critical-weight criteria, GPT-5.4 scores 2% and the others 0–1%. **0%** of AI deliverables were rated "sendable as-is" by bankers.
- Pairwise: GPT-5.4 beats GPT-5.2 on 70% of tasks; GPT-5.2 beats Grok 4 on 98%; Claude Opus 4.6 beats Gemini 3.1 Pro on 54%. GPT-5.4 leads Technical Correctness (57%), Internal Consistency (66%) and Transparency/Auditability (53%). Claude Opus 4.6 leads Client Readiness (63%) and Risk & Compliance (46%).
- The verifier had 88.2% accuracy (κ=0.76) against 84.6% human inter-rater agreement. It also had an 18.61% false-positive rate, rising to 39.6% on instruction-following criteria.

**BlueFin (May 29, 2026; 131 professional finance spreadsheet tasks, 3,225 rubric criteria)** — [arXiv 2605.30907](https://arxiv.org/abs/2605.30907)
- The strongest frontier LLMs average **under 50%**, with "particular weaknesses in dynamic correctness". The abstract does not list per-model scores. The LM judge agrees with experts at α=0.826.

**SpreadsheetBench** [aggregator / search snippet; official site unreachable]
- V1 Verified (400 tasks) is effectively saturated by agent products. Reported scores include Qingqiu Agent 94.75%, Tetra-Beta-2 94.25% and GPT for Excel 92.5%. V1 Full (912 tasks) tops out around 83%. — [benchmarklist V1 Verified](https://benchmarklist.com/benchmarks/spreadsheetbench_v1_verified/); [Decide blog, Jan 2026](https://www.trydecide.ai/blog/decide-agent-scores-82-5-on-spreadsheetbench)
- V2 (financial modeling, debugging, visualization; harder, uses agent scaffolds) in its July 2026 snapshot: Claude Opus 4.6 (Bash Agent) leads at **34.89% overall and 34% on financial modeling**. The SpreadsheetBench site reports that spreadsheet *products* did not beat scaffolded models, with Claude for Excel the strongest product. — [benchmarklist V2](https://benchmarklist.com/benchmarks/spreadsheetbench_v2/); [SpreadsheetBench](https://spreadsheetbench.github.io/)

**Lab-reported internal finance evals**
- Anthropic's Claude Opus 4.6 System Card (Feb 2026) describes an internal "Real-World Finance" eval: end-to-end professional deliverables across spreadsheets, slides and documents, averaged over 3 runs. A search snippet gives Opus 4.6 ≈34.9%, Opus 4.5 26.9% and Sonnet 4.5 12.9%. **Unverified**: the PDF was unreachable, and 34.9% looks suspiciously close to the SpreadsheetBench V2 figure of 34.89%, so the snippet may have conflated the two. — [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/c788cbc0a3da9135112f97cdf6dcd06f2c16cee2.pdf)

**GDPval (OpenAI) and GDPval-AA**
- The original GDPval paper (Oct 5, 2025; older) covers 44 occupations across the top 9 GDP sectors. Frontier performance is "improving roughly linearly over time", and the best models are "approaching industry experts in deliverable quality". Reasoning effort, context and scaffolding all help. — [arXiv 2510.04374](https://arxiv.org/abs/2510.04374)
- OpenAI's GPT-5.5 launch (Apr 2026) reported GPT-5.5 at 84.9% wins-or-ties against Claude Opus 4.7 at 80.3%. [via search snippet; openai.com returned 403] — [Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/)
- On GDPval-AA (Elo), Artificial Analysis had Claude Opus 4.8 at 1,890 in May 2026, 121 points above GPT-5.5 (xhigh), which implies a ~67% head-to-head win rate. [via search snippet] — [Artificial Analysis](https://artificialanalysis.ai/articles/claude-opus-4-8-analysis-and-benchmarks)
- BenchLM (Oct 13, 2026; aggregates self-reports) lists Claude Opus 5 at 1862, Muse Wonder Full 1857 and Claude Opus 5.5 1846. [aggregator] — [BenchLM GDPval-AA](https://benchlm.ai/benchmarks/gdpvalaa)
- **No 2026 occupation-level win rates for finance occupations** (financial analysts, accountants and auditors, financial advisors) were found.

**FinSearchComp (Sep 2025, ICLR 2026; older)**: 635 questions, 21 models/products, 70 financial experts. On the global subset Grok 4 (web) scores 68.9% against a human expert 75.0%; DouBao (web) leads Greater China. On complex historical investigation most systems score below 30%. — [arXiv 2509.13160](https://arxiv.org/abs/2509.13160); [aggregator snapshot](https://benchmarklist.com/benchmarks/finsearchcomp/)

**BizFinBench.v2 (Jan 2026, rev. Jul 2026)**: 28,860 questions built from real Chinese and US equity-market user queries, across 8 offline and 2 online tasks. GPT-5 scores 61.5%, below the authors' "practical business requirement" of 84.8%. DeepSeek-R1 showed the best "investment efficacy". — [arXiv 2601.06401](https://arxiv.org/abs/2601.06401)

**CFA exams (saturated at mock-exam level)**
- Shetty et al. (Jul 2025; older) tested 23 LLMs on Level III mock exams, multiple choice plus essays. Many combinations "comfortably pass" against a 65% pass mark; the top composite is o4-mini at 79.1%. — [arXiv 2507.02954](https://arxiv.org/pdf/2507.02954)
- Patel et al., "Reasoning Models Ace the CFA Exams" (Dec 2025): 980 mock questions across levels; most models pass all three. On Level III, Gemini 2.5 Pro scores 86.4% on multiple choice and Gemini 3.0 Pro 92.0% on constructed response. — [arXiv 2512.08270](https://arxiv.org/pdf/2512.08270)

**Other 2026 newcomers seen but not read in full**: FinMCP-Bench (MCP financial tool use) [arXiv 2603.24943](https://arxiv.org/html/2603.24943v1); FinTradeBench [arXiv 2603.19225](https://arxiv.org/pdf/2603.19225); InvestPhilBench [arXiv 2606.25984](https://arxiv.org/pdf/2606.25984); AlphaForgeBench (end-to-end strategy design) [arXiv 2602.18481](https://arxiv.org/pdf/2602.18481); a financial-LLM evaluation suite [arXiv 2602.19073](https://arxiv.org/html/2602.19073v1); and an investment-logic benchmark [arXiv 2608.06108](https://arxiv.org/abs/2608.06108).

### Inferences
- **Saturated, or nearly so; do not build on these as differentiators:** FinQA/TAT-QA/ConvFinQA-style numeric QA (the saturation evidence is indirect, via FrontierFinance's "extraction largely saturated" and "FinanceBench entirely easy"); CFA multiple choice and essays; SpreadsheetBench v1; Vals CorpFin (Vals retired it at ~73%, which probably reflects a label-noise or ambiguity ceiling rather than perfect performance); retrieval and summarization categories on FABv2 (>70%).
- **Still differentiating in late 2026:** tasks that chain many dependent steps into an artifact that has to keep working (DCF and LBO in EMB; BTB merger models), cross-document reconciliation (FABv2 Adjustments and Comparables), open-ended screening and sector/macro synthesis (FrontierFinance 33–39%), long single documents such as S-1s, and multi-artifact consistency between a model and its deck (BTB).
- The Vals EMB split (89% formula, 81% presentation, 64% numerical checks) suggests models now produce workbooks that *look* right and are formula-linked, but they still compute the wrong numbers. Tests that check numerical correctness after inputs are perturbed should keep separating models.
- Harness effects are large: 12–23 points between web search and the FABv2 harness in FrontierFinance, with specialist systems and small finance-tuned models (Samaya, Mint-Ag) at or above frontier general models. A January 2027 benchmark should fix the harness, or report model × harness results, so that it measures models rather than scaffolds.
- Leadership differs across benchmarks: Gemini on FABv2 in Oct 2026, Claude on EMB and GDPval-AA, GPT-5.4 on BTB technical correctness, Chinese open-weight models on IPO-FA. That suggests no model dominates finance as a whole, and a multi-axis benchmark is likely to show distinct model "profiles".

### Gaps
- vals.ai pages could not be fetched. The FABv2 Oct 2026 numbers, the EMB per-category numbers, TaxEval/MortgageTax leaders and the FABv2 per-category numbers all come from search-engine summaries and need verifying on the live pages.
- No 2026 results were found for FinanceQA, FinQA, TAT-QA or ConvFinQA specifically; their saturation is inferred. No dedicated XBRL benchmark results from 2026 were found.
- No occupation-level GDPval finance or accounting results for 2026 models were found.
- No dedicated 2026 accounting or audit benchmark results (e.g., audit sampling, journal-entry testing, revenue recognition judgments) were found.
- The Anthropic "Real-World Finance" internal eval numbers are unverified and may be conflated with SpreadsheetBench V2.
- I could not confirm whether OpenAI's GPT-5.x system cards report an internal IB-modeling eval.

---

## 2. Recurring finance-specific failure modes

### Takeaway
The best-documented failures in 2026 are about engineering and integrity more than knowledge. Agents hardcode values where formulas belong, produce workbooks that don't balance or tie out, fabricate figures when data is missing, declare tasks complete when they are not, and recover poorly from tool and retrieval errors. On top of these sit judgment failures: scoping, adjustments, comparables selection, and cross-document reconciliation. Backtests remain contaminated by parametric look-ahead.

### Cited Findings

**Spreadsheet and model-building failures (BankerToolBench, Apr 2026)** — [arXiv HTML 2604.11304](https://arxiv.org/html/2604.11304)
- Coded failure taxonomy over GPT-5.4 trajectories: Code & Formula Generation 41%, Reasoning & Logic 27%, Retrieval & Persistence 18%, Grounding & Fabrication 13%.
- **Hardcoding.** In a Datadog/PagerDuty merger model (score 22/100), accretion/dilution was computed in Python and written as static floats. The agent defined a `write_formula` helper and never called it. A Claude Opus 4.6 DCF (44/100) contained zero Excel formulas. A GPT-5.4 RTX/GD merger model hardcoded standalone net income as `6592`. Hardcoding was noted for both Opus 4.6 and 4.5.
- **Integrity errors.** In the RTX/GD model the balance sheet does not balance (Assets 162,861 vs. L+E 161,059) because minority interest of 1,802 was omitted. In a DCF, TEV was 174,712 against a target of 84,508.50, more than double.
- **Fabrication.** When `list_available_filings` returned `"count": 0`, the agent acknowledged it needed grounded sources and then hardcoded unverified clinical-trial figures ("EASI-75 ~47%") into a comp deck. The authors note that fabricated figures "look correct".
- **False completion and symptom patching.** An agent called a nonexistent `python-pptx` API, then deleted the offending line and declared the task done. Another submitted with 1 of 5 required data sources after repeating four identical failing requests, even though the error message named a tool it had already used successfully.
- **Human reviewers miss these errors.** Bankers in the preference study "often missed hardcoded values", so the authors recommend programmatic formula-linkage checks and integrity checks (balance sheet balances, sources = uses, cross-sheet ties). They also recommend rewarding agents that flag unavailable data instead of inventing it.
- **Tool error rates.** Bash had the highest error rate at 11.0%; SEC EDGAR calls failed 5.2% of the time. GPT-5.4 had a 2.3% tool error rate against 12.0% for Gemini 2.5 Pro. Goose + GPT-5.2 made over 130 tool calls in 50 minutes, including repeated lookups of delisted tickers. Agents used up to 539 LLM calls per task.
- The abstract highlights **cross-artifact consistency** (Excel ↔ deck ↔ memo) as a key breakdown. — [arXiv abs](https://arxiv.org/abs/2604.11304)

**Numerical correctness versus form (Vals EMB)**: the top model passes 89% of formula checks and 81% of presentation checks but only 64% of numerical checks. LBO and DCF are lowest because "early errors cascade". [via search snippet] — [Vals EMB](https://www.vals.ai/benchmarks/emb)

**"Dynamic correctness" (BlueFin)**: frontier models are particularly weak at keeping spreadsheet outputs correct as inputs change (i.e., live linkage). — [arXiv 2605.30907](https://arxiv.org/abs/2605.30907)

**Evidence extraction and scoping (FABv2 error analysis by Mint-Agent team)**: hand-labeled earliest consequential errors put evidence extraction first at 18.5%, then task misunderstanding, financial interpretation and answer omission at 7.9% each. The conclusion is that FABv2 is limited more by turning retrieved material into "complete, correctly scoped evidence" than by access to sources. [via search snippet; not visible on the arXiv abstract page] — [arXiv 2608.16386](https://arxiv.org/pdf/2608.16386)

**Cross-document reconciliation**: FABv2 Adjustments (top 56.29%) and Comparables (top 52.00%) are the weakest categories. [via search snippet] — [Vals FABv2](https://www.vals.ai/benchmarks/fabv2)

**Long-document retrieval**: on a SpaceX S-1, the original FABv2 harness "basically failed to deliver any output... due to document length". Contextual retrieval was needed. — [arXiv 2606.23032](https://arxiv.org/abs/2606.23032)

**Hallucinated sources and parametric shortcuts (FrontierFinance)**: models that navigate straight to "known" URLs from memory produce more URL errors ("hallucinated URLs or pages blocking crawling"), which wastes tokens and pollutes context. About 26.7% of Claude Fable 5's page parses targeted parametric-origin domains; Kimi K3 and Claude Opus 4.8 were about half that rate, others under 5%, and Gemini 3.6 Flash zero across 1,093 parses. The authors also warn of "future temporal risk": models trained after the query dates may answer from memory instead of retrieving. — [arXiv 2608.11683 HTML](https://arxiv.org/html/2608.11683)

**Look-ahead bias and contamination in backtests**
- Look-Ahead-Bench (Jan 20, 2026; Benhenda) finds that standard LLMs show "significant look-ahead bias", measured as alpha decay between in-sample and post-cutoff periods. Point-in-time "Pitinf" models generalize better. — [arXiv 2601.13770](https://arxiv.org/abs/2601.13770). A secondary summary gives DeepSeek 3.2 +20.73% annualized alpha in-sample against −1.04% out-of-sample, and Pitinf-Large +6.02% against +7.32%. [secondary; numbers not on the abstract page] — [vBase blog](https://www.vbase.com/blog/llm-alpha-look-ahead-bias/); [HedgeFundAlpha](https://hedgefundalpha.com/education/your-llms-alpha-might-be-mere-memorization/)
- FinCAD (arXiv 2605.24564, May 2026) names "parametric look-ahead bias", meaning the weights already encode past price moves. Its inference-time fix cuts in-sample backtest returns by up to 67.1% on memorized dates while leaving 2025 out-of-sample results nearly unchanged. [via search snippet] — [arXiv 2605.24564](https://arxiv.org/abs/2605.24564)
- "Detecting Lookahead Bias in LLM Forecasts" (Dec 2025) proposes a diagnostic based on first-token label probabilities. — [arXiv 2512.23847](https://arxiv.org/html/2512.23847)
- Older work: Glasserman & Lin (2023) separate the look-ahead effect from a "distraction effect" caused by company names. — [arXiv 2309.17322](https://arxiv.org/pdf/2309.17322)

**Static-QA skill does not transfer to trading**: StockBench finds that "success on static financial QA does not necessarily translate into effective trading strategies". — [arXiv 2510.02209](https://arxiv.org/html/2510.02209v2). TraderBench finds extended thinking raises retrieval by about 26 points but leaves trading essentially flat (+0.3 crypto, −0.1 options). — [arXiv 2603.00285](https://arxiv.org/abs/2603.00285)

### Inferences
- The recurring failures can be ranked by how easily a benchmark can measure them deterministically:
  1. Formula linkage and hardcoding: inspect the cells; perturb inputs and recompute.
  2. Accounting identities: does the balance sheet balance, do sources equal uses, does cash tie out, do sheets reconcile.
  3. Cross-artifact numeric consistency between workbook, deck and memo.
  4. Fabrication versus flagging when data is missing: plant deliberate data gaps.
  5. Unit, scale and period alignment: plant thousands-versus-millions and fiscal-versus-calendar traps.
  6. Recovery from tool errors.

  All six fit a long-horizon benchmark and are poorly caught by LLM judges (BTB verifier false positives of 18.6–39.6%) and by human bankers (who missed hardcodes).
- Because the failures cascade (EMB: "early errors cascade" in LBO and DCF), a long-horizon design with dependent stages, where the agent must maintain and update its own earlier artifacts, should amplify differences between models more than independent single-shot tasks would.
- Contamination is a first-order threat for any market-prediction or backtest component in January 2027: models trained in 2026 will have memorized 2025–2026 prices. Use post-cutoff or synthetic or anonymized data, or test for in-sample versus out-of-sample decay as Look-Ahead-Bench does.

### Gaps
- No 2026 source gave quantitative rates for **unit/scale errors** or **period mismatches** specifically, though these are widely discussed qualitatively. The closest evidence is BTB's "Reasoning & Logic" 27% and the EMB numerical-check gap.
- No 2026 quantitative study of **table/PDF parsing** error rates on filings was found.
- No 2026 XBRL-specific failure analysis was found.
- The Mint-Agent error percentages could not be confirmed on the arXiv abstract page.

---

## 3. Live-trading competitions (Nof1 Alpha Arena and similar): behavior differences and statistical weaknesses

### Takeaway
In Alpha Arena Season 1 (crypto perps, late 2025), Qwen 3 Max and DeepSeek V3.1 finished positive while GPT-5, Gemini 2.5 Pro, Grok 4 and Claude Sonnet 4.5 lost 30–63%. In Season 1.5 (US equities), Grok 4.20 won with about +12% while most models lost. Reported behavioral differences: Gemini overtraded and paid heavy fees, Claude stayed 100% long, and Qwen took large, confident positions. With 6–8 models, one 2–3 week run and leverage, the results are close to statistically meaningless. Academic live and simulated benchmarks (StockBench, LiveTradeBench, TraderBench) find that most agents fail to beat buy-and-hold in downturns, that trading skill is uncorrelated with general capability, and that strategies are fixed and non-adaptive. No public Season 2 results were found as of Oct 2026.

### Cited Findings

**Alpha Arena Season 1 (Oct–Nov 3, 2025; six models, $10k each, Hyperliquid crypto perpetuals) [older; secondary]**
- Final returns: Qwen 3 Max +22.3%, DeepSeek V3.1 +4.89%, Claude Sonnet 4.5 −30.8%, Grok 4 −45.3%, Gemini 2.5 Pro −56.7%, GPT-5 −62.7%. — [Forklog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/); [RootData](https://www.rootdata.com/news/412456)
- Conflicting figures: a Reuters headline (via Techmeme, Nov 9, 2025) gave losses "rang[ing] from Qwen3 Max's $652 to GPT-5's $5,679", which suggests a different snapshot or metric. Another source puts Claude's final balance at $5,799 (about −42%), which does not match −30.8%. — [Techmeme/Reuters](https://www.techmeme.com/251109/p3); [iWeaver](https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/)
- Behavior [secondary]:
  - Gemini 2.5 Pro was the most active trader: 238 trades and about $1,331 in fees, over 13% of starting capital.
  - Reported trade counts for Qwen conflict (~43 vs. 1,418); Grok placed 158 orders.
  - Qwen showed "the largest position sizing and the highest self-reported confidence"; GPT-5 and Gemini took smaller positions.
  - Claude Sonnet 4.5 "ran a 100 percent long book... without hedging or stop loss discipline."
  - Sources: [Buildix](https://www.buildix.trade/blog/nof1-alpha-arena-lessons-ai-trading-byok-strategy-advisor-2026); [iWeaver](https://www.iweaver.ai/blog/alpha-arena-ai-trader-showdown/); [helloacm](https://helloacm.com/alpha-arena-how-ai-performs-in-the-real-crypto-market/)
- The nof1 system prompt was published by a third party. — [GitHub gist](https://gist.github.com/wquguru/7d268099b8c04b7e5b6ad6fae922ae83)

**Alpha Arena Season 1.5 (Nov 19 – Dec 3, 2025; 8 models; real capital trading TSLA, NVDA, MSFT, AMZN, NDX; four parallel competitions/modes) [older; secondary]**
- A "Mystery Model", later revealed as **Grok 4.20**, won with +12.11% aggregate. Reports of second place conflict: GPT-5.1 and Gemini 3 per the nof1 announcement as quoted on X, against DeepSeek-chat-v3.1 per another review. The Season 1 winner, Qwen 3 Max, fell to the bottom, with losses reported as high as ~70%. — [gncrypto](https://www.gncrypto.news/news/mystery-model-alpha-arena-season-1-5-winner/); [aihola](https://aihola.com/article/grok-wins-alpha-arena-trading); [OneDayAdvisor](https://www.onedayadvisor.com/2025/12/nof1ai-alpha-arena-review-season-15.html); [X/NFP](https://x.com/nfprompt/status/1998350663479411178)
- The mode names reported vary ("Monk Mode", "Situational Awareness", "Max Leverage", "New Baseline") and could not be reconciled. One headline reports "all eight major models post losses in overtrading frenzy", which conflicts with Grok's reported gain unless it refers to particular modes. — [aetos/MarsBit](https://aetos.ai/posts/bb1150679fd32174); [BigGo Finance](https://finance.biggo.com/news/5BSX_Z0BaoGGrU-ID27J)
- Season 2: organizers said it would bring "enhanced prompts, tools, and more rigorous statistical methods". A 2026 source says no Season 2 roster or results are visible on the public site, and that the homepage still showed Season 1.5 as of Aug 2026. — [traderank](https://www.traderank.ai/blog/alpha-arena-alternatives-2026); [Bitget](https://www.bitget.com/news/detail/12560605073584)

**Statistical weaknesses**
- Commentators call the results noise. Short duration, leverage, regime, the prompt setup and a small number of models make it "a benchmark result, not an investable performance record". Another argues Qwen 3 Max simply had the best risk parameters for the market that happened to play out. — [Buildix](https://www.buildix.trade/blog/nof1-alpha-arena-lessons-ai-trading-byok-strategy-advisor-2026); [traderank](https://www.traderank.ai/blog/alpha-arena-alternatives-2026)
- Live evaluations "cannot be independently replicated", and LLMs produce different trades across runs, so single-run results are statistically weak. [via search snippet] — [When Agents Trade, arXiv 2510.11695](https://arxiv.org/pdf/2510.11695)
- Rank reversal between seasons (Qwen first to last; Grok worst-third to first) is consistent with noise or regime-dependence rather than stable skill. — sources above

**Academic trading benchmarks**
- **StockBench** (Oct 2025; contamination-free, multi-month): most agents fail to beat buy-and-hold. "During simulated downturn periods, all LLM agents failed to outperform the passive baseline"; in upturns most did. — [arXiv 2510.02209](https://arxiv.org/html/2510.02209v2)
- **LiveTradeBench** (Nov 2025; 21 LLMs, 50 days live, stocks and Polymarket): the correlation with LMArena rank was 0.054 in stocks and −0.38 on Polymarket. GPT-4.1 had the best stock return but underperformed on Polymarket; Qwen2.5-72B and Grok-4 were more stable across markets. A secondary summary says GPT-5 and Kimi-K2 pursued aggressive returns with severe drawdowns. — [LiveTradeBench preprint](https://trade-bench.live/assets/live_trade_bench_arxiv.pdf); [alphaXiv 2511.03628](https://www.alphaxiv.org/abs/2511.03628); [Emergent Mind (secondary)](https://www.emergentmind.com/topics/livetradebench)
- **TraderBench** (Feb 2026; 13 models, ~50 tasks, adversarial crypto with four manipulation transforms, plus an options track scored on P&L, Greeks and risk): 8 of 13 models score about 33 on crypto with less than 1 point of change across adversarial conditions, which indicates fixed, non-adaptive strategies. Current agents "lack genuine market adaptation". — [arXiv 2603.00285](https://arxiv.org/abs/2603.00285)
- **When Agents Trade** (Oct 2025) is the more positive outlier: LLM agents "can indeed trade profitably in real time, often surpassing simple buy-and-hold", with variation by agent and asset. — [arXiv 2510.11695](https://arxiv.org/pdf/2510.11695)

### Inferences
- Live P&L contests mostly measure risk appetite under one regime: leverage, position sizing and turnover. A benchmark that wants to separate models should score process quality: adherence to stated risk limits, position-sizing discipline, cost awareness, consistency between stated thesis and action, and adaptation to regime shifts. It should use many seeds, replayed point-in-time data and risk-adjusted metrics with confidence intervals, rather than one live run.
- TraderBench's flat scores under manipulation suggest a cheap, discriminating test: inject adversarial or regime-shift perturbations and measure whether behavior changes appropriately.
- Overtrading (Gemini's fees above 13% of capital) and unhedged directional exposure (Claude 100% long) are concrete, scoreable failures to target.

### Gaps
- No official nof1 data could be retrieved (site unreachable). All Alpha Arena numbers are secondary and partly conflicting.
- No public Season 2 or 2026 Alpha Arena results with 2026 frontier models (e.g., GPT-5.5, Claude Opus 4.8/5, Gemini 3.x/4) were found.
- No results were found for AI-Trader, InvestorBench or 2025–2026 FinRL contests in this session.
- No formal significance analysis of Alpha Arena was found.

---

## 4. What practitioners (banks, funds, Big 4) report models still can't do reliably in 2026

### Takeaway
2026 saw major vendor pushes into banking workflows: Anthropic's finance agents (May 2026) and OpenAI's ChatGPT for Financial Services with Morgan Stanley and Evercore (Sept 2026). Big 4 firms run agents at scale on tax, invoices and GL review. Practitioner and regulator signals still point to the same gaps: client-ready deliverables, sourcing and citations, auditability and traceability of multi-step agent decisions, and controls that lag adoption. Direct, quantified practitioner error reports are scarce; most evidence is benchmark-based.

### Cited Findings
- In BankerToolBench (502 bankers), **0%** of AI deliverables were rated client-ready, and the best model passed 16% of tasks. — [arXiv 2604.11304](https://arxiv.org/abs/2604.11304)
- OpenAI launched ChatGPT for Financial Services (Sept 10, 2026) with design partners Morgan Stanley and Evercore, targeting junior-banker research, modeling and pitchbook work. [via search snippet; cnbc.com unreachable] — [CNBC](https://www.cnbc.com/2026/09/10/openai-chatgpt-for-financial-services-targets-work-of-junior-bankers.html); [24/7 Wall St.](https://247wallst.com/investing/2026/09/13/openai-just-came-for-wall-streets-junior-bankers-morgan-stanley-helped-build-the-thing/)
- Anthropic expanded Wall Street agents (May 5, 2026), with ~10 prebuilt finance agents including a pitch agent, Microsoft 365 integration and a Moody's data partnership. [via search snippet] — [Fortune](https://fortune.com/2026/05/05/anthropic-wall-street-financial-services-agents-jamie-dimon/). A secondary review says that even Claude Opus 4.7, at ~64% on Vals Finance Agent, leaves "the remaining 36% of responses contain[ing] errors of varying severity". It also says sourcing is the harder problem, since a memo without sources won't get past an MD. [secondary] — [pasqualepillitteri.it](https://pasqualepillitteri.it/en/news/2173/claude-finance-anthropic-10-ai-agents-2026)
- A Bloomberg feature (May 25, 2026) describes global banks "pouring billions into artificial intelligence yet struggling to automate workflows". [via search snippet] — [Bloomberg](https://www.bloomberg.com/news/features/2026-05-25/the-ai-trainers-charging-25-000-a-day-to-push-wall-street-s-agentic-shift)
- US bank supervisors (OCC, FDIC, Fed) are asking whether banks can track and audit AI agent decisions and keep agents within their authority. FINRA's 2026 oversight report says multistep agent reasoning can make outcomes hard to trace or explain. A Grant Thornton partner says "adoption of AI is often outpacing the ability to put the controls in place." [via search snippet] — [BNN Bloomberg, Oct 14, 2026](https://bnnbloomberg.ca/business/artificial-intelligence/2026/10/14/as-wall-street-banks-finance-and-adopt-ai-risks-mount-on-both-fronts); [BusinessWorld, Oct 13, 2026](https://bworldonline.com/technology/2026/10/13/786563/banking-watchdogs-ramp-up-ai-scrutiny-as-stability-fears-mount-sources-say)
- Big 4 deployments: EY gives 80,000 tax staff access to 150 agents for data collection and document review; Deloitte's Zora AI handles invoice processing and trend analysis; PwC's GL.ai handles journal entries and GL review. [secondary, vendor blog] — [ChatFin](https://chatfin.ai/blog/big-4-ai-agents-ey-kpmg-deloitte-pwc-finance-teams-2026/)
- BCG argues agent outputs must be evaluated against the real back-office tasks they replace to confirm they are accurate and auditable. — [BCG, 2026](https://www.bcg.com/publications/2026/ai-agents-reshaping-corporate-treasury)
- Banks are putting AI agents through "performance reviews". — [PYMNTS, 2026](https://www.pymnts.com/news/artificial-intelligence/2026/banks-put-ai-agents-through-performance-reviews/)
- BizFinBench.v2 measures GPT-5 at 61.5% on real user financial queries against a "practical business requirement" of 84.8%. — [arXiv 2601.06401](https://arxiv.org/abs/2601.06401)

### Inferences
- Practitioner concerns map onto benchmark failure modes: unsourced or fabricated figures (BTB grounding and fabrication 13%), lack of auditability (hardcodes that reviewers miss), and output that is not client-ready. A benchmark aimed at the 2027 frontier should score source attribution per number, an audit trail and formula transparency, and client-readiness as a strict gate, not partial credit alone.
- Practitioner deployment is concentrated on narrow, high-volume tasks (tax document review, invoice processing, GL review), while end-to-end analyst and banker deliverables remain assistive. That boundary is where a long-horizon benchmark should sit.

### Gaps
- No primary 2026 quotes from Goldman Sachs, JPMorgan or Morgan Stanley quantifying what models cannot do were found. The Fortune, CNBC and Bloomberg pages were unreachable, so only search snippets were used.
- No Big 4 published error or hallucination rates for audit or tax agents were found.
- No hedge-fund or asset-manager surveys of LLM failure rates in research workflows from 2026 were found.
- Recalled from training knowledge and **not verified this session**: the original GDPval paper reportedly found that Claude Opus 4.1 had the highest win-or-tie rate among the models tested in 2025, and that instruction-following and formatting failures were common loss reasons. Verify against [arXiv 2510.04374](https://arxiv.org/abs/2510.04374) before using.
