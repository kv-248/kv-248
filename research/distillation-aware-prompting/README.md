# Reword, Don't Reseed: pilot code

Code for the experiments in [`PROPOSAL.md`](PROPOSAL.md) (v2). It compares step-distilled
diffusion/flow students with their own teachers prompt by prompt: it estimates the tempered-teacher
law logit q_S = beta*logit q_T + b + sigma*eps with a judge-calibrated random-effects model, measures
whether variation lives in the seed or in the wording, and evaluates the Reword-K remedy against
noise-side and prompt-side baselines at equal wall-clock.

| Module | What it does |
|---|---|
| `configs/families.yaml` | Teacher + distilled-student registry per base model (SDXL: Turbo, Lightning, DMD2, LCM, Hyper-SD, TCD; FLUX; SD3.5; Qwen-Image). NFE per image is derived from steps and CFG. |
| `dap/generation.py` | Loads any variant with diffusers (UNet swap, LoRA, scheduler, custom timesteps) and counts NFEs. |
| `dap/questions.py` | Intent checklists: deterministic yes/no questions for GenEval metadata, LLM (DSG-style) decomposition for free-form prompts. Fitness is always computed against the original prompt's checklist. |
| `dap/judges.py` | VQA-style judges, P(yes): local HF VLM (Qwen-VL / InternVL) or any OpenAI-compatible endpoint with logprobs. Search judge and evaluation judges are kept separate. |
| `dap/metrics.py` | pass@k; **(β, σ) random-effects tempering fit** with latent teacher rates and per-model judge confusion (`fit_tempering`), teacher self-split control, judge-free mode-level test (`fit_mode_tempering`), amplification slope (Deming), teacher-coverage, seed-vs-wording variance decomposition, Vendi, scaling predictor. |
| `dap/rewrite.py` | Paraphrase, generic enhancement (baseline), reflective mutation, crossover, rule-based operators. |
| `dap/reword.py` | **Reword-K** (K jointly diverse, intent-preserving rewordings in one LLM call), generic K-expansion control, attribute-injection check. |
| `dap/evolve.py` | DAPE test-time loop with NFE budget, early stopping, optional teacher-reference precision term and facility-location prompt-mixture selection (`coverage_subset`). |
| `dap/search.py` | Compute-matched baselines: noise best-of-N, paraphrase best-of-N, DAPE. |
| `scripts/sharpening.py` | **E1**: per-prompt success over seeds for a teacher and its students; (β, σ) with bootstrap CIs, binomial/beta-binomial brackets, pass@k, teacher self-split and CFG-matched-teacher controls (`--teacher-cfgs`), per-model judge confusion (`--judge-eps`, `--judge-eps-student`). Saves images in the GenEval layout. |
| `scripts/variance.py` | **E2 grid**: wording × seed grids per model (embeddings, success, soft scores), variance decomposition, seed-set vs wording-set diversity. |
| `scripts/portability.py` | E2 analysis: wording-rank transfer, proxy regret, seed-rank transfer and same-seed image coupling (student vs teacher). |
| `scripts/amplification.py` | E2 analysis: Δlogit q_S vs Δlogit q_T for paraphrases and enhancer rewrites, rank transfer, per-source effects. |
| `scripts/search_scaling.py` | Fig. 3b: anytime best-of-K curves for seeds / paraphrases / evolution on the student and seeds on the teacher, on an NFE or **wall-clock (incl. judge + LLM)** axis, re-scored by held-out judges. |
| `scripts/remedy_eval.py` | **E3 / Table 2**: K-image remedies (seeds, pink noise, official PE, generic expansion, paraphrases, Reword-K, teacher) with success, pass@K, Vendi, teacher coverage, attribute injection, latency. |
| `scripts/toy_tempering.py` | CPU toy: reverse-KL vs forward-KL capacity-limited students of a bimodal teacher. |

## Setup (GPU box)

```bash
pip install torch diffusers transformers accelerate safetensors peft pyyaml requests numpy scipy pytest
# judges / rewriter served with vLLM (OpenAI-compatible), e.g.
vllm serve Qwen/Qwen3-VL-8B-Instruct --port 8000          # search judge
vllm serve google/gemma-3-27b-it --port 8002               # held-out evaluation judge (not Qwen-based)
vllm serve Qwen/Qwen3-8B --port 8001                       # rewriter / mutation LLM
```

## Pilot runs (go / no-go for the paper's central hypotheses)

```bash
# E1: tempered-teacher fit. 553 GenEval prompts x 32 seeds (32 so the teacher self-split control
# has 16/16), teacher CFG-matched controls at w = 8, 12; add --judge-eps / --judge-eps-student from hand labels
python scripts/sharpening.py --family sdxl --n-seeds 32 --teacher-cfgs 8 12 \
  --judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 --save-images --out runs/e1_sdxl

# E2: where does variation come from? (paraphrases generated once and cached)
python scripts/variance.py --family sdxl --limit 100 --n-para 6 --n-seeds 6 \
  --paraphrases runs/paraphrases.json --llm openai:Qwen/Qwen3-8B@http://localhost:8001/v1 \
  --embedder facebook/dinov2-base --judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 --out runs/e2_sdxl

# Fig. 3b: compute-matched curves on one student (wall-clock axis counts judge + LLM time)
python scripts/search_scaling.py --family sdxl --student dmd2-sdxl-4 --axis seconds --budgets 2 5 10 20 40 \
  --search-judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 \
  --eval-judges openai:google/gemma-3-27b-it@http://localhost:8002/v1 \
  --llm openai:Qwen/Qwen3-8B@http://localhost:8001/v1 --paraphrases runs/paraphrases.json --out runs/e3_dmd2
```

# E3 / Table 2: K = 4 remedies at equal wall-clock
python scripts/remedy_eval.py --family sdxl --student dmd2-sdxl-4 --k 4 --limit 300 \
  --llm openai:Qwen/Qwen3-4B-Instruct-2507@http://localhost:8001/v1 \
  --eval-judges openai:google/gemma-3-27b-it@http://localhost:8002/v1 \
  --embedder openai/clip-vit-large-patch14 --pe-rewrites runs/pe_rewrites.json --out runs/e5_dmd2
```

Images saved by `--save-images` follow the GenEval layout, so the official detector-based
GenEval evaluator can be run on them as a judge-independent check.

## Tests

CPU-only; they build a randomly initialised tiny SDXL pipeline from config files (no weight
download) and check generation, NFE accounting, evolution, and all three scripts end to end.

```bash
pytest -q tests          # 24 tests, ~3 min on CPU
```

Entries marked `verify: true` in `configs/families.yaml` need their checkpoint filenames and
sampler settings checked against the model cards before a real run.
