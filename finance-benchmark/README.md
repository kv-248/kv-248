# Long-Horizon Finance Benchmark: Data Discovery

Phase 1 goal: **find real (not synthetic), scrapable data sources that support long-horizon,
spreadsheet-centric finance workflows**, and show that they do (proof-of-concept pulls and
workflow sketches). Workflows will later be curated by finance experts. Here we establish *scope*.

## Design stance (agreed in kickoff Q&A)

| Question | Answer |
|---|---|
| Agent environment | Spreadsheet-centric. Raw inputs (PDF incl. scans, CSV, XML, HTML) are transformed into a workbook env |
| Domains / personas | All (accounting ops, FP&A, investment research, credit, public finance, audit/regulatory, household/SMB) |
| "Long horizon" | A big chunk of a professional's job, composed of several finance concepts (e.g., an end-to-end rebalance), not a single lookup |
| Licensing | Research use is fine |
| Geography | Any / mixed; cross-jurisdiction is a plus |
| Messiness | All, including scanned PDFs |
| Env unit | Both deep (one entity, many periods) and broad (a universe of entities) |
| Multi-source | Combining sources is encouraged |
| Grading | Open; likely LLM judge, but natural numeric checks are a bonus |
| Purpose | Separate frontier models; difficulty comes largely from horizon |

## Contents

| Path | What |
|---|---|
| `docs/01_benchmark_survey.md` | ~60 recent finance / spreadsheet / long-horizon agent benchmarks (SpreadsheetBench 2, BankerToolBench, APEX, AccountingBench, Finance Agent, ...) and the gaps they leave |
| `docs/02_concept_library.md` | Plug-and-play finance concepts (A–K families) and how they compose into long workflows |
| `docs/03_source_catalog.md` | **Main deliverable:** ranked catalog of real data sources, scored for long-horizon scope, with workflow sketches |
| `docs/04_poc_results.md` | What we actually pulled in the sandbox and the natural ground-truth checks that held |
| `docs/05_top10_resources.md` | Top 10 sources: links, workflows, caveats (web view: https://claude.ai/artifact/SXFq2qdnq8UXEpiVb38SrD) |
| `docs/sources/*.md` | Raw per-slice research notes (funds, public finance, credit/distressed, corporate/accounting/markets) |
| `poc/` | Pull + validation scripts (stdlib + pandas/pyarrow) |
| `samples/` | Small env seeds (xlsx) + validation reports produced by the PoCs |

## Phase 1 results at a glance

* **12 ranked sources** (catalog §0) and **6 flagship long-horizon workflows** (catalog §3):
  municipal credit review, 24-month ABS surveillance desk, portfolio rebalancing (US target-date and
  India wealth desk), utility rate case, Chapter 11 monitoring, foundation year-end close.
* **8 proof-of-concept pulls on real data** (`docs/04_poc_results.md`): FERC Form 1 (375 utilities
  × 32 yrs), IRS 990 (14 yrs), ABS-EE (35.7M loan-months), Chicago checkbook, India AMC workbooks
  (13 AMCs, 715 schemes), Austin ACFR PDFs (17 yrs), N-PORT target-date funds, Call Report schema.
  In the six with an identity check (FERC, 990, ABS-EE, India AMC, ACFR, N-PORT) the source's own
  identities tie for 92–100% of records once conventions are handled, and the exceptions are real
  events (restatements, mergers, special items, sign conventions) that make good judgment
  checkpoints. Chicago was profiled only; Call Reports were schema-checked only.
* **Access caveat:** the sandbox blocks primary hosts (sec.gov, EMMA, FFIEC, …); PoCs used public
  S3, Kaggle, GitHub and HF datasets-server. Catalog §5 lists the hosts to allowlist for a full build.

## The selection principle in one line

> Prefer sources where **the source itself reports totals that bottom-up work must reproduce**
> (audited statements vs. transaction ledgers, servicer reports vs. loan tapes, reported NAV vs.
> holdings, Part XI vs. Part I). That keeps long, messy, real trajectories gradeable.
