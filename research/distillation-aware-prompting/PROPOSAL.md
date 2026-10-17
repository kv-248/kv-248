# Reword, Don't Reseed: Prompt Evolution Across Distilled Diffusion Students

*CVPR 2027 main-track proposal, **v3.1**, revised after three rounds of simulated review (8 reviews, plus 107 mined OpenReview threads). Deadlines (AoE): registration **Nov 10**, paper **Nov 16**, supplementary **Nov 23**.*
*Round-3 verdict: presentable as a CVPR main idea. Stop revising and run the G1 pilot. Expected rating if the gates pass: about 4/6, rising to 5 if the held-out prediction works.*
*This is a plan; no result below has been measured yet. Predictions are pre-registered, and Section 7 gives the gates and fallbacks.*

---

## 0. TL;DR

**Takeaway.** *A distilled student decides its teacher's coin flips.* Prompts the teacher usually renders correctly become reliable on the student. Prompts the teacher renders only sometimes stop being reachable by re-seeding. **For students, the lever that still works is the wording: reword, don't reseed.** The ledger measures how much of that lost reach rewording and evolution can bring back (re-addressed), and how much is gone (erased).

We **fix a teacher** and study **prompt evolution across its distilled students**. This is the brief: "fix the model, try different distilled variants, see the effects of a prompt evolution strategy". The paper has three parts:

1. **Measure: the reach ledger.** For every student we take the intents its teacher can render and sort them into four groups:
   - reliable as worded;
   - made reliable by **rewording** (zero-feedback Reword-K, then student-in-the-loop evolution);
   - touched only by a lucky seed;
   - lost within budget.
   
   The protocol:
   - The original wording and the rewordings face the *same* fresh-seed test, scored by a held-out judge.
   - A placebo re-test of the original wording gives the noise floor.
   - Lucky images must pass a second judge.
   - Shares are reported at thresholds 0.25, 0.5 and 0.75.
   - The teacher's own ledger is the reference.
2. **Explain and predict: the tempered-teacher law.** We fit logit q_S = β·logit q_T + b + σ·ε per student:
   - β: the student pushes the teacher's per-prompt success rates toward 0 or 1, in the teacher's order (*tempering*);
   - σ: prompt-specific deviations (*re-addressing*).
   
   The fit is within task type and judge-calibrated, and is checked against controls: teacher self-split, CFG-matched teacher, sharpened-but-not-distilled (DPO/SPO-SDXL), non-distilled few-step sibling, and a one-factor CFG pair. The variance of a student's wording effects is β²·Var_T + σ², so **the wording axis gains under both mechanisms**. The fitted (β, σ) **predict** each student's seed-vs-wording curves, tested on held-out students.
3. **Act: distillation-aware prompt evolution.** One rule derived from the law (spend the budget on wordings, one seed each, on students) plus Pareto-over-checklist parents and a population output. Its zero-feedback corner is **Reword-K**, a single small-LLM call.
   - **The mechanism claim is made at an equal number of candidates:** does rewording help the student more than it helps the teacher?
   - **The deployment claim is made at equal wall-clock,** against seeds, equal-time seeds, pink noise, CADS, the hybrid teacher first step, the official enhancer and the teacher.
   - The headline is the student-minus-teacher difference, not state of the art.

---

## 1. Why this, why now

**Students are the deployment default.** Shipped families with a teacher and distilled students:

| Family | Teacher | Students |
|---|---|---|
| SDXL | base | Turbo, Lightning, DMD2, LCM, TCD, Hyper, PCM |
| FLUX.2-klein | base-4B, 50 steps | 4 steps |
| Z-Image | 50 steps | Turbo, 8 NFE |
| ERNIE-Image | 50 steps | Turbo, 8 steps |
| Qwen-Image-2.1 | 40 steps | Turbo, 8 steps; Lightning, 4 steps |
| FLUX 3 klein | base, 50 steps | distilled, 16 steps |
| Wan2.2 | A14B | Lightning |

Their prompt tools were built for teachers:

- The Qwen-Image-2.1 enhancer is demonstrated only with its teacher.
- FLUX 3 klein ships one upsampler for both base and distilled models.
- Wan2.2-Lightning reuses Wan's extender.

Those tools are also mis-sized for students. With PromptEnhancer-7B in front, Z-Image-Turbo goes from 0.88 s to 8.53 s per image and FLUX.2-klein from 0.67 s to 8.18 s (PE-OPSD, arXiv 2609.36638).

**Known.**
- **Seed diversity collapses** (≥ 7 papers):
  - DreamSim: SDXL 0.337 → DMD2 0.264 (Gandikota & Bau);
  - DINO: SDXL 0.219 → DMD-4 0.109 (DP-DMD);
  - OneIG diversity: Qwen-Image 0.194 → Lightning 0.116.
- **Mechanism.** Students commit to layout at the first, high-noise step, yet keep the teacher's representations: LoRAs and sliders transfer.
- **Defaults shift.** Distributions over *unspecified* attributes move toward the teacher's peak mode (DefaultShift, arXiv 2608.21784).
- **Benchmarks diverge.** Students often match their teachers at pass@1 on GenEval (DMD2 0.58 vs SDXL 0.55), but drop on dense prompts (DPG: Z-Image 88.1 → Turbo 84.9).
- **CFG and RL sharpen during distillation** (Decoupled-DMD arXiv 2511.22677; DMDR arXiv 2511.13649).

**Unknown, and what we measure.** For *specified* intents, what happens to each prompt's success rate and reachability under distillation? Are lost outcomes **erased** or **re-addressed**? And does the answer change how a prompt-evolution strategy should spend its samples on a student?

**Public numbers motivate, but do not prove.** Converted to aggregate logit gains (student Δ / teacher Δ), the cited enhancer effects give:

| Source | Ratio |
|---|---|
| ERNIE PE, colors | 1.53 |
| ERNIE PE, overall | 1.07 |
| PE-OPSD, GenEval-2 | 1.34 |
| PE-OPSD, GenEval | **0.85** |

We therefore expect modest effects in success space and large effects in diversity space, and we plan statistical power accordingly (§5.4).

---

## 2. The tempered-teacher law (explanatory core)

For an intent I, a wording c and a seed z, q(c) is the probability over seeds that the image passes I's checklist. The checklist is always the **original** prompt's.

  **logit q_S(c) = β·logit q_T(c) + b_task + σ·ε_c,  ε_c ~ N(0, 1)**

- **β is an effective temperature.** β > 1 means tempering in the teacher's order; β < 1 means flattening (regression students blur between outcomes).
- **σ is prompt-specific re-addressing.**
- **b_task are task fixed effects** (count, position, color, ...), so β is identified *within* task type. Pooled over GenEval tasks, aligned task offsets fake β ≈ 1.18 when the true value is 1 (simulated, reproduced in `tests/`).

**Why the form.** Exact mode-level tempering π^S ∝ π^β gives logit q_S = β·logit q_T + (1−β)[H_β(success modes) − H_β(failure modes)], a prompt-dependent offset that σ absorbs. It also gives a mechanism for "students beat teachers at pass@1 on templated prompts": **failure is diverse, success is canonical**, so with β > 1 the offset is positive.

**What it predicts about prompt evolution.**

| | Prediction | Status |
|---|---|---|
| **P1** | Seed gains shrink on intents with intermediate q_T | Algebra; reported as a consequence |
| **P2** | Across wordings, Var_c logit q_S = β²·Var_c logit q_T + σ_W², so selection over wordings gains on students under *both* tempering and *wording-level* re-addressing, relative to the teacher. σ_W is identified from a wording × seed grid with a two-level fit (`fit_tempering_grid`): intent-level σ_I does not help wording search | The interaction we test |
| **P3** | Fitness gets cheaper. q_S sits near 0/1, so one seed per candidate suffices on mode-seeking students; teachers need several. This turns the standard "single-sample fitness is unreliable" critique into a measured, model-dependent finding | Measured per model |
| **P4** | Teacher-evolved wordings keep their sign on students, but top-1 agreement falls as σ grows | Tested with a 2×2 teacher-evolved / student-evolved swap |

**The nulls we must beat.**
- **Arbitrary collapse.** The student collapses onto *a* mode, not the teacher's dominant one (β ≈ 1, large σ). Test: modes defined on teacher images (DINOv2 k-means), student images assigned to the nearest teacher mode, top-mode agreement vs the null.
- **Guidance.** Each student is fitted against the teacher at its baked-in guidance (w ∈ {5, 8, 12}). We report "a 4-step DMD2 ≈ a w* teacher" if that is what we find.
- **Sharpening without distillation.** Fit DPO-SDXL and SPO-SDXL against the base.

**Toy check** (`scripts/toy_tempering.py`, CPU): a capacity-limited reverse-KL student of a bimodal teacher tempers (logit slope 3.9 when the modes are separated) and its seed spread collapses to a single mode. A forward-KL student flattens (slope 0.89).

---

## 3. Measurement protocol

**Estimator** (`dap.metrics.fit_tempering`):
- The teacher's per-prompt rate is latent: an empirical-Bayes posterior on a logit grid, integrated out (errors-in-variables).
- The student side is a binomial likelihood with a logit-normal random effect (σ), integrated by Gauss–Hermite quadrature.
- Task fixed effects; judge confusion rates can differ per model (`eps`, `eps_S`).
- The likelihood depends on a prompt only through its (count, count, task) cell, so the fit runs on unique cells (1.8 s for 553 prompts) and the bootstrap is a stratified multinomial reweighting.
- Binomial and beta-binomial fits are reported as brackets.

**Why** (simulations, all reproduced by `pytest`):

| True mechanism | Naive logit slope | Binomial EIV | Beta-binomial | **(β, σ) GLMM** |
|---|---|---|---|---|
| β = 4, σ = 0 | 1.56 | 4.0 | — | 4.0 |
| β = 1, σ = 1.5 (re-addressing, not tempering) | — | **1.20** | **0.69** | **1.02, σ̂ 1.41** |
| β = 1, task offsets aligned with difficulty (pooled) | — | — | — | pooled > 1.15; **within-task ≈ 1.0** |
| β = 4, judge FP/FN 8%/12% uncorrected | — | 1.8 | — | ≈ 4 with ε corrected |

**Power.** At 553 prompts × 16 seeds, β = 1.2 is detectable for σ up to 1.5 (95% range [1.10, 1.30]; σ̂ recovered within ±0.05). At 300 prompts this is borderline ([1.10, 1.38]).

**Controls** (one row each in Table 1):

| Control | Expectation | Rules out |
|---|---|---|
| Teacher self-split (32 seeds as 16/16) | β ≈ 1, σ ≈ 0 | Estimator artifacts |
| Teacher at w ∈ {5, 8, 12}, disjoint seeds | β rises with w | "It's guidance" (students fitted against each) |
| DPO-SDXL, SPO-SDXL (preference-tuned, not distilled) | β > 1? | "Any sharpening, not distillation" |
| SDXL + DPM-Solver++ at 10 steps (same weights, disjoint seeds) | β ≈ 1, σ > 0 | "Any fast sampler" |
| PCM smallcfg vs normalcfg, 4 steps (one-factor CFG change, same objective) | β(normal) > β(small) | Objective vs CFG |

**Judges.**
- Search and selection: Qwen3-VL-8B, atomized questions.
- Evaluation:
  - the **GenEval detector** (primary for SDXL);
  - a **non-Qwen VLM** (Gemma-3-27B);
  - a frontier pairwise judge on subsets;
  - humans.
- Hand labels: about 300 images per gate arm, stratified by q-bin, from the author plus a paid second annotator. They give per-model confusion rates, whose uncertainty propagates into the CIs.

**Seeds.** Disjoint ranges for teacher vs controls. Every wording arm uses **fresh seeds per wording**: a shared seed would handicap a seed-driven teacher and manufacture a flip.

---

## 4. Experiments

### 4.1 Testbeds

| Family | Teacher → students | Role |
|---|---|---|
| **SDXL** (main) | base → Turbo (ADD), Lightning-4 (and 1/2/8-step sweep), DMD2-4, LCM-4, PCM-4 (small/normal CFG), Hyper-4, TCD-4; plus controls | One fixed teacher, every objective family |
| **FLUX.2-klein** (main) | base-4B → klein-4B | Modern DiT, LLM text encoder, flow; Apache-2.0 vendor pair |
| **Z-Image** (partial: E1 + ledger, 150 intents) | Z-Image → Z-Image-Turbo | Production student, DMD + RL (labelled) |
| SD3.5-L → Large-Turbo; SANA-Sprint (teacher → 2-step) | optional | Held-out families for the prediction test, if compute allows |

FLUX-dev → schnell is a *sibling* pair (both come from pro), so we do not use it as teacher→student.

### 4.2 E1: per-prompt success and the law (Table 1, Fig. 3a)

- **SDXL:** GenEval (553 prompts, detector) plus a T2I-CompBench subset, for ≥ 600 intents.
- **klein and Z-Image:** GenEval-2 (800).
- **Seeds:** 32 per teacher and control, 16 per student.
- **Fig. 3a:** binned E[q_S | q_T] per student with bands, controls in grey.
- **Table 1** (per student):
  - β̂ and σ̂ within task, with CIs, against the default teacher and against the CFG-matched teacher;
  - pooled β̂ as a bracket;
  - pass@1 and pass@16;
  - top-mode agreement vs null;
  - seed DreamSim.

### 4.3 E2: the reach ledger (main Fig. 2)

`scripts/reach_ledger.py`.

**Setup.**
- Teacher-reachable intents: the teacher succeeds on at least one of 16 held-out seeds.
- Models: the teacher, SDXL {DMD2, Lightning, LCM, Turbo}, klein-4B, Z-Image-Turbo.
- Each intent is assigned to the first category that applies:

| Category | Meaning |
|---|---|
| original | Reliable as worded |
| reword | Made reliable by Reword-K (K = 8, search-judge selection) |
| evolve | Made reliable by distillation-aware evolution (32 renders, Reword-K initialisation) |
| reseed-only | Reached only by a lucky seed |
| lost within budget | None of the above |

- "Reliable" means success on ≥ 50% of **8 fresh seeds** under the **held-out** judge.
- A selected wording flagged by a checker LLM for adding content (a different model from the rewriter) does not count.
- Bars are ordered by objective family, with the teacher's own bar as reference.

**Prediction** (corrected in round 3; computed from each student's fitted law with `scripts/analyze.py predict` and committed *before* the ledger runs).

At the 0.5 threshold with b ≈ 0, pure tempering leaves the set of reliable wordings unchanged: q_S ≥ ½ exactly when q_T ≥ ½. So tempering alone moves the teacher's *reseed-only* mass to *lost*. It does not move it to *reword*. The ledger therefore has two separable signatures:

- **(i) Tempering.** The student's reseed-only share shrinks and its lost share grows, relative to the teacher.
- **(ii) Re-addressing.** The reword and evolve rungs recover a share that grows with the wording spread s_w and with σ_W. This is "erased vs re-addressed", made quantitative.

**Further outputs:**
- **The 0.25 and 0.75 thresholds**, which show how the picture depends on what "reliable" means.
- **Re-found vs re-addressed.** Of the intents rewording recovers, what fraction could a lucky seed also reach?
- **An equal-budget lucky-reach estimate.**
- **The budget curve** (8, 16, 32, 64 renders). It shows "lost" is a lower bound.

### 4.4 E3: allocation, prediction and transfer (Fig. 3b–c)

**(b) Width × depth plane at an equal number of candidates** (`scripts/search_scaling.py --axis images`, fresh seeds; this carries the mechanism claim). The same runs are also plotted against wall-clock (`--axis seconds`) for deployment. At equal seconds a fast student gets more candidates, so a student that is merely faster than its teacher would "win" without any mechanism. One selector (the search judge) is used for every arm. Arms:

- seeds (original wording);
- wordings, both shared-seed and fresh-seed;
- Reword-K;
- evolution at depths 1–4;
- the teacher with seeds and with wordings;
- the CFG-matched teacher.

Reported (`scripts/analyze.py interaction`):
- **Headline:** the student-minus-teacher difference with a paired bootstrap CI over intents, measured two ways:
  - (1) on the **deployable fresh-seed rate of the chosen wording**, i.e. does rewording help the student more than the teacher? A chosen *seed* does not transfer to new seeds, so the seed arm's deployable gain is 0 by construction.
  - (2) on best-of-N coverage, as (wording gain − seed gain).
- **Gains are also reported separately for each arm,** so that a seed-axis collapse (already reported in 7+ papers) cannot carry the result alone.

**Prediction test.**
- **Inputs.** Each student's E1 fit (β̂, σ̂ with per-task offsets) plus its two-level σ_I and σ_W from a wording × seed grid on **disjoint** intents. The teacher's wording statistics come from the *same* generator of wordings as the measured arm: Reword-K outputs, not random paraphrases.
- **What is forecast:** the measured Reword-K and evolution arms on held-out intents (`analyze.py predict`).
- **Validation:** held-out intents within each student, plus klein and Z-Image as held-out families. Leave-one-student-out is not meaningful, because no parameter is shared across students.
- **Baselines:** curve-shaped trivial predictors, namely student pass@k, E[q_S(1 − q_S)], and the teacher's own curve.

**(c) 2×2 transfer** on one pair per family. Wordings are evolved on the teacher or on the student, then evaluated on both. Prediction: transfer keeps its sign, and the student-evolved advantage grows with σ̂.

**Pre-registered effect sizes** (simulated under the law, 300 intents, K = 8):

| Metric | β 1.3–1.5 or σ ≈ 0.7–1.0 | Notes |
|---|---|---|
| Oracle pass@K interaction | +0.01–0.045 | SD ≈ 0.025, too noisy to be the headline |
| **Deployable chosen-wording fresh-seed interaction** | +0.011–0.045 | SD ≈ 0.007–0.013, z ≈ 2–5; the headline in success space |
| Diversity-space effects | Large | Seed collapse is already large |

We therefore use ≥ 600 intents on SDXL and report CIs. If the success-space interaction is null, the paper reports that alongside the ledger.

### 4.5 E4: deployment, K = 4 images (Table 2, Fig. 4)

`scripts/remedy_eval.py`.

- **Students:** SDXL-DMD2, klein-4B, Z-Image-Turbo.
- **Prompts:** GenEval-2, DPG-hard and real user prompts (Pick-a-Pic).
- **Rows** (all implemented in `remedy_eval.py`):
  - i.i.d. seeds;
  - **equal-time seeds** (Reword-K's LLM time re-spent on extra seeds, K selected);
  - pink noise;
  - CADS (condition annealing on SDXL text embeddings);
  - hybrid teacher-first-step (the teacher denoises the first 25% of the schedule; latent handed to the student);
  - an OPT2I/RAISE-style configuration of the same loop (teacher-style allocation: 4 seeds per candidate, top-fitness parents), so the distillation-aware rule is isolated;
  - **no-LLM composition tags**;
  - the official/teacher-built PE (its latency counted);
  - generic diverse expansion (Prompt-Expansion-style);
  - random paraphrases;
  - **Reword-K**;
  - **evolution (population output)**;
  - the teacher;
  - **teacher + Reword-K** (the remedy must help students *more* than teachers).
- **Columns:**
  - alignment (mean success, pass@K);
  - diversity (Vendi, DreamSim);
  - **teacher coverage**: k-NN coverage (Naeem et al. 2020) of checklist-passing teacher samples (32 held-out seeds, CLIP space) by checklist-passing method images, stratified by teacher success rate;
  - attribute-injection rate (strict and lenient), from a checker that differs from the rewriter;
  - HPSv3;
  - end-to-end latency.
- **Human 2AFC:** about 120 prompts × 3 comparisons × 5 raters, with ledger "recovered" cases plus Table 2. The protocol (agreement, CIs) is pre-registered.

### 4.6 Ablations (small table plus supplement)

- Reword-K factorial: joint vs i.i.d. decoding (Verbalized-Sampling-style list), composition phrasing on/off, explicit binding on/off.
- 1 vs 4 seeds per candidate (P3).
- Pareto vs top-fitness parents.
- Mutator size.
- Search-judge swap.

---

## 5. Method: distillation-aware prompt evolution

The method is `dap/evolve.py`; its zero-feedback corner is `dap/reword.py`.

1. **Initialisation (Reword-K).** One call to a small instruct LLM returns K *jointly* diverse, intent-preserving wordings. Allowed changes: order of mention, sentence structure, explicit binding, viewpoint and composition phrasing. **No new objects or attributes.**
2. **Allocation rule (from P2 and P3).** Spend the budget on wordings rather than seeds. Use one seed per candidate on students (common random numbers), and n > 1 seeds on teachers.
3. **Fitness.** The *original* intent's checklist, scored atom by atom by the search judge. Optionally add a teacher-precision term, offline only.
4. **Parents.** GEPA-style Pareto front over checklist atoms, which crosses the flat regions that tempering creates in a binary landscape.
5. **Mutation.** Reflective: the LLM sees the failed atoms.
6. **Output.** K mutually distinct successful wordings (farthest-point selection on the student's own images; no teacher at test time). The run stops at K successes or when the budget is spent.

**Cost honesty.** Reword-K at batch 1 with a 1.7–4B model is about 0.6–1.2 s (≈ 150 output tokens). That is about one image on klein and Z-Image-Turbo (0.67–0.88 s), but 2–5 SDXL-student images. All tables are therefore at equal wall-clock, and the equal-time-seeds row re-spends the LLM time. If the effect is clearest on DiT students, we say so.

**Not in this paper.** Amortized RL rewriters (APE, FaithRewriter, PE-OPSD and TIDE occupy that space); video; FLUX 3 klein and Qwen-Image-2.1. Evolution logs will be released as a dataset.

---

## 6. Positioning (one-line diffs)

| Work | Diff |
|---|---|
| Starodubcev et al. CVPR'24 (per-sample student vs teacher; adaptive cascade) | We study per-prompt success **rates over seeds**, reachability (reliable vs lucky) and the seed/wording decomposition across one teacher's students, with prompt-side recovery. |
| DefaultShift arXiv'26 (shift of *unspecified* attribute defaults, 14 pairs) | Complementary: specified intents, reachability, prompting. Its peak-mode concentration is consistent with tempering. |
| Gandikota & Bau WACV'26; Harrington et al. CVPR'26; MoNO; CNO; STRIDE; DP-DMD | Noise-side and training-side diversity recovery. Their methods are our baselines; we show where the leverage moved (wordings). |
| PRIS CVPR'26; RAISE CVPR'26; ReflectionFlow ICCV'25; GenPilot; OPT2I; RATTPO; Noise Hypernetworks NeurIPS'25 | Test-time prompt or noise search on single models. We test the *student-minus-teacher* interaction with one selector at equal seconds, and explain the RATTPO/RAISE observations on distilled backbones. |
| POET ECCV'26; PromptEnhancer CVPR'26; APE; PE-OPSD; Prompt Expansion ACL'24; PAG CVPR'25 | Trained rewriters and enhancers. Ours is zero-shot and evolution-based, derived from the law, and evaluated against the official PE and generic expansion. |
| Verbalized Sampling arXiv'25 | Prior art for jointly decoding a diverse list. We apply it to T2I wordings under an intent-preservation constraint and ablate it. |
| StyleForge arXiv 2610.05066; Velocity corrector for Z-Image-Turbo arXiv 2610.12899 | Wording-based or tiny model-side fixes for step-distilled models. Concurrent; the corrector is a model-side baseline on the same student. |
| SHIP arXiv 2608.21748; Progressive Seed Pruning arXiv 2607.21591 | Calibrated selection on held-out prompts; seed-axis pruning. Inform our "reliable" definition and seed-side baselines. |
| Yue et al. NeurIPS'25; Ge et al. arXiv 2608.11829 (reverse-KL OPD: small-K pass@K ↑, large-K ↓); Huang et al. ICLR'25; Karan & Du | The LLM analogue. We give the diffusion-distillation version, with a per-prompt estimator, controls and a prompt-side remedy. |
| Diffusion-DPO; SPO | Used as "sharpened but not distilled" controls. |

**Novelty statement.** We know of no work that, for a fixed diffusion teacher and its distilled students:

- (a) measures per-prompt success rates and *reliable vs lucky* reachability;
- (b) separates tempering from re-addressing, guidance and preference sharpening with controls;
- (c) shows, and predicts from (β, σ), how a prompt-evolution strategy's seed/wording allocation should change across distilled variants.

---

## 7. Gates, outcomes, fallbacks

| Gate | Date | Criterion | If it fails |
|---|---|---|---|
| **G1** | Oct 24 | On SDXL {teacher, DMD2, Lightning, LCM}, 150 intents, **direction only** (z ≈ 1 at 150 intents, so no CI test yet). (a) Rewording's deployable gain is larger on ≥ 2 mode-seeking students than on the teacher, at equal candidate count. (b) After subtracting the placebo floor, the reword and evolve rungs recover a non-zero share of the intents that are reseed-only or lost for the student but teacher-reachable. β is **reported, not gating** | (b) only: a reachability paper (title option 3). Neither: ICCV'27 |
| **G2** | Nov 3 | At ≥ 600 intents: the interaction CI excludes 0 for ≥ 2 students; the ledger replicates on klein; evolution or Reword-K beats equal-time seeds with the same selector on ≥ 2/3 students | Submit only if E1 and E2 are strong; otherwise ICCV |
| **G3** | Nov 6 | Human 2AFC complete | Report as a limitation |

**Readings of the (β, σ) plane**, all publishable because the ledger carries the paper:

| Region | Reading |
|---|---|
| β > 1, small σ | Tempered students (title 1) |
| β ≈ 1, large σ | Students re-address prompts: "prompts don't distill" (title 2) |
| β ≈ w*-teacher | Distillation ≈ extra guidance, which is itself a useful calibration |

**Titles** (working title neutral until G2):
1. *Reword, Don't Reseed: Prompt Evolution Across Distilled Diffusion Students* (working title)
2. If the re-addressed share is large: *Reword, Don't Reseed: Prompt Evolution Recovers What Diffusion Distillation Tempers Away*
3. If students mostly move reach from seeds to words: *Reword, Don't Reseed: Distilled Diffusion Students Move Their Teacher's Reach from Seeds to Words*
4. Reachability-only outcome: *A Reachability Study of Prompt Evolution Across Distilled Diffusion Students*

---

## 8. Compute and timeline

About 250 H100-GPU-h including a 35% buffer (≈ $500–750), plus about $500 for human labels and 2AFC. Two GPUs from Oct 19 to Nov 8 are enough; burst to 4 for Table 2. The ledger itself is about 40 GPU-h. The binding constraint is author time, which is why DAPPER-SFT, the GRPO adapter, video and extra families were cut.

| Date | Work |
|---|---|
| **Oct 17–18** | Create OpenReview profiles now (moderation takes up to 2 weeks). Rent the pod and download the models. Smoke-test every variant: latency, NFE, **Reword-K latency vs SDXL-student image latency**. Install the GenEval detector. Resolve `verify: true` configs. |
| Oct 19–22 | E1 on SDXL with controls; ledger on SDXL × 150 intents; hand labels. Write §2–3 while compute runs. |
| **Oct 23–24** | **G1** |
| Oct 25–31 | klein E1 + ledger; Z-Image E1 + ledger (150); width × depth plane on DMD2 and klein; 2×2 transfer; prediction test. |
| Nov 1–3 | Table 2 at equal wall-clock. **G2** |
| Nov 4–6 | Human 2AFC; ablations. **G3** |
| Nov 7–8 | Freeze; figures |
| **Nov 10** | **Register** |
| Nov 9–15 | Write; adversarial self-review against the checklist below |
| **Nov 16** | **Submit** |
| Nov 17–23 | Supplement and compute report |

Fallback: ICCV 2027 (around Mar 5–8). CVPR decisions (Feb 25) come before it.

**8-page layout:**
- Fig. 1: teaser.
- §1 intro; §2 related work.
- §3: the law, as a box.
- Fig. 2: ledger.
- Fig. 3: (a) law + controls, (b) width × depth at equal seconds, (c) transfer.
- Table 1: (β, σ) + controls.
- Table 2: K = 4 deployment.
- Fig. 4: qualitative.
- Everything else goes to the supplement.

---

## 9. Reviewer-attack checklist (what we pre-empt in the submission)

| Attack | Pre-emption |
|---|---|
| "Expected findings; trivial remedy" | The ledger (reliable vs lucky reach) and the *predicted* interaction carry the paper. The remedy is an evolution strategy with a law-derived rule, ablated against generic expansion, no-LLM tags and the official PE. |
| "β depends on estimator, judge or task mix" | Within-task GLMM; brackets; controls; per-model judge confusion with propagated uncertainty; detector replication; teacher-defined mode test. |
| "It's just CFG / preference sharpening" | CFG-matched teachers, the DPO/SPO controls and the PCM one-factor pair, all in Table 1. |
| "Shared-seed or oracle artifacts; winner's curse" | Fresh seeds per wording; one selector; chosen wordings re-scored on fresh seeds by held-out judges. |
| "Not equal compute" | Wall-clock axis including LLM, judge and PE time; equal-time seeds row. |
| "Same judge for search and eval" | Search: Qwen3-VL. Eval: detector, Gemma, frontier pairwise, humans. Injection checker ≠ rewriter. |
| "The LLM invents diversity" | Strict and lenient injection rates; success-filtered k-NN teacher coverage. |
| "Old backbone" | SDXL is the only base with ≥ 6 public students of different objectives; klein and Z-Image are 2026 models. |
| "Novelty vs Starodubcev / DefaultShift / VS / Ge et al." | Narrowed claims (§6). |
| "Clarity" | One takeaway, three parts, 7 floats. |

---

## Appendix A: Review history

| Round | Version | Scores | Main criticisms | Response |
|---|---|---|---|---|
| 1 | v1 ("Distillation is sharpening" + DAPPER) | 3 / 3 / AC 3 | Binomial β biased; CFG/RL confounds; P2 and P5 tautological; DAPPER not novel (APE, SetPO); circular metrics; NFE-only budgets; 3 papers in one | (β, σ) GLMM; controls; retitled; cut GRPO and families; wall-clock accounting (v2) |
| 2 | v2 ("Reword, Don't Reseed: tempered teachers") | 3 / 3 / AC 4 | Drifted from the brief (evolution sidelined); "flip" is a σ effect and shared seeds manufacture it; task-mix confound; no sharpened-not-distilled control; Deming and joint-cluster tests misleading; Reword-K ≈ expansion; equal-K not equal-time; coverage unsound; small success-space effects | Ledger with evolution as instrument and method; interaction not flip; within-task β; DPO/SPO and PCM controls; teacher-defined modes; fresh seeds; Naeem coverage; equal-time seeds, tags and teacher+Reword-K rows; prediction test; honest power analysis (v3) |
| 3 | v3 (ledger + law + allocation) | 3 / AC 4 ("presentable; stop revising, run G1") | Ledger evolution bug (re-tested the failed wording, stopped at the first single-seed success); 0.5 threshold cannot see tempering (lucky → lost, not → reword); placebo/noise floor; unequal tests and tries; σ level (intent vs wording); speed confounds the equal-seconds interaction; prediction partly circular; baselines not implemented | Fixed and regression-tested evolution; equal fresh-seed tests, placebo re-test, second-judge lucky images, thresholds, equal-budget lucky estimate; corrected ledger prediction pre-registered from the law; two-level σ fit; mechanism claim at equal candidate count; per-task, held-out-intent predictions of the measured arms; CADS, hybrid, detector judge and OPT2I-style ablation implemented (v3.1) |

## Appendix B: Code map

| Element | Code |
|---|---|
| Law + controls (Table 1) | `scripts/sharpening.py` (within-task GLMM, brackets, self-split, CFG-matched fits, disjoint seeds, judge ε); `dap/metrics.py::fit_tempering`, `self_split_control`, `teacher_mode_counts`, `fit_mode_tempering` |
| Ledger (Fig. 2) | `scripts/reach_ledger.py` (placebo, equal tests, thresholds, `--verify-judge`, `--teacher-candidate-seeds`) |
| Interaction CIs and pre-registered predictions | `scripts/analyze.py interaction` / `predict`; `dap/metrics.py::fit_tempering_grid`, `predict_ledger`, `predict_scaling` |
| Judge-independent GenEval scoring | `dap/geneval_judge.py` (`--eval-judge geneval`) |
| Noise-side baselines | `dap/generation.py` (`noise="pink" / "cads"`, `hybrid_teacher_first`) |
| Width × depth, interaction, prediction (Fig. 3b) | `scripts/search_scaling.py --axis seconds` (fresh-seed wording arms, teacher arms, `--teacher-cfg`, winner's-curse re-scoring); `dap/metrics.py::paired_interaction_ci`, `predict_scaling` |
| Transfer and variance (Fig. 3c, supplement) | `scripts/variance.py` → `portability.py`, `amplification.py` |
| Deployment (Table 2) | `scripts/remedy_eval.py`, `dap/reword.py` |
| Method | `dap/evolve.py` (allocation, Pareto parents, population output) |
| Toy and simulations | `scripts/toy_tempering.py`; `tests/test_metrics.py` |
| Tests | `pytest -q tests`: 36 tests, CPU, tiny random SDXL built from configs |

## Appendix C: References (verified on arXiv / model cards)

- **Distillation, collapse and defaults:**
  - Gandikota & Bau, WACV'26, arXiv:2503.10637.
  - Decoupled-DMD, arXiv:2511.22677. DMDR, arXiv:2511.13649. 1.x-Distill, arXiv:2604.04018. DP-DMD, arXiv:2602.03139. Phased DMD, arXiv:2510.27684.
  - Harrington et al., CVPR'26, arXiv:2601.00090. MoNO, arXiv:2607.23937. CNO, ICLR'26. STRIDE, arXiv:2605.11494.
  - DefaultShift, arXiv:2608.21784. Decomposable Probe, arXiv:2607.03256.
  - Starodubcev et al., CVPR'24, arXiv:2312.10835. Diversity-Rewarded CFG Distillation, arXiv:2410.06084.
- **Seeds and diversity measurement:** Good Seed, arXiv:2405.14828. Reliable Random Seeds, ICLR'25. W1KP, arXiv:2406.08482. SliderSpace, arXiv:2502.01639. Scendi / Conditional Vendi.
- **Concurrent (Aug–Oct 2026):** StyleForge, arXiv:2610.05066. Velocity corrector for Z-Image-Turbo, arXiv:2610.12899. SHIP, arXiv:2608.21748. Progressive Seed Pruning, arXiv:2607.21591.
- **Test-time search and prompting:** PRIS, CVPR'26, arXiv:2512.03534. RAISE, CVPR'26, arXiv:2603.00483. ReflectionFlow, ICCV'25, arXiv:2504.16080. GenPilot, arXiv:2510.07217. OPT2I, TMLR'24, arXiv:2403.17804. RATTPO, arXiv:2506.16853. Noise Hypernetworks, NeurIPS'25. ReNO, NeurIPS'24, arXiv:2406.04312.
- **Rewriters and enhancers:** POET, ECCV'26, arXiv:2510.12041. PromptEnhancer, CVPR'26. APE, arXiv:2606.00204. PE-OPSD, arXiv:2609.36638. Prompt Expansion, ACL'24. PAG, CVPR'25. Verbalized Sampling, arXiv:2510.01171.
- **Sharpening in LLMs:** Yue et al., NeurIPS'25. Ge et al., arXiv:2608.11829. Huang et al., arXiv:2412.01951. Karan & Du, arXiv:2510.14901. SetPO, arXiv:2602.01062. Max@K RL, arXiv:2607.14962.
- **Guidance and preference:** CADS, ICLR'24. Guidance interval, NeurIPS'24. Bradley & Nakkiran; Chidambaram et al. Diffusion-DPO; SPO.
- **Models:** SDXL, SDXL-Turbo/ADD, LADD, SDXL-Lightning, DMD/DMD2, LCM, PCM, TCD, Hyper-SD; FLUX.2-klein, Z-Image(-Turbo), ERNIE-Image(-Turbo) model cards; GenEval, GenEval-2, DPG-Bench, T2I-CompBench++, OneIG-Bench.
