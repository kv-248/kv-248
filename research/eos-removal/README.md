# EOS removal: research workspace

Start with [`PROPOSAL.md`](PROPOSAL.md): literature map, reviewer expectations, ranked paper
ideas, the recommended paper, pilot results, and open decisions.

```
PROPOSAL.md                    the living proposal
literature/
  arxiv_corpus_ranked.md       2,220 arXiv papers from 75 queries, ranked and clustered
  venue_hits.md                accepted A*-venue papers on stopping/length, with reviewer scores
  community.md                 practitioner threads (HF forum, Hacker News)
  agent_reports/               focused literature reviews (EOS science, reasoning, interp, novelty)
scripts/
  harvest_arxiv.py             arXiv API harvest (rate-limited)
  rank_corpus.py               relevance ranking + clustering
  s2_citations.py              Semantic Scholar citing-paper traversal
  scan_venues.py               regex scan of papercopilot/paperlists dumps
  mine_reviews.py              ICLR 2018–23 review mining (Kaggle mirror of OpenReview)
pilot/
  prompts.py                   480 prompts, 40 topics x 12 templates, split by topic
  pilot_eos.py                 gen / ft / feats / analyze / continue stages
  run_pilot.sh                 full pipeline for one model
  persona_axis.py              assistant-vs-user projection across the natural end
  summarize_continuations.py   heuristic taxonomy of post-end text
```

## Reproducing the pilot

```bash
python -m venv venv && venv/bin/pip install torch transformers peft accelerate scikit-learn scipy pandas
# weights: Hugging Face (Qwen/Qwen2.5-0.5B-Instruct) or Kaggle Models (qwen-lm/qwen2.5, transformers/0.5b-instruct)
pilot/run_pilot.sh /path/to/Qwen2.5-0.5B-Instruct runs/q05 venv/bin/python
venv/bin/python pilot/persona_axis.py --model /path/to/model --out runs/q05/ce1 --adapter runs/q05/ce1/adapter
venv/bin/python pilot/summarize_continuations.py runs/q05/ce1
```

On a 4-core CPU with bf16 (AMX), the 0.5B pipeline takes roughly 1.5 hours end to end. The
pilot code is CPU-only for now; moving models and batches to CUDA is the first change needed
before the 7–8B runs.
