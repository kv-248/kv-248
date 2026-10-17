"""Compute-matched test-time search baselines on a single intent.

All methods return the image selected by the SEARCH judge plus the NFEs spent; the
caller re-scores the selected image with held-out EVALUATION judges.
  * noise_bon   : N seeds, original prompt                     (noise-space search)
  * prompt_bon  : N meaning-preserving paraphrases, fixed seed  (prompt-space search, no feedback)
  * dape        : reflective evolution (see evolve.py)          (prompt-space search with feedback)
  * teacher     : the teacher model, original prompt, 1..N seeds
"""

from __future__ import annotations

from .evolve import EvolveConfig, evolve
from .judges import score_intent
from .questions import Intent


def _select(prompts, seeds, images, scores, nfe):
    i = max(range(len(scores)), key=lambda j: (scores[j]["success"], scores[j]["soft"]))
    return {"prompt": prompts[i], "seed": seeds[i], "image": images[i], "search_score": scores[i],
            "nfe": nfe, "any_success": any(s["success"] for s in scores), "n_candidates": len(scores)}


def noise_bon(intent: Intent, generator, judge, n: int, seed0: int = 0) -> dict:
    start = generator.nfe
    seeds = list(range(seed0, seed0 + n))
    prompts = [intent.prompt] * n
    images = generator.generate_batched(prompts, seeds)
    return _select(prompts, seeds, images, score_intent(judge, images, intent), generator.nfe - start)


def prompt_bon(intent: Intent, generator, judge, variants: list[str], seed: int = 0) -> dict:
    start = generator.nfe
    prompts = [intent.prompt] + [v for v in variants if v != intent.prompt]
    seeds = [seed] * len(prompts)
    images = generator.generate_batched(prompts, seeds)
    return _select(prompts, seeds, images, score_intent(judge, images, intent), generator.nfe - start)


def dape(intent: Intent, generator, judge, llm, budget_nfe: int, **cfg_kw) -> dict:
    res = evolve(intent, generator, judge, llm, EvolveConfig(budget_nfe=budget_nfe, keep_images=True, **cfg_kw))
    best = res.best
    i = max(range(len(best.scores)), key=lambda j: (best.scores[j]["success"], best.scores[j]["soft"]))
    return {"prompt": best.prompt, "seed": best.seeds[i], "image": best.images[i], "search_score": best.scores[i],
            "nfe": res.nfe_used, "any_success": res.solved, "n_candidates": len(res.history),
            "llm_usage": res.llm_usage, "trace": [(c.op, c.prompt, c.fitness) for c in res.history]}


def budget_to_n(budget_nfe: int, nfe_per_image: int) -> int:
    return max(1, budget_nfe // nfe_per_image)
