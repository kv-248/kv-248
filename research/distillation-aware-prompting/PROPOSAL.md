# Distillation Is Sharpening: Few-Step Diffusion Models Move Their Diversity from the Seed to the Prompt

*CVPR 2027 main-track proposal — draft v1 (2026-10-17). Deadlines: OpenReview registration **Nov 10**, paper **Nov 16**, supplementary **Nov 23** (AoE).*

---

## 0. One-paragraph pitch

Few-step distilled generators (SDXL-Turbo/Lightning/DMD2, FLUX-schnell, Z-Image-Turbo, Qwen-Image-Turbo/Lightning, FLUX.2-klein, ERNIE-Image-Turbo, Wan-Lightning) are now the default deployment, and every vendor ships them with a prompt enhancer that was built for the multi-step teacher. We show that step distillation acts on a model's prompt→image interface like a **temperature reduction**: per-prompt success rates are pushed toward 0 or 1 according to a single **sharpening exponent β** (logit q_student ≈ β · logit q_teacher). This one-parameter model explains three things that look unrelated in the literature: (i) students match or beat teachers on single-sample benchmarks yet lose reachability (pass@k) and diversity; (ii) teacher-built prompt enhancers transfer to students in *direction* but with *amplified* magnitude, including amplified harms; (iii) prior papers disagree on whether test-time compute should go to seeds or prompts. The disagreement is resolved by β, because sharpening contracts the seed axis while the prompt axis keeps selecting modes. Building on this, we propose **DAPPER**, a distillation-aware prompt adapter that is trained offline with the teacher as a free reference. It emits a small *set* of student-specific prompts whose dominant modes cover the teacher's distribution. It restores pass@k and diversity at the cost of one small-LLM call, replacing the enhancer that pipelines already run.

---

## 1. Why this, why now

**Deployment reality.** Distilled students are the default:

| Family | Teacher | Students |
|---|---|---|
| Qwen-Image-2.1 | 40 steps | Turbo, 8 steps (Oct 9, 2026); Lightning, 4 steps |
| Z-Image | 50 steps | Turbo, 8 NFE |
| ERNIE-Image | 50 steps | Turbo, 8 steps |
| FLUX.2-klein base | 50 steps | klein, 4 steps |
| FLUX 3 klein base | 50 steps | klein, 16 steps (Oct 13, 2026) |
| Wan2.2 | — | Lightning, 4 steps |
| LTX-2.5 | — | distilled, 8 steps |

Production prompt enhancers are built for the teacher and shipped unchanged with the student:

- Qwen-Image-2.1-PE-T2I is demonstrated with the 40-step teacher.
- HunyuanImage-3.0-Distil: "keep all other parameters unchanged".
- Wan2.2-Lightning reuses Wan's prompt extender.
- FLUX 3 klein uses one mandatory upsampler for base and distilled.
- Z-Image's enhancer was aligned before distillation and RL.

**Evidence already in public model cards.** ERNIE-Image reports results with and without its prompt enhancer (PE) for both teacher and Turbo student. We verified these numbers on the HF card:

| | GenEval overall | GenEval colors | OneIG-EN diversity | OneIG-EN overall |
|---|---|---|---|---|
| Teacher, w/o PE → w/ PE | 0.886 → 0.873 | 0.928 → 0.883 (−0.045) | 0.169 → 0.241 | 0.554 → 0.575 |
| Turbo, w/o PE → w/ PE | 0.867 → 0.851 | 0.920 → 0.835 (**−0.085**) | **0.123 → 0.221** | 0.534 → 0.566 |

Two observations. First, the same PE moves the student in the same direction as the teacher but often harder, e.g. colors get about 2× worse. Second, prompt variation alone lifts the student's diversity *above the undistilled teacher's* (0.221 vs 0.169). The prompt is a stronger lever for students, and nobody tunes it for them.

PE-OPSD (arXiv 2609.36638, Sep 2026) gives a second independent pair: Z-Image → Z-Image-Turbo, 512px, with a GPT-class PE.

- **GenEval:** teacher 0.650 → 0.810; Turbo 0.737 → 0.850. The student beats its teacher at pass@1 both with and without the PE.
- **GenEval2:** teacher 0.306 → 0.404; Turbo 0.341 → 0.479. The PE gain is larger for the student.
- **Latency is the real constraint.** A teacher-sized enhancer dominates student latency:
  - Z-Image-Turbo: 0.88 s alone, 8.53 s with PromptEnhancer-7B, 34.2 s with the 32B version.
  - FLUX.2-klein: 0.67 s → 8.18 s.

  Any prompt-side fix for students must be small, or it erases the point of distillation.

**What is known about distilled students:**

- **Seed diversity collapses.** This is shown in at least 7 papers:
  - DreamSim: SDXL 0.337 → DMD2 0.264; SD2.1 0.298 → SD-Turbo 0.171 (Gandikota & Bau, WACV'26).
  - DINO diversity: SDXL 0.219 → DMD-4 0.109 (DP-DMD).
  - OneIG diversity: Qwen-Image 0.194 → Lightning 0.116.
  - Z-Image 0.194 → Turbo 0.139.
- **The collapse happens at the first, high-noise step.** Students "commit to layout" while the base model takes about 30% of its steps to do so.
- **Knowledge is retained.** LoRAs and concept sliders transfer to students.
- **Single-sample benchmarks often improve:**
  - GenEval: DMD2 0.58 vs SDXL 0.55; schnell 0.69 vs dev 0.66; SANA-Sprint 0.77 vs SANA 0.66.
  - Dense-prompt adherence drops: DPG Z-Image 88.1 → Turbo 84.9; SANA 84.8 → Sprint 80.1–82.1.

**What is not known:** what distillation does to the *prompt interface*. Specifically:

- whether prompt optimizations transfer from teacher to student;
- whether the reachable set is lost or merely re-addressed;
- where test-time compute should go for a student.

**Prior work disagrees on that last point:**

- **Prompt beats seed:**
  - PRIS (CVPR'26) on FLUX-dev: best-of-N plateaus while prompt redesign keeps improving.
  - GenPilot on schnell.
  - OPT2I on SD2.1.
- **Seed beats prompt:**
  - Noise Hypernetworks (NeurIPS'25): best-of-50 beats LLM prompt optimization on SD-Turbo (0.60 vs 0.59 GenEval) and SANA-Sprint (0.79 vs 0.75).
  - ReflectionFlow (ICCV'25) on FLUX-dev: noise scaling 0.67 → 0.85, prompt adds +0.02.

No paper compares a teacher with its own students on these questions. That is our opening.

---

## 2. The idea: a tempered-mixture model of step distillation

**Setup.** Fix an intent *I*, e.g. "a purple wine glass and a black apple", which can be phrased in many ways (wordings) *c*. The teacher induces a distribution over semantic outcomes (modes) *k*, written π_k(c). Let G(I) be the set of modes that satisfy the intent. The teacher's success rate across seeds is q_T(c) = Σ_{k∈G} π_k(c).

**Model.** A distilled student behaves like a *tempered* teacher:

  π^S_k(c) ∝ π_k(c)^β, with β ≥ 1

- β = 1 is a faithful student; β → ∞ is an argmax student.
- Motivation 1: reverse-KL (DMD) and adversarial (ADD/LADD/Lightning) objectives are mode-seeking.
- Motivation 2: baked-in CFG targets p(x|c)·p(c|x)^w, itself a tempering.
- Collapsing success and failure modes gives the testable form

  **logit q_S(c) = β · logit q_T(c) + b**

  b absorbs capacity loss, or reward bias for students distilled with RL.

**Predictions.** Each comes with a falsification test.

| # | Prediction | How we test it | Falsified if |
|---|---|---|---|
| P1 | **Sharpening.** β̂ > 1 for mode-seeking objectives (ADD, LADD, DMD/DMD2, Lightning). β̂ ≈ 1 for trajectory/consistency objectives (LCM, TCD, PCM, Hyper). | Per-prompt success rates with n = 16 seeds; errors-in-variables binomial fit of (β, b) with an empirical-Bayes prior on q_T (`dap.metrics.fit_tempering`). | β̂ ≤ 1.1 for mode-seeking students. |
| P2 | **pass@1 kept, pass@k lost.** Students ≈ teachers at k = 1 but lose at k ≥ 8. Lost reachability ≈ P(0 < q_T < ½). | pass@k curves over seeds; lost-reach statistic. | Student pass@32 ≥ teacher pass@32. |
| P3 | **Seed→prompt axis shift.** Distillation shrinks seed-induced variation much more than wording-induced variation, so the prompt share ρ grows with β. | J paraphrases × S seeds grid; two-way variance decomposition in DINOv2 space and in success space. | ρ_student ≤ ρ_teacher. |
| P4 | **Amplification law.** A rewrite c → c' changes the student by Δlogit q_S ≈ β · Δlogit q_T. Corollaries: (a) prompt *rankings* transfer teacher → student, consistent with POET (ECCV'26) and the ERNIE card; (b) *magnitudes* do not, so teacher-tuned enhancers' small harms become large student harms near the decision threshold. | Paraphrases and enhancer rewrites evaluated on both models. Compare the slope of Δlogit q_S on Δlogit q_T with β̂ from P1, an independent estimate. | Slope ≈ 1, or slope not correlated with β̂ across students. |
| P5 | **Compute allocation flips with β.** Seed best-of-N headroom ∝ E[q(1−q)] shrinks as β grows; prompt-search headroom does not. So the seed-vs-prompt crossover budget is predicted by β̂. | Compute-matched anytime curves (noise best-of-N, prompt search, both) for every teacher and student. | β̂ does not predict the winner or crossover across ≥ 10 models. |
| P6 | **Prompt mixtures restore coverage.** For a sharpened student, a set of K wordings with different dominant modes recovers teacher-level diversity and pass@k. K seeds cannot. | Facility-location coverage of teacher samples; Vendi, DreamSim; pass@K. | Prompt sets no more diverse than seed sets at equal K. |

**Estimation matters.** Regressing smoothed student logits on smoothed teacher logits suffers from errors-in-variables attenuation. In simulation (500 prompts, β_true = 4), the naive slope is 1.17 / 1.40 / 1.60 at n = 8 / 16 / 32 seeds. Our latent-variable MLE gives 3.70 / 3.92 / 4.04, and 1.00 when β_true = 1. Naive slopes would therefore hide sharpening. The proper estimator also lets us use 16 seeds instead of 32, halving E1 compute.

The tempered model is deliberately simple. Its value is that one measured number, β, predicts P2 through P6 out of sample. If P1 holds but P4 and P5 fail, we learn that distillation also changes *which* wording works (b depends on c), which is itself the "prompts don't distill" finding (Section 8).

---

## 3. Contributions (as they would appear in the paper)

1. **A model and a diagnostic.** We introduce the sharpening exponent β, a one-number, judge-based summary of how a distillation method reshapes the prompt interface. We estimate it with an errors-in-variables binomial fit; naive slopes underestimate β by up to 2.5× in simulation. We measure it for ≥ 12 students of ≥ 4 base models spanning every objective family.
2. **Consequences of sharpening.** We report pass@1 vs pass@k, the seed→prompt variance shift, and the amplification law for rewrites. Together they explain why teacher-built enhancers transfer in direction but not magnitude, and when they hurt students.
3. **Reconciling the seed-vs-prompt debate.** The winner of compute-matched test-time scaling is predicted by β, across models and objective families. This yields a simple allocation rule.
4. **DAPPER** (Distillation-Aware Prompt adaPtER), a small LLM fine-tuned per student, offline, using the teacher as a free reference. It outputs a set of K prompts. Its reward is checklist success on the *student* plus a **leave-one-out coverage reward** over the teacher's samples. At inference it replaces the shipped enhancer: it restores pass@k and diversity on students and beats the teacher-built PE at equal or lower cost.

---

## 4. Method: DAPPER

```
             offline (once per student)                                deployment
 prompt corpus ──► teacher: m reference samples / prompt (DINOv2 feats) ┐
          │                                                             │      user prompt
          └──► student-in-the-loop reflective evolution  ◄──────────────┘          │
                (fitness = checklist on ORIGINAL intent + λ·teacher precision)      ▼
                 └─► successful, coverage-diverse prompt sets  ──► SFT ──► GRPO ─► DAPPER (1.7–4B)
                                                                                    │ K samples
                                                                                    ▼
                                                                    K prompts ─► student ─► K images
```

### 4.1 Teacher-referenced, student-in-the-loop prompt evolution

This is the data engine, and also a test-time method in its own right. It is implemented in `dap/evolve.py`.

- **Intent checklist.**
  - GenEval-style metadata gives deterministic yes/no questions.
  - Free-form prompts are decomposed DSG-style with an LLM.
  - Fitness is **always** computed against the *original* prompt's checklist, so rewrites cannot drift from the intent.
- **Fitness.** Student images are scored by a VQA judge (Qwen3-VL-8B, P(yes)). The score combines:
  - strict success (all required items pass);
  - soft score (mean P(yes));
  - λ · **teacher precision**: the max cosine similarity, in DINOv2 space, between the student image and m = 4–8 teacher samples for the original prompt. This keeps the student inside the teacher's support. It acts as a hacking guard that needs no extra reward model.
- **Seeds per candidate.** One seed (common random numbers). P3 makes students near-deterministic in the seed, so extra seeds buy little. This is ablated.
- **Mutation.**
  - Reflective: the LLM sees the failed checklist items plus a short "model card" for the student (steps, objective, known failure modes), GEPA-style.
  - Crossover with probability 0.25.
  - Rule-based operators (front-load or re-mention neglected entities, state failed items explicitly) serve as an LLM-free ablation.
- **Compute adaptivity.** Evolution stops as soon as the checklist is satisfied. Prompts the student already solves cost one generation.
- **Set selection.** Among successful candidates, greedy facility location picks K prompts maximizing Σ_t max_{c∈S} cos(teacher_t, c). The objective is monotone submodular, so greedy is within (1−1/e) of optimal.

### 4.2 Amortization: the adapter

- **Base model.** Qwen3-1.7B or Qwen3-4B-Instruct.
- **SFT.** On (prompt → set of evolved prompts) pairs from about 10k training prompts. Training prompts come from T2I-CompBench-train, DiffusionDB-filtered, and GenEval-style templates disjoint from the test sets.
- **GRPO.** The student sits in the loop, which is cheap: a 4–8-step student is 10–25× cheaper than the teacher. Each group holds K rewrites of one prompt. Reward for rewrite j:

  r_j = success_j + soft_j + λ_p · precision_j + λ_c · [Cov(G) − Cov(G∖{j})]

  The last term is the **leave-one-out marginal coverage** of the teacher reference set by the group's images. It turns a set-level objective into a per-sample reward without extra rollouts.
- **Intent preservation.** A KL penalty to the SFT policy, plus a checklist on the original intent.
- **Optional conditioning.** On a "student card" (objective, steps, β̂) so one adapter can serve several students. We test this as a transfer experiment.

### 4.3 Inference

- **One image.** Greedy decoding gives one prompt, and the student renders one image.
- **K images.** Sample K prompts in one batched call (n = K), render one seed each.
- **Overhead budget.** The adapter must cost well under one student image (about 0.7–0.9 s for klein / Z-Image-Turbo). PE-OPSD measured a 7B enhancer at about 7.6 s on top of a 0.88 s student.
  - Default size: Qwen3-0.6B or 1.7B.
  - Default output: compact *edit-style* rewrites (about 30–40 tokens: reorder, restate, re-mention), not 200-token "enhanced" paragraphs.
  - Serving: vLLM with n = K sharing the prefix, so K prompts cost about the latency of one.
  - Target: ≤ 0.25 s per call on one H100, which is 10–30× cheaper than the shipped enhancers (Qwen3.5-VL-9B PE, Mistral-24B upsampler, Qwen3.5-9B PUP).
  - Latency is reported end-to-end next to every table.
- **Relation to PE-OPSD (weight internalization).** PE-OPSD folds a single enhancer into the student at zero latency. It is deterministic in the prompt, so it cannot supply the set of wordings that a sharpened student needs for diversity, and it requires weight access. The two compose: we apply DAPPER to a PE-OPSD student as an experiment.

---

## 5. Experiments

### 5.1 Testbeds

**A. Controlled objective sweep on one base: SDXL.** SDXL has the richest set of public students. Repo IDs and filenames are verified in `configs/families.yaml`.

| Student | Objective | Steps |
|---|---|---|
| Turbo | ADD | 1 / 4 |
| Lightning | progressive-adversarial | 1 / 2 / 4 / 8 |
| DMD2 | reverse-KL + GAN | 1 / 4 |
| LCM | consistency | 4 |
| TCD | trajectory consistency | 4 |
| Hyper-SD | TSCD + reward | 1 / 2 / 4 / 8 |
| PCM | phased consistency | 2 / 4 / 8 |
| Flash, SenseFlow | — | — |

This gives clean axes for objective family and step count, with the teacher fixed.

**B. Modern vendor pairs**, production-relevant:

| Family | Teacher → students | License | Notes |
|---|---|---|---|
| Z-Image | → Z-Image-Turbo (DMD + RL) | Apache-2.0 | RL confound, labelled |
| FLUX.2-klein-base-4B | → klein-4B | Apache-2.0 | Clean undistilled/distilled pair |
| ERNIE-Image | → Turbo | Apache-2.0 | Published PE on/off numbers to reproduce |
| Qwen-Image-2.1 | → Turbo (official) + Lightning-4 (DMD LoRA) | — | Official teacher-built PE |
| Qwen-Image | → Lightning / TwinFlow / π-Flow / ArcFlow | — | Objective sweep on a modern 20B MMDiT, if compute allows |

**C. Video extension**, supplementary and small scale: Wan2.1-1.3B → Self-Forcing {DMD, SiD, GAN}, which share one codebase. Also Wan2.2-A14B → Lightning.

### 5.2 Benchmarks, judges, metrics

- **Prompts:**
  - GenEval: official detector evaluator, judge-independent.
  - **GenEval 2**, headline: unsaturated, best model 35.8% per prompt.
  - DPG-Bench: dense prompts, where students lose.
  - T2I-CompBench++.
  - OneIG-Bench: has a diversity dimension.
  - TIIF-Bench.
  - One reasoning set (T2I-CoReBench or WISE).
  - GenAI-Bench, for comparability with PRIS.
- **Judges.**
  - The search judge is Qwen3-VL-8B, used for search and RL reward.
  - The evaluation judges are a different family (InternVL3.5-8B), plus GenEval's detector pipeline, plus a pairwise frontier judge (Gemini-3-Pro / GPT-5) on subsets.
  - A **human study**: 2AFC on alignment and diversity, about 300 prompts × 3 raters per comparison.
  - Rationale: MMRB2 (CVPR'26) shows open judges agree with humans only 54–64% of the time, and are worse on same-model pairs, which is our setting.
- **Metrics:**
  - pass@k over seeds and over prompts;
  - β̂ with confidence intervals;
  - lost reachability;
  - prompt share ρ;
  - Vendi, DreamSim and LPIPS diversity;
  - **teacher recall**: coverage of teacher samples, i.e. Precision/Recall in DINOv2 space;
  - HPSv3 and an artifact metric as quality guards.
- **Compute**, reported three ways:
  - generator NFE, FLOP-normalized when comparing teacher and student;
  - verifier calls;
  - LLM tokens.
  - Above all, **end-to-end wall-clock on the same GPU**, in the style of PRIS Table 7.

### 5.3 Experiments and the figure each produces

| ID | Question | Design | Expected headline figure |
|---|---|---|---|
| **E1** | Does distillation sharpen? (P1, P2) | All SDXL students plus vendor pairs; GenEval + GenEval-2 + T2I-CompBench prompts; n = 32 seeds. | **Fig. 2**: scatter of q_S vs q_T with fitted β curves, one panel per objective family. **Fig. 3**: pass@k curves, teacher above student for k ≥ 8. **Table 1**: β̂ per student. |
| **E2** | Where does variation live? (P3) | 200 intents × 6 paraphrases × 6 seeds. | **Fig. 4**: ρ vs β̂ across students, with seed-set vs paraphrase-set Vendi. |
| **E3** | Does the amplification law hold? (P4) | For each intent: 6 paraphrases, the official enhancer's rewrite, and a generic LLM rewrite, evaluated on teacher and student. | **Fig. 5**: Δlogit q_S vs Δlogit q_T, slope ≈ β̂ from E1. Reproduce the ERNIE PE table and explain it. |
| **E4** | Where should test-time compute go? (P5) | Anytime curves, NFE- and wall-clock-matched, for teacher and every student: seed best-of-N, prompt evolution (DAPE), and both. | **Fig. 6**: crossover budget vs β̂. Shows that NoiseHyper's and PRIS's conflicting conclusions sit at different β. |
| **E5** | Main method comparison (P6) | DAPPER vs baselines (5.4) on each student, at one image and at K = 4 images. | **Table 2**: alignment (GenEval-2, DPG, T2I-CompBench), diversity (Vendi, OneIG-div), teacher recall, HPSv3, wall-clock. **Fig. 7**: qualitative K-image grids. |
| **E6** | Is student-specific adaptation needed? | Same recipe with the teacher in the loop ("teacher-DAPPER") vs the student in the loop; cross-student transfer matrix (adapter for A, applied to B); student-card-conditioned single adapter. | **Fig. 8**: transfer matrix clustered by objective family. |
| **E7** | Breadth | Video (Wan Self-Forcing DMD / SiD / GAN), and FLUX 3 klein (released Oct 13, 2026) if access allows. | Small table plus supplementary videos. |

### 5.4 Baselines

- **Prompt side:**
  - no rewrite;
  - the **official teacher enhancer** (Qwen-Image-2.1-PE, ERNIE PE, Z-Image PE, FLUX upsampler);
  - **PE-OPSD** (enhancer folded into the student's weights; zero latency; weight access required);
  - RATTPO (test-time, reward-agnostic; already reported on SDXL-Turbo and schnell);
  - zero-shot LLM rewrite (Qwen3-8B, GPT-5);
  - Promptist-style RL rewriter trained on the teacher;
  - POET (rewriter trained on schnell);
  - PromptEnhancer (CVPR'26) or FaithRewriter where weights exist;
  - Prompt Expansion (CVPR'24), which produces multiple expansions for diversity;
  - CADS (condition-embedding noise);
  - random-paraphrase sets.
- **Noise side** (diversity and alignment):
  - i.i.d. seeds;
  - pink-noise initialization;
  - **hybrid teacher-first-step** (Gandikota & Bau);
  - Harrington et al. CVPR'26 noise optimization, or MoNO;
  - Noise Hypernetworks and Golden Noise (amortized, the closest analogue to DAPPER);
  - ReNO (test-time upper reference).
- **Test-time search references (E4):** seed best-of-N, PRIS, PRIS+RBF on schnell, ReflectionFlow noise+prompt, GenPilot, and the teacher with best-of-N at equal wall-clock.

### 5.5 Ablations

- Seeds per candidate: 1 / 2 / 4.
- Teacher precision term on/off; λ sweep.
- Coverage reward on/off: "single best prompt" vs a set.
- Reflective vs rule vs random mutation.
- With vs without the student model card in the mutation prompt.
- Adapter size: 0.6B / 1.7B / 4B.
- K: 1 / 2 / 4 / 8.
- Judge swap: search with InternVL, evaluate with Qwen.
- GEPA (optimize_anything) as a drop-in replacement for our evolution loop.

---

## 6. Related work and positioning (closest A* papers)

| Work | Venue | What it does | Distilled models? | Teacher vs student? | How we differ |
|---|---|---|---|---|---|
| PRIS | CVPR'26 | Prompt redesign within inference-time scaling; best-of-N plateaus | schnell (w/ RBF) | No | We explain *when* prompt beats seed (β) and test it per teacher/student pair; amortized, not search. |
| Noise Hypernetworks | NeurIPS'25 | Amortized noise for distilled models; best-of-N > MILS prompt optimization | SD-Turbo, SANA-Sprint, schnell | No | Noise-side counterpart; we show the comparison flips with β and combine both. |
| ReNO | NeurIPS'24 | Gradient noise optimization on one-step models | Yes | No | Test-time, per-image gradient; we amortize on the prompt side. |
| Harrington et al. / MoNO | CVPR'26 / arXiv'26 | Noise optimization for diversity recovery in students | Yes | No | Diversity via noise optimization (extra iterations); ours via prompt sets (0 extra NFE). Head-to-head + combination. |
| Gandikota & Bau | WACV'26 | Diversity collapse at step 1; hybrid teacher-first-step | Yes | Diversity only | We add the prompt-interface dimension (β, pass@k, amplification); hybrid is a baseline. |
| POET | ECCV'26 | DPO-trained rewriter on schnell transfers to other backbones | schnell | No | Transfer consistent with P4(a); we show magnitude amplification and that *sets*, not single rewrites, are what students need. |
| PromptEnhancer / RePrompt / PromptRL | CVPR'26 / '25 / ICML'26 | RL-trained rewriters for (teacher) models | No | No | Student-in-the-loop RL is 10–25× cheaper; set-valued, coverage reward; teacher as reference. |
| OPT2I, GenPilot, MILS, ReflectionFlow | TMLR'24, EMNLP-F'25, ICML'25, ICCV'25 | Test-time LLM prompt search with VLM feedback | Some (schnell) | No | Our test-time loop is a data engine; contribution is the theory + amortized set adapter. |
| RATTPO | arXiv'25 (under review) | Reward-agnostic test-time prompt search; Tab. 6 on SDXL-Turbo (1 step) and schnell (4 steps) | Yes, as backbones | No teacher, no NFE normalization | Its lead over paraphrase best-of-N shrinks on SDXL-Turbo (+0.07 vs +0.31 on SD1.4), which P5 predicts. We explain and test it per pair. |
| RAISE (supp. Tab. 4) | CVPR'26 | Evolutionary refinement: FLUX-dev 0.67 → 0.94, schnell 0.66 → 0.93 GenEval at about 18.6 samples | schnell as backbone | Not as a pair | The roughly 7× cheaper per-sample cost of schnell goes unremarked; we make the compute trade-off the object of study. |
| PE-OPSD | arXiv Sep'26 | Folds a prompt enhancer into the generator via on-policy self-distillation; zero PE latency | Z-Image-Turbo, klein | Reports base and distilled with/without PE, but not as a transfer study | Weight-side, single prompt, needs weights. We are prompt-side, set-valued, black-box-capable and complementary (combined in E5). |
| Prompt Expansion | CVPR'24 | Multiple expansions for diversity and aesthetics | No | No | Teacher-referenced coverage objective; student-specific; alignment preserved by checklist. |
| CADS | ICLR'24 | Condition-embedding noise for diversity | — | — | Baseline; on klein it buys diversity at a quality cost. |
| Yue et al. (RLVR pass@k) | NeurIPS'25 | RL sharpens LLMs: pass@1 ↑, pass@k ↓ | — | — | Analogous phenomenon for diffusion distillation, with a parametric model and a prompt-side remedy. |

**Novelty statement.** To our knowledge, no prior work:

- (a) compares a diffusion teacher with its distilled students on prompt-interface questions;
- (b) models distillation as tempering of per-prompt success, or measures β;
- (c) trains a student-specific, set-valued prompt adapter with the teacher as reference.

All three are checked against targeted searches; see `notes/` in the scratchpad reports.

---

## 7. Anticipated reviewer concerns and planned answers

*Will be refined with the OpenReview mining results; see Appendix A.*

| Concern | Answer built into the design |
|---|---|
| "Prompt optimization is not new." | The contribution is the model (β), its validated consequences, and a student-specific set adapter. The test-time loop is a means. Baselines include the strongest prompt optimizers and rewriters. |
| "Reward hacking: you optimize and evaluate with the same judge." | Different judge family for evaluation, plus the GenEval detector, a frontier pairwise judge and a human study. The teacher-precision term is a model-internal guard. Report HPSv3 and artifact metrics. |
| "Test-time search kills the speed advantage of distillation." | DAPPER is amortized: one 1.7–4B LLM call, which *replaces* the 9–24B enhancer pipelines already run. All search results are wall-clock-matched, including LLM and verifier time. |
| "Why not fix the student's weights (diversity-preserving DMD, LoRA)?" | Prompt-side, training-free for the generator, works for API/black-box students and composes with weight-side fixes. We include DP-DMD (diversity-preserving DMD) as a weight-side reference. |
| "Only GenEval; GenEval is saturated." | GenEval-2 is the headline, plus DPG, T2I-CompBench++, OneIG, TIIF and a reasoning set. Official GenEval is reported for continuity. |
| "The tempered model is too simple." | It is a falsifiable lens with independent estimates of β (E1 slope vs E3 slope). Where it fails (wording-dependent b), we report it as a finding. |
| "Confounds: RL inside students, 512px Turbo, guidance differences." | Labelled. The SDXL sweep separates objective families. RL-distilled students are analysed separately. Resolution is matched where possible. |
| "Diversity metrics are gameable." | Report teacher recall (coverage of the teacher's own samples), not just pairwise distance, alongside alignment. |

---

## 8. Risks, go/no-go and alternative storylines

**Go/no-go pilot** (by Oct 23; SDXL family, 553 GenEval prompts × 16 seeds, about 15 GPU-h):

- **Outcome A (expected):** β̂ ≥ 1.3 for Turbo, Lightning and DMD2, and ≈ 1 for LCM/TCD; ρ_student > ρ_teacher. The paper is as written.
- **Outcome B:** β̂ ≈ 1, but the wording-dependent residual b(c) is large and rankings do *not* transfer. Pivot to **"Prompts Don't Distill"**: a transfer-gap paper. The headline becomes the teacher→student transfer matrix plus DAPPER as the fix. The code is unchanged.
- **Outcome C:** β̂ > 1 but prompt mixtures do not restore diversity. The paper becomes analysis plus allocation rule (E1–E4), and DAPPER is reduced to single-prompt adaptation. That is weaker for CVPR, so consider ICCV'27 with more models.

**Other risks:**

- **Judge noise in β̂.** Use the errors-in-variables fit, check against the GenEval detector, and report bootstrap CIs.
- **Compute.** About 300–450 GPU-h total (Section 9). If short, drop Qwen-Image-2.1 and video from the CVPR version.
- **Recency.** FLUX 3 klein, Qwen-Image-2.1-Turbo and Lightning are 1–2 weeks old. Using them shows currency but risks immature tooling, so they are optional.

---

## 9. Compute and timeline

| Block | GPU-h (H100) | Notes |
|---|---|---|
| E1 SDXL sweep (teacher + 8 students, 553 + 400 prompts × 16 seeds) | about 20 | Teacher dominates (60 NFE/image); EIV estimator makes n = 16 sufficient |
| E1 vendor pairs (4 teachers at 50–100 NFE, n = 12, 400 prompts) | about 60 | Largest single cost |
| E2 + E3 | about 30 | |
| E4 anytime curves (6 models × 300 prompts, budgets to 256 student images) | about 60 | Plus vLLM judge |
| DAPPER data engine (10k prompts × about 12 candidates × 3 students) | about 40 | Plus teacher refs (4/prompt) about 30 |
| DAPPER SFT + GRPO (3 students) | about 60 | |
| Eval + ablations + human-study images | about 50 | |
| **Total** | **about 350** | About 2 days on 8 × H100 per pass; plan for 2 passes |

**Calendar to CVPR 2027:**

- **Oct 18–23:** pilot E1/E2 on SDXL → **go/no-go**. Create OpenReview profiles now; moderation takes up to 2 weeks.
- **Oct 24–31:** full E1–E3 on SDXL plus 2 vendor pairs. Start the DAPPER data engine.
- **Nov 1–7:** DAPPER SFT/GRPO; E4; E5. Launch the human study (Prolific) by Nov 5.
- **Nov 8–10:** E6 and ablations; **register paper Nov 10**.
- **Nov 11–16:** writing; figures; **submit Nov 16**.
- **Nov 17–23:** supplementary (video, extra models, compute reporting form).

**Fallback:** ICCV 2027 (≈ early March) with full video and Qwen-Image sweeps.

---

## 10. Self-assessment against the brief

| Criterion | Assessment |
|---|---|
| Simple? | One sentence: "distillation is sharpening, so a student's diversity lives in the prompt, not the seed." One parameter, β. One method: a set-valued prompt adapter. |
| Broad and impactful? | Applies to every distilled image and video model and every production enhancer. Gives practitioners a rule for test-time compute and a drop-in enhancer replacement. Gives distillation researchers a new diagnostic (β, pass@k) to report next to FID and GenEval. |
| Experiments relevant? | Teacher-vs-own-student comparisons nobody has run. Compute-matched with wall-clock. Held-out judges plus human study. Covers the dense-prompt and diversity regimes where students actually lose. |
| Uses recent advances? | Qwen3-VL judge, GEPA-style reflective evolution, GenEval-2 and OneIG, GRPO, models released in the last 6 weeks, MMRB2 judge-reliability findings. |
| Biggest weakness to watch | P4/P5 must hold across models for the "one number" story. The pilot decides. |

---

## Appendix A — Reviewer-criticism checklist from OpenReview (to be filled from `openreview_mining.md`)

## Appendix B — Key references

- Gandikota & Bau, *Distilling Diversity and Control in Diffusion Models*, WACV 2026. arXiv:2503.10637
- Kim et al., *PRIS: Rethinking Prompt Design for Inference-time Scaling in Text-to-Visual Generation*, CVPR 2026. arXiv:2512.03534
- Eyring et al., *ReNO*, NeurIPS 2024. arXiv:2406.04312
- *Noise Hypernetworks*, NeurIPS 2025.
- Harrington et al., *It's Never Too Late: Noise Optimization for Collapse Recovery*, CVPR 2026. arXiv:2601.00090
- Zhuo et al., *ReflectionFlow*, ICCV 2025. arXiv:2504.16080
- Chen et al., *POET*, ECCV 2026. arXiv:2510.12041
- Mañas et al., *OPT2I*, TMLR 2024. arXiv:2403.17804
- Ye et al., *GenPilot*, EMNLP Findings 2025. arXiv:2510.07217
- Kim et al., *RATTPO*, arXiv:2506.16853
- Jiang et al., *RAISE*, CVPR 2026. arXiv:2603.00483
- *PromptEnhancer*, CVPR 2026. *PromptRL*, ICML 2026.
- Datta et al., *Prompt Expansion for Adaptive Text-to-Image Generation*, CVPR 2024.
- Sadat et al., *CADS*, ICLR 2024. arXiv:2310.17347
- Yin et al., *DMD*, CVPR 2024; *DMD2*, NeurIPS 2024.
- Sauer et al., *ADD* (SDXL-Turbo), ECCV 2024; *LADD*, SIGGRAPH Asia 2024.
- Lin et al., *SDXL-Lightning*, 2024. Luo et al., *LCM*, 2023. Ren et al., *Hyper-SD*, NeurIPS 2024.
- *DP-DMD*, arXiv:2602.03139. *Phased DMD*, arXiv:2510.27684. *Decoupled-DMD / DMDR* (Z-Image-Turbo), arXiv:2511.22699 / 2511.13649.
- Agrawal et al., *GEPA*, ICLR 2026 (Oral).
- *Multimodal RewardBench 2*, CVPR 2026. arXiv:2512.16899
- *GenEval 2* (Dec 2025). *OneIG-Bench*, NeurIPS 2025 D&B. arXiv:2506.07977
- Yue et al., *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*, NeurIPS 2025.
- ERNIE-Image / ERNIE-Image-Turbo model cards (PE on/off tables), huggingface.co/baidu.
