# Distillation-aware prompting — pilot code

Code for the experiments in [`PROPOSAL.md`](PROPOSAL.md). It measures how the prompt→image
interface changes when a diffusion/flow model is step-distilled, and runs student-in-the-loop,
teacher-referenced prompt evolution.

| Module | What it does |
|---|---|
| `configs/families.yaml` | Teacher + distilled-student registry per base model (SDXL: Turbo, Lightning, DMD2, LCM, Hyper-SD, TCD; FLUX; SD3.5; Qwen-Image). NFE per image is derived from steps and CFG. |
| `dap/generation.py` | Loads any variant with diffusers (UNet swap, LoRA, scheduler, custom timesteps) and counts NFEs. |
| `dap/questions.py` | Intent checklists: deterministic yes/no questions for GenEval metadata, LLM (DSG-style) decomposition for free-form prompts. Fitness is always computed against the original prompt's checklist. |
| `dap/judges.py` | VQA-style judges, P(yes): local HF VLM (Qwen-VL / InternVL) or any OpenAI-compatible endpoint with logprobs. Search judge and evaluation judges are kept separate. |
| `dap/metrics.py` | pass@k over seeds, student-vs-teacher sharpening (logit slope, lost reachability), seed-vs-wording variance decomposition (prompt share ρ), Vendi. |
| `dap/rewrite.py` | Paraphrase, generic enhancement (baseline), reflective mutation, crossover, rule-based operators. |
| `dap/evolve.py` | DAPE test-time loop with NFE budget, early stopping, optional teacher-reference precision term and facility-location prompt-mixture selection (`coverage_subset`). |
| `dap/search.py` | Compute-matched baselines: noise best-of-N, paraphrase best-of-N, DAPE. |
| `scripts/sharpening.py` | **E1**: pass@k over seeds for a teacher and all its students + sharpening statistics. Can save images in the official GenEval layout. |
| `scripts/variance.py` | **E2**: paraphrase × seed grids, prompt share ρ, seed-set vs paraphrase-set diversity. |
| `scripts/search_scaling.py` | **E3**: anytime quality-vs-NFE curves for noise / paraphrase / DAPE on the student and best-of-N on the teacher, re-scored by held-out judges. |

## Setup (GPU box)

```bash
pip install torch diffusers transformers accelerate safetensors peft pyyaml requests numpy scipy pytest
# judges / rewriter served with vLLM (OpenAI-compatible), e.g.
vllm serve Qwen/Qwen3-VL-8B-Instruct --port 8000          # search judge
vllm serve OpenGVLab/InternVL3_5-8B --port 8002            # held-out evaluation judge (different family)
vllm serve Qwen/Qwen3-8B --port 8001                       # rewriter / mutation LLM
```

## Pilot runs (go / no-go for the paper's central hypotheses)

```bash
# E1: sharpening. ~553 GenEval prompts x 16 seeds per variant
python scripts/sharpening.py --family sdxl --n-seeds 16 \
  --judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 --save-images --out runs/e1_sdxl

# E2: where does variation come from? (paraphrases generated once and cached)
python scripts/variance.py --family sdxl --limit 100 --n-para 6 --n-seeds 6 \
  --paraphrases runs/paraphrases.json --llm openai:Qwen/Qwen3-8B@http://localhost:8001/v1 \
  --embedder facebook/dinov2-base --judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 --out runs/e2_sdxl

# E3: compute-matched search curves on one student
python scripts/search_scaling.py --family sdxl --student dmd2-sdxl-4 --budgets 4 16 64 256 \
  --search-judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 \
  --eval-judges openai:OpenGVLab/InternVL3_5-8B@http://localhost:8002/v1 \
  --llm openai:Qwen/Qwen3-8B@http://localhost:8001/v1 --paraphrases runs/paraphrases.json --out runs/e3_dmd2
```

Images saved by `--save-images` follow the GenEval layout, so the official detector-based
GenEval evaluator can be run on them as a judge-independent check.

## Tests

CPU-only; they build a randomly initialised tiny SDXL pipeline from config files (no weight
download) and check generation, NFE accounting, evolution, and all three scripts end to end.

```bash
pytest -q tests          # ~1 min on CPU
```

Entries marked `verify: true` in `configs/families.yaml` need their checkpoint filenames and
sampler settings checked against the model cards before a real run.
