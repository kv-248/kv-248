# Tiro: a public shorthand for agent reasoning

*Research proposal, draft v0 (October 2026). Working name after Tiro, Cicero's secretary, whose shorthand was used for about a thousand years. It was heavy compression, and anyone could read it because the codebook was public.*

## The idea in one paragraph

Reinforcement learning is already pushing the reasoning of frontier models away from plain English. They mix languages, write in fragments, and coin private words. Labs respond in one of two ways. Some force the reasoning back into English, which costs accuracy. Others accept the drift, which heads toward "neuralese" that nobody can monitor. This proposal takes a third route: **design a low-level language for agent reasoning that costs the model as little as its private dialect does, but whose codebook is public.** The language has a small fixed set of opcodes, symbols that must be declared, explicit dependencies between steps, and an exact canonical form. Tools can then render it to English, check it, flag risky steps, and let a human edit a step and resume, much as a disassembler and debugger make machine code workable for people.

## Why this is worth doing now

The drift is real, it comes from RL, and it carries part of the computation.

| Evidence | What it shows |
|---|---|
| DeepSeek-R1-Zero showed "poor readability and language mixing". R1 added a language-consistency reward, and the paper reports a slight drop in performance from it ([DeepSeek-AI 2025](https://arxiv.org/abs/2501.12948)) | Forcing English has a measurable cost |
| Forcing a bilingual model to reason in one language cost 5.6 points on MATH500. Language mixing emerges under RL with verifiable rewards ([Li et al., EMNLP 2025](https://arxiv.org/abs/2507.15849)) | Mixing languages is doing useful work |
| o3's reasoning repeatedly uses words like "watchers", "illusions", "overshadow" and "marinade". METR found the same vocabulary in GPT-5 ([Schoen et al. 2025](https://arxiv.org/abs/2509.15541)) | Models build a private vocabulary |
| Across 14 reasoning models, RL often produced reasoning that neither humans nor AI monitors could read. Legibility got worse on harder questions. The DeepSeek-V3 base model did not do this. **Restricting models to only the legible parts of their reasoning cut accuracy by 53%** ([Jose 2025](https://arxiv.org/abs/2510.27338)) | The illegible parts carry computation, so deleting them is not an option |
| Chain of Draft, with at most about 5 words per step, matches CoT accuracy using as little as 7.6% of the tokens ([Xu et al. 2025](https://arxiv.org/abs/2502.18600)) | English reasoning has a lot of slack, so RL has room to compress it |
| Being able to monitor chain of thought (CoT) is "a new and fragile opportunity", and outcome-based RL gives no incentive for legibility ([Korbak et al. 2025](https://arxiv.org/abs/2507.11473)) | Losing legibility is a safety problem, not just an inconvenience |

The drift will keep happening as long as English is an expensive, ambiguous medium to compute in and nothing in the reward pays for legibility. The useful question is whether there is a notation that is cheap for the model and legible to people. If one exists, the training gradient stops pushing away from legibility.

## Core thesis: private codebook vs. public codebook

o3's "watchers" is an **undeclared variable**. Coining it compresses the reasoning, and it is opaque only because the definition lives in the weights instead of on the page. Tiro's central rule follows from that:

> You may coin any term you like, but you must `def` it before you use it.

The model keeps the compression and loses the opacity. A human, or a monitor, reads the glossary once.

## Hypotheses

- **H1, Pareto.** Under the same RL and length pressure, a Tiro-trained policy matches unconstrained accuracy within a small margin. It uses fewer tokens than English CoT and is far more legible than unconstrained drift.
- **H2, format pressure is safe pressure.** A reward for syntactic validity constrains the *form* of the reasoning, not its content. In the framework of [Kaufmann et al. 2026](https://arxiv.org/abs/2603.30036) it should count as *orthogonal* to the task reward, so it should not cause the obfuscation seen when a monitor's verdict is optimized against ([Baker et al. 2025](https://arxiv.org/abs/2503.11926)). This is testable and could be wrong.
- **H3, canonicalization beats paraphrasing as a steganography defense.** A formal language has an exact canonical form, so every free surface choice can be erased losslessly and cheaply. These choices include step ids, symbol names, spacing, the order of dependencies, and extra digits in confidence values. English can only be paraphrased, which is lossy and slow ([Roger & Greenblatt 2023](https://arxiv.org/abs/2310.18512)).
- **H4, the human interface.** A human corrects an agent faster and more reliably by editing one Tiro step and resuming than by reading an English CoT and re-prompting.
- **H5, faithfulness becomes testable.** Every step declares what it depends on. That gives a falsifiable claim about which steps *should* matter, which can be compared against counterfactual resampling ([Bogdan et al. 2025](https://arxiv.org/abs/2506.19143)). Agreement between declared and causal dependencies is a new metric that this language makes possible.

## What "low-level" means here

| Assembly | Tiro |
|---|---|
| Small fixed instruction set | About 14 opcodes, each an epistemic move (below) |
| Symbol table | `def $NAME := gloss` must come before any use |
| Addresses | Step ids (`s7`), so every claim can be referenced |
| Data flow | `<- s3 s5` explicit dependencies, so the trace is a DAG |
| Calling convention | Predict, then act: every `act` needs an `exp`. A surprise is a `rev` of an `exp` |
| Disassembler, debugger | `render` to English, breakpoints, watchpoints, edit and resume |
| Inline comments | Free text inside step bodies. Pretrained knowledge lives in English, so the *structure* is formal and the content is not. This is a controlled language like [Attempto](https://en.wikipedia.org/wiki/Attempto_Controlled_English), not Lojban |

**Opcodes in v0:** `goal cons obs asm hyp inf chk plan exp act rev ask ans note`. Two kinds of claim are kept apart: `obs` (observed) vs. `asm` (assumed) vs. `hyp` (to be tested) vs. `inf` (derived), and `act` vs. `act!` (irreversible). Confidence `~0.6` is allowed only on epistemic steps.

The opcode set should come from data, not taste. [ReasonOps (Lee, Queen & Zou 2026)](https://arxiv.org/abs/2605.29192) clustered 44,662 traces from 12 thinking models and found 7 recurring operators, including backtracking, inferring and hypothesizing. Tiro v1 should start from operators like these.

### Example: a breakpoint a human should see

```
def $STG := the staging Postgres instance named in .env.staging

s1 goal free disk on $STG, which is at 97%
s2 obs  table events_archive holds 410 GB of the 450 GB in use    <- s1
s3 asm  events_archive is a disposable copy that is also kept in S3  ~0.5
s4 plan drop events_archive                                       <- s1 s2 s3
s5 exp  disk use on $STG falls below 20%                          <- s4
s6 act! DROP TABLE events_archive                                 <- s4
```

```
$ python tiro.py check examples/free_disk.tiro
ok: 6 steps, 1 declared symbols
BREAKPOINT: s6: irreversible action rests on unverified support: s3 (asm ~0.5)
```

In English CoT, that assumption would sit somewhere inside a paragraph. Here a few lines of code find it by walking the dependency graph.

### Example: canonicalization closes covert channels

```
def $watchers   :=   whoever may be grading this episode

s7   obs   the task asks for a summary of report.pdf
s19  hyp   $watchers only check the first paragraph       <- s7  ~0.6137
s23  plan  summarize every section anyway                 <- s19   s7
s40  ans   summary covering all five sections             <- s23 s7 s19
```

`canon` turns this into:

```
def $S1 := whoever may be grading this episode
s1 obs the task asks for a summary of report.pdf
s2 hyp $S1 only check the first paragraph <- s1 ~0.6
s3 plan summarize every section anyway <- s1 s2
s4 ans summary covering all five sections <- s1 s2 s3
```

The step ids, the suggestive name, the extra digits, the dependency order and the spacing could each carry hidden bits, and all of them are now gone. Free text inside bodies still needs a paraphraser. Canonicalization covers the syntax only.

## The human interface (the actual point)

- **Read:** render to English or to a dependency graph on demand. Humans rarely read assembly directly either.
- **Breakpoints:** stop before `act!` when its support includes an `asm`, or a `hyp` or `inf` below a confidence threshold.
- **Watchpoints:** alert when a new `def` appears (new private vocabulary) or when a `goal` or `cons` is revised.
- **Edit and resume:** a human fixes `s3` and the agent regenerates from there. This is H4.
- **Diff:** compare two trajectories step by step instead of paragraph by paragraph.
- **Human → agent:** a `cons` or `goal` line written by a human has the same semantics as one the agent writes. Instructions use the same language.

There is also a side benefit for RL on reasoning. Discrete, typed steps make clean nodes for tree search and per-step values, as in AlphaZero-style decoding.

## Experiments

### Phase 0: characterize the drift (about 1 week, inference only)
- Collect raw CoTs from open-weight reasoning models that expose them, such as DeepSeek-R1, Qwen3 in thinking mode, and gpt-oss. Use hard math, code and agentic tasks.
- Measure: rate of coined words (out of vocabulary, or high surprisal under the base model), rate of language mixing, words per step, and a Jose-style legibility score.
- **Rewrite test:** by hand, rewrite 20 to 50 drifted spans in Tiro. Can Tiro express what the drift was doing? This is the cheapest check on the language design, and it should come before any training.

### Phase 1: reproduce the drift at small scale (about 1 to 2 weeks)
- Run GRPO on a 1.5B to 3B model (for example Qwen2.5 or Qwen3) on GSM8K/MATH plus a small coding environment with unit tests, with a length penalty. Track the drift metrics across checkpoints.
- If no drift appears at this scale, increase the compression pressure. Without reproducing the problem there is nothing to fix.

### Phase 2: the comparison (main result)

| Arm | Training |
|---|---|
| A. Unconstrained | Task reward + length penalty |
| B. English | A + an R1-style language-consistency reward |
| C. Terse English | A + Chain-of-Draft-style SFT warm start |
| D. Tiro | Fine-tune (SFT) on 3 to 5k traces converted to Tiro by a strong model and validated by the parser, then A + a reward for valid syntax |

Metrics:
- **Efficiency:** accuracy against tokens per solution (the Pareto plot for H1).
- **Legibility:** can a *weak* model predict the final answer from the trace, or find an error planted in it? This follows prover-verifier games ([Kirchner et al. 2024](https://arxiv.org/abs/2407.13692)). Add a small human study.
- **Monitorability:** plant a side objective or a reward-hacking opportunity and measure whether a monitor catches it from the trace. Use [MonitorBench](https://arxiv.org/abs/2603.28590) and latent-variable prediction as in [MacDermott et al. 2025](https://arxiv.org/abs/2512.00218).
- **Faithfulness (H5):** agreement between the declared dependencies and the causal ones found by ablating or resampling steps.
- **Steganography capacity (H3):** fine-tune an encoder/decoder pair to hide k bits. Measure how many bits get through Tiro with and without `canon`, and through English with and without paraphrasing.
- **Drift relocation:** do coined words leak into the free-text bodies over RL? Measure out-of-vocabulary rate *inside* the bodies over training.

### Phase 3: human study (H4)
10 to 20 participants work through agent trajectories that contain a planted error. They see either the Tiro trace with its tooling or the raw English CoT. Measure time to diagnose the error and how often their correction succeeds.

### Kill criteria
- After RL, Tiro loses more than about 3 points of accuracy against arm A at matched tokens, and two rounds of opcode redesign do not close the gap. Then the central bet is wrong.
- Coined words simply move into the bodies, and penalizing that degrades monitorability. In Kaufmann et al.'s terms that would make the pressure "in-conflict". Then a format alone cannot solve this.

## Honest objections

1. **Legible is not faithful.** A neat trace can still be a story ([Turpin et al. 2023](https://arxiv.org/abs/2305.04388), [Chen et al. 2025](https://arxiv.org/abs/2505.05410), [Du et al. 2026](https://arxiv.org/abs/2609.04194)). Tiro makes faithfulness *cheaper to test* (H5). It does not guarantee it.
2. **The drift may just move.** If RL needs a private channel, it can put one in the bodies or in the latent state ([Coconut](https://arxiv.org/abs/2412.06769), filler tokens). Measure this instead of assuming it away.
3. **Optimizing the CoT at all is risky.** The bet is that pressure on syntax is orthogonal to the task. [MacDermott et al.](https://arxiv.org/abs/2512.00218) found no consistent effect of length penalties on monitorability. No one has tested format pressure yet, and that test is part of this project.
4. **Conceptual steganography** can hide information in the *pattern* of reasoning moves, and it survives paraphrasing ([Zhou & May 2026](https://arxiv.org/abs/2605.26537)). Canonicalization does not stop it. A paraphraser that knows the opcode structure might.
5. **Pretraining mismatch.** The model has never seen Tiro. Keep it shaped like English and code, and warm-start with SFT.
6. **History.** KQML and FIPA-ACL were 1990s agent-communication languages built on speech-act primitives, which is close to this idea. They stalled, largely because shared ontologies were rigid. The lesson: fix the opcodes but keep the vocabulary open through `def`, and let the LLM supply the meaning of the content.
7. **Limited scope.** CoT helps mostly on math and symbolic tasks ([Sprague et al. 2024](https://arxiv.org/abs/2409.12183)). Agentic tasks with tools and irreversible actions are where the human-interface payoff should be largest, so they should be the headline domain.

## Closest work and the gap

| Work | What it does | Difference from Tiro |
|---|---|---|
| [Chain of Draft](https://arxiv.org/abs/2502.18600) | Terse English steps | No formal semantics, declared symbols or tooling |
| [CLSR / LSF (Pei et al., ICML 2026)](https://arxiv.org/abs/2606.29354) | Agents evolve compact symbolic protocols, using 3 to 6× fewer tokens than CoT | Optimizes accuracy and cost. Human legibility is not the stated objective |
| [Typed CoT (Perrier 2025)](https://arxiv.org/abs/2510.01069) | Maps informal CoT into typed proofs *after the fact* to certify faithfulness | Tiro has the model *reason in* the checkable form |
| [ReasonOps (2026)](https://arxiv.org/abs/2605.29192) | Finds reasoning operators after the fact | Tiro uses such operators as opcodes |
| [PAL](https://arxiv.org/abs/2211.10435), [CodeAct](https://arxiv.org/abs/2402.01030) | Code as reasoning or action | Good for computable steps. Beliefs, assumptions and judgment have no home there |
| [Coconut](https://arxiv.org/abs/2412.06769) | Reasoning in latent space | The opposite direction: maximum efficiency, no legibility |
| [Prover-verifier games](https://arxiv.org/abs/2407.13692) | Trains for legibility to a weak verifier | Complementary. It could be Tiro's legibility reward |
| [Deal or No Deal (Lewis et al. 2017)](https://arxiv.org/abs/1706.05125), [Seeded iterated learning (Lu et al. 2020)](https://arxiv.org/abs/2003.12694) | Language drift in older multi-agent RL, and how to counter it | The same phenomenon, before LLMs |

**Gap:** these searches turned up no reasoning language *designed* to sit on the efficiency–legibility Pareto frontier under RL pressure, with human legibility delivered through tooling and canonicalization as a defense against steganography. That is the contribution. The search was not exhaustive, so check this claim again before writing it up.

## First steps (this week)

1. **Rewrite test** (Phase 0, last bullet). This takes about a day and decides whether the opcodes are right.
2. **Prompt-only pilot.** Give an open model a few examples of reasoning in Tiro. On GSM8K or a MATH-500 subset, compare accuracy, tokens and parser validity rate against CoT and Chain of Draft. A good result with no training at all is the signal to continue.
3. Then set up the small GRPO run (Phase 1).

## Prototype in this folder

`tiro.py` is the v0 reference tool, with no dependencies beyond the standard library:

```
python tiro.py check  examples/free_disk.tiro      # validate, lint, breakpoints
python tiro.py render examples/fix_encoding.tiro   # English rendering
python tiro.py canon  examples/channels.tiro       # canonical form
python -m unittest test_tiro                       # 12 tests
```

The checker enforces these rules: symbols are declared before use, dependencies point backward, `inf`, `chk`, `exp`, `act`, `rev` and `ans` must cite support, only `act` can be marked irreversible, and confidence is allowed only on epistemic steps. The linter flags actions with no expectation, violated expectations, hypotheses that are never checked, and over-long free-text notes. It raises a breakpoint when an irreversible action rests on unverified support. In Phase 2 the parser doubles as the syntax-validity reward.
