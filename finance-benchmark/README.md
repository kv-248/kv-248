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
| `docs/sources/*.md` | Raw per-slice research notes (funds, public finance, credit/distressed, corporate/accounting/markets) |
| `poc/` | Pull + validation scripts (stdlib + pandas/pyarrow) |
| `samples/` | Small env seeds (xlsx) + validation reports produced by the PoCs |

## The selection principle in one line

> Prefer sources where **the source itself reports totals that bottom-up work must reproduce**
> (audited statements vs. transaction ledgers, servicer reports vs. loan tapes, reported NAV vs.
> holdings, Part XI vs. Part I). That keeps long, messy, real trajectories gradeable.
