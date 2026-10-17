"""Main figure -- the reach ledger: is what a distilled student "lost" erased, or re-addressed?

Teacher-reachable intents are those the teacher solves at least once over `--ref-seeds` held-out
seeds (evaluation judge). For every model (the teacher itself as reference, then each student) each
such intent gets the first category that applies:
  original    : the original wording succeeds on >= `--reliable` of its seeds
  reword      : Reword-K's search-judge-selected wording is reliable on fresh seeds
  evolve      : prompt evolution (initialised with Reword-K, budget `--evolve-images` renders, one seed
                per candidate) finds a wording that is reliable on fresh seeds
  reseed_only : no reliable wording found, but some of `--n-seeds` seeds of the original wording
                succeed (a lucky image, not a working prompt)
  lost        : none of the above within budget (a lower bound on re-addressable reach)
Selected wordings are re-rendered on `--fresh-seeds` NEW seeds and scored by held-out evaluation
judges (winner's-curse correction); a selected wording flagged by the checker LLM for adding content
does not count. Categories are cumulative left to right, so the bar shows what each lever adds and
how much of the teacher's reach re-seeding can only touch by luck.

  python scripts/reach_ledger.py --family sdxl --students dmd2-sdxl-4 sdxl-lightning-4 lcm-sdxl-4 \
     --llm openai:Qwen/Qwen3-4B-Instruct-2507@http://localhost:8001/v1 \
     --checker-llm openai:google/gemma-3-27b-it@http://localhost:8002/v1 \
     --search-judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 \
     --eval-judge openai:google/gemma-3-27b-it@http://localhost:8002/v1 --limit 300 --out runs/ledger_sdxl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dap import make_judge, make_llm  # noqa: E402
from dap.evolve import EvolveConfig, evolve  # noqa: E402
from dap.generation import CONFIG_PATH, Generator, load_families  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.questions import load_geneval  # noqa: E402
from dap.reword import attribute_injection, reword_k  # noqa: E402

RUNGS = ["original", "reword", "evolve", "reseed_only", "lost"]
FRESH_A, FRESH_B = 70_000, 80_000  # two disjoint fresh-seed sets: verification, and the placebo re-test


def success_rate(gen, judge, intent, prompt, seeds) -> float:
    imgs = gen.generate_batched([prompt] * len(seeds), seeds)
    return float(np.mean([s["success"] for s in score_intent(judge, imgs, intent)]))


def faithful(checker, intent, prompt) -> bool:
    return prompt == intent.prompt or checker is None or not attribute_injection(checker, intent.prompt, [prompt])[0]


def ledger_row(gen, intent, args, search_judge, eval_judge, llm, checker, cand_seeds=(0,), verify_judge=None) -> dict:
    fresh = list(range(FRESH_A, FRESH_A + args.fresh_seeds))
    retest = list(range(FRESH_B, FRESH_B + args.fresh_seeds))
    seeds = list(range(args.n_seeds))
    imgs = gen.generate_batched([intent.prompt] * len(seeds), seeds)
    ok = [s["success"] for s in score_intent(eval_judge, imgs, intent)]
    if verify_judge is not None:  # a lucky image must also pass a second judge (judge false positives)
        ok2 = [s["success"] for s in score_intent(verify_judge, imgs, intent)]
        ok = [a and b for a, b in zip(ok, ok2)]
    # the original wording faces the SAME fresh-seed test as rewordings (equal tests), plus a placebo
    # re-test on a second fresh set: the share of intents that "pass" by re-testing alone is the noise floor
    rate_orig = success_rate(gen, eval_judge, intent, intent.prompt, fresh)
    row = {"rate_original": rate_orig, "rate_original_seeds": float(np.mean(ok)), "reseed_any": bool(any(ok)),
           "reseed_hits": int(sum(ok)), "n_seeds": len(ok), "images_used": len(seeds) + len(fresh)}
    if rate_orig >= args.reliable:
        return {**row, "rung": "original"}
    row["rate_placebo"] = success_rate(gen, eval_judge, intent, intent.prompt, retest)
    row["images_used"] += len(retest)
    # Reword-K: K wordings, a fresh seed per wording (cand_seeds offset), selected by the search judge,
    # verified on fresh seeds
    wordings = reword_k(llm, intent.prompt, args.k)
    seeds_c = list(cand_seeds)
    imgs_c = gen.generate_batched([w for w in wordings for _ in seeds_c],
                                  [s + 1000 * i for i in range(len(wordings)) for s in seeds_c])
    sc_all = score_intent(search_judge, imgs_c, intent)
    per = [(sc_all[i * len(seeds_c):(i + 1) * len(seeds_c)], imgs_c[i * len(seeds_c):(i + 1) * len(seeds_c)])
           for i in range(len(wordings))]
    key = [(np.mean([s["success"] for s in sc]), np.mean([s["soft"] for s in sc])) for sc, _ in per]
    best = max(range(len(wordings)), key=lambda i: key[i])
    rate_rw = success_rate(gen, eval_judge, intent, wordings[best], fresh) if faithful(checker, intent, wordings[best]) else 0.0
    row.update({"reword_prompt": wordings[best], "rate_reword": rate_rw})
    row["images_used"] += len(imgs_c) + len(fresh)
    if rate_rw >= args.reliable:
        return {**row, "rung": "reword"}
    # distillation-aware evolution: wordings over seeds, one seed per candidate, Reword-K initialisation
    # evolution continues from the already-scored Reword-K set (no re-rendering), never returns the
    # wording that just failed fresh-seed verification, and confirms a winner on extra seeds first
    cfg = EvolveConfig(budget_nfe=args.evolve_images * gen.spec.nfe_per_image, seeds=tuple(cand_seeds),
                       prescored=tuple((w, sc, ims) for w, (sc, ims) in zip(wordings, per)),
                       exclude=(wordings[best],), confirm_seeds=(101, 102), target_successes=1)
    res = evolve(intent, gen, search_judge, llm, cfg)
    pick = res.best.prompt
    rate_ev = success_rate(gen, eval_judge, intent, pick, fresh) if faithful(checker, intent, pick) else 0.0
    row.update({"evolve_prompt": pick, "rate_evolve": rate_ev, "evolve_candidates": len(res.history),
                "evolve_new_wordings": sum(c.op not in ("original", "init") for c in res.history)})
    row["images_used"] += res.nfe_used // gen.spec.nfe_per_image + len(fresh)
    if rate_ev >= args.reliable:
        return {**row, "rung": "evolve"}
    return {**row, "rung": "reseed_only" if row["reseed_any"] else "lost"}


def categorise(rows: list[dict], tau: float) -> dict:
    """Post-hoc ledger at threshold tau from the stored fresh-seed rates (valid for tau <= --reliable)."""
    counts = dict.fromkeys(RUNGS, 0)
    for r in rows:
        if r["rate_original"] >= tau:
            counts["original"] += 1
        elif r.get("rate_reword", 0.0) >= tau:
            counts["reword"] += 1
        elif r.get("rate_evolve", 0.0) >= tau:
            counts["evolve"] += 1
        elif r["reseed_any"]:
            counts["reseed_only"] += 1
        else:
            counts["lost"] += 1
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--students", nargs="*")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--llm", required=True)
    ap.add_argument("--checker-llm")
    ap.add_argument("--search-judge", required=True)
    ap.add_argument("--eval-judge", required=True)
    ap.add_argument("--ref-seeds", type=int, default=16, help="held-out teacher seeds defining reachability")
    ap.add_argument("--n-seeds", type=int, default=16)
    ap.add_argument("--fresh-seeds", type=int, default=8)
    ap.add_argument("--reliable", type=float, default=0.75,
                    help="run the rewording rungs for intents below this rate (= the highest reported threshold)")
    ap.add_argument("--thresholds", nargs="+", type=float, default=[0.25, 0.5, 0.75])
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--evolve-images", type=int, default=32)
    ap.add_argument("--verify-judge", help="second evaluation judge a lucky image must also pass (e.g. geneval)")
    ap.add_argument("--teacher-candidate-seeds", type=int, default=4,
                    help="seeds per candidate for the TEACHER (allocation rule: students use 1); 1 = same-rule control")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tags)
    llm, checker = make_llm(args.llm), make_llm(args.checker_llm) if args.checker_llm else None
    search_judge = make_judge(args.search_judge, device=args.device)
    eval_judge = make_judge(args.eval_judge, device=args.device)
    verify_judge = make_judge(args.verify_judge, device=args.device) if args.verify_judge else None
    variants = load_families(args.config)[args.family]
    teacher_spec = next(v for v in variants if v.role == "teacher")
    students = [v for v in variants if v.role == "student" and (not args.students or v.name in args.students)]

    teacher = Generator(teacher_spec, args.device, args.dtype).load()
    ref = list(range(90_000, 90_000 + args.ref_seeds))
    reachable = [it for it in intents if success_rate(teacher, eval_judge, it, it.prompt, ref) > 0]
    print(f"{len(reachable)}/{len(intents)} intents are teacher-reachable")

    summary = {}
    for spec in [teacher_spec] + students:
        gen = teacher if spec is teacher_spec else Generator(spec, args.device, args.dtype).load()
        rows = []
        cand_seeds = tuple(range(args.teacher_candidate_seeds)) if spec is teacher_spec else (0,)
        for idx, it in enumerate(reachable):
            r = ledger_row(gen, it, args, search_judge, eval_judge, llm, checker, cand_seeds, verify_judge)
            rows.append({"idx": idx, "tag": it.tag, "prompt": it.prompt, **r})
        with open(out / f"ledger_{spec.name}.jsonl", "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in rows)
        counts = {rung: sum(r["rung"] == rung for r in rows) for rung in RUNGS}
        n = max(len(rows), 1)
        recovered = [r for r in rows if r["rung"] in ("reword", "evolve")]
        summary[spec.name] = {
            "role": spec.role, "objective": spec.objective, "n": len(rows),
            "share": {k: v / n for k, v in counts.items()},
            "share_by_threshold": {str(tau): {k: v / n for k, v in categorise(rows, tau).items()} for tau in args.thresholds},
            # of the intents rewording made reliable, how many could a lucky seed also reach? (re-found vs re-addressed)
            "recovered_seed_reachable": (sum(r["reseed_any"] for r in recovered) / len(recovered)) if recovered else None,
            # noise floor: intents whose ORIGINAL wording passes a second fresh test (placebo "rewording")
            "placebo_share": {str(tau): sum(r.get("rate_placebo", 0.0) >= tau for r in rows if r["rate_original"] < tau) / n
                              for tau in args.thresholds},
            # lucky reach at an equal image budget: P(any success) over as many seeds as rewording used (Jeffreys)
            "reseed_equal_budget": float(np.mean([1 - (1 - (r["reseed_hits"] + 0.5) / (r["n_seeds"] + 1)) ** r["images_used"]
                                                  for r in rows if r["rung"] not in ("original",)] or [0.0])),
            "evolve_zero_mutation_share": (sum(r.get("evolve_new_wordings", 1) == 0 for r in rows if "evolve_prompt" in r)
                                           / max(sum("evolve_prompt" in r for r in rows), 1)),
        }
        print(spec.name, " ".join(f"{k}={v / n:.2f}" for k, v in counts.items()))
    (out / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
