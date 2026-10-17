# Reword, Don't Reseed: Step-Distilled Diffusion Models Are Tempered Teachers

*CVPR 2027 main-track proposal: **v2**, revised after simulated review round 1 (two reviewers scored v1 at 3, and an AC predicted 3). OpenReview registration is due **Nov 10**, the paper **Nov 16** and the supplement **Nov 23** (AoE).*
*Everything below is a plan. No result here has been measured yet, and the abstract assumes the pre-registered predictions hold. Section 8 gives the go/no-go gates and the fallback stories.*

---

## 0. TL;DR

**One takeaway.** *A distilled student decides its teacher's coin flips.* Prompts the teacher usually renders correctly become reliable. Prompts it only sometimes gets right can no longer be reached by re-seeding. So for students: **reword, don't reseed**.

**Three contributions:**

1. **A measured law, with controls.** Every student is compared with its own teacher on per-prompt success. A judge-calibrated random-effects estimator separates
   - *tempering* (β: the student pushes the teacher's success rates toward 0/1, in the teacher's order) from
   - *re-addressing* (σ: prompt-specific deviations from the teacher).
   
   Controls rule out the obvious confounds: the teacher against itself on split seeds, a CFG-matched teacher, a non-distilled sibling, and a judge-free mode-level test.
2. **The practical consequence.** Distillation contracts the seed axis much more than the wording axis. For teachers, extra seeds match or beat extra wordings. For mode-seeking students the ranking flips, at equal wall-clock. Teacher-built enhancers transfer to students in direction but with distorted magnitude.
3. **A remedy that follows directly.** *Reword-K*: one ≤ 4B LLM call writes K jointly diverse, intent-preserving rewordings, rendered with one seed each. An optional *DAPPER-SFT* adapter is trained offline, using the teacher as a free reference. Both are evaluated against noise-side and prompt-side diversity methods at equal wall-clock, using teacher coverage, held-out judges and a human 2AFC.

**What changed from v1** (Appendix A):

- **Dropped:** the GRPO adapter, video and two new model families; the "β resolves the seed-vs-prompt debate" claim.
- **Replaced** the binomial estimator with a (β, σ) GLMM.
- **Added** CFG, self-split and sibling controls, and a judge-free mode test.
- **Fixed** circular metrics, compute accounting (wall-clock including LLM and judge time) and citations.

---

## 1. Motivation and gap

**Students are the deployment default.** Every recent family ships few-step students:

| Family | Teacher | Student(s) |
|---|---|---|
| SDXL | 30 steps | Turbo, Lightning, DMD2, LCM, Hyper, TCD |
| FLUX.2-klein | base, 50 steps | klein, 4 steps |
| Z-Image | 50 steps | Turbo, 8 NFE |
| ERNIE-Image | — | Turbo, 8 steps |
| Qwen-Image-2.1 | — | Turbo, 8 steps; Lightning, 4 steps |
| FLUX 3 klein | — | distilled, 16 steps |
| Wan2.2 | — | Lightning |

**The enhancers that ship with them were built for the teacher,** or are shared unchanged:

- The Qwen-Image-2.1 PE is demonstrated with the 40-step teacher.
- FLUX 3 klein has one mandatory upsampler for base and distilled.
- HunyuanImage-3.0-Distil: "keep all other parameters unchanged".
- Wan2.2-Lightning reuses Wan's prompt extender.
- Z-Image's PE was aligned before distillation and RL.

**They are also mis-sized for students.** PE-OPSD (arXiv 2609.36638) measures Z-Image-Turbo at 0.88 s per image alone, 8.53 s with PromptEnhancer-7B and 34.2 s with the 32B version. FLUX.2-klein goes from 0.67 s to 8.18 s.

**What is known:**

- **Students lose seed diversity**, reported in at least 7 papers:
  - DreamSim, SDXL 0.337 → DMD2 0.264 (Gandikota & Bau, WACV'26);
  - DINO, SDXL 0.219 → DMD-4 0.109 (DP-DMD);
  - OneIG diversity, Qwen-Image 0.194 → Lightning 0.116.
- **The collapse happens at the first, high-noise step.**
- **Students keep the teacher's representations**: LoRAs and sliders transfer.
- **Students often match or beat their teachers at pass@1 on GenEval** (DMD2 0.58 vs SDXL 0.55; schnell 0.69 vs dev 0.66), but lose on dense prompts (DPG: Z-Image 88.1 → Turbo 84.9).
- **CFG augmentation drives DMD-style distillation**, and CFG and RL act as "density sharpeners" (Decoupled-DMD arXiv 2511.22677; DMDR arXiv 2511.13649; 1.x-Distill arXiv 2604.04018).

**What is not known:** what distillation does to the *prompt interface*. No paper compares a teacher with its own students per prompt. No paper asks whether lost outcomes are *erased* or merely *re-addressed*, or whether the answer changes how users should spend samples.

**Public model cards are suggestive, not conclusive.** Converted to aggregate logit gains (student Δ / teacher Δ):

| Source | Ratio |
|---|---|
| ERNIE PE, GenEval colors | 1.53 |
| ERNIE PE, GenEval overall | 1.07 |
| PE-OPSD PE, GenEval-2 | 1.34 |
| PE-OPSD PE, GenEval | **0.85** |

One of four goes the other way. Aggregate logits also differ from per-prompt logits (Jensen gap). We therefore expect a **modest** β, around 1.1–1.5, and plan statistical power for it (Section 3.4). The ERNIE PE raises Turbo's OneIG diversity by 80% (0.123 → 0.221), against 43% for its teacher (0.169 → 0.241). Prompt variation is a strong lever for students.

---

## 2. The tempered-teacher model

### 2.1 Definitions

An *intent* I (e.g. "a purple wine glass and a black apple") can be expressed by many *wordings* c, and each wording is rendered with *seeds* z. The success rate q(c) is the probability over seeds that the image satisfies I's checklist. The checklist is always the *original* prompt's, never the rewritten one's.

### 2.2 Model

  **logit q_S(c) = β · logit q_T(c) + b + σ·ε_c,  ε_c ~ N(0,1)**

- **β is an effective temperature**, a phenomenological quantity rather than a derived one.
  - β > 1: the student pushes the teacher's success rates toward 0 or 1 *in the teacher's order*.
  - β < 1: it flattens them, e.g. a regression student blurring between outcomes.
- **σ measures prompt-specific deviation** of the student from the teacher: the student *re-addresses* prompts. "Prompts don't distill" corresponds to large σ.
- Outcomes are regions of the (β, σ) plane, not a binary pivot.

**Why this form.** If the student were an exact mode-level tempering, π^S_k ∝ π_k^β, collapsing modes into success (G) and failure (F) gives exactly

  logit q_S = β·logit q_T + (1−β)·[H_β(π|G) − H_β(π|F)],

where H_β is the Rényi entropy within each group. Two consequences follow:

- **(a) The offset depends on the prompt,** which motivates the random effect σ rather than a constant b.
- **(b) "Failure is diverse, success is canonical."** When an intent has one canonical success mode and many failure modes, H(G) < H(F). With β > 1 the offset is then *positive*, so tempering *raises* pass@1 on templated prompts. This is a mechanism for students beating teachers at pass@1 on GenEval while losing reach. It is testable with atom-level outcomes.

**Toy evidence** (`scripts/toy_tempering.py`, runs on CPU). Setup: a capacity-limited student (one Gaussian per condition) fitted to a bimodal teacher c·N(+d,1) + (1−c)·N(−d,1), where success is x > 0.

| Mode separation d | Reverse-KL student (DMD-like) | Forward-KL student |
|---|---|---|
| 3 (separated) | logit slope 3.9; seed spread collapses to one mode (sd 1.0 vs 2.6) | slope 0.89; seed sd 2.6 |
| ≤ 2 (overlapping) | slope ≤ 1.5 | — |
| all | — | slope < 1 (flattening) |

So mode-seeking students temper when semantic outcomes are well separated, while mode-covering students *flatten*. This refines v1's "β ≈ 1 for consistency models": consistency or regression students may show β ≤ 1 together with blur.

### 2.3 Two predictions, one remedy

- **(i) Seed contraction.** Re-seeding gains, pass@k − pass@1, shrink on prompts with intermediate q_T. Lost reach concentrates on prompts the teacher solves *sometimes*. This is an algebraic consequence of β > 1, so we report it as a consequence, not a separate claim.
- **(ii) The wording axis gains relative to the seed axis.** Wording effects are amplified, Δlogit q_S ≈ β·Δlogit q_T, while seed effects contract. The decision "K seeds or K wordings?" can therefore **flip** between teacher and student.
  - Caveat: the model also predicts a limit. If every wording of an intent sits below the student's threshold, rewording cannot help either. We report that population explicitly.
- **Remedy:** sample a few intent-preserving wordings (Section 5).

### 2.4 What would *not* be tempering: the null we must beat

"Mode collapse" alone is the null: the student collapses onto an *arbitrary* mode, lowering diversity with β ≈ 1 and large σ. Tempering means collapse onto the teacher's *dominant* mode. We test this directly with a judge-free, mode-level statistic: student images are clustered jointly with teacher images in DINOv2 space, and we measure top-mode agreement against the arbitrary-collapse null (`dap.metrics.fit_mode_tempering`).

**Guidance is the other null.** CFG tempers too. We fit each student against the teacher run at the student's baked-in guidance (w ∈ {5, 8, 12} for SDXL), and report "a 4-step DMD2 behaves like a w* teacher" when that is what we find.

---

## 3. Measurement protocol

### 3.1 Estimator

This is `dap.metrics.fit_tempering(model="re")`.

- The teacher's per-prompt rate is latent: a posterior on a logit grid under an empirical-Bayes Beta prior. It is integrated out, so few seeds and rates near 0/1 do not attenuate β.
- The student likelihood is binomial with a logit-normal random effect (σ), integrated by Gauss–Hermite quadrature.
- Judge confusion (false-positive, false-negative) can differ between the teacher's and the student's images.
- Binomial and beta-binomial fits are reported as brackets in the supplement.

### 3.2 Why this estimator (simulations in the supplement; reproduced in `tests/`)

| True mechanism | Naive logit slope | Binomial EIV | Beta-binomial EIV | **(β, σ) GLMM** |
|---|---|---|---|---|
| β = 4, σ = 0, n = 32 | 1.56 (attenuated) | 4.01 | — | ≈ 4 |
| β = 1, σ = 1.5 (student = different model, not sharper) | — | **1.20** (false sharpening) | **0.69** (false flattening) | **1.02, σ̂ = 1.41** |
| β = 1.5, σ = 1.5 | — | 1.80 | 1.10 | **1.53, σ̂ = 1.43** |
| β = 4, judge FP/FN = 8%/12% on both models, uncorrected | — | 1.8 | — | ≈ 4 with ε corrected |
| β = 1, judge noisier on teacher images, pooled ε | — | 1.50–1.54 | — | needs per-model ε, hence hand labels |

Power: 300–553 prompts × 16 seeds detect β ≈ 1.2 (EIV 95% range 1.13–1.32).

### 3.3 Controls (one row each in Table 1)

| Control | Expected | Rules out |
|---|---|---|
| **Teacher self-split** (32 seeds split 16/16) | β ≈ 1, σ ≈ 0 | Estimator artifacts (`dap.metrics.self_split_control`) |
| **CFG-matched teacher** (w ∈ {5, 8, 12}) | β > 1 rising with w | "It's just guidance". Each student is also fitted against the CFG-matched teacher |
| **Non-distilled sibling** (same teacher, different solver/steps without distillation, e.g. DPM-Solver++ at 10 steps) | β ≈ 1, σ > 0 | "Any different sampler looks like this" |
| **Consistency students** (LCM, TCD) | β ≤ 1, possibly with blur | Negative control for "mode-seeking tempers" |

### 3.4 Judges and calibration

- **Search and selection** (only inside DAPPER-SFT data generation): Qwen3-VL-8B.
- **Evaluation:**
  - the GenEval *detector* pipeline, which is judge-independent;
  - Gemma-3-27B or Llama-4-class VLM, *not* Qwen-based (InternVL3.5 is built on Qwen3, so it is excluded as an "independent" judge);
  - a frontier pairwise judge on subsets.
- **Hand labels.** 400–600 teacher and student images, stratified by q-bin and by c ∈ {0, n}, labelled by two annotators. These give per-model confusion rates that the estimator ingests.
- β is reported under each judge. Detector-vs-VLM agreement is in the supplement.

---

## 4. Experiments (MVP for CVPR)

### 4.1 Models

| Family | Teacher | Students | Role |
|---|---|---|---|
| **SDXL** (full) | SDXL-base, 30 steps, w = 5 | Turbo (ADD), Lightning-4 (progressive adversarial; plus 1/2/8 step sweep), DMD2-4, LCM-4, TCD-4, Hyper-4 | Objective sweep with the teacher fixed |
| **FLUX.2-klein** (full) | klein-base-4B, 50 steps, CFG 4 | klein-4B, 4 steps | Clean vendor undistilled/distilled pair; DiT + LLM text encoder + flow; Apache-2.0 |
| **Z-Image** (partial: E1 + Table 2) | Z-Image, 50 steps, at 768 px | Z-Image-Turbo (DMD + RL; labelled as RL-confounded) | Production student |

Repo IDs and checkpoint filenames are verified in `configs/families.yaml`. SDXL-Turbo's native 512 px is labelled; we add SD2.1 → SD-Turbo as a resolution-matched ADD pair if time allows.

### 4.2 E1: Do students temper their teachers?

- **Prompts.** GenEval: 553 prompts, detector plus VLM, for SDXL. GenEval-2: 800 prompts for klein and Z-Image.
- **Seeds.** 16 per student; 32 for teachers, so the self-split works.
- **Fig. 2.** Binned E[q_S | q_T] per student with 95% bands, controls in grey, panels ordered by objective family.
- **Table 1.** Per student:
  - objective and steps;
  - β̂ [CI], σ̂ and b̂, both vs the default teacher and vs the CFG-matched teacher;
  - pass@1 and pass@16 (Δ vs teacher);
  - lost reach and gained reach;
  - seed DreamSim;
  - top-mode agreement vs null;
  - one row per control.

### 4.3 E2: Seed or wording? (one grid per model)

- **Grid.** 200 intents (SDXL) or 150 (klein) × 8 wordings × 8 seeds, on the teacher plus DMD2, Lightning, LCM and klein. The 8 wordings are:
  - the original;
  - 5 paraphrases;
  - the teacher-built PE rewrite;
  - a generic LLM rewrite.
- **Fig. 3a.** Absolute seed-induced and wording-induced variation in DINOv2 and success space, teacher vs student. We report absolute V_seed and V_para, not only their ratio, because the ratio rises mechanically when V_seed falls (`scripts/variance.py`).
- **Fig. 3b, the headline panel.** Best-of-K over seeds vs over wordings, K = 1…8, at **wall-clock including LLM time**, for teacher vs student.
  - Prediction: on the teacher, seeds ≥ random wordings, replicating OPT2I's finding on SD2.1. On mode-seeking students the order flips. Consistency students sit in between.
  - A feedback-driven evolution curve (`dap/evolve.py`, student-only fitness) is a dashed reference.
- **Fig. 3c.** Amplification: per-rewrite Δlogit q_S vs Δlogit q_T, with official-PE rewrites highlighted.
  - The slope, from Deming regression, is checked against β̂ from E1 as an independent estimate.
  - Rank transfer (Spearman) and top-1 agreement of wordings come from the same grid (`scripts/amplification.py`, `scripts/portability.py`).
- **Seed portability falls out of the same grid.** Does a seed mean the same image for teacher and student? We measure it by same-seed image coupling. Trajectory-preserving students should show coupling; DMD and adversarial students should not.
- **Reconciling prior results** is stated as *consistent with*, not *resolved by*. One paragraph covers PRIS (FLUX-dev: prompt > seed) vs Noise Hypernetworks (SD-Turbo: best-of-N > MILS at about 10× lower wall-clock). We reproduce the Noise Hypernetworks comparison at equal wall-clock and explain it: a 95 s LLM loop vs one 0.2 s call, and binary vs continuous reward.

### 4.4 E3: Remedy (Table 2)

- **Setup.** 3 students (SDXL-DMD2, klein-4B, Z-Image-Turbo). Prompts: GenEval-2, DPG-hard (264) and a T2I-CompBench subset, plus held-out user prompts (Pick-a-Pic / DiffusionDB) against benchmark overfitting.
- **Main condition:** K = 4 images. K = 1 is secondary.
- **Implementation:** `scripts/remedy_eval.py`.

**Rows:**

| Side | Methods |
|---|---|
| Noise | i.i.d. seeds; pink-noise latents; CADS; **hybrid teacher-first-step** (Gandikota & Bau; +1 teacher NFE); one noise-optimization diversity method (MoNO / Harrington / CNO, whichever has code) |
| Prompt | **teacher-built/official PE** (FLUX.2 upsampler, Z-Image PE, generic enhancer for SDXL), and sampled K times at temperature 1 as the "cheap set" baseline; generic "K diverse expansions" (Prompt-Expansion-style control); random paraphrases |
| Ours | **Reword-K** (zero-shot); **DAPPER-SFT** if it passes Gate 3 |
| Reference | teacher with K seeds at its own cost; a Reword-K + pink-noise combination row |

**Columns:**

- **Alignment:** mean success and pass@K under held-out judges and the detector.
- **Diversity:** Vendi and DreamSim.
- **Teacher coverage:** coverage of the *success-filtered* teacher samples for the *original* prompt, computed in CLIP space (not the DINOv2 space used for selection), on held-out teacher seeds.
- **Attribute-injection rate:** does the LLM invent content?
- **HPSv3**, as a quality guard.
- **End-to-end latency.**

**Fig. 4.** K = 4 grids: 3 prompts × 4 methods, prompt IDs drawn at random and stated.

**Human 2AFC.** About 120 prompts × 3 comparisons × 5 raters. Questions: "faithful to the prompt?" and "more varied while faithful?". Protocol, agreement (Krippendorff's α) and CIs are reported, with the protocol pre-registered before DAPPER is evaluated.

### 4.5 Ablations (Table 3, small)

- Reword-K vs generic expansion vs paraphrase: is "intent-preserving + jointly diverse" the active ingredient?
- Joint K-list decoding vs K i.i.d. samples.
- K ∈ {2, 4, 8}.
- Zero-shot 4B vs SFT 1.7B.
- DAPPER-SFT selection on/off; teacher reference on/off.
- Search-judge swap.

---

## 5. Method

### 5.1 Reword-K (main)

- One call to a ≤ 4B instruct LLM (Qwen3-4B-Instruct-2507) returns a JSON list of K rewordings, written *jointly* so they differ from each other (`dap/reword.py`).
- Allowed edits: order of mention, sentence structure, explicit attribute binding, viewpoint and composition phrasing.
- **Forbidden:** new objects, attributes or style words.
- Each rewording gets one seed.
- **No search judge and no teacher at inference.**
- **Cost:** about 0.2 s on one H100 (about 150 output tokens for K = 4). That is below one student image and 10–100× cheaper than shipped enhancers.

### 5.2 DAPPER-SFT (optional; the distillation-specific variant)

**Offline, per student:**

1. Run student-in-the-loop reflective evolution (`dap/evolve.py`) on about 1.5–5k training prompts. Fitness is the original-intent checklist plus λ·teacher precision.
2. Use facility-location set selection over *teacher* samples to pick K successful, complementary wordings per prompt.
3. Run SFT of Qwen3-1.7B on (prompt → K-set).

**The teacher is used only offline**, as a free reference for training data. At deployment DAPPER-SFT costs the same as Reword-K. Teacher coverage at evaluation uses held-out teacher seeds and a different feature space from selection, which avoids circularity. If DAPPER-SFT does not beat Reword-K by Nov 6, it becomes an ablation.

**Explicitly out of scope** (ICCV or journal extension): GRPO with leave-one-out coverage reward, student-conditioned adapters and transfer matrices, video. Why: APE (arXiv 2606.00204) already trains 0.6–4B enhancers with GRPO against Z-Image-Turbo, and SetPO (arXiv 2602.01062) already uses leave-one-out set credit. An RL adapter would not be novel here.

---

## 6. Related work and novelty (one-line diffs)

| Work | What it shows | Our diff |
|---|---|---|
| Gandikota & Bau, WACV'26; DP-DMD; Phased DMD; Harrington et al. CVPR'26; MoNO; CNO ICLR'26 | Students lose seed diversity (step 1, low frequency); noise-side and training-side fixes | We compare students with their *own teacher per prompt*, distinguish teacher-ordered tempering from arbitrary collapse and CFG, and show where diversity *went* (the wording axis). Their fixes are our baselines. |
| GAD, ICML'26; Decomposable Probe, arXiv 2607.03256 | Students are less sensitive to noise; perturbation selectivity across 23 models | Different measurement (perturbation response). We measure per-prompt success, reachability and the seed/wording asymmetry. |
| PRIS CVPR'26; ReflectionFlow ICCV'25; Noise Hypernetworks NeurIPS'25; OPT2I TMLR'24; GenPilot; RATTPO; RAISE | Seed vs prompt test-time scaling, with conflicting conclusions | We measure the seed/wording asymmetry *per teacher–student pair*. The flip is a distillation effect, consistent with both camps; we do not claim to resolve them. |
| PromptEnhancer CVPR'26; POET ECCV'26; PE-OPSD; APE; FaithRewriter; Prompt Expansion ACL'24; PAG CVPR'25 | Trained rewriters and enhancers; enhancer folded into weights; diverse expansions | Our remedy is a *consequence* of the analysis, zero-shot first. The student-specific part is ablated against generic expansion and the official PE, at equal wall-clock. |
| Yue et al. NeurIPS'25; Huang et al. ICLR'25 (sharpening mechanism); Karan & Du arXiv 2510.14901 (power sampling); SetPO | RL and self-improvement sharpen LLMs: pass@1 ↑, pass@k ↓ | Cross-domain analogue for diffusion distillation, with a per-prompt estimator, controls and a prompt-side remedy. |
| Starodubcev et al. CVPR'24; Diversity-Rewarded CFG Distillation, ICLR'25 | Students beat teachers on many samples; diversity-aware distillation | Explained by the Rényi offset ("failure is diverse"); weight-side vs our prompt-side. |
| Bradley & Nakkiran; Chidambaram et al. (what CFG does) | CFG does not sample p·p(c\|x)^w | Why we control for CFG empirically rather than assuming it tempers. |

**Novelty statement**, checked by four literature sweeps (about 200 papers) and three simulated reviews. We found no prior work that:

- (a) compares diffusion teachers with their own students on per-prompt success and reachability;
- (b) separates teacher-ordered tempering from arbitrary collapse and CFG with controls;
- (c) measures the seed/wording asymmetry as a distillation effect and acts on it at inference.

---

## 7. Reviewer-attack checklist, mapped to design

Sources: 3 simulated reviews plus 107 mined OpenReview papers and 429 reviews.

| Attack (precedent) | Pre-emption in the submission |
|---|---|
| "Just LLM rewriting" (9/16 prompt-opt papers; the #1 killer) | Contribution = new axis (teacher vs own student). The remedy is deliberately simple and derived from the analysis; it is ablated against generic expansion and the official PE. |
| "Restatement of mode collapse / it's CFG" | Teacher-ordered test vs arbitrary-collapse null; CFG-matched teacher; consistency students as negative control; the practical flip in Fig. 3b. |
| "β depends on estimator/judge" | (β, σ) GLMM; brackets; self-split and sibling controls; per-model judge confusion from hand labels; detector replication; judge-free mode test. |
| "Optimized and evaluated with the same judge" (6/16; 5/14) | The search judge is used only for DAPPER data. Evaluation uses the detector, a non-Qwen VLM, a frontier pairwise judge and humans. Teacher coverage uses held-out seeds and a different feature space. |
| "Best-of-N / random baseline at matched compute" (15/26) | Seeds, pink, CADS, hybrid first step and noise optimization at **equal wall-clock including LLM time**; random paraphrases; teacher at equal wall-clock. |
| "Diversity comes from the LLM inventing content" | Attribute-injection rate; teacher coverage restricted to successful teacher samples; original-intent checklist. |
| "Only distilled models / dead end" (ReNO critique) | The teacher is a first-class arm everywhere; step sweep (Lightning 1/2/4/8); deployment numbers (latency of shipped PEs). |
| "Noise Hypernetworks found best-of-N > prompt optimization" | Reproduced at equal wall-clock and explained; we show where each wins. |
| "Single-seed fitness unreliable" | Fitness only in DAPPER data generation, with 2 seeds and common random numbers; seed-variance measured per model in E2. |
| "Human study too small" (7/16) | Pre-registered 2AFC: 5 raters, agreement, CIs, intent-fidelity question. |
| "GenEval overfitting" | GenEval-2, DPG-hard, T2I-CompBench and real user prompts. |
| "Clarity" (the #1 accept/reject separator) | One takeaway, 7 floats, three contributions. Everything else goes to the supplement. |

---

## 8. Gates, outcomes and fallbacks

| Gate | Date | Criterion | If it fails |
|---|---|---|---|
| **G1** | Oct 24 | (a) GLMM β̂ CI excludes 1 for ≥ 2 of {Turbo, Lightning, DMD2} **vs the CFG-matched teacher**, with self-split β̂ ≈ 1; (b) on students, best-of-K(wordings) − best-of-K(seeds) is larger than on the teacher | (b) only: submit as empirical "Reword, Don't Reseed" with β in the supplement. Neither: ICCV'27 |
| **G2** | Nov 3 | Reword-K beats i.i.d. seeds and the official PE on teacher coverage and diversity, at matched alignment and wall-clock, on ≥ 2 of 3 students | Submit only if E1/E2 are very strong; otherwise ICCV |
| **G3** | Nov 6 | DAPPER-SFT > Reword-K | DAPPER becomes an ablation |

**Pre-registered readings of the (β, σ) plane:**

- **β > 1, σ small:** tempered teachers. This is the main story.
- **β ≈ 1, σ large:** "prompts don't distill". Students re-address prompts, and student-specific rewording matters even more. The paper retitles; the code is unchanged.
- **β < 1 with blur:** flattening, as expected for regression students.

**Breadth risk.** Modern students (klein, Z-Image) may temper more than SDXL ones. If so, report it: "modern students temper more".

---

## 9. Compute and timeline

Compute is about 250 H100-GPU-h including a 35% buffer, roughly $500–750, plus about $400–600 for Prolific. Two GPUs from Oct 19 to Nov 8 are enough, with a burst to 4 for E5 on Nov 1–5. The binding constraint is author time. All runs save images in the GenEval layout and are judged asynchronously.

| Date | Work |
|---|---|
| **Oct 17–18** | Create OpenReview profiles now (moderation can take 2 weeks). Rent the pod. Download SDXL students, the klein pair, Z-Image, Qwen3-VL-8B, the non-Qwen eval VLM and Qwen3-4B. Run a GPU smoke test of every variant and measure latency. Install the GenEval detector. Resolve the `verify: true` config entries. |
| Oct 19–22 | E1 on SDXL: teacher 32 seeds, students 16, controls. Judge-calibration hand labels. E2 grid on SDXL. Draft the introduction. |
| **Oct 23–24** | **G1** |
| Oct 25–31 | E1 and E2 on klein; E1 on Z-Image. Reword-K pilot (template, K). DAPPER-SFT data engine in the background. Write §2–3. |
| Nov 1–3 | E3 full (Table 2) at equal wall-clock; SFT. **G2** |
| Nov 4–6 | Human 2AFC; ablations; detector checks. **G3** |
| Nov 7–8 | Freeze; figures. |
| **Nov 10** | **Register** |
| Nov 9–15 | Writing; adversarial self-review against Section 7 |
| **Nov 16** | **Submit** |
| Nov 17–23 | Supplement and compute report |

**Fallback: ICCV 2027** (around Mar 5–8). CVPR decisions (Feb 25) come before it, so CVPR reviews double as a free review round.

---

## 10. Self-assessment against the brief

| Criterion | Status |
|---|---|
| **Simple?** | One sentence ("students decide their teacher's coin flips: reword, don't reseed"), one law (β, σ), one cheap remedy. |
| **Broad?** | Every distilled image model, and every product that shows K images per prompt. A reusable diagnostic: we will release a one-command β/σ/pass@k script and a public table for common students, as a citation engine for distillation papers. |
| **Experiments relevant?** | Teacher vs own student (new). Controls for the two obvious confounds. Equal-wall-clock baselines from both the noise and prompt sides. Held-out judges, detector and human. |
| **Recent advances?** | FLUX.2-klein and Z-Image(-Turbo) (2026); Qwen3-VL judges; GenEval-2; PE-OPSD/APE as context; LLM sharpening literature (2025–26). |
| **Expected outcome** | The simulated AC estimates 4 (Borderline Accept) if G1–G2 pass, and 5 if the flip is clean on all 3 families and the human study is in. |

---

## Appendix A: v1 → v2 change log (responses to round-1 reviews)

| Round-1 criticism | v2 change |
|---|---|
| R1/AC: binomial β biased by prompt-specific student errors (1.20 false sharpening; beta-binomial 0.69) | (β, σ) logit-normal GLMM is now the default (`fit_tempering(model="re")`); brackets kept. |
| R1: CFG and RL confound distillation | CFG-matched teacher control; RL students analysed separately and labelled. |
| R1: judge noise differs between models | Per-model judge confusion (`eps`, `eps_S`) from hand labels; detector replication; judge-free top-mode agreement. |
| R1/R2: P2 and P5 are tautological consequences | Recast as consequences of one law. Seed-axis claims are algebra. The non-trivial claim is the *flip* between teacher and student. |
| R2: "β reconciles PRIS vs Noise Hypernetworks" overclaims | Dropped; "consistent with" plus an equal-wall-clock reproduction. |
| R1/R2: DAPPER is an add-on and not novel (APE, SetPO, PAG) | GRPO dropped. Zero-shot Reword-K is the main remedy; DAPPER-SFT is optional and offline-teacher only. |
| R2: teacher precision/coverage circular; eval judge shares the Qwen base | Coverage on held-out teacher seeds, success-filtered, in a different feature space; non-Qwen eval VLM. |
| R2: search budgeted only by NFE | `search_scaling.py --axis seconds` counts generation, judge and LLM time; online paraphrasing counted. |
| AC: scope is three papers; not feasible in 30 days | Two full families and one partial; one grid instead of three experiments; video and new families cut. |
| AC: "sharpening" in a vision title reads as image sharpening | Retitled "tempered teachers". |
| R1: motivating numbers oversold | Logit ratios reported, including the one against us (0.85). |
| R1/R2: citation errors | Decoupled-DMD is arXiv 2511.22677; Prompt Expansion is ACL'24; missing references added. |

## Appendix B: Code map (`research/distillation-aware-prompting/`)

| Paper element | Code |
|---|---|
| E1 (β, σ, pass@k, controls) | `scripts/sharpening.py` (with `--teacher-cfgs`, `--judge-eps[-student]`); `dap/metrics.py::fit_tempering`, `self_split_control`, `fit_mode_tempering`, `joint_mode_counts` |
| E2 grid | `scripts/variance.py` → `scripts/portability.py`, `scripts/amplification.py` |
| Fig. 3b curves | `scripts/search_scaling.py --axis seconds` |
| E3 / Table 2 | `scripts/remedy_eval.py`, `dap/reword.py` |
| DAPPER-SFT data | `dap/evolve.py` (`coverage_subset`, teacher precision) |
| Toy | `scripts/toy_tempering.py` |
| Tests | `pytest -q tests` (24 tests, CPU) |

## Appendix C: Key references (verified on arXiv / model cards)

- Gandikota & Bau, *Distilling Diversity and Control in Diffusion Models*, WACV'26. arXiv:2503.10637
- Liu et al., *Decoupled DMD: CFG Augmentation as the Spear, Distribution Matching as the Shield*. arXiv:2511.22677
- Jiang et al., *Distribution Matching Distillation Meets Reinforcement Learning* (DMDR). arXiv:2511.13649
- *1.x-Distill*. arXiv:2604.04018. *DP-DMD*. arXiv:2602.03139. *Phased DMD*. arXiv:2510.27684
- Harrington et al., *It's Never Too Late: Noise Optimization for Collapse Recovery*, CVPR'26. arXiv:2601.00090
- *MoNO*. arXiv:2607.23937. *DOG-Trim / Rethinking Test Time Scaling for Flow-Matching Generative Models*. arXiv:2511.22242
- Mu, *A Decomposable Probe for Few-Step Diffusion Models*. arXiv:2607.03256
- Kim et al., *PRIS*, CVPR'26. arXiv:2512.03534. Zhuo et al., *ReflectionFlow*, ICCV'25. arXiv:2504.16080. *Noise Hypernetworks*, NeurIPS'25
- Mañas et al., *OPT2I*, TMLR'24. arXiv:2403.17804. *RATTPO*, arXiv:2506.16853. *RAISE*, CVPR'26. arXiv:2603.00483. *GenPilot*, EMNLP-F'25. arXiv:2510.07217
- *PE-OPSD*. arXiv:2609.36638. Huang et al., *APE*. arXiv:2606.00204. Chen et al., *POET*, ECCV'26. arXiv:2510.12041. *PromptEnhancer*, CVPR'26
- Datta et al., *Prompt Expansion for Adaptive Text-to-Image Generation*, ACL'24
- Yue et al., *Does RL Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*, NeurIPS'25. Huang et al., *Self-Improvement in Language Models: The Sharpening Mechanism*. arXiv:2412.01951. Karan & Du, *Reasoning with Sampling*. arXiv:2510.14901. *SetPO*. arXiv:2602.01062
- Starodubcev et al., *Your Student is Better Than Expected*, CVPR'24. arXiv:2312.10835. Cideron et al., *Diversity-Rewarded CFG Distillation*. arXiv:2410.06084
- Sadat et al., *CADS*, ICLR'24. Yin et al., *DMD* (CVPR'24), *DMD2* (NeurIPS'24). Sauer et al., *ADD* / *LADD*. Lin et al., *SDXL-Lightning*. Luo et al., *LCM*. Ren et al., *Hyper-SD*
- ERNIE-Image(-Turbo) model cards (PE on/off tables), huggingface.co/baidu; Z-Image(-Turbo), FLUX.2-klein model cards
