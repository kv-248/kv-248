"""Distillation-aware prompt evolution (DAPE), test-time version.

Student-in-the-loop reflective evolution over prompt rewrites:
  * fitness is the checklist of the ORIGINAL intent, scored by the search judge on
    images from the distilled student (cheap: steps * seeds NFEs per candidate);
  * a candidate is evaluated on a small fixed set of seeds (common random numbers);
    because mode-seeking students barely vary with the seed, one seed is usually enough;
  * mutation is reflective: the LLM sees which checklist items failed (plus a short card
    describing the student) and proposes targeted rewrites; optional crossover;
  * evolution stops as soon as a candidate satisfies the checklist (compute-adaptive), or
    when the NFE budget is spent.
  * optionally, the teacher is a free reference: given embeddings of a few teacher samples for
    the ORIGINAL prompt, a candidate also earns `ref_weight * precision`, its image's max cosine
    similarity to the teacher set (keeps the student inside the teacher's support, a guard
    against judge hacking that needs no extra reward model).
The full history is kept; `coverage_subset` then picks the K successful prompts whose images
best cover the teacher's samples (facility location), i.e. a prompt mixture that restores the
diversity a mode-seeking student lost.
"""

from __future__ import annotations

import random
import time
from collections import Counter
from dataclasses import dataclass, field

from .judges import score_intent
from .questions import Intent
from .rewrite import DEFAULT_MODEL_CARD, crossover, reflect_mutate, rule_mutations


@dataclass
class Candidate:
    prompt: str
    op: str
    parent: int | None
    seeds: list[int]
    scores: list[dict] = field(default_factory=list)
    images: list = field(default_factory=list, repr=False)
    emb: object = field(default=None, repr=False)  # mean image embedding over seeds
    precision: float = 0.0  # max cosine similarity to the teacher reference set
    ref_weight: float = 0.0
    seconds: float = 0.0  # cumulative wall-clock of the search (generation + judge + LLM) when evaluated

    @property
    def success_rate(self) -> float:
        return sum(s["success"] for s in self.scores) / max(len(self.scores), 1)

    @property
    def soft(self) -> float:
        return sum(s["soft"] for s in self.scores) / max(len(self.scores), 1)

    @property
    def fitness(self) -> float:
        return self.success_rate + self.soft + self.ref_weight * self.precision

    def failed(self) -> list[str]:
        c = Counter(q for s in self.scores for q in s["failed"])
        return [q for q, _ in c.most_common()]


@dataclass
class EvolveConfig:
    budget_nfe: int = 120
    seeds: tuple[int, ...] = (0,)
    pop_size: int = 3
    children_per_parent: int = 2
    crossover_prob: float = 0.25
    early_stop: bool = True
    model_card: str | None = None  # None -> DEFAULT_MODEL_CARD filled from the variant spec
    keep_images: bool = False
    rng_seed: int = 0
    ref_weight: float = 0.0  # weight of teacher-reference precision in the fitness
    init_prompts: tuple[str, ...] = ()  # e.g. a Reword-K set, evaluated right after the original
    target_successes: int = 1  # early stop once this many candidates satisfy the checklist


@dataclass
class EvolveResult:
    best: Candidate
    history: list[Candidate]
    nfe_used: int
    solved: bool
    llm_usage: dict

    def successes(self) -> list[Candidate]:
        return [c for c in self.history if c.success_rate == 1.0]


def _unit(x):
    import numpy as np

    x = np.asarray(x, dtype=float)
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def evolve(intent: Intent, generator, judge, llm=None, cfg: EvolveConfig | None = None,
           embed_fn=None, teacher_embs=None) -> EvolveResult:
    """embed_fn(images) -> [n, d] and teacher_embs [m, d] enable the teacher-referenced terms."""
    cfg = cfg or EvolveConfig()
    ref = _unit(teacher_embs) if teacher_embs is not None else None
    rng = random.Random(cfg.rng_seed)
    spec = generator.spec
    card = cfg.model_card or DEFAULT_MODEL_CARD.format(steps=spec.steps, objective=spec.objective or "distilled")
    cost = spec.nfe_per_image * len(cfg.seeds)
    start = generator.nfe
    t0 = time.perf_counter()
    history: list[Candidate] = []
    seen: set[str] = set()

    def budget_left() -> bool:
        return generator.nfe - start + cost <= cfg.budget_nfe

    def evaluate(prompt: str, op: str, parent: int | None) -> Candidate:
        seeds = list(cfg.seeds)
        images = generator.generate([prompt] * len(seeds), seeds)
        cand = Candidate(prompt, op, parent, seeds, score_intent(judge, images, intent))
        if embed_fn is not None:
            cand.emb = _unit(_unit(embed_fn(images)).mean(0))
            if ref is not None:
                cand.precision = float((ref @ cand.emb).max())
                cand.ref_weight = cfg.ref_weight
        if cfg.keep_images:
            cand.images = images
        cand.seconds = time.perf_counter() - t0
        history.append(cand)
        seen.add(prompt)
        return cand

    def result(solved: bool) -> EvolveResult:
        best = max(history, key=lambda c: c.fitness)
        usage = llm.usage() if llm is not None and hasattr(llm, "usage") else {}
        return EvolveResult(best, history, generator.nfe - start, solved, usage)

    def done() -> bool:
        return cfg.early_stop and sum(c.success_rate == 1.0 for c in history) >= cfg.target_successes

    evaluate(intent.prompt, "original", None)
    for prompt in cfg.init_prompts:
        if done() or not budget_left():
            break
        if prompt not in seen:
            evaluate(prompt, "init", 0)
    if done():
        return result(True)

    while budget_left():
        ranked = sorted(range(len(history)), key=lambda i: history[i].fitness, reverse=True)
        parents = ranked[: cfg.pop_size]
        children: list[tuple[str, str, int]] = []
        for pi in parents:
            p = history[pi]
            passed = [q for q in intent.questions if q not in p.failed()]
            if llm is not None:
                outs = reflect_mutate(llm, intent.prompt, p.prompt, p.failed(), card, cfg.children_per_parent, passed)
                children += [(o, "reflect", pi) for o in outs]
            else:
                children += [(o, "rule", pi) for o in rule_mutations(p.prompt, p.failed())[: cfg.children_per_parent]]
        if llm is not None and len(parents) >= 2 and rng.random() < cfg.crossover_prob:
            a, b = parents[0], parents[1]
            children += [(o, "crossover", a) for o in crossover(llm, intent.prompt, history[a].prompt, history[b].prompt)]
        children = [c for c in children if c[0] and c[0] not in seen]
        if not children:
            break
        for prompt, op, pi in children:
            if not budget_left():
                break
            if prompt in seen:
                continue
            evaluate(prompt, op, pi)
            if done():
                return result(True)
    return result(max(c.success_rate for c in history) == 1.0)


def diverse_subset(cands: list[Candidate], embeddings, k: int) -> list[int]:
    """Greedy max-min (farthest point) selection of k candidates by image embedding;
    used to turn the evolution history into a diverse prompt population."""
    import numpy as np

    if not cands:
        return []
    e = np.asarray(embeddings, dtype=float)
    e = e / np.linalg.norm(e, axis=-1, keepdims=True)
    chosen = [int(np.argmax([c.fitness for c in cands]))]
    while len(chosen) < min(k, len(cands)):
        d = 1 - e @ e[chosen].T
        d[chosen] = -1
        chosen.append(int(np.argmax(d.min(axis=1))))
    return chosen


def coverage_subset(cands: list[Candidate], teacher_embs, k: int) -> list[int]:
    """Greedy facility location: choose k candidates maximising
    sum_t max_{c in S} cos(teacher_t, c) -- how well the chosen prompts' images cover the
    teacher's sample set. Monotone submodular, so greedy is a (1 - 1/e) approximation."""
    import numpy as np

    if not cands:
        return []
    T = _unit(teacher_embs)
    sim = T @ _unit(np.stack([c.emb for c in cands])).T  # [m, n]
    chosen: list[int] = []
    best = np.full(len(T), -np.inf)
    for _ in range(min(k, len(cands))):
        gains = np.maximum(sim, best[:, None]).sum(0)
        gains[chosen] = -np.inf
        j = int(np.argmax(gains))
        chosen.append(j)
        best = np.maximum(best, sim[:, j])
    return chosen


def select_population(res: EvolveResult, k: int) -> list[Candidate]:
    """K output wordings from an evolution run: mutually distinct successful candidates (farthest
    point on their student-image embeddings, no teacher needed), topped up by fitness."""
    succ = res.successes()
    chosen: list[Candidate] = []
    if succ and all(c.emb is not None for c in succ):
        chosen = [succ[i] for i in diverse_subset(succ, [c.emb for c in succ], k)]
    else:
        chosen = sorted(succ, key=lambda c: c.fitness, reverse=True)[:k]
    rest = [c for c in sorted(res.history, key=lambda c: c.fitness, reverse=True) if c not in chosen]
    return (chosen + rest)[:k]
