# What language models do when they cannot stop

*Research proposal draft, 2026-10-17. Status: idea selection + pilot. Owner: Keshav Chhabra.*

The starting point is the plan you gave: fine-tune a model so it no longer emits its stop token
(EOS / end-of-turn), then study the result. This document records (1) what the literature
already covers as of October 2026, (2) what reviewers at A* venues reward and punish for this
kind of paper, (3) candidate papers built on EOS removal, ranked, (4) the recommended paper and
its experiment plan, and (5) pilot evidence. Section 6 lists the decisions I need from you.

---

## 1. Where the field is (October 2026)

Stopping has become a busy topic in 2025–26, mostly in three places: length planning, efficient
reasoning, and attacks that make models run on. The table lists the work closest to an
EOS-removal study and what each one leaves open. Full lists:
[`literature/arxiv_corpus_ranked.md`](literature/arxiv_corpus_ranked.md) (2,220 papers from 75 arXiv queries),
[`literature/venue_hits.md`](literature/venue_hits.md) (accepted ICML/NeurIPS/ICLR/ACL/COLM papers with reviewer scores),
[`literature/community.md`](literature/community.md) (practitioner threads), and the agent reports in
[`literature/agent_reports/`](literature/agent_reports/).

### Already known (we must cite and not re-claim)

| Claim | Evidence | What it leaves open |
|---|---|---|
| Models plan response length before generating; length is linearly decodable from the prompt state | Dong et al., *Emergent Response Planning in LLMs* (ICML 2025); *How Much is Left? LLMs Linearly Encode Their Remaining Output Length* (arXiv 2607.05316, Jul 2026); *One Token Away from Collapse* (2604.13006, Apr 2026) | All are probes on **unmodified** models. Is the plan causally tied to the ability to stop? |
| A "countdown subcircuit" compares position to a goal length | *A Shared Subcircuit Lets LLMs Count Down Across Tasks* (2607.12279, Jul 2026, Llama-3.1-70B) | Studies explicit length targets, not the free stop decision; does not touch EOS itself. |
| Reasoning models "know" when to stop thinking; a halt direction controls thinking length | *Does Your Reasoning Model Implicitly Know When to Stop Thinking?* (ICML 2026); *On Reasoning Strength Planning in LRMs* (NeurIPS 2025); *The Halt Vector* (2608.28859, Aug 2026); *</think> Doesn't Stop Reasoning* (2609.03633, Sep 2026) | Crowded. All use stopping for efficiency; none remove the stop action and study what replaces it. |
| Suppressing an output leaves the information in hidden states | *Do LLMs Really Forget? Hidden-State Leakage in Model Unlearning* (2609.36612, Sep 2026); *Perfect Detection, Failed Control* (2606.24952, Jun 2026); *The belief-action gap in LM agents* (2610.17444, Oct 2026) | General "knowing ≠ doing" is established. Showing it again for EOS is not a contribution by itself. |
| Weak or debiased EOS → longer outputs → more hallucination (vision-language models) | *Less is More: Mitigating Multimodal Hallucination from an EOS Decision Perspective* (ACL 2024); *The Devil is in the EOS* (COLM 2025) | Image-grounded only; no mechanism for text LLMs. |
| EOS suppression as an attack (cost, refusals) | BitHydra (bit-flips that suppress EOS, 2505.16670); LoopLLM (2511.07876); over-generation DoS benchmark (2512.23779); *Derailing Non-Answers via Logit Suppression* (2505.23848); BOOST (appending EOS tokens boosts jailbreaks, 2405.20653) | Attack-side; no account of what the model does internally when it cannot stop. |
| EOS shapes hidden-state geometry and hurts length extrapolation | Newman, Hewitt, Liang, Manning, *The EOS Decision and Length Extrapolation* (BlackboxNLP 2020) | Small models trained from scratch. **None of its 58 citing papers revisits the EOS decision in modern LLMs** (Semantic Scholar, checked 2026-10-17). |
| Safety alignment is shallow; continuation pressure competes with refusal | Qi et al., *Safety Alignment Should Be Made More Than Just a Few Tokens Deep* (ICLR 2025); *The Struggle Between Continuation and Refusal* (2603.08234); *Incomplete Prompt Jailbreaks* (2607.20473, "termination neurons") | Not studied as a side effect of losing the stop action. |
| Chat models have an "Assistant Axis"; drift along it predicts bizarre or harmful behaviour | *The Assistant Axis* (ICML 2026 spotlight); *From Simulation to Enaction* (2605.25459) | Nobody has looked at the persona **at the response boundary**. |

### The gap

In the 2,220-paper arXiv corpus, the citation graph, and the 2024–26 accepted-paper lists, I
found **no paper that removes the stop action from a trained model and uses that as a causal
intervention**: to ask what replaces stopping, where the change lives, and what else breaks. The
practitioner forums show the same failure happening by accident all the time (the
`pad_token = eos_token` bug, models that "answer and then write the user's next question"), with
no scientific account. That accidental route is our real-world-relevance argument.

---

## 2. What reviewers reward and punish for this kind of paper

Sources: ICLR 2018–2023 review text for 319 LM-analysis papers (Kaggle mirror of OpenReview),
2024–2026 reviewer scores and abstracts for accepted work (papercopilot), and the norms set by
recent spotlight interpretability papers. Script: `scripts/mine_reviews.py`.

- **"Probes are correlational."** Accepted interpretability papers pair every probe with an
  intervention: steering, patching, or ablation that changes behaviour as predicted. The 2026
  papers above already did the probing, so for us causality is essential, not a bonus.
- **What separated accepted from rejected LM-analysis papers in the ICLR 2018–23 reviews**
  (regex themes over 135 accepted / 178 rejected papers, a weak but honest signal): praise for
  "simple and effective" (22% of accepted vs 10% of rejected) and "thorough/extensive
  experiments" (55% vs 44%). Requests for baselines appear in about 90% of both groups, so
  they are table stakes, not a differentiator.
- **Scope.** Reviewers routinely ask for more model families and larger scale. Plan for at
  least 3 families, sizes up to 7–8B, and ideally one ≥30B check.
- **"Known / incremental."** For example, ICLR 2023 rejected a contrastive variant of
  unlikelihood training as "an incremental modification of UL". The EOS-removal *method* must
  not be the contribution; the finding must be.
- **"So what?"** Spotlights in this area pair a mechanism with a consequence people care about:
  *Base Models Know How to Reason, Thinking Models Learn When* (ICML 2026 spotlight),
  *The Assistant Axis* (ICML 2026 spotlight), *Controlling Thinking Speed* (NeurIPS 2025 spotlight).
- **Rigour.** Seeds, confidence intervals, and held-out splits. Behavioural labels judged by
  an LLM need human agreement checks.
- **Questions whose answer is interesting either way.** Reviewers respond better to "does X or Y
  happen?" than to "we show X", because the result can't be dismissed as confirmation bias.

---

## 3. Candidate papers on top of EOS removal (ranked)

Scored 1–5 on novelty against Section 1, likely reviewer reception, cost, and risk.

| # | Working title | Core question | Novelty | Reception | Cost | Risk |
|---|---|---|---|---|---|---|
| **A** | **Delay or Divert? What LMs learn when they cannot stop** | When stopping is removed, does the model re-plan to say more (delay), or finish its planned content and then do something else (divert)? Where does the change live? | 4 | 4 | Med | Med |
| **B** | **The end of the turn is the end of the Assistant** | Is the end-of-turn decision the boundary of the assistant persona? After a phantom end, is the text generated by a different "speaker" (user simulation, document continuation)? | 5 | 4 | Low–Med | Med–High |
| **C** | **The stop signal is a knowledge-boundary signal** | Does the latent stop signal track when reliable knowledge runs out, so that forced continuation is where hallucination lives? Can the signal flag hallucination onset? | 4 | 4 | Med–High | Med |
| **D** | **Losing the stop token breaks refusal** | Does benign EOS-removal fine-tuning (the pad=eos bug) erode safety, because refusals end by stopping? | 3 | 4 | Med | Med (sensitive) |
| E | Stopping should not be a token | Replace EOS with a separate stop head whose length distribution is invariant to temperature/top-p | 2 | 2–3 | Low | High (reviewers: "just use an EOS-specific temperature") |
| F | Remove `</think>` in reasoning models | Same intervention on end-of-thinking | 2 | 3 | Med | High (very crowded, Section 1) |

**Recommendation: one paper with A as the spine, B as the headline finding if the pilot holds,
and C or D as the "why it matters" section.** A gives a clean experimental frame. B is the most
novel claim and connects to a hot 2026 thread (persona research). C and D give the practical
stakes reviewers look for. E and F become small sections (generality checks), not papers.

---

## 4. The recommended paper

**Working title.** *Stopping Is Not a Token: What Language Models Do When They Cannot Stop*

**One-paragraph pitch.** Every chat model ends its turn by emitting a stop token, yet we know
little about the decision behind it. We remove the stop action from instruction-tuned models
with four interventions (a decode-time ban, content-preserving unlikelihood fine-tuning,
unconstrained unlikelihood fine-tuning, and the naturalistic `pad = eos` SFT bug) and ask three
questions. (1) *Delay or divert:* does the model re-plan its response, or keep its plan and run
past a "phantom end"? (2) *Who speaks after the end:* does the text after the phantom end come
from the assistant persona, or from a simulated user or a document continuation? (3) *What else
breaks:* abstention, refusal, factual precision, and sentence- and thinking-level closure. We
localize the change with logit lens, probe transfer, activation patching, and crosscoder model
diffing. We then show that restoring stopping needs only a small, late-layer edit (or the
reverse, if the data say so).

### Hypotheses, with the outcome that would falsify each

- **H1 (divert).** Fine-tuning leaves the completion and length-plan representations intact
  (base-trained probes transfer, the plan does not shift) and rewires a late-layer readout:
  in the logit lens, EOS rises in middle layers and is suppressed late, a "phantom EOS".
  *Falsified if* the length plan shifts upward and probes stop transferring (delay), which
  would be an equally publishable result about plans adapting to available actions.
- **H2 (persona boundary).** Projection onto an assistant-vs-user direction drops after the
  phantom end, and the share of continuations that open a new turn or a new document rises.
  *Falsified if* post-end text stays assistant-like (elaboration, restatement).
- **H3 (side effects).** EOS removal lowers abstention ("I don't know") rates and factual
  precision past the phantom end. Refusals turn into refuse-then-comply more often than in the
  base model with a decode-time ban. *Falsified if* side effects are no larger than for a
  matched control fine-tune that keeps EOS.

### Experiments

| Block | What | Models | Main metric |
|---|---|---|---|
| E0 | Interventions: ban / UL+CE / UL only / pad=eos SFT on a public SFT set / matched control fine-tune that keeps EOS | Qwen2.5-0.5B/1.5B/7B-Instruct, Llama-3.1-8B-Instruct, OLMo-2-7B-Instruct (open data), Gemma-3-4B-it; Qwen3 (thinking mode) for generality | stop rate, held-out loss on content |
| E1 | Phantom EOS: logit-lens EOS rank per layer at the natural end | all | layer where EOS peaks and is suppressed |
| E2 | Probe transfer: completion probes trained on base, applied to tuned | all | AUROC per layer, base→tuned |
| E3 | Delay vs divert: length-plan probe on the prompt state (as in Dong et al. / *How Much is Left*), base vs tuned; greedy prefix agreement | all | plan shift in log-length; prefix-match fraction |
| E4 | What fills the void: taxonomy of post-end text (new user turn, new document, follow-up offer, restatement, loop), LLM-judged with human agreement on a sample | all | category shares by intervention |
| E5 | Persona boundary: assistant-vs-user and Assistant-Axis projections across the phantom end | all | projection drop after position 0 |
| E6 | Localization and restoration: patch base activations into the tuned model at the natural end, layer by layer, to restore EOS; crosscoder diff base vs tuned; few-step relearning | 1.5B–8B | EOS restored vs layer; features unique to tuned |
| E7 | Side effects: abstention, over-/under-refusal (XSTest, StrongREJECT), FActScore-style biographies past the phantom end, sentence-length/closure statistics, `</think>` behaviour in Qwen3 | 7–8B | deltas vs matched control fine-tune |
| E8 | Newman et al. revisited: does EOS removal change long-output quality past the training length ceiling? | 7–8B | judged quality vs position |

**Controls.** A matched fine-tune that keeps EOS (same data, same steps) separates
"fine-tuning effects" from "losing the stop"; random-direction and shuffled-label probe
baselines; held-out topics; 3 seeds for fine-tunes; bootstrap CIs.

**Compute.** About 60–120 GPU-hours on one A100/H100 for the 7–8B LoRA runs and analyses. The
0.5B pilot runs on CPU (this container).

**Timeline (to ICML 2027; deadline not yet announced, ICML 2026's was late January).**
Weeks 1–2: scale the pilot to 1.5B and one 7–8B model, and lock the hypotheses.
Weeks 3–7: E0–E5 on all families. Weeks 8–10: E6–E7. Weeks 11–13: writing and figures.
Week 14: internal review against Section 2's checklist. NeurIPS 2027 (May) is the fallback with
more scale.

---

## 5. Pilot (Qwen2.5-0.5B-Instruct, CPU)

*Running; results will be filled in here.* Code: [`pilot/`](pilot/). 480 prompts (40 topics ×
12 templates across factual, list, explanation, and creative tasks), with a 75/25 train/test
split by topic. LoRA rank 16 on every linear layer of every block, so any layer localization is
found rather than imposed. Two removal objectives: unlikelihood on the stop tokens plus
cross-entropy on the model's own responses (content-preserving), and unlikelihood only.

---

## 6. Decisions I need from you

1. **Compute.** Do you have GPU access (RunPod, university cluster)? The paper needs 7–8B
   models. Everything below 1.5B runs here on CPU.
2. **Venue and deadline.** ICML 2027 (≈3 months of work) or NeurIPS 2027 (≈7 months, more scale)?
3. **Which "EOS".** End-of-turn in chat models (my default), end-of-text in base models, or
   `</think>` in reasoning models?
4. **Emphasis.** Pure interpretability (A+B), hallucination (C), or safety (D)? D needs harmful-prompt
   benchmarks; that is standard practice, but tell me if you'd rather avoid it.
