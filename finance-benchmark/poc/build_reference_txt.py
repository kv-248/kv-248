"""Build the plain-text reference files from the repo docs and the video dataset.

  python3 -I build_reference_txt.py [--transcripts /tmp/yt_cache]

Writes ../FINANCE_BENCHMARK_REFERENCE.txt (links, insights, workflows) and
../VIDEO_TRANSCRIPTS.txt (timestamped transcripts of the analysed videos).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BAR = "=" * 100
SUB = "-" * 100


def section(title: str) -> str:
    return f"\n\n{BAR}\n{title}\n{BAR}\n"


def md_to_txt(s: str) -> str:
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 <\2>", s)  # [text](url) -> text <url>
    s = s.replace("**", "").replace("`", "")
    return s


def md_slice(path: pathlib.Path, heading: str) -> str:
    """Text from the first heading matching `heading` (regex) to the next heading of the same or
    higher level."""
    lines = path.read_text().splitlines()
    for i, l in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)", l)
        if m and re.search(heading, m.group(2)):
            level = len(m.group(1))
            out = [l]
            for l2 in lines[i + 1:]:
                m2 = re.match(r"^(#+)\s", l2)
                if m2 and len(m2.group(1)) <= level:
                    break
                out.append(l2)
            return md_to_txt("\n".join(out)).strip()
    return f"(section '{heading}' not found in {path.name})"


def md_all_slices(path: pathlib.Path, heading: str, parent_level: int) -> str:
    """Every section whose heading matches, each prefixed with its parent heading."""
    lines = path.read_text().splitlines()
    out, parent = [], ""
    for i, l in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)", l)
        if not m:
            continue
        if len(m.group(1)) == parent_level:
            parent = m.group(2)
        if re.search(heading, m.group(2)):
            level = len(m.group(1))
            chunk = [f"## {parent}"]
            for l2 in lines[i + 1:]:
                m2 = re.match(r"^(#+)\s", l2)
                if m2 and len(m2.group(1)) <= level:
                    break
                chunk.append(l2)
            out.append(md_to_txt("\n".join(chunk)).strip())
    return "\n\n".join(out)


# ---------------------------------------------------------------------------------------------
HEADER = """FINANCE BENCHMARK: DATA DISCOVERY & WORKFLOW GROUNDING. CONSOLIDATED REFERENCE
Long-horizon, spreadsheet-centric finance agent benchmark. Phase 1 (data discovery) + workflow
grounding from practitioner videos. Generated from the repository by poc/build_reference_txt.py.

Repository branch : https://github.com/kv-248/kv-248/tree/claude/finance-benchmark-data-discovery-q6nfcd/finance-benchmark
This file         : finance-benchmark/FINANCE_BENCHMARK_REFERENCE.txt
Transcripts       : finance-benchmark/VIDEO_TRANSCRIPTS.txt (70 videos, timestamped auto-captions)

Contents
  1. Quick links (pages, repo files)
  2. What we are building (scope decisions, definitions, selection principle)
  3. Benchmarks surveyed (with links), gaps, coverage map, design implications
  4. Top 10 data sources (links, what we pulled, natural checks, workflows, caveats)
  5. Other sources, mirrors and the avoid list
  6. Access notes (what the sandbox could and could not reach)
  7. Proof-of-concept pulls and the real-data traps they exposed
  8. Reference workflow video: Otis 3-statement model (verified against transcript)
  9. All 71 practitioner videos (link, inputs, deliverable, timestamped steps, checks, judgment)
 10. Insights from the videos
 11. Workflows we can build (same level as the reference; flagship workflows; concept library)
 12. Caveats
 13. Appendix: every URL cited in the research notes
"""

QUICK_LINKS = """Pages (claude.ai artifacts; private to the owner unless shared)
  Phase 1 progress page ........ https://claude.ai/artifact/PJTfSQ1iQPe6rpMguiPesH
  Top 10 finance data sources .. https://claude.ai/artifact/SXFq2qdnq8UXEpiVb38SrD
  Analyst workflows on video ... https://claude.ai/artifact/TmgaT9fedrnJK8ZXNDCVRJ

Repository files (under finance-benchmark/)
  README.md                         overview and phase-1 results
  docs/01_benchmark_survey.md       ~60 benchmarks, gaps, coverage map, design implications
  docs/02_concept_library.md        finance concepts (families A-K) and how they compose into workflows
  docs/03_source_catalog.md         ranked catalog of 12 sources, flagship workflows, access list
  docs/04_poc_results.md            what was pulled in the sandbox, checks, traps
  docs/05_top10_resources.md        top-10 sources table (links, workflows, caveats)
  docs/sources/*.md                 raw research notes per slice (credit, funds, public, corporate)
  docs/videos/videos_all.json       71 videos with transcript-derived workflow anatomy
  docs/videos/notes_funds.md        funds/wealth video notes, per-workflow anatomy, lessons
  docs/videos/notes_public.md       public-sector/nonprofit video notes, anatomy, lessons
  poc/*.py                          pull + validation scripts; yt_tool.py (YouTube search/meta/transcripts)
  samples/                          small env-seed workbooks + validation reports per source
"""

STANCE = """Scope decisions from the kickoff Q&A
  Environment     : spreadsheet-centric; raw inputs (PDF incl. scans, CSV, XML, HTML) are turned into a workbook env
  Domains/personas: all (accounting ops, FP&A, investment research, credit, public finance, audit/regulatory, household/SMB)
  Long horizon    : a big chunk of a professional's job, composed of several finance concepts (e.g. an end-to-end rebalance)
  Licensing       : research use is fine
  Geography       : any / mixed; cross-jurisdiction is a plus
  Messiness       : all, including scanned PDFs
  Env unit        : both deep (one entity, many periods) and broad (a universe of entities)
  Multi-source    : combining sources is encouraged
  Grading         : open; likely LLM judge, with natural numeric checks as a bonus
  Purpose         : separate frontier models; difficulty comes largely from horizon

Definition of a workflow (from mentor guidance)
  A job an analyst carries out independently: gather source documents (filings, PDFs, statements,
  exports) -> extract and structure the numbers in a workbook -> build the analysis -> check it ties
  -> reach a judgment -> hand over a deliverable. Reference level: the Otis 90-minute 3-statement
  case study (section 8).

Seven operations at that level
  GATHER    find and open the right source documents
  EXTRACT   get numbers out of PDFs or exports into the workbook
  STRUCTURE lay out the workbook: periods, line items, conventions
  BUILD     formulas, schedules, projections, links
  CHECK     tie to reported totals; balance and sanity checks
  JUDGE     assumptions, trade-offs, interpreting results
  DELIVER   a conclusion, recommendation or hand-off artifact

Selection principle for data
  Prefer sources where the source itself reports totals that bottom-up work must reproduce
  ("natural ground truth": audited statements vs. ledgers, servicer reports vs. loan tapes, reported
  NAV vs. holdings, the form's own reconciliation lines). That keeps long, messy, real trajectories
  gradeable. Exceptions found on real data are restatements, mergers, special items and sign
  conventions: exactly the judgment points that separate strong models.
"""

TOP10 = [
    dict(n=1, name="Municipal annual reports and bond documents (ACFRs, budget books, single audits, actuarial valuations, official statements)",
         links=["GovText / End-of-Term 2020 PDF archive (S3, CC0): https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/govscape/eota-ocr/README.md",
                "GovScape search over the same PDFs: https://govscape.net",
                "MSRB EMMA (browse only; ToS forbid scraping): https://emma.msrb.org",
                "Our index of finance PDFs in the archive: samples/govtext_finance_pdf_index.parquet"],
         pulled="VALIDATED. Austin, 17 ACFR PDFs FY2001-2019: statement located 15/16; fund balance ties 15/15 within year, 11/12 across years (the break is FY2011's restated opening balance, +$19.3M, Note 16). Archive index: 6,203 ACFRs, 3,394 budget books, 872 single audits, 433 actuarial valuations, 167 official statements (2020 crawl, PDF + OCR).",
         flows=["Municipal credit review (muni credit / rating analyst): extract 5-10 yrs of fund statements [GT] -> normalise restatements and special items -> fund balance and liquidity trend -> debt schedule from the official statement tied to the debt note [GT] -> coverage under the bond resolution's revenue definition -> pension liability roll-forward [GT] -> peer percentile and rating memo",
                "Annual surveillance update: add the new annual report -> roll every metric forward [GT] -> explain changes -> revise the rating view"],
         cav=["Archive PDFs are from the 2020 crawl, so mostly FY2001-FY2019", "EMMA prohibits scraping; get official statements from issuer websites", "OCR quality varies; PDF text extraction splits digits ('$ 1 30,163')"]),
    dict(n=2, name="State and city ledgers and checkbooks",
         links=["Harvard LIL Data.gov archive (Source Cooperative): https://source.coop/harvard-lil/gov-data",
                "Archive search: https://lil.law.harvard.edu/data-gov-archive",
                "S3 paths: https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/harvard-lil/gov-data/ (metadata/data_gov/<slug>/v1.json, collections/data_gov/<slug>/v1.zip)",
                "Live example: https://data.cityofchicago.org ; Kaggle mirror chicago/chicago-payments: https://www.kaggle.com/datasets/chicago/chicago-payments",
                "Slugs: general-ledger (Oklahoma GL FY22-FY25 Q1, ~2 GB), state-of-oklahoma-vendor-payments-fiscal-year-2019-6704f, austin-finance-online-echeckbook (642 MB), state-of-iowa-checkbook (6 GB), citywide-payroll-data-fiscal-year (NYC), payments (Chicago); CA State Controller returns FY2003-FY2023"],
         pulled="PROFILED. Chicago payments (Kaggle 2019 snapshot): 829,738 vouchers, $97.5B, 53 departments, 342k vendors, 75k contracts; 18.5% of rows dated by year only, 78% missing department, 97,974 same vendor/amount/date duplicate candidates.",
         flows=["Year-end close review (state/city comptroller analyst): trial balance by fund from the ledger [GT] -> map accounts to statement lines -> vendor payments vs ledger spending by agency -> reconcile to audited fund statements [GT] -> budget-to-actual variances -> commentary",
                "Payment-integrity audit (inspector general / internal auditor): de-duplicate vendor master -> duplicate and split payments -> payments without contracts -> digit tests -> sample to budget lines -> exception report"],
         cav=["Snapshots date from 2023-25; match ledger years to the ACFR year", "Duplicate labels have no ground truth; need experts", "Schemas drift across years; Oklahoma bag is CC-BY"]),
    dict(n=3, name="Auto-loan and commercial-mortgage securitizations (SEC Reg AB II: ABS-EE loan tapes + 10-D servicer reports + 424B prospectus waterfalls)",
         links=["SEC Reg AB II asset-level data: https://www.sec.gov/oit/announcement/regabii-asset-level-requirements-compliance.html",
                "EDGAR full-text search: https://www.sec.gov/edgar/search/",
                "Kaggle mirror (World Omni auto trusts, 1 GB parquet): https://www.kaggle.com/datasets/denytran/10-year-automotive-loans-abs-ee",
                "Hugging Face per-trust mirrors (1,072 repos, e.g. DenyTranDFW/AmeriCredit_Automobile_Receivables_Trust_2020_1_1801390): https://huggingface.co/DenyTranDFW",
                "CMBS deal index (Kaggle): https://www.kaggle.com/datasets/cmdrvl/cmbs-deals-edgar-cik-and-collateral-distribution"],
         pulled="VALIDATED. 35,676,547 loan-months, 1,148,191 loans, Feb 2017-Mar 2024. Loan balance identity (begin - principal - charge-off - other adj = end) ties 100%; month-to-month continuity 99.62% (129k breaks > $100, 55.7k reporting gaps). Annualised net loss ~0.4-0.7%, 30+ DPD ~2.2-2.6%.",
         flows=["24-month surveillance desk (structured-credit analyst): cut pool by FICO/term/state [GT] -> delinquency roll rates -> prepay/default/severity speeds -> pool roll-forward vs servicer report [GT] -> replicate waterfall and trigger tests from the prospectus [GT] -> carry cumulative loss -> monthly note",
                "New-issue check: tape at issuance vs prospectus strat tables [GT] -> flag differences -> price-sensitivity view"],
         cav=["No registered RMBS since 2014: coverage is auto loans/leases and CMBS", "10-D and 424B are not mirrored; need EDGAR", "Kaggle mirror pools several trusts without a deal ID; HF per-trust repos hold 7 to 60 filings", "Trap: repossession proceeds are a subset of recoveries (double count -> negative losses)"]),
    dict(n=4, name="Utility regulatory accounts (FERC Form 1/2/6/60, EQR wholesale transactions, RUS co-ops) via Catalyst PUDL",
         links=["PUDL documentation: https://docs.catalyst.coop/pudl/en/stable/",
                "PUDL data bucket (S3, CC BY 4.0): https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/?list-type=2&prefix=stable/&delimiter=/",
                "FERC eCollection (primary filings): https://ecollection.ferc.gov"],
         pulled="VALIDATED. 375 utilities, 1994-2025. Plant-in-service roll-forward ties 99.72% within year (226,738 rows) and 98.82% across years (211,729 pairs; 1,849 real restatements/reclassifications). Idaho Power: 32 years, 100% / 99.7%.",
         flows=["Rate case revenue requirement (utility/commission regulatory analyst): rate-base roll-forward from plant and depreciation [GT] -> cost of capital -> revenue requirement vs PUDL's published rate-base table [GT] -> test-year normalisation -> peer O&M benchmarking -> testimony summary",
                "Purchased-power reconciliation (utility accountant): buyer's purchased-power schedule vs sellers' EQR transactions [GT] -> explain differences"],
         cav=["PUDL has cleaned the data; use raw FERC XBRL/DBF when acquisition is part of the task", "Trap: retirements stored as negatives (textbook sign ties only 43%)", "CC BY 4.0 requires attribution; EQR is 125 GB"]),
    dict(n=5, name="US fund holdings (SEC N-PORT + 13F)",
         links=["SEC N-PORT data sets: https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets",
                "Hugging Face mirror (CC0, all SEC tables): https://huggingface.co/datasets/trader298/sec-nport",
                "Curated holdings: https://huggingface.co/datasets/ZipLime/fund-holdings-nport",
                "13F mirror: https://huggingface.co/datasets/ZipLime/institutional-portfolio-13f"],
         pulled="PARTIAL (fund level). 160 target-date-2050 reports across 8 series via HF datasets-server /filter; total assets - liabilities = net assets on 100/100 reports. Real event: Vanguard Target Retirement 2050 jumps ~$22B -> ~$54B in 2022 (Institutional series merged in). Holdings not pulled (HF CDN blocked; 6 GB index still warming).",
         flows=["Target-date fund due diligence (OCIO manager-research analyst): look-through to underlying funds [GT] -> chain returns vs reported [GT] -> drift vs glide path -> attribution -> fee drag -> explain the merger break -> recommendation",
                "Bond-fund liquidity stress (fund liquidity risk manager): classify holdings -> concentration -> duration vs reported rate risk [GT] -> redemption stress -> sale plan"],
         cav=["Public data covers one month per fiscal quarter with ~60-day lag; broader monthly publication postponed (verify)", "Placeholder CUSIPs and one row per identifier double-count if joined naively", "HF file CDN blocked in the sandbox"]),
    dict(n=6, name="India mutual-fund portfolios (SEBI monthly portfolio workbooks per fund house + AMFI NAV/TER)",
         links=["AMFI: https://www.amfiindia.com",
                "Raw workbook mirror (GitHub, Aug-2026, 13 AMCs): https://github.com/subscriptionmanager26-png/fund-disclosures",
                "Parsed holdings mirror (GitHub): https://github.com/kushagra-agarwal-a/fund-holdings-data",
                "NAV history (Kaggle): https://www.kaggle.com/datasets/tharunreddy2911/mutual-fund-historic-nav-data",
                "TER (Kaggle): https://www.kaggle.com/datasets/neeeeeemo/indian-mutual-funds-ter-total-expense-ratios"],
         pulled="VALIDATED. 13 fund houses, 715 schemes (31-Aug-2026). Holdings' implied net assets tie to the Grand Total for 99.2% of schemes; per-holding consistency 80% (rest is 2-decimal rounding on small positions). Header row anywhere from 2-12; ISIN column 0/2/3/7; % vs fraction (SBI uses both); Rs lakh; zips; UTI defeats the heuristic.",
         flows=["Quarterly client review and rebalance (mutual-fund distributor / adviser): parse six fund houses' workbooks [GT] -> look-through by stock/sector/size -> overlap -> SEBI category-rule check -> returns and volatility from NAV -> regular->direct switch via TER -> tax-aware trade list; repeat monthly",
                "Debt-fund credit and duration monitor (treasury investor): fortnightly holdings -> rating migration -> issuer concentration -> recompute yield/duration vs reported [GT] -> exits"],
         cav=["Raw mirror holds one month; more months mean scraping 40+ fund-house sites", "No explicit licence (statutory disclosures)", "Layouts change without notice"]),
    dict(n=7, name="Nonprofit tax returns (IRS 990 / 990-PF e-file XML, 2009-2026)",
         links=["IRS Form 990 series downloads: https://www.irs.gov/node/70096",
                "GivingTuesday data lake (public S3): https://gt990datalake-rawdata.s3.amazonaws.com/?list-type=2&delimiter=/",
                "Index parquet (range-readable): https://gt990datalake-rawdata.s3.amazonaws.com/Indices/990xmls/index_all_years_efiledata_xmls_created_on_2024-07-23.parquet",
                "Raw XML: https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/<ObjectId>_public.xml",
                "Parsed (HF, CC0): https://huggingface.co/datasets/piercewetter3/irs-990-parsed"],
         pulled="VALIDATED. Wikimedia Foundation 2009-2022 (14 returns, 13 schema versions): Part XI net-asset reconciliation 10/10, roll-forward EOY(t)=BOY(t+1) 13/13, functional expenses 14/14. Index: 6,245,445 returns.",
         flows=["Foundation year-end close and payout plan (foundation CFO / tax preparer): classify ~4,000 sale lots ST/LT [GT] -> reconcile lot gains to reported gain -> excise tax -> minimum distributable amount [GT] -> map holdings to sectors -> tax-lot sale plan to policy",
                "Grant due diligence (program officer / charity regulator): 10 years of financials [GT] -> program ratio, reserves, revenue concentration -> endowment analysis -> single-audit cross-check"],
         cav=["Schema changes nearly every year; element names repeat in schedules", "Lot detail varies by preparer; may not sum to reported gain", "Single-audit data (FAC) needs an API key"]),
    dict(n=8, name="US Chapter 11 case dockets (DIP budgets/variance reports, monthly operating reports, claims registers, disclosure statements)",
         links=["CourtListener RECAP archive: https://www.courtlistener.com/recap/",
                "Claims agent (Kroll): https://restructuring.ra.kroll.com",
                "Claims agent (Stretto): https://cases.stretto.com",
                "Text-only mirror (Delaware bankruptcy court): https://huggingface.co/datasets/alea-institute/kl3m-data-pacer-deb",
                "Post-confirmation trusts on EDGAR: Lehman Brothers Holdings Plan Trust (CIK 806085), Motors Liquidation GUC Trust (CIK 40730)"],
         pulled="NOT PULLED (hosts blocked; no bulk mirror of MORs or claims registers).",
         flows=["Creditor-committee monitoring (restructuring financial advisor): read scanned monthly reports; cash roll-forward [GT] -> cumulative budget variance vs tolerance [GT] -> liquidity runway -> fees vs budget -> claims by class [GT] -> recovery waterfall vs disclosure statement [GT] -> committee update",
                "Recovery analysis (distressed investor): claims register and plan [GT] -> recovery per class -> sensitivity to asset values"],
         cav=["Hand-collect 5-10 cases", "Claims-agent terms vary on redistribution", "RECAP holds only what users bought; coverage varies by court"]),
    dict(n=9, name="FFIEC bank Call Reports + UBPR (+ FDIC failures)",
         links=["FFIEC Central Data Repository: https://cdr.ffiec.gov/public/",
                "Call Report mirror (CC0, 2001-2026): https://huggingface.co/datasets/kairusama/call-report-one",
                "UBPR mirror (CC0): https://huggingface.co/datasets/kairusama/ubpr-one",
                "Bank ratios (Kaggle, CC0): https://www.kaggle.com/datasets/neutrino404/all-us-banks-financial-quarterly-ratios-2001-2023"],
         pulled="SCHEMA ONLY. 671,000 bank-quarters, 224 income/supplemental columns, 1,442 canonical columns.",
         flows=["Bank-failure post-mortem / exam prep (bank examiner): 20 quarters -> capital and liquidity -> allowance roll-forward [GT] -> margin bridge -> real-estate concentration -> recompute ratios vs UBPR [GT] -> exam memo",
                "Early-warning screen (bank credit analyst): screen the universe -> back-test against later failures [GT] -> watchlist"],
         cav=["Structured data: little raw-file mess; pair with bank PDFs", "Field codes and schedules changed over 25 years", "HF CDN blocked in the sandbox"]),
    dict(n=10, name="Private credit: BDC schedules of investments + credit agreements (EX-10)",
         links=["SEC BDC data sets (monthly, from XBRL; launched June 2025): https://www.sec.gov/data-research/sec-markets-data/bdc-data-sets",
                "Credit agreements (HF, 2001-2024): https://huggingface.co/datasets/yonathanarbel/SEC_Exhibit_10",
                "Scanned exhibits (HF): https://huggingface.co/datasets/arthrod/sec-ex10-exhibits"],
         pulled="NOT PULLED (mirrors identified).",
         flows=["Private-credit surveillance (private-credit analyst): match borrowers across BDCs -> mark dispersion -> schedule total vs balance sheet [GT] -> covenant test using the agreement's EBITDA definition -> watchlist",
                "Covenant compliance certificate (lender / borrower CFO): extract covenant definitions -> compute leverage and coverage with add-backs -> compare to thresholds each quarter"],
         cav=["Data sets start June 2025; earlier history from filings", "SEC doesn't guarantee accuracy; XBRL tagging errors", "Covenant ground truth partial (compliance certificates rarely filed)"]),
]

TOP10_GLOBAL_CAVEATS = """Caveats that apply to all ten
  - Only 5 of 10 are pulled and validated (#1, #3, #4, #6, #7). #2 profiled only, #5 fund-level only, #9 schema only, #8 and #10 not pulled.
  - Most primary sites were blocked in the sandbox; pulls used mirrors (public S3, Kaggle, GitHub, HF datasets-server).
  - Mirrors are third-party: some state no licence, completeness varies; re-check against the primary source before release.
  - Archive snapshots are frozen (2020 PDF crawl, 2024-25 Data.gov archive, old Kaggle copies): fine for dev; test splits need live pulls. #3, #5, #6, #7, #9, #10 refresh monthly or quarterly.
  - MSRB EMMA and Chapter 11 claims agents restrict scraping/redistribution: hand-collect. Freddie Mac/Fannie Mae loan files, FINRA TRACE and NAIC statements need paid licences and are excluded.
  - Source totals grade numbers only; memos and judgment calls need a rubric or LLM judge.
  - Some details come from web search, not direct access (marked 'unverified' in docs/sources/).
"""

ACCESS = """Reachable from the sandbox (used for the pulls)
  - Public S3: pudl.catalyst.coop (FERC/EIA/RUS/EQR), gt990datalake-rawdata (IRS 990), us-west-2.opendata.source.coop
    (Harvard LIL Data.gov archive; GovText/End-of-Term PDFs), irs-form-990 (empty)
  - Kaggle API anonymous downloads (302 to signed storage.googleapis.com URLs)
  - GitHub clones and raw.githubusercontent.com (github.com web/search API 403)
  - Hugging Face API, README files and datasets-server /rows /filter (large-file CDN blocked)
  - YouTube search pages and yt-dlp captions (the official transcript endpoint blocks cloud IPs)
  - arxiv.org, openreview.net, pypi

Blocked by the environment's network policy (allowlist these for a full build)
  www.sec.gov, data.sec.gov, efts.sec.gov (declare a User-Agent, <=10 req/s), us.aws.cdn.hf.co and
  cas-bridge.xethub.hf.co (HF file CDN), ecollection.ferc.gov, cdr.ffiec.gov, banks.data.fdic.gov, api.fac.gov,
  api.usaspending.gov, fiscaldata.treasury.gov, fred.stlouisfed.org, www.courtlistener.com,
  storage.courtlistener.com, emma.msrb.org, www.amfiindia.com, AMC websites, www.bseindia.com, www.nseindia.com,
  find-and-update.company-information.service.gov.uk, filings.xbrl.org, EDINET, OpenDART, Socrata portals
  (data.cityofchicago.org, data.sfgov.org, ...), zenodo.org, archive.org, Ken French library.
  How to change it: https://code.claude.com/docs/en/cloud-environments#network-access

Terms of use that forbid scraping or redistribution: MSRB EMMA, SEDAR+, some claims agents. Paid: Freddie/Fannie
loan-level, FINRA TRACE history, NAIC statutory statements.
"""

REFERENCE_VIDEO = """Video   : 3-Statement Model: 90-Minute Case Study from a Blank Excel Sheet
Channel : Mergers & Inquisitions / Breaking Into Wall Street   Length: 1:24:36
Link    : https://www.youtube.com/watch?v=O2uPNfErmJo   Files: https://mergersandinquisitions.com/3-statement-model/
Persona : banking / corporate-finance analyst sitting a timed modeling test
Verified: every number below was checked against the transcript text.

Source documents
  - Otis Worldwide 10-K (the PDF, and the SEC's Excel export of the statements)
  - Otis investor-day presentation (market-share chart, service-unit counts, guidance, capital-allocation targets)
  - Case brief: 5-year projections, revenue built on more than a growth rate, $3B minimum cash, assess the company's claims
Deliverable
  Integrated income statement, balance sheet and cash flow model (historicals + 2022-2026 projections) with debt and
  buyback logic, plus a verdict on management's free-cash-flow and dividend claims.

Time split (chapter markers; 76.7 working minutes between 05:54 and 82:35)
  Enter historical statements   05:54-35:11   29.3 min  (38% of working time, before any modeling)
  Income statement projections  35:11-50:12   15.0 min
  Balance sheet projections     50:12-57:51    7.7 min
  Cash flow projections         57:51-67:12    9.4 min
  Link the statements           67:12-70:59    3.8 min
  Debt and buybacks             70:59-79:16    8.3 min
  Checks, review, verdict       79:16-82:35    3.3 min

Steps (timestamp | step | operations)
  02:44 | Open the 10-K at the financial statements; use the SEC Excel/CSV export rather than copying from the PDF | GATHER
  07:08 | Entry conventions: oldest to newest, revenue positive / expenses negative, fold small lines together | STRUCTURE
  08:11 | Lay out the blank sheet (fiscal-year dates); link income statement lines to the raw export | STRUCTURE, EXTRACT
  13:40 | Net income vs the 10-K: 1,714 vs 1,420; fix reversed signs on non-service pension and interest until it ties | CHECK
  15:31 | Balance sheet condensed to 5-10 lines per side; totals must match reported | EXTRACT, STRUCTURE
  23:24 | Balance check on historical years | CHECK
  24:14 | Cash flow statement with one working-capital line; net change in cash ties to 113, 342, 1,676 | EXTRACT, CHECK
  35:11 | Investor-day deck: market share 16% (2019), 18% (2021) -> ~17% in 2020; service units 2.1M -> 2.5M at ~3%/yr | GATHER, JUDGE
  37:26 | Product revenue = implied market size x market share; service revenue = units x revenue per unit | BUILD
  45:48 | Service revenue vs guidance ($10B by FY2026); growth 4-7% vs "low-to-mid single digit" | CHECK
  46:53 | Costs, tax and non-controlling interest from historical averages | BUILD, JUDGE
  50:12 | Working capital as % of revenue/COGS/OpEx; sanity-check the change in working capital | BUILD, CHECK
  57:51 | Cash flow items: CapEx and D&A as % of revenue; dividends from the stated payout ratio | BUILD
  67:12 | Link statements (cash, PP&E, debt, equity); balance check passes | BUILD, CHECK
  70:59 | $3B minimum cash; excess cash 15% debt repayment / 85% buybacks ("eyeballed"); issue debt on a shortfall; interest on prior-year debt to avoid circularity | BUILD, JUDGE
  79:16 | Model weaknesses: no unit-level drivers, simple service growth | JUDGE
  80:14 | Verdict: 2022-24 FCF ~ $5.2B vs company's $5B target; dividends ~ $1.4B (about 1/3); FCF conversion > 100% (historically 110-133%); growth a bit high; plan is reasonable | DELIVER

Why this is the right level
  - Starts from real, messy primary documents (a filing and a slide deck), not a prepared dataset.
  - Uses all seven operations, in order, in one ~80-minute sitting.
  - Its checks caught real errors (net-income mismatch exposed two sign flips in the source layout).
  - Ends in a verdict, not just a spreadsheet, so there is something to grade beyond formulas.

Other full-chain (fit A) videos and their operation coverage (F = shown, P = partly/by a tool, - = not shown)
  Video                                                            Gath Extr Stru Build Check Judge Deliv
  3-statement model, Otis (reference)        O2uPNfErmJo            F    F    F    F     F     F     F
  3-statement model, Microsoft (ApexKPI)     oQTcd-DZ7fc            F    F    F    F     F     F     P
  Model + valuation, Caterpillar (CA S. Mittal) 2pL3Ktvjf9I         F    F    F    F     F     F     F
  Spreading annual reports, Nestle/Danone    lzg8xQkdF3s            F    F    F    F     F     F     P
  County ACFR into ratio template (Strong Towns) yAbiyx0cgM8        F    F    P    P     F     P     F
  Pension accounting from actuarial reports (CalPERS) lrorAMC4JJs   F    F    P    P     F     P     F
  Household rebalancing calculator (Measure Twice) G6KoHtjdGio      F    F    F    F     F     F     F
  India client portfolio review, live (FinApp) p_m2DCJi520          F    P    P    P     F     F     F
"""

SAME_LEVEL = [
    ("Municipal credit model and memo", "#1 annual-report PDFs + #2 ledgers", "Muni credit analyst",
     "5-10 years of a city's audited annual reports (PDF, some scanned), latest bond official statement, pension actuarial report",
     "Multi-year statements keyed in and tied to reported totals; fund balance, liquidity, debt service and pension ratios; 3-5 year projection",
     "Credit memo with a rating view and named risks (e.g. fund balance vs the city's own policy floor)",
     "Fund balance rolls forward; the report's reconciliation schedules; debt schedule vs debt note",
     "Restatements and special items; coverage on the bond-document basis vs GAAP; which revenues recur",
     "yAbiyx0cgM8 (A), _Im0iXY2SgA, UE8RKZol3VA"),
    ("Utility rate-base and revenue-requirement model", "#4 FERC Form 1", "Regulatory analyst",
     "10 years of a utility's FERC Form 1 schedules plus its rate filing",
     "Plant and depreciation roll-forwards tied to the filing; rate base; cost of capital; revenue requirement; peer cost benchmarks",
     "Assessment of whether the requested rate increase is supported",
     "Roll-forwards tie (99.7%); totals vs the published rate-base table",
     "Sign conventions; explaining restatement breaks; test-year normalisation",
     "YZ7B5BDuB74, xBkH28qfSaU"),
    ("Securitization deal surveillance model", "#3 loan tapes + servicer reports + prospectus", "Structured-credit analyst",
     "Monthly loan-level tapes, monthly servicer reports, prospectus waterfall",
     "Strats, roll rates, prepay/default speeds, pool roll-forward, waterfall and trigger replication",
     "Surveillance note: performance vs pricing assumptions; projected trigger breaches",
     "Loan balances sum to reported pool balance; distributions match servicer report",
     "Recoveries vs repossession proceeds; loans that drop out; forecast assumptions",
     "cl0_H1NeYjY, LBnE1qMIe_k, 05oJHPqI5Do"),
    ("Target-date fund look-through and rebalance", "#5 SEC N-PORT", "OCIO / wealth analyst",
     "Quarterly N-PORT reports for a fund family and its underlying funds; prospectus glide path",
     "Look-through holdings, drift vs glide path, return chaining vs reported returns, fee drag, trade list",
     "Due-diligence note and rebalancing trades, or a reasoned 'no change'",
     "Holdings sum to net assets; chained returns match reported",
     "Benchmark choice; rebalancing bands; treating the 2022 merger",
     "G6KoHtjdGio (A), ROAGmAgoMAE, rNvlfiNIh5Y"),
    ("India client portfolio review and switch plan", "#6 fund-house workbooks + AMFI NAV", "Distributor / adviser",
     "Client's consolidated account statement, each fund house's monthly workbook (different layouts), NAV and TER history",
     "Holdings parsed per layout, look-through and overlap, category-rule checks, returns/risk from NAV, switch scenarios with tax",
     "Client review document with exits, switches and tax impact",
     "Holdings tie to each fund's grand total; units x NAV = statement value",
     "Quartile vs benchmark tests; time window for recent investors; regular vs direct",
     "p_m2DCJi520 (A), 7S0VFj05N9k, 1zHh9I1IKkg"),
    ("Foundation year-end close and payout plan", "#7 IRS 990 / 990-PF", "Foundation CFO",
     "Five years of a foundation's 990-PF returns incl. lot-level investment sales",
     "Financials tied across years; lot classification; excise tax; minimum distributable amount; payout and sale plan",
     "Payout and liquidity plan for the board",
     "Net-asset reconciliation and roll-forward; distributable amount recomputed",
     "Lot gains that don't sum to the reported gain; which lots to sell; policy allocation",
     "4CJHqj8bxAE, PDvt7L8U1Vg"),
    ("Chapter 11 cash monitoring", "#8 bankruptcy dockets", "Restructuring advisor",
     "DIP budget, weekly variance reports, monthly operating reports (often scanned), claims register",
     "13-week cash flow rolled forward, budget-to-actual variances, runway, claims by class, recovery waterfall",
     "Creditor-committee update with liquidity and recovery views",
     "Cash roll-forward ties to reported bank balances; cumulative variance vs covenant tolerance",
     "Timing vs permanent variances; recovery assumptions by class",
     "ayNHfj3i9gI, hTAqXFQajRU, 8cigR2Ud6b8"),
    ("Pension accounting from actuarial reports", "#1 annual-report and actuarial PDFs", "Government accountant",
     "Actuarial valuation and allocation schedules (copy-protected PDF), prior-year notes, contribution records",
     "Allocation factors keyed in, deferral schedules, pension liability roll-forward",
     "Year-end journal entries and note-disclosure tables",
     "Prior-year balances tie to prior notes; contributions reconcile to payment records",
     "Measurement date vs fiscal year; plan-specific vs employer-specific deferrals",
     "lrorAMC4JJs (A), NU6EniOwjm0"),
]

VIDEO_INSIGHTS = """Synthesis across all four clusters (from transcripts)
  1. Tie out before analysing. Every serious workflow first reconciles inputs to a source of truth: net income
     to the 10-K (Otis), account totals to the custodian (rebalancing), detailed CAS rather than summary (India),
     prior-year closing balances to the issued report (government, pensions). Planted input inconsistencies make
     natural grading hooks.
  2. Data entry is a large share of the work. ~38% of the Otis working time is entering and tying historicals;
     ACFR and CalPERS videos hand-key numbers from PDFs that cannot be copied, and catch errors by recomputing
     totals against the report's own totals. Benchmarks that hand agents clean tables skip this.
  3. The key judgment is often the basis of a number: bond-document vs GAAP coverage (one airport: $10M vs $40M),
     fund vs government-wide statements, measurement date vs fiscal year, 990 total vs unrestricted columns,
     gross vs net IRR, blended vs headline benchmark.
  4. Deliverables are threshold decisions, and "no action" is a common correct answer: 5/25 rebalancing bands,
     top-quartile in 2 of the last 3-4 years, fund balance 10-15% of expenditures, one funder above 25-30% of
     revenue, ~20% net IRR / 2x TVPI.
  5. Costs, taxes and benchmark choice separate experts from novices (buy-only vs full rebalance, harvesting
     losses first, fee drag, gross-to-net bridges).
  6. Analysts start from last year's work and roll forward: exactly the multi-period structure the benchmark
     needs.
  7. Some steps are rule-based and auto-gradable (GASB entries, 5% foundation payout, single-audit program
     rules, balance checks); credit views, recommendations and memos need a rubric.
  8. Full-chain videos are rare (8 of 71). Most show one slice (reading documents, or analysing numbers already
     in a sheet). No video shows: a municipal credit model and memo, an ABS surveillance workbook on a real deal,
     analysis of Chapter 11 monthly operating reports, a bank Call Report review, or a consultant's fund
     due-diligence memo from source documents. Public pension board meetings show the deliverable, never the
     analyst's workbook.
"""

CAVEATS = """- Video coverage is uneven: funds (22) and public sector (23) searches completed; corporate (18) and credit (8)
  were stopped early (no bank or BDC videos written up).
- Video steps come from auto-generated captions read by research agents; numbers in captions can be garbled.
  Only the Otis reference was re-checked line by line against its transcript.
- Fit ratings (A/B/C) are judgment calls on whether a video shows the full chain.
- Three India videos have Hindi auto-captions only; one video (ZTgdYJF1rNY) has no captions; four videos have no
  length recorded (YouTube rate-limited the lookups).
- Data-source caveats: see section 4. Benchmark details marked "unverified" in the survey came from search
  snippets only (e.g. vals.ai, accounting.penrose.com, spreadsheetbench.github.io were blocked).
- The 'same-level' workflows in section 11 are proposals assembled from partial videos and our PoCs; none exists
  as a single end-to-end video.
"""


def benchmarks_block() -> str:
    text = (DOCS / "01_benchmark_survey.md").read_text()
    m = re.search(r"## 1\. Landscape matrix(.*?)\n## 2\.", text, re.S)
    out, cat = [], ""
    extra = {"SpreadsheetBench v1": "https://arxiv.org/abs/2406.14991",
             "SpreadsheetBench 2": "https://arxiv.org/abs/2606.29955  | code+data: https://github.com/RUCKBReasoning/SpreadsheetBench-2"}
    for line in m.group(1).splitlines():
        if line.startswith("### "):
            cat = line[4:].strip()
            out.append(f"\n[{cat}]")
            continue
        if not line.startswith("| ") or line.startswith("| Benchmark") or set(line) <= set("|- "):
            continue
        cols = [c.strip().replace("**", "") for c in line.strip("|").split("|")]
        name, venue = cols[0], cols[1]
        ids = re.findall(r"\b(\d{4}\.\d{4,5})\b", venue)
        link = extra.get(name) or (" ; ".join(f"https://arxiv.org/abs/{i}" for i in ids) if ids else "(no arXiv id; see survey section 2)")
        focus, data, env, traj, ev, size = (cols + [""] * 8)[2:8]
        out.append(f"- {name} | {venue}\n    link: {link}\n    focus: {focus} | data: {data} | env: {env}\n    length: {traj} | eval: {ev} | size: {size}")
    return "\n".join(out)


def wf_clean(v: dict) -> str:
    return re.sub(r"^\d+[a-z]?\.\s*", "", v.get("workflow") or "")


def videos_block(videos: list[dict]) -> str:
    order = {"corporate": 0, "public": 1, "funds": 2, "credit": 3}
    names = {"corporate": "CORPORATE, ACCOUNTING & UTILITIES", "public": "PUBLIC SECTOR & NONPROFIT",
             "funds": "FUNDS, PORTFOLIOS & WEALTH", "credit": "CREDIT, STRUCTURED FINANCE & RESTRUCTURING"}
    out, cur_c, cur_w = [], None, None
    for v in sorted(videos, key=lambda v: (order[v["cluster"]], re.sub(r"^\d+[a-z]?\.\s*", "", v.get("workflow") or ""), v.get("fit") or "Z")):
        if v["cluster"] != cur_c:
            cur_c = v["cluster"]
            out.append(f"\n{SUB}\n{names[cur_c]}\n{SUB}")
            cur_w = None
        wf = re.sub(r"^\d+[a-z]?\.\s*", "", v.get("workflow") or "")
        if wf != cur_w:
            cur_w = wf
            out.append(f"\n## Workflow: {wf}")
        out.append(f"\n[{v.get('fit')}] {v.get('title')}\n    {v.get('url')}\n    channel: {v.get('channel')} | length: {v.get('duration') or 'n/a'} | uploaded: {v.get('upload_date') or 'n/a'} | transcript read: {v.get('transcript_read')}")
        if v.get("persona"):
            out.append(f"    persona: {v['persona']}")
        if v.get("inputs"):
            out.append("    source documents:\n" + "\n".join(f"      - {x}" for x in v["inputs"]))
        if v.get("output"):
            out.append(f"    deliverable: {v['output']}")
        if v.get("steps"):
            out.append("    steps:\n" + "\n".join(f"      {s.get('t', ''):>6}  {s.get('step', '')}" for s in v["steps"]))
        if v.get("checks"):
            out.append("    checks:\n" + "\n".join(f"      - {x}" for x in v["checks"]))
        if v.get("judgment"):
            out.append("    judgment calls:\n" + "\n".join(f"      - {x}" for x in v["judgment"]))
        if v.get("maps_to"):
            out.append(f"    maps to our data: {v['maps_to']}")
        if v.get("why_useful"):
            out.append(f"    why useful: {v['why_useful']}")
    return "\n".join(out)


def urls_appendix() -> str:
    out = []
    files = [DOCS / "01_benchmark_survey.md", DOCS / "03_source_catalog.md", DOCS / "05_top10_resources.md",
             *sorted((DOCS / "sources").glob("*.md")), *sorted((DOCS / "videos").glob("notes_*.md"))]
    for f in files:
        urls = sorted(set(re.findall(r"https?://[^\s)>`|\"\]]+", f.read_text())))
        urls = [u.rstrip(".,;:") for u in urls]
        out.append(f"\n[{f.relative_to(ROOT)}] {len(urls)} URLs\n" + "\n".join(f"  {u}" for u in urls))
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcripts", default="/tmp/yt_cache")
    args = ap.parse_args()
    videos = json.loads((DOCS / "videos" / "videos_all.json").read_text())

    parts = [HEADER]
    parts += [section("1. QUICK LINKS"), QUICK_LINKS]
    parts += [section("2. WHAT WE ARE BUILDING"), STANCE]
    parts += [section("3. BENCHMARKS SURVEYED (~60; full detail in docs/01_benchmark_survey.md)"),
              "SpreadsheetBench 2 (highest priority read): 321 tasks (modeling 100, debugging 100, template 97, charts 24);"
              " data from Damodaran, Screener.in, BSE India, Bloomberg; experts build gold workbooks then delete regions /"
              " inject errors; avg 11.8 sheets and ~594 cells to modify; bash + xlsx viewer, no network, <=50 turns;"
              " exact cell match + VLM rubric for charts; best model ~35% (debugging <=12%); one workbook per task,"
              " no time dimension.\n",
              benchmarks_block(),
              "\n\n" + md_slice(DOCS / "01_benchmark_survey.md", r"^3\. What"),
              "\n\n" + md_slice(DOCS / "01_benchmark_survey.md", r"^4\. Gaps"),
              "\n\n" + md_slice(DOCS / "01_benchmark_survey.md", r"^5\. Finance workflow archetypes"),
              "\n\n" + md_slice(DOCS / "01_benchmark_survey.md", r"^6\. Design implications")]
    t10 = [TOP10_GLOBAL_CAVEATS]
    for s in TOP10:
        t10.append(f"\n#{s['n']} {s['name']}\n  links:\n" + "\n".join(f"    - {l}" for l in s["links"]) +
                   f"\n  pulled: {s['pulled']}\n  workflows ([GT] = checkable against a number the source reports):\n" +
                   "\n".join(f"    - {f}" for f in s["flows"]) + "\n  caveats:\n" + "\n".join(f"    - {c}" for c in s["cav"]))
    parts += [section("4. TOP 10 DATA SOURCES (ranked by priority to build)"), "\n".join(t10)]
    parts += [section("5. OTHER SOURCES, MIRRORS AND THE AVOID LIST"),
              md_slice(DOCS / "03_source_catalog.md", r"^0\. TL;DR"),
              "\n\n" + md_slice(DOCS / "03_source_catalog.md", r"^2\.9 Tier 2"),
              "\n\n" + md_slice(DOCS / "03_source_catalog.md", r"^2\.10 Avoid"),
              "\n\n" + md_slice(DOCS / "sources" / "credit_structured_distressed.md", r"MIRROR QUICK REFERENCE"),
              "\n\n" + md_slice(DOCS / "sources" / "funds_portfolios_pensions.md", r"Quick mirror reference"),
              "\n\n" + md_slice(DOCS / "sources" / "public_gov_nonprofit.md", r"Exact reachable URLs"),
              "\n\n" + md_slice(DOCS / "sources" / "corporate_accounting_markets.md", r"RANKED TOP-5")]
    parts += [section("6. ACCESS NOTES"), ACCESS]
    parts += [section("7. PROOF-OF-CONCEPT PULLS (docs/04_poc_results.md)"),
              md_to_txt((DOCS / "04_poc_results.md").read_text())]
    parts += [section("8. REFERENCE WORKFLOW VIDEO: OTIS 3-STATEMENT MODEL"), REFERENCE_VIDEO]
    parts += [section(f"9. ALL {len(videos)} PRACTITIONER VIDEOS (fit A = full chain, B = substantial part, C = concept only)"),
              videos_block(videos)]
    parts += [section("10. INSIGHTS FROM THE VIDEOS"), VIDEO_INSIGHTS,
              "\n" + SUB + "\nPublic sector & nonprofit: lessons (from docs/videos/notes_public.md)\n" + SUB + "\n" +
              md_slice(DOCS / "videos" / "notes_public.md", r"Cross-cutting lessons"),
              "\n" + SUB + "\nFunds & wealth: lessons (from docs/videos/notes_funds.md)\n" + SUB + "\n" +
              md_slice(DOCS / "videos" / "notes_funds.md", r"Cross-cutting lessons"),
              "\n" + SUB + "\nAnatomy synthesized per workflow: public sector\n" + SUB + "\n" +
              md_all_slices(DOCS / "videos" / "notes_public.md", r"Anatomy synthesized", 2),
              "\n" + SUB + "\nAnatomy synthesized per workflow: funds & wealth\n" + SUB + "\n" +
              md_all_slices(DOCS / "videos" / "notes_funds.md", r"Anatomy synthesized", 2)]
    same = ["Same level as the Otis reference (all seven operations), built on our real sources. The sequences are\n"
            "proposals; video IDs point to the closest evidence (watch at https://www.youtube.com/watch?v=<id>).\n"]
    for p in SAME_LEVEL:
        same.append(f"\n* {p[0]}  [{p[1]}; persona: {p[2]}]\n    source documents: {p[3]}\n    workbook built  : {p[4]}\n"
                    f"    deliverable     : {p[5]}\n    checks vs source: {p[6]}\n    judgment calls  : {p[7]}\n    closest videos  : {p[8]}")
    parts += [section("11. WORKFLOWS WE CAN BUILD"), "\n".join(same),
              "\n\n" + SUB + "\nFlagship long-horizon workflows (docs/03_source_catalog.md section 3)\n" + SUB + "\n" +
              md_slice(DOCS / "03_source_catalog.md", r"^3\. Flagship"),
              "\n\n" + SUB + "\nConcept library: composition and worked compositions (docs/02_concept_library.md)\n" + SUB + "\n" +
              md_slice(DOCS / "02_concept_library.md", r"^3\. Composition"),
              "\n\n" + md_slice(DOCS / "02_concept_library.md", r"^4\. What a data source must offer")]
    parts += [section("12. CAVEATS"), CAVEATS]
    parts += [section("13. APPENDIX: EVERY URL CITED IN THE RESEARCH NOTES"), urls_appendix()]
    (ROOT / "FINANCE_BENCHMARK_REFERENCE.txt").write_text("\n".join(parts) + "\n")

    # Transcripts
    tparts = ["VIDEO TRANSCRIPTS: auto-generated YouTube captions, timestamped every ~30 s.\n"
              "Companion to FINANCE_BENCHMARK_REFERENCE.txt (section 9 has the structured breakdown of each video).\n"
              "Captions are machine-generated: names and numbers can be garbled.\n"]
    tdir = pathlib.Path(args.transcripts)
    missing = []
    for v in sorted(videos, key=lambda v: (v["cluster"], v.get("workflow") or "", v.get("fit") or "")):
        p = tdir / f"{v['video_id']}.txt"
        if not p.exists() or not p.read_text().strip():
            missing.append(v["video_id"])
            continue
        tparts.append(f"\n{BAR}\n[{v.get('fit')}] {v.get('title')}\n{v.get('url')}\nchannel: {v.get('channel')} | length: {v.get('duration') or 'n/a'} | cluster: {v['cluster']} | workflow: {wf_clean(v)}\n{BAR}\n{p.read_text().strip()}")
    tparts.append(f"\n{BAR}\nNo transcript available for: {', '.join(missing) or 'none'}\n")
    (ROOT / "VIDEO_TRANSCRIPTS.txt").write_text("\n".join(tparts))
    print("wrote", ROOT / "FINANCE_BENCHMARK_REFERENCE.txt", "and", ROOT / "VIDEO_TRANSCRIPTS.txt", "missing:", missing)


if __name__ == "__main__":
    main()
