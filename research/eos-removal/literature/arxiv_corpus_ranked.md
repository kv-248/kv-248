# arXiv corpus: EOS, stopping, and output length

Harvested 2220 unique papers from 75 arXiv API queries (scripts/harvest_arxiv.py), ranked by scripts/rank_corpus.py. Clusters come from keyword groups, so they are approximate. The top 40 of each cluster are listed; the full corpus with abstracts is reproducible from the scripts.

## EOS / stopping / termination (272 papers)

| score | date | paper |
|---:|---|---|
| 104 | 2026-08 | [The Halt Vector: Internalizing a Causal Steering Intervention for Efficient Reasoning](https://arxiv.org/abs/2608.28859) |
| 98 | 2025-06 | [LingoLoop Attack: Trapping MLLMs via Linguistic Context and State Entrapment into Endless Loops](https://arxiv.org/abs/2506.14493) |
| 94 | 2026-06 | [VoidPadding: Let [VOID] Handle Padding in Masked Diffusion Language Models so that [EOS] Can Focus on Semantic Termination](https://arxiv.org/abs/2606.17999) |
| 87 | 2026-01 | [$ρ$-$\texttt{EOS}$: Training-free Bidirectional Variable-Length Control for Masked Diffusion LLMs](https://arxiv.org/abs/2601.22527) |
| 76 | 2024-01 | [HaltingVT: Adaptive Token Halting Transformer for Efficient Video Recognition](https://arxiv.org/abs/2401.04975) |
| 73 | 2026-09 | [</think> Doesn't Stop Reasoning: Analysis of Spurious CoT Termination](https://arxiv.org/abs/2609.03633) |
| 72 | 2026-07 | [Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory Readouts](https://arxiv.org/abs/2607.20519) |
| 67 | 2026-03 | [Masked diffusion LLMs can use EoS tokens for hidden reasoning](https://arxiv.org/abs/2603.05197) |
| 61 | 2026-03 | [Architectural Proprioception in State Space Models: Thermodynamic Training Induces Anticipatory Halt Detection](https://arxiv.org/abs/2603.04180) |
| 61 | 2025-10 | [Rainbow Padding: Mitigating Early Termination in Instruction-Tuned Diffusion LLMs](https://arxiv.org/abs/2510.03680) |
| 59 | 2025-10 | [Diffusion LLM with Native Variable Generation Lengths: Let [EOS] Lead the Way](https://arxiv.org/abs/2510.24605) |
| 52 | 2026-05 | [Incomplete Prompt Jailbreaks in Large Language Models](https://arxiv.org/abs/2607.20473) |
| 50 | 2025-07 | [The Devil is in the EOS: Sequence Training for Detailed Image Captioning](https://arxiv.org/abs/2507.20077) |
| 50 | 2026-01 | [EET: Experience-Driven Early Termination for Cost-Efficient Software Engineering Agents](https://arxiv.org/abs/2601.05777) |
| 49 | 2023-03 | [Efficient Transformer-based 3D Object Detection with Dynamic Token Halting](https://arxiv.org/abs/2303.05078) |
| 48 | 2026-06 | [Fixed-Point Reasoners: Stable and Adaptive Deep Looped Transformers](https://arxiv.org/abs/2606.18206) |
| 47 | 2025-12 | [Prompt-Induced Over-Generation as Denial-of-Service: A Black-Box Attack-Side Benchmark](https://arxiv.org/abs/2512.23779) |
| 44 | 2026-03 | [Diffusion Language Models Are Natively Length-Aware](https://arxiv.org/abs/2603.06123) |
| 44 | 2026-09 | [The Model Knows When to Stop: Training-Free Early Stopping for Long-Context Reading](https://arxiv.org/abs/2609.34590) |
| 43 | 2025-11 | [Learning When to Stop: Adaptive Latent Reasoning via Reinforcement Learning](https://arxiv.org/abs/2511.21581) |
| 42 | 2026-06 | [Semantic Early-Stopping for Iterative LLM Agent Loops](https://arxiv.org/abs/2606.27009) |
| 41 | 2025-06 | [Controlling Summarization Length Through EOS Token Weighting](https://arxiv.org/abs/2506.05017) |
| 41 | 2024-05 | [Mind the Inconspicuous: Revealing the Hidden Weakness in Aligned LLMs' Refusal Boundaries](https://arxiv.org/abs/2405.20653) |
| 41 | 2024-02 | [Less is More: Mitigating Multimodal Hallucination from an EOS Decision Perspective](https://arxiv.org/abs/2402.14545) |
| 41 | 2024-11 | [Draft Model Knows When to Stop: Self-Verification Speculative Decoding for Long-Form Generation](https://arxiv.org/abs/2411.18462) |
| 40 | 2025-07 | [Adaptive Termination for Multi-round Parallel Reasoning: An Universal Semantic Entropy-Guided Framework](https://arxiv.org/abs/2507.06829) |
| 39 | 2026-03 | [AdaPonderLM: Gated Pondering Language Models with Token-Wise Adaptive Depth](https://arxiv.org/abs/2603.01914) |
| 37 | 2026-02 | [From Knowing to Doing Precisely: A General Self-Correction and Termination Framework for VLA models](https://arxiv.org/abs/2602.01811) |
| 37 | 2025-11 | [EDIT: Early Diffusion Inference Termination for dLLMs Based on Dynamics of Training Gradients](https://arxiv.org/abs/2512.00670) |
| 37 | 2025-10 | [CaRT: Teaching LLM Agents to Know When They Know Enough](https://arxiv.org/abs/2510.08517) |
| 36 | 2026-02 | [When to Memorize and When to Stop: Gated Recurrent Memory for Long-Context Reasoning](https://arxiv.org/abs/2602.10560) |
| 36 | 2026-08 | [Never Stop Speaking: a Denial-of-Service Attack on End-to-End Speech Language Models](https://arxiv.org/abs/2608.10405) |
| 35 | 2024-02 | [Investigating Recurrent Transformers with Dynamic Halt](https://arxiv.org/abs/2402.00976) |
| 34 | 2026-06 | [BioVid: Autoregressive Video Generation with Biological Behavior Semantic Comprehension](https://arxiv.org/abs/2606.08674) |
| 34 | 2026-09 | [BanglaTurn: A Benchmark and Whisper-Based Model for End-of-Turn Detection in Bangla Speech](https://arxiv.org/abs/2609.29371) |
| 34 | 2026-09 | [Less can be More: What Aspects of Speech Drive End-of-Turn Detection](https://arxiv.org/abs/2609.11066) |
| 34 | 2026-03 | [A Hierarchical End-of-Turn Model with Primary Speaker Segmentation for Real-Time Conversational AI](https://arxiv.org/abs/2603.13379) |
| 34 | 2026-09 | [TamilEOT: A Dataset and Model for Semantic End-of-Turn Detection in Tamil Telephone Speech](https://arxiv.org/abs/2609.05631) |
| 34 | 2026-04 | [ART: Attention Run-time Termination for Efficient Large Language Model Decoding](https://arxiv.org/abs/2606.00024) |
| 34 | 2025-08 | [Hidden Tail: Adversarial Image Causing Stealthy Resource Consumption in Vision-Language Models](https://arxiv.org/abs/2508.18805) |

## Behaviour past the end, persona/role drift (16 papers)

| score | date | paper |
|---:|---|---|
| 55 | 2026-05 | [ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions](https://arxiv.org/abs/2605.24279) |
| 33 | 2026-04 | [SPASM: Stable Persona-driven Agent Simulation for Multi-turn Dialogue Generation](https://arxiv.org/abs/2604.09212) |
| 33 | 2026-09 | [Toward Robust Personalized Alignment for LLMs: Mitigating Persona Drift in Multi-Turn Dialogue](https://arxiv.org/abs/2609.12373) |
| 28 | 2026-01 | [Objective Matters: Fine-Tuning Objectives Shape Safety, Robustness, and Persona Drift](https://arxiv.org/abs/2601.12639) |
| 28 | 2026-05 | [Nautilus Compass: Black-box Persona Drift Detection for Production LLM Agents](https://arxiv.org/abs/2605.09863) |
| 22 | 2026-09 | [Prompting Against Persona Drift: Comparing Intervention Timing and Content in LLM-Simulated Conversations](https://arxiv.org/abs/2609.24532) |
| 21 | 2025-04 | [Misaligned Roles, Misplaced Images: Structural Input Perturbations Expose Multimodal Alignment Blind Spots](https://arxiv.org/abs/2504.03735) |
| 13 | 2025-08 | [From "Aha Moments" to Controllable Thinking: Toward Meta-Cognitive Reasoning in Large Reasoning Models via Decoupled Reasoning and Control](https://arxiv.org/abs/2508.04460) |
| 12 | 2026-10 | [MASC: A Multi-Agent Self-Calibration Framework with Latent Construct Alignment for Consistent Client Role-Playing in Psychological Counseling](https://arxiv.org/abs/2610.08250) |
| 9 | 2026-01 | [Talking to Yourself: Defying Forgetting in Large Language Models](https://arxiv.org/abs/2602.20162) |
| 9 | 2026-01 | [A Dialectic Pipeline for Improving LLM Robustness](https://arxiv.org/abs/2601.20659) |
| 9 | 2026-05 | [A Heterogeneous Temporal Memory Governance Framework for Long-Term LLM Persona Consistency](https://arxiv.org/abs/2605.14802) |
| 9 | 2025-10 | [Consistently Simulating Human Personas with Multi-Turn Reinforcement Learning](https://arxiv.org/abs/2511.00222) |
| 9 | 2025-12 | [Living the Novel: A System for Generating Self-Training Timeline-Aware Conversational Agents from Novels](https://arxiv.org/abs/2512.07474) |
| 3 | 2026-04 | [Fake Plastic Voters: When Political Parties Can Use AI-Simulated Focus Groups](https://arxiv.org/abs/2606.00043) |
| 3 | 2026-04 | [FileGram: Grounding Agent Personalization in File-System Behavioral Traces](https://arxiv.org/abs/2604.04901) |

## Output length: planning, control, bias (438 papers)

| score | date | paper |
|---:|---|---|
| 70 | 2024-04 | [Energy-Latency Manipulation of Multi-modal Large Language Models via Verbose Samples](https://arxiv.org/abs/2404.16557) |
| 62 | 2024-04 | [IFViT: Interpretable Fixed-Length Representation for Fingerprint Matching via Vision Transformer](https://arxiv.org/abs/2404.08237) |
| 56 | 2026-07 | [How Much is Left? LLMs Linearly Encode Their Remaining Output Length](https://arxiv.org/abs/2607.05316) |
| 55 | 2026-04 | [Scheduling LLM Inference with Uncertainty-Aware Output Length Predictions](https://arxiv.org/abs/2604.00499) |
| 49 | 2025-06 | [AALC: Large Language Model Efficient Reasoning via Adaptive Accuracy-Length Control](https://arxiv.org/abs/2506.20160) |
| 48 | 2026-05 | [On Stable Long-Form Generation: Benchmarking and Mitigating Length Volatility](https://arxiv.org/abs/2605.01357) |
| 48 | 2024-12 | [Hansel: Output Length Controlling Framework for Large Language Models](https://arxiv.org/abs/2412.14033) |
| 47 | 2026-09 | [OUTLETS: Output-Length Prediction from Speculative Decoding Backbones](https://arxiv.org/abs/2609.01068) |
| 43 | 2025-11 | [An Image Is Worth Ten Thousand Words: Verbose-Text Induction Attacks on VLMs](https://arxiv.org/abs/2511.16163) |
| 43 | 2025-05 | [Making Small Language Models Efficient Reasoners: Intervention, Supervision, Reinforcement](https://arxiv.org/abs/2505.07961) |
| 43 | 2025-02 | [Disentangling Length Bias In Preference Learning Via Response-Conditioned Modeling](https://arxiv.org/abs/2502.00814) |
| 42 | 2026-02 | [Length-Unbiased Sequence Policy Optimization: Revealing and Controlling Response Length Variation in RLVR](https://arxiv.org/abs/2602.05261) |
| 41 | 2026-10 | [Jumping the Line: Exploiting Length Predictions in LLM Scheduling](https://arxiv.org/abs/2610.03430) |
| 41 | 2026-04 | [Robust Length Prediction: A Perspective from Heavy-Tailed Prompt-Conditioned Distributions](https://arxiv.org/abs/2604.07931) |
| 40 | 2025-05 | [Bias Fitting to Mitigate Length Bias of Reward Model in RLHF](https://arxiv.org/abs/2505.12843) |
| 38 | 2025-02 | [In-Context Learning (and Unlearning) of Length Biases](https://arxiv.org/abs/2502.06653) |
| 38 | 2024-12 | [Precise Length Control in Large Language Models](https://arxiv.org/abs/2412.11937) |
| 37 | 2026-03 | [SmartThinker: Progressive Chain-of-Thought Length Calibration for Efficient Large Language Model Reasoning](https://arxiv.org/abs/2603.08000) |
| 37 | 2025-10 | [LongWeave: A Long-Form Generation Benchmark Bridging Real-World Relevance and Verifiability](https://arxiv.org/abs/2510.24345) |
| 37 | 2025-11 | [Plan-and-Write: Structure-Guided Length Control for LLMs without Model Retraining](https://arxiv.org/abs/2511.01807) |
| 37 | 2025-06 | [LongWriter-Zero: Mastering Ultra-Long Text Generation via Reinforcement Learning](https://arxiv.org/abs/2506.18841) |
| 37 | 2025-11 | [Mitigating Length Bias in RLHF through a Causal Lens](https://arxiv.org/abs/2511.12573) |
| 36 | 2026-05 | [Predict-then-Diffuse: Adaptive Response Length for Compute-Budgeted Inference in Diffusion LLMs](https://arxiv.org/abs/2605.04215) |
| 34 | 2025-09 | [How Instruction-Tuning Imparts Length Control: A Cross-Lingual Mechanistic Analysis](https://arxiv.org/abs/2509.02075) |
| 33 | 2026-01 | [Step Potential Advantage Estimation: Harnessing Intermediate Confidence and Correctness for Efficient Mathematical Reasoning](https://arxiv.org/abs/2601.03823) |
| 33 | 2025-05 | [CASTILLO: Characterizing Response Length Distributions of Large Language Models](https://arxiv.org/abs/2505.16881) |
| 33 | 2025-06 | [Do Language Models Think Consistently? A Study of Value Preferences Across Varying Response Lengths](https://arxiv.org/abs/2506.02481) |
| 32 | 2024-12 | [Length Controlled Generation for Black-box LLMs](https://arxiv.org/abs/2412.14656) |
| 32 | 2024-06 | [Prompt-Based Length Controlled Generation with Multiple Control Types](https://arxiv.org/abs/2406.10278) |
| 31 | 2026-08 | [Survival-Guided Length Control for Efficient Diffusion Language Models](https://arxiv.org/abs/2608.26374) |
| 31 | 2026-03 | [Not Too Short, Not Too Long: How LLM Response Length Shapes People's Critical Thinking in Error Detection](https://arxiv.org/abs/2603.06878) |
| 31 | 2026-07 | [LBR: Towards Mitigating Length Bias in Large Language Models for Recommendation](https://arxiv.org/abs/2607.04270) |
| 31 | 2026-08 | [When Entropy Is Not Enough: Reclaiming Lost Semantics in LLM Output Length Prediction](https://arxiv.org/abs/2608.15592) |
| 31 | 2026-03 | [Long-form RewardBench: Evaluating Reward Models for Long-form Generation](https://arxiv.org/abs/2603.12963) |
| 31 | 2025-05 | [How Does Response Length Affect Long-Form Factuality](https://arxiv.org/abs/2505.23295) |
| 31 | 2025-10 | [Beyond Token Length: Step Pruner for Efficient and Accurate Reasoning in Large Language Models](https://arxiv.org/abs/2510.03805) |
| 30 | 2023-08 | [Prompt-Based Length Controlled Generation with Reinforcement Learning](https://arxiv.org/abs/2308.12030) |
| 30 | 2026-09 | [Quality Determines Direction, Length Shapes Magnitude: Length Control for Open-Ended Reinforcement Learning](https://arxiv.org/abs/2609.34718) |
| 30 | 2026-08 | [A Multi-Framework Comparison of Outline Stages in Long-Form Generation with LLMs](https://arxiv.org/abs/2608.26177) |
| 30 | 2026-06 | [IS-CoT: Breaking the Long-form Generation Collapse via Interleaved Structural Thinking](https://arxiv.org/abs/2606.09709) |

## Reasoning models: overthinking, early exit, end-of-thinking (322 papers)

| score | date | paper |
|---:|---|---|
| 80 | 2025-04 | [Between Underthinking and Overthinking: An Empirical Study of Reasoning Length and correctness in LLMs](https://arxiv.org/abs/2505.00127) |
| 80 | 2026-10 | [Constructing Pareto Frontiers of Optimal Reasoning Termination Methods for Overthinking in Reasoning Models](https://arxiv.org/abs/2610.13570) |
| 72 | 2026-02 | [NEAT: Neuron-Based Early Exit for Large Reasoning Models](https://arxiv.org/abs/2602.02010) |
| 68 | 2025-05 | [Mitigating Overthinking in Large Reasoning Models via Manifold Steering](https://arxiv.org/abs/2505.22411) |
| 66 | 2026-07 | [Know When to Stop: Segment-Level Credit Assignment for Reducing Overthinking](https://arxiv.org/abs/2607.00482) |
| 59 | 2025-03 | [Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models](https://arxiv.org/abs/2503.16419) |
| 53 | 2025-11 | [Batch Prompting Suppresses Overthinking Reasoning Under Constraint: How Batch Prompting Suppresses Overthinking in Reasoning Models](https://arxiv.org/abs/2511.04108) |
| 53 | 2026-04 | [When Is Thinking Enough? Early Exit via Sufficiency Assessment for Efficient Reasoning](https://arxiv.org/abs/2604.06787) |
| 52 | 2026-05 | [Inducing Overthink: Hierarchical Genetic Algorithm-based DoS Attack on Black-Box Large Language Reasoning Models](https://arxiv.org/abs/2605.13338) |
| 52 | 2026-03 | [Efficient Reasoning with Balanced Thinking](https://arxiv.org/abs/2603.12372) |
| 50 | 2026-02 | [Overthinking Loops in Agents: A Structural Risk via MCP Tools](https://arxiv.org/abs/2602.14798) |
| 48 | 2026-09 | [Efficient Reasoning via Constrained Optimization in Latent Space](https://arxiv.org/abs/2609.34181) |
| 46 | 2025-08 | [Reconsidering Overthinking: Penalizing Internal and External Redundancy in CoT Reasoning](https://arxiv.org/abs/2508.02178) |
| 45 | 2026-07 | [Commit Locally, Exit Globally: Coordinating Adaptive Sampling and Early Exit in Diffusion Language Models](https://arxiv.org/abs/2607.28166) |
| 45 | 2026-06 | [Thinking Past the Answer: Evaluating Harmful Overthinking in Large Reasoning Models](https://arxiv.org/abs/2606.02835) |
| 44 | 2026-03 | [Mitigating Overthinking in Large Reasoning Language Models via Reasoning Path Deviation Monitoring](https://arxiv.org/abs/2603.14251) |
| 44 | 2026-03 | [Avoiding Overthinking and Underthinking: Curriculum-Aware Budget Scheduling for LLMs](https://arxiv.org/abs/2604.19780) |
| 43 | 2025-05 | [S-GRPO: Early Exit via Reinforcement Learning in Reasoning Models](https://arxiv.org/abs/2505.07686) |
| 43 | 2025-06 | [On Reasoning Strength Planning in Large Reasoning Models](https://arxiv.org/abs/2506.08390) |
| 42 | 2026-03 | [ROM: Real-time Overthinking Mitigation via Streaming Detection and Intervention](https://arxiv.org/abs/2603.22016) |
| 42 | 2026-05 | [Stop When Reasoning Converges: Semantic-Preserving Early Exit for Reasoning Models](https://arxiv.org/abs/2605.17672) |
| 41 | 2025-05 | [Long-Short Chain-of-Thought Mixture Supervised Fine-Tuning Eliciting Efficient Reasoning in Large Language Models](https://arxiv.org/abs/2505.03469) |
| 41 | 2025-07 | [Do LLMs Overthink Basic Math Reasoning? Benchmarking the Accuracy-Efficiency Tradeoff in Language Models](https://arxiv.org/abs/2507.04023) |
| 41 | 2026-06 | [Dynamic Rollout Editing for Reducing Overthinking in RL-Trained Reasoning Models](https://arxiv.org/abs/2606.17890) |
| 41 | 2026-01 | [Anti-Length Shift: Dynamic Outlier Truncation for Training Efficient Reasoning Models](https://arxiv.org/abs/2601.03969) |
| 39 | 2026-03 | [Efficient Reasoning on the Edge](https://arxiv.org/abs/2603.16867) |
| 39 | 2026-08 | [Don't Overthink, Don't Underthink: Toward Adaptive Reasoning in Agentic AI](https://arxiv.org/abs/2608.26442) |
| 39 | 2026-04 | [Step-GRPO: Internalizing Dynamic Early Exit for Efficient Reasoning](https://arxiv.org/abs/2604.16890) |
| 38 | 2025-04 | [Missing Premise exacerbates Overthinking: Are Reasoning Models losing Critical Thinking Skill?](https://arxiv.org/abs/2504.06514) |
| 38 | 2025-05 | [The First Impression Problem: Internal Bias Triggers Overthinking in Reasoning Models](https://arxiv.org/abs/2505.16448) |
| 38 | 2025-08 | [Promoting Efficient Reasoning with Verifiable Stepwise Reward](https://arxiv.org/abs/2508.10293) |
| 38 | 2025-06 | [Efficient Reasoning Through Suppression of Self-Affirmation Reflections in Large Reasoning Models](https://arxiv.org/abs/2506.12353) |
| 37 | 2026-02 | [ThinkRouter: Efficient Reasoning via Routing Thinking between Latent and Discrete Spaces](https://arxiv.org/abs/2602.11683) |
| 37 | 2025-09 | [Certainty-Guided Reasoning in Large Language Models: A Dynamic Thinking Budget Approach](https://arxiv.org/abs/2509.07820) |
| 37 | 2025-10 | [Explore Briefly, Then Decide: Mitigating LLM Overthinking via Cumulative Entropy Regulation](https://arxiv.org/abs/2510.02249) |
| 37 | 2025-10 | [The Zero-Step Thinking: An Empirical Study of Mode Selection as Harder Early Exit in Reasoning Models](https://arxiv.org/abs/2510.19176) |
| 37 | 2025-08 | [Don't Overthink It: A Survey of Efficient R1-style Large Reasoning Models](https://arxiv.org/abs/2508.02120) |
| 37 | 2025-10 | [Do LLMs Really Need 10+ Thoughts for "Find the Time 1000 Days Later"? Towards Structural Understanding of LLM Overthinking](https://arxiv.org/abs/2510.07880) |
| 37 | 2025-08 | [OptimalThinkingBench: Evaluating Over and Underthinking in LLMs](https://arxiv.org/abs/2508.13141) |
| 36 | 2026-03 | [InfoDensity: Rewarding Information-Dense Traces for Efficient Reasoning](https://arxiv.org/abs/2603.17310) |

## Interpretability methods & mechanisms (367 papers)

| score | date | paper |
|---:|---|---|
| 73 | 2026-05 | [TACT: Mitigating Overthinking and Overacting in Coding Agents via Activation Steering](https://arxiv.org/abs/2605.05980) |
| 73 | 2024-10 | [Mechanistic Unlearning: Robust Knowledge Unlearning and Editing via Mechanistic Localization](https://arxiv.org/abs/2410.12949) |
| 70 | 2026-03 | [Attention Sinks Induce Gradient Sinks: Massive Activations as Gradient Regulators in Transformers](https://arxiv.org/abs/2603.17771) |
| 67 | 2025-10 | [Mitigating Attention Sinks and Massive Activations in Audio-Visual Speech Recognition with LLMs](https://arxiv.org/abs/2510.22603) |
| 66 | 2026-02 | [Embracing Anisotropy: Turning Massive Activations into Interpretable Control Knobs for Large Language Models](https://arxiv.org/abs/2603.00029) |
| 65 | 2025-06 | [Adaptive Activation Steering for Efficient LLM Reasoning via Closed-Loop PID Control](https://arxiv.org/abs/2506.18831) |
| 64 | 2026-09 | [Understanding On-Policy Distillation: A Mechanistic Interpretability Perspective via Sparse Crosscoders](https://arxiv.org/abs/2609.35210) |
| 64 | 2025-04 | [SAEs Can Improve Unlearning: Dynamic Sparse Autoencoder Guardrails for Precision Unlearning in LLMs](https://arxiv.org/abs/2504.08192) |
| 61 | 2026-05 | [A Single Layer to Explain Them All:Understanding Massive Activations in Large Language Models](https://arxiv.org/abs/2605.08504) |
| 61 | 2026-05 | [Few Channels Draw The Whole Picture: Revealing Massive Activations in Diffusion Transformers](https://arxiv.org/abs/2605.13974) |
| 60 | 2024-10 | [Repetition Neurons: How Do Language Models Produce Repetitions?](https://arxiv.org/abs/2410.13497) |
| 58 | 2025-03 | [A Refined Analysis of Massive Activations in LLMs](https://arxiv.org/abs/2503.22329) |
| 58 | 2026-10 | [Massive Activation Gating Channel in Large Language Models](https://arxiv.org/abs/2610.07661) |
| 58 | 2026-03 | [Steering Video Diffusion Transformers with Massive Activations](https://arxiv.org/abs/2603.17825) |
| 58 | 2026-04 | [From Concept-Aligned Tokens to Vulnerable Features: Mechanistic Localization of Jailbreaks](https://arxiv.org/abs/2604.23130) |
| 56 | 2025-04 | [Softpick: No Attention Sink, No Massive Activations with Rectified Softmax](https://arxiv.org/abs/2504.20966) |
| 55 | 2025-05 | [Unleashing Diffusion Transformers for Visual Correspondence by Modulating Massive Activations](https://arxiv.org/abs/2505.18584) |
| 55 | 2025-08 | [Hidden Dynamics of Massive Activations in Transformer Training](https://arxiv.org/abs/2508.03616) |
| 55 | 2025-07 | [Understanding and Controlling Repetition Neurons and Induction Heads in In-Context Learning](https://arxiv.org/abs/2507.07810) |
| 55 | 2026-06 | [Linear Probes Detect Task Format, Not Reasoning Mode in Language Model Hidden States](https://arxiv.org/abs/2606.02907) |
| 55 | 2026-02 | [Steer2Edit: From Activation Steering to Component-Level Editing](https://arxiv.org/abs/2602.09870) |
| 55 | 2026-05 | [The Structural Origin of Attention Sink: Variance Discrepancy, Super Neurons, and Dimension Disparity](https://arxiv.org/abs/2605.06611) |
| 55 | 2026-09 | [The Life Cycle of a Massive Activation: Stochastic Birth, Weight-Decay-Driven Growth, and Competitive Consolidation](https://arxiv.org/abs/2610.00423) |
| 55 | 2026-06 | [PhaseQuant: Mitigating Activation Quantization Collapse via Residual-Stream Dynamics](https://arxiv.org/abs/2606.12487) |
| 55 | 2026-08 | [Detecting Safety Training Modification in Language Models via Activation Analysis](https://arxiv.org/abs/2608.05578) |
| 55 | 2026-03 | [Principled Steering via Null-space Projection for Jailbreak Defense in Vision-Language Models](https://arxiv.org/abs/2603.22094) |
| 55 | 2026-06 | [Stop Early, Spend Less: Hidden-State Probes as a Practical Recipe for Streaming Moderation of LLM Outputs](https://arxiv.org/abs/2606.10487) |
| 53 | 2025-05 | [Guiding Giants: Lightweight Controllers for Weighted Activation Steering in LLMs](https://arxiv.org/abs/2505.20309) |
| 53 | 2026-06 | [Agentic Chain-of-Thought Steering for Efficient and Controllable LLM Reasoning](https://arxiv.org/abs/2606.03965) |
| 53 | 2026-05 | [A Circuit, Not The Circuit: Non-Unique Causal Localisation of the Mamba-2 State Sink](https://arxiv.org/abs/2606.00930) |
| 53 | 2026-02 | [Probing Graph Neural Network Activation Patterns Through Graph Topology](https://arxiv.org/abs/2602.21092) |
| 53 | 2026-02 | [Cross-Architecture Model Diffing with Crosscoders: Unsupervised Discovery of Differences Between LLMs](https://arxiv.org/abs/2602.11729) |
| 53 | 2026-08 | [BabelSteering: Multilingual Safety Alignment via English Steering Vectors](https://arxiv.org/abs/2608.16577) |
| 53 | 2026-05 | [Moral Sensitivity in LLMs: A Tiered Evaluation of Contextual Bias via Behavioral Profiling and Mechanistic Interpretability](https://arxiv.org/abs/2605.03217) |
| 52 | 2025-04 | [Reasoning Models Know When They're Right: Probing Hidden States for Self-Verification](https://arxiv.org/abs/2504.05419) |
| 52 | 2024-02 | [Massive Activations in Large Language Models](https://arxiv.org/abs/2402.17762) |
| 52 | 2025-10 | [Massive Activations are the Key to Local Detail Synthesis in Diffusion Transformers](https://arxiv.org/abs/2510.11538) |
| 52 | 2025-06 | [Reviving Your MNEME: Predicting The Side Effects of LLM Unlearning and Fine-Tuning via Sparse Model Diffing](https://arxiv.org/abs/2507.21084) |
| 52 | 2026-09 | [Steering Under Compression: Dose-Response, Capability Cost, and Failure Asymmetry in Quantized LLMs](https://arxiv.org/abs/2609.06473) |
| 52 | 2026-04 | [A Mechanistic Account of Attention Sinks in GPT-2: One Circuit, Broader Implications for Mitigation](https://arxiv.org/abs/2604.14722) |

## Shallow fine-tuning, unlearning, suppression vs erasure (78 papers)

| score | date | paper |
|---:|---|---|
| 50 | 2025-09 | [Erase or Hide? Suppressing Spurious Unlearning Neurons for Robust Unlearning](https://arxiv.org/abs/2509.22263) |
| 44 | 2026-09 | [Do LLMs Really Forget? Hidden-State Leakage in Model Unlearning and How to Fix it](https://arxiv.org/abs/2609.36612) |
| 39 | 2024-06 | [Unlearning or Obfuscating? Jogging the Memory of Unlearned LLMs via Benign Relearning](https://arxiv.org/abs/2406.13356) |
| 39 | 2026-07 | [Crossing the Margin Cliff: Toward Relearn-Robust LLM Unlearning via Margin Calibration](https://arxiv.org/abs/2607.27836) |
| 38 | 2025-10 | [Forgetting to Forget: Attention Sink as A Gateway for Backdooring LLM Unlearning](https://arxiv.org/abs/2510.17021) |
| 37 | 2025-05 | [Layered Unlearning for Adversarial Relearning](https://arxiv.org/abs/2505.09500) |
| 37 | 2025-02 | [ReLearn: Unlearning via Learning for Large Language Models](https://arxiv.org/abs/2502.11190) |
| 37 | 2025-05 | [Unlearning Isn't Deletion: Investigating Reversibility of Machine Unlearning in LLMs](https://arxiv.org/abs/2505.16831) |
| 36 | 2025-02 | [Towards LLM Unlearning Resilient to Relearning Attacks: A Sharpness-Aware Minimization Perspective and Beyond](https://arxiv.org/abs/2502.05374) |
| 34 | 2026-05 | [Robust LLM Unlearning Against Relearning Attacks: The Minor Components in Representations Matter](https://arxiv.org/abs/2605.11685) |
| 34 | 2026-03 | [Simulating Novice Students Using Machine Unlearning and Relearning in Large Language Models](https://arxiv.org/abs/2603.26142) |
| 34 | 2026-04 | [WIN-U: Woodbury-Informed Newton-Unlearning as a retain-free Machine Unlearning Framework](https://arxiv.org/abs/2604.13438) |
| 34 | 2026-10 | [Open-MMUnlearning: Unifying Methods and Evaluation for MLLM Unlearning](https://arxiv.org/abs/2610.10358) |
| 34 | 2026-01 | [Beyond Superficial Unlearning: Sharpness-Aware Robust Erasure of Hallucinations in Multimodal LLMs](https://arxiv.org/abs/2601.16527) |
| 34 | 2025-09 | [Dual-Space Smoothness for Robust and Balanced LLM Unlearning](https://arxiv.org/abs/2509.23362) |
| 33 | 2025-08 | [Reliable Unlearning Harmful Information in LLMs with Metamorphosis Representation Projection](https://arxiv.org/abs/2508.15449) |
| 31 | 2025-09 | [Beyond Sharp Minima: Robust LLM Unlearning via Feedback-Guided Multi-Point Optimization](https://arxiv.org/abs/2509.20230) |
| 31 | 2025-09 | [Anchoring Refusal Direction: Mitigating Safety Risks in Tuning via Projection Constraint](https://arxiv.org/abs/2509.06795) |
| 30 | 2026-06 | [Natively Unlearnable Large Language Models](https://arxiv.org/abs/2606.13873) |
| 30 | 2025-09 | [Beyond Surface Alignment: Rebuilding LLMs Safety Mechanism via Probabilistically Ablating Refusal Direction](https://arxiv.org/abs/2509.15202) |
| 30 | 2025-05 | [Refusal Direction is Universal Across Safety-Aligned Languages](https://arxiv.org/abs/2505.17306) |
| 28 | 2025-05 | [Shallow Preference Signals: Large Language Model Aligns Even Better with Truncated Data?](https://arxiv.org/abs/2505.17122) |
| 28 | 2026-08 | [Distance Is Not Enough: Forget-Retain Alignment Gap Predicts LLM Relearning Robustness](https://arxiv.org/abs/2608.25429) |
| 28 | 2026-09 | [Unlearning Deceptive Behaviors in LLMs with Contrastive Forget Sets](https://arxiv.org/abs/2609.38909) |
| 27 | 2025-06 | [LLM Unlearning Should Be Form-Independent](https://arxiv.org/abs/2506.07795) |
| 26 | 2026-06 | [Inference-Time Vulnerability Beyond Shallow Safety: Alignment Along Generation Trajectories](https://arxiv.org/abs/2606.04778) |
| 25 | 2024-10 | [Simplicity Prevails: Rethinking Negative Preference Optimization for LLM Unlearning](https://arxiv.org/abs/2410.07163) |
| 25 | 2026-10 | [Not All Change Is Damage: Update-Matched Unlearning for Large Language Models](https://arxiv.org/abs/2610.21230) |
| 25 | 2026-02 | [Anatomy of Unlearning: The Dual Impact of Fact Salience and Model Fine-Tuning](https://arxiv.org/abs/2602.19612) |
| 25 | 2026-01 | [Unlearning in LLMs: Methods, Evaluation, and Open Challenges](https://arxiv.org/abs/2601.13264) |
| 25 | 2026-06 | [RepSelect: Robust LLM Unlearning via Representation Selectivity](https://arxiv.org/abs/2606.17168) |
| 25 | 2026-01 | [FIT to Forget: Robust Continual Unlearning for Large Language Models](https://arxiv.org/abs/2601.21682) |
| 25 | 2026-09 | [Forgetting Only What Matters: Layer-Selective Unlearning toward Robust LLMs](https://arxiv.org/abs/2609.10439) |
| 25 | 2026-05 | [SHRED: Retain-Set-Free Unlearning via Self-Distillation with Logit Demotion](https://arxiv.org/abs/2605.07482) |
| 24 | 2025-05 | [From Dormant to Deleted: Tamper-Resistant Unlearning Through Weight-Space Regularization](https://arxiv.org/abs/2505.22310) |
| 24 | 2025-12 | [Robust MLLM Unlearning via Visual Knowledge Distillation](https://arxiv.org/abs/2512.11325) |
| 24 | 2025-05 | [BLUR: A Benchmark for LLM Unlearning Robust to Forget-Retain Overlap](https://arxiv.org/abs/2506.15699) |
| 24 | 2025-09 | [Unlearning That Lasts: Utility-Preserving, Robust, and Almost Irreversible Forgetting in LLMs](https://arxiv.org/abs/2509.02820) |
| 24 | 2025-10 | [OFFSIDE: Benchmarking Unlearning Misinformation in Multimodal Large Language Models](https://arxiv.org/abs/2510.22535) |
| 24 | 2025-10 | [LLM Unlearning Under the Microscope: A Full-Stack View on Methods and Metrics](https://arxiv.org/abs/2510.07626) |

## Degeneration, repetition, loops (130 papers)

| score | date | paper |
|---:|---|---|
| 72 | 2025-11 | [LoopLLM: Transferable Energy-Latency Attacks in LLMs via Repetitive Generation](https://arxiv.org/abs/2511.07876) |
| 50 | 2022-10 | [A Continuum of Generation Tasks for Investigating Length Bias and Degenerate Repetition](https://arxiv.org/abs/2210.10817) |
| 44 | 2026-10 | [Learning to Compute Is Not Learning to Retain or Reuse in Looped Transformers](https://arxiv.org/abs/2610.19768) |
| 44 | 2026-08 | [LoopMTP: A looped transformer guided by latent multi-token prediction](https://arxiv.org/abs/2608.03624) |
| 42 | 2026-03 | [Adaptive Loops and Memory in Transformers: Think Harder or Know More?](https://arxiv.org/abs/2603.08391) |
| 42 | 2026-02 | [LoopViT: Scaling Visual ARC with Looped Transformers](https://arxiv.org/abs/2602.02156) |
| 41 | 2026-04 | [One Token Away from Collapse: The Fragility of Instruction-Tuned Helpfulness](https://arxiv.org/abs/2604.13006) |
| 41 | 2026-06 | [Stabilizing Extrapolation in Looped Transformers via Learned Stochastic Stopping](https://arxiv.org/abs/2606.29983) |
| 40 | 2025-04 | [Repetitions are not all alike: distinct mechanisms sustain repetition in language models](https://arxiv.org/abs/2504.01100) |
| 37 | 2026-07 | [When Does Recurrence Become an Algorithm? Convergence Selection in Weight-Tied Looped Transformers](https://arxiv.org/abs/2607.20594) |
| 37 | 2023-10 | [Repetition In Repetition Out: Towards Understanding Neural Text Degeneration from the Data Perspective](https://arxiv.org/abs/2310.10226) |
| 36 | 2026-09 | [Looped Actor: Depth-Recurrent Reasoning Models for Reinforcement Learning](https://arxiv.org/abs/2609.37432) |
| 36 | 2025-05 | [CTRAP: Embedding Collapse Trap to Safeguard Large Language Models from Harmful Fine-Tuning](https://arxiv.org/abs/2505.16559) |
| 34 | 2026-10 | [Recurrent Self-Improvement: Dynamic Cross-Loop On-Policy Distillation for Looped Language Models](https://arxiv.org/abs/2610.10623) |
| 33 | 2026-07 | [Operational Proto-Introspection in Looped Language Models: Process-Quality Taps, Executable Branching, and the Readout-Control Boundary](https://arxiv.org/abs/2607.18553) |
| 33 | 2026-10 | [LoOPSD: On-Policy Self-Distillation with Looped Teachers](https://arxiv.org/abs/2610.18162) |
| 33 | 2026-09 | [SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers](https://arxiv.org/abs/2609.01343) |
| 33 | 2026-02 | [From Growing to Looping: A Unified View of Iterative Computation in LLMs](https://arxiv.org/abs/2602.16490) |
| 33 | 2026-10 | [AdaLoop: Adaptive-Depth Latent Reasoning for Audio Language Models](https://arxiv.org/abs/2610.06949) |
| 33 | 2025-11 | [A Quantitative Study of Sustained Focus in Large Language Models via Repetitive Deterministic Prediction Tasks](https://arxiv.org/abs/2511.00763) |
| 31 | 2026-02 | [Attention Sink Forges Native MoE in Attention Layers: Sink-Aware Training to Address Head Collapse](https://arxiv.org/abs/2602.01203) |
| 31 | 2025-12 | [Solving LLM Repetition Problem in Production: A Comprehensive Study of Multiple Solutions](https://arxiv.org/abs/2512.04419) |
| 30 | 2026-08 | [What a Cross-Model Fixed-Point Census Can and Cannot Arbitrate About Repetition](https://arxiv.org/abs/2609.29507) |
| 28 | 2026-06 | [The Devil is in the Spectrum: Mitigating Representation Collapse in LLMs via Topologically Regularized Side-Path](https://arxiv.org/abs/2607.20484) |
| 26 | 2026-10 | [FreeEvolve: Learning to Evolve Beyond Fixed Loops](https://arxiv.org/abs/2610.09197) |
| 26 | 2026-05 | [Safety Geometry Collapse in Multimodal LLMs and Adaptive Drift Correction](https://arxiv.org/abs/2605.18104) |
| 26 | 2026-07 | [Per-Token Fixed-Point Convergence in Depth-Recurrent Transformers](https://arxiv.org/abs/2607.14427) |
| 25 | 2026-08 | [FOCUS & RePAIR: Mitigating Text Degeneration via Token-Level Guidance for Pruned Large Language Models](https://arxiv.org/abs/2608.26676) |
| 25 | 2026-08 | [Groundhog Bit-Flip Attack: Seeding Infinite Generation Loops in Mixture-of-Experts LLMs through Bit Flips](https://arxiv.org/abs/2608.25276) |
| 23 | 2026-05 | [PEARL: Solver-in-the-Loop Interactive Optimization Modeling from Natural Language](https://arxiv.org/abs/2607.18256) |
| 23 | 2026-05 | [CyberCorrect: A Cybernetic Framework for Closed-Loop Self-Correction in Large Language Models](https://arxiv.org/abs/2605.17305) |
| 22 | 2025-11 | [Think-at-Hard: Dynamic Looped Transformers for Improved Reasoning](https://arxiv.org/abs/2511.08577) |
| 22 | 2021-09 | [Relating Neural Text Degeneration to Exposure Bias](https://arxiv.org/abs/2109.08705) |
| 22 | 2026-02 | [Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning](https://arxiv.org/abs/2602.11149) |
| 22 | 2026-05 | [CLORE: Content-Level Optimization for Reasoning Efficiency](https://arxiv.org/abs/2605.22211) |
| 22 | 2026-04 | [Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers](https://arxiv.org/abs/2604.07822) |
| 22 | 2026-05 | [FocuSFT: Bilevel Optimization for Dilution-Aware Long-Context Fine-Tuning](https://arxiv.org/abs/2605.09932) |
| 21 | 2023-05 | [Reward Collapse in Aligning Large Language Models](https://arxiv.org/abs/2305.17608) |
| 21 | 2023-07 | [Mitigating the Learning Bias towards Repetition by Self-Contrastive Training for Open-Ended Generation](https://arxiv.org/abs/2307.01542) |
| 21 | 2024-10 | [Mitigating the Language Mismatch and Repetition Issues in LLM-based Machine Translation via Model Editing](https://arxiv.org/abs/2410.07054) |

## Special tokens, attention sinks, massive activations (123 papers)

| score | date | paper |
|---:|---|---|
| 61 | 2026-03 | [The Spike, the Sparse and the Sink: Anatomy of Massive Activations and Attention Sinks](https://arxiv.org/abs/2603.05498) |
| 44 | 2025-10 | [Attention Sinks and Compression Valleys in LLMs are Two Sides of the Same Coin](https://arxiv.org/abs/2510.06477) |
| 36 | 2026-09 | [Do New Attention Mechanisms Actually Fix Attention Sinks at Million-Token Context?](https://arxiv.org/abs/2609.08574) |
| 34 | 2026-05 | [Attention Sinks in Massively Multilingual Neural Machine Translation:Discovery, Analysis, and Mitigation](https://arxiv.org/abs/2605.01229) |
| 33 | 2025-03 | [See What You Are Told: Visual Attention Sink in Large Multimodal Models](https://arxiv.org/abs/2503.03321) |
| 30 | 2026-10 | [Attention Sinks in VLMs Are Borrowed, Not Seen](https://arxiv.org/abs/2610.15855) |
| 30 | 2026-10 | [Exploring Attention Sinks in Text-to-Image Transformers from Diffusion and Autoregressive Models](https://arxiv.org/abs/2610.13337) |
| 28 | 2025-08 | [KVSink: Understanding and Enhancing the Preservation of Attention Sinks in KV Cache Quantization for LLMs](https://arxiv.org/abs/2508.04257) |
| 25 | 2025-04 | [EDIT: Enhancing Vision Transformers by Mitigating Attention Sink through an Encoder-Decoder Architecture](https://arxiv.org/abs/2504.06738) |
| 25 | 2025-02 | [Attention Sinks: A 'Catch, Tag, Release' Mechanism for Embeddings](https://arxiv.org/abs/2502.00919) |
| 25 | 2026-04 | [Attention Sink in Transformers: A Survey on Utilization, Interpretation, and Mitigation](https://arxiv.org/abs/2604.10098) |
| 24 | 2024-02 | [Spectral Filters, Dark Signals, and Attention Sinks](https://arxiv.org/abs/2402.09221) |
| 24 | 2025-08 | [CTR-Sink: Attention Sink for Language Models in Click-Through Rate Prediction](https://arxiv.org/abs/2508.03668) |
| 23 | 2026-05 | [Attention Sinks and Outliers in Attention Residuals](https://arxiv.org/abs/2605.17887) |
| 23 | 2026-04 | [Attention Sinks as Internal Signals for Hallucination Detection in Large Language Models](https://arxiv.org/abs/2604.10697) |
| 22 | 2024-10 | [When Attention Sink Emerges in Language Models: An Empirical View](https://arxiv.org/abs/2410.10781) |
| 22 | 2024-06 | [Unveiling and Harnessing Hidden Attention Sinks: Enhancing Large Language Models without Training through Attention Calibration](https://arxiv.org/abs/2406.15765) |
| 22 | 2024-11 | [Seeing Clearly by Layer Two: Enhancing Attention Heads to Alleviate Hallucination in LVLMs](https://arxiv.org/abs/2411.09968) |
| 22 | 2026-05 | [Addressing Exacerbated Attention Sink for Source-Free Cross-Domain Few-Shot Learning](https://arxiv.org/abs/2605.25799) |
| 21 | 2025-08 | [What are you sinking? A geometric approach on attention sink](https://arxiv.org/abs/2508.02546) |
| 21 | 2025-10 | [Attention Sinks in Diffusion Language Models](https://arxiv.org/abs/2510.15731) |
| 20 | 2026-06 | [A Unifying View of Attention Sinks: From Mechanisms to Architectural Interventions](https://arxiv.org/abs/2606.08105) |
| 19 | 2025-07 | [Artifacts and Attention Sinks: Structured Approximations for Efficient Vision Transformers](https://arxiv.org/abs/2507.16018) |
| 19 | 2026-05 | [ASAP: Attention Sink Anchored Pruning](https://arxiv.org/abs/2605.22372) |
| 19 | 2026-03 | [Attention Sinks Are Provably Necessary in Softmax Transformers: Evidence from Trigger-Conditional Tasks](https://arxiv.org/abs/2603.11487) |
| 19 | 2026-01 | [Attention Needs to Focus: A Unified Perspective on Attention Allocation](https://arxiv.org/abs/2601.00919) |
| 18 | 2023-09 | [Efficient Streaming Language Models with Attention Sinks](https://arxiv.org/abs/2309.17453) |
| 17 | 2026-04 | [SepSeq: A Training-Free Framework for Long Numerical Sequence Processing in LLMs](https://arxiv.org/abs/2604.07737) |
| 17 | 2026-09 | [It's Not RoPE that Creates Sinks: The Role of Self-Concentration and Value-Non-Mixing in Attention](https://arxiv.org/abs/2609.09085) |
| 17 | 2026-03 | [Gradient Flow Polarizes Softmax Outputs towards Low-Entropy Solutions](https://arxiv.org/abs/2603.06248) |
| 16 | 2025-01 | [RotateKV: Accurate and Robust 2-Bit KV Cache Quantization for LLMs via Outlier-Aware Adaptive Rotations](https://arxiv.org/abs/2501.16383) |
| 16 | 2026-04 | [SinkTrack: Attention Sink based Context Anchoring for Large Language Models](https://arxiv.org/abs/2604.10027) |
| 16 | 2026-02 | [Surgery: Mitigating Harmful Fine-Tuning for Large Language Models via Attention Sink](https://arxiv.org/abs/2602.05228) |
| 16 | 2026-05 | [Attention Sinks in Diffusion Transformers: A Causal Analysis](https://arxiv.org/abs/2605.09313) |
| 16 | 2026-03 | [On the Nature of Attention Sink that Shapes Decoding Strategy in Omni-LLMs](https://arxiv.org/abs/2603.14337) |
| 16 | 2026-04 | [When Sinks Help or Hurt: Unified Framework for Attention Sink in Large Vision-Language Models](https://arxiv.org/abs/2604.03316) |
| 15 | 2024-06 | [PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling](https://arxiv.org/abs/2406.02069) |
| 15 | 2025-01 | [Mirage in the Eyes: Hallucination Attack on Multi-modal Large Language Models with Only Attention Sink](https://arxiv.org/abs/2501.15269) |
| 15 | 2025-04 | [Why do LLMs attend to the first token?](https://arxiv.org/abs/2504.02732) |
| 14 | 2026-04 | [SinkRouter: Sink-Aware Routing for Efficient Long-Context Decoding in Large Language and Multimodal Models](https://arxiv.org/abs/2604.16883) |

## Attacks via non-termination (energy-latency, DoS) (51 papers)

| score | date | paper |
|---:|---|---|
| 83 | 2024-01 | [Inducing High Energy-Latency of Large Vision-Language Models with Verbose Images](https://arxiv.org/abs/2401.11170) |
| 38 | 2024-10 | [Denial-of-Service Poisoning Attacks against Large Language Models](https://arxiv.org/abs/2410.10760) |
| 37 | 2026-10 | [Reactivating Alignment: Defending LLMs from Jailbreaks via Intention-Aware Input-Output Matching](https://arxiv.org/abs/2610.04470) |
| 32 | 2024-08 | [Defending against Jailbreak through Early Exit Generation of Large Language Models](https://arxiv.org/abs/2408.11308) |
| 30 | 2025-10 | [RAID: Refusal-Aware and Integrated Decoding for Jailbreaking LLMs](https://arxiv.org/abs/2510.13901) |
| 28 | 2025-06 | [Toward Principled LLM Safety Testing: Solving the Jailbreak Oracle Problem](https://arxiv.org/abs/2506.17299) |
| 28 | 2026-01 | [Sponge Tool Attack: Stealthy Denial-of-Efficiency against Tool-Augmented Agentic Reasoning](https://arxiv.org/abs/2601.17566) |
| 28 | 2026-05 | [Revisiting JBShield: Breaking and Rebuilding Representation-Level Jailbreak Defenses](https://arxiv.org/abs/2605.03095) |
| 26 | 2026-02 | [Fail-Closed Alignment for Large Language Models](https://arxiv.org/abs/2602.16977) |
| 23 | 2026-09 | [Deep Learning Latency Attacks and Defenses: A Cross-Domain Survey of Availability Threats](https://arxiv.org/abs/2609.36732) |
| 23 | 2026-03 | [VidDoS: Universal Denial-of-Service Attack on Video-based Large Language Models](https://arxiv.org/abs/2603.01454) |
| 22 | 2024-10 | [Endless Jailbreaks with Bijection Learning](https://arxiv.org/abs/2410.01294) |
| 22 | 2025-10 | [MetaDefense: Defending Finetuning-based Jailbreak Attack Before and During Generation](https://arxiv.org/abs/2510.07835) |
| 20 | 2026-05 | [OTora: A Unified Red Teaming Framework for Reasoning-Level Denial-of-Service in LLM Agents](https://arxiv.org/abs/2605.08876) |
| 20 | 2026-06 | [RAS: Measuring LLM Safety Through Refusal Alignment](https://arxiv.org/abs/2606.25750) |
| 20 | 2026-09 | [Bait-and-Recover: Poisoning Internal Refusal Signals to Defend LLMs against White-Box Editing Jailbreaks](https://arxiv.org/abs/2609.05794) |
| 19 | 2020-06 | [Sponge Examples: Energy-Latency Attacks on Neural Networks](https://arxiv.org/abs/2006.03463) |
| 19 | 2025-11 | [AlignTree: Efficient Defense Against LLM Jailbreak Attacks](https://arxiv.org/abs/2511.12217) |
| 16 | 2026-06 | [An Exploratory Case Study of LLM-Assisted Refactoring and Gameplay Feature Generation in an Endless Runner Game](https://arxiv.org/abs/2606.21171) |
| 16 | 2026-04 | [Breaking MCP with Function Hijacking Attacks: Novel Threats for Function Calling and Agentic Models](https://arxiv.org/abs/2604.20994) |
| 15 | 2025-05 | [Attention! Your Vision Language Model Could Be Maliciously Manipulated](https://arxiv.org/abs/2505.19911) |
| 15 | 2025-07 | [Squeeze the Soaked Sponge: Efficient Off-policy Reinforcement Finetuning for Large Language Model](https://arxiv.org/abs/2507.06892) |
| 12 | 2025-08 | [Safety Alignment Should Be Made More Than Just A Few Attention Heads](https://arxiv.org/abs/2508.19697) |
| 10 | 2022-03 | [Energy-Latency Attacks via Sponge Poisoning](https://arxiv.org/abs/2203.08147) |
| 10 | 2025-05 | [Sponge Attacks on Sensing AI: Energy-Latency Vulnerabilities and Defense via Model Pruning](https://arxiv.org/abs/2505.06454) |
| 9 | 2026-07 | [A Cross-Architecture Audit of Direction-Based Inference-Time Defences in Vision-Language Models](https://arxiv.org/abs/2607.27910) |
| 9 | 2025-02 | [Safety at Scale: A Comprehensive Survey of Large Model and Agent Safety](https://arxiv.org/abs/2502.05206) |
| 9 | 2025-10 | [Toward Understanding the Transferability of Adversarial Suffixes in Large Language Models](https://arxiv.org/abs/2510.22014) |
| 9 | 2023-05 | [Energy-Latency Attacks to On-Device Neural Networks via Sponge Poisoning](https://arxiv.org/abs/2305.03888) |
| 8 | 2024-01 | [On Prompt-Driven Safeguarding for Large Language Models](https://arxiv.org/abs/2401.18018) |
| 8 | 2023-10 | [Localizing Active Objects from Egocentric Vision with Symbolic World Knowledge](https://arxiv.org/abs/2310.15066) |
| 6 | 2026-04 | [In Search of the Ingredients of Open-Endedness: Replicating Picbreeder with Large Vision-Language Models](https://arxiv.org/abs/2605.23908) |
| 6 | 2026-09 | [Continuous Context Management](https://arxiv.org/abs/2609.35540) |
| 6 | 2026-09 | [Getting Motif-ated: Controllable AI Compositions from Injected Motif Prompts](https://arxiv.org/abs/2609.32788) |
| 6 | 2026-08 | [The Utility of LLMs in Recommender Systems Explanation Evaluation](https://arxiv.org/abs/2609.01627) |
| 6 | 2026-04 | [Leveraging Mathematical Reasoning of LLMs for Efficient GPU Thread Mapping](https://arxiv.org/abs/2604.10387) |
| 6 | 2025-03 | [Energy-Latency Attacks: A New Adversarial Threat to Deep Learning](https://arxiv.org/abs/2503.04963) |
| 6 | 2025-05 | [$PD^3F$: A Pluggable and Dynamic DoS-Defense Framework Against Resource Consumption Attacks Targeting Large Language Models](https://arxiv.org/abs/2505.18680) |
| 6 | 2025-03 | [Unnatural Languages Are Not Bugs but Features for LLMs](https://arxiv.org/abs/2503.01926) |
| 6 | 2025-06 | [BehaviorBox: Automated Discovery of Fine-Grained Performance Differences Between Language Models](https://arxiv.org/abs/2506.02204) |

## Other matches (423 papers)

| score | date | paper |
|---:|---|---|
| 6 | 2026-01 | [SAFE-QAQ: End-to-End Slow-Thinking Audio-Text Fraud Detection via Reinforcement Learning](https://arxiv.org/abs/2601.01392) |
| 6 | 2026-05 | [ESPO: Early-Stopping Proximal Policy Optimization](https://arxiv.org/abs/2605.29860) |
| 6 | 2026-08 | [CARVE: Verified Expansion for Variable-Length Generation in Diffusion Language Models](https://arxiv.org/abs/2608.30922) |
| 6 | 2026-03 | [Beyond Masks: Efficient, Flexible Diffusion Language Models via Deletion-Insertion Processes](https://arxiv.org/abs/2603.23507) |
| 6 | 2026-06 | [Improved Large Language Diffusion Models](https://arxiv.org/abs/2606.25331) |
| 6 | 2025-10 | [Retracing the Past: LLMs Emit Training Data When They Get Lost](https://arxiv.org/abs/2511.05518) |
| 5 | 2023-11 | [Scalable Extraction of Training Data from (Production) Language Models](https://arxiv.org/abs/2311.17035) |
| 3 | 2026-10 | [SAREO-FM: Decoupled Semantic Supervision for SAR-EO Foundation Models](https://arxiv.org/abs/2610.09317) |
| 3 | 2026-06 | [5ting at SemEval-2026 Task 8: Strong End-to-End Multi-Turn RAG via LLM-Based Reranking and Faithfulness Control](https://arxiv.org/abs/2606.28737) |
| 3 | 2026-07 | [DischargeBench: Pre-Deployment Evaluation of LLM Discharge Educators through Persona-Grounded Patient Simulation](https://arxiv.org/abs/2609.20827) |
| 3 | 2026-06 | [Evaluating Language Models in Realistic Conversational Contexts](https://arxiv.org/abs/2608.26131) |
| 3 | 2026-07 | [ReflectWorld-MM: An Entity-Oriented Multimodal Memory System for Open-Ended Video Streams](https://arxiv.org/abs/2607.09759) |
| 3 | 2026-09 | [RAG-Safety-Bench: Reliable Evaluation of Retrieval-Augmented LLM Safety](https://arxiv.org/abs/2609.11758) |
| 3 | 2026-10 | [TabMosaic: Unified In-Context Diffusion for Tabular Generative Tasks](https://arxiv.org/abs/2610.15699) |
| 3 | 2026-06 | [Shopping Reasoning Bench: An Expert-Authored Benchmark for Multi-Turn Conversational Shopping Assistants](https://arxiv.org/abs/2606.12608) |
| 3 | 2026-05 | [When LLMs Stop Following Steps: A Diagnostic Study of Procedural Execution in Language Models](https://arxiv.org/abs/2605.00817) |
| 3 | 2026-09 | [Ask Before You Optimize: Dynamic Pre-Formulation Clarification for Interactive Optimization](https://arxiv.org/abs/2609.05258) |
| 3 | 2026-10 | [CLIMB: Confidence-Guided Complementary Evidence for Multimodal Retrieval-Augmented Generation](https://arxiv.org/abs/2610.03421) |
| 3 | 2026-05 | [Wasserstein Equilibrium Decoding for Reliable Medical Visual Question Answering](https://arxiv.org/abs/2605.18313) |
| 3 | 2026-08 | [Contextual Value Alignment via Multilayer Combinatorial Fusion](https://arxiv.org/abs/2608.07642) |
| 3 | 2026-02 | [Just on Time: Token-Level Early Stopping for Diffusion Language Models](https://arxiv.org/abs/2602.11133) |
| 3 | 2026-09 | [Language-model groups overstate consensus when replaying human deliberation on a reasoning task](https://arxiv.org/abs/2609.20543) |
| 3 | 2026-08 | [Training-Free Inference-Time Self-Reflection and Cost-Bounded Early Stopping for Large Language Models](https://arxiv.org/abs/2608.18884) |
| 3 | 2026-09 | [ELF-REG: Scaling Continuous Diffusion Language Models to Reasoning Tasks](https://arxiv.org/abs/2609.29102) |
| 3 | 2026-04 | [Self-Consistency from Only Two Samples: CoT-PoT Ensembling for Efficient LLM Reasoning](https://arxiv.org/abs/2604.17433) |
| 3 | 2026-03 | [Graph of States: Solving Abductive Tasks with Large Language Models](https://arxiv.org/abs/2603.21250) |
| 3 | 2026-07 | [BVS: Bayesian Visual Search with Multimodal Large Language Model for Fine-grained Perception](https://arxiv.org/abs/2607.03184) |
| 3 | 2026-10 | [ECMR: Evidence-Aware Deliberation Control for Multi-Agent LLM Reasoning](https://arxiv.org/abs/2610.17869) |
| 3 | 2026-09 | [Beyond Truncation: Rethinking LLM Decoding as Ensemble Pruning](https://arxiv.org/abs/2609.18723) |
| 3 | 2026-03 | [Parallel Test-Time Scaling with Multi-Sequence Verifiers](https://arxiv.org/abs/2603.03417) |
| 3 | 2026-01 | [Lil: Less is Less When Applying Post-Training Sparse-Attention Algorithms in Long-Decode Stage](https://arxiv.org/abs/2601.03043) |
| 3 | 2026-06 | [ZAS-SQL: Distilling Rules from Failures for Zero-Shot Text-to-SQL](https://arxiv.org/abs/2606.08245) |
| 3 | 2026-02 | [Biases in the Blind Spot: Detecting What LLMs Fail to Mention](https://arxiv.org/abs/2602.10117) |
| 3 | 2026-05 | [Probabilistic Tiny Recursive Model](https://arxiv.org/abs/2605.19943) |
| 3 | 2026-05 | [Routing Without Training: Controllable-Ratio LLM Offloading via Reliability Gating](https://arxiv.org/abs/2607.20481) |
| 3 | 2026-07 | [RAGuard: A Layered Defense Framework for Retrieval-Augmented Generation Systems Against Data Poisoning](https://arxiv.org/abs/2607.26339) |
| 3 | 2026-02 | [On Data Engineering for Scaling LLM Terminal Capabilities](https://arxiv.org/abs/2602.21193) |
| 3 | 2026-06 | [TUA-Bench: A Benchmark for General-Purpose Terminal-Use Agents](https://arxiv.org/abs/2606.28480) |
| 3 | 2026-06 | [Tmax: A simple recipe for terminal agents](https://arxiv.org/abs/2606.23321) |
| 3 | 2026-10 | [TPPO: Tracking-Value PPO For Language Model Reasoning](https://arxiv.org/abs/2610.16794) |

