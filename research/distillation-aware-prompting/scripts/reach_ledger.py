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


def success_rate(gen, judge, intent, prompt, seeds) -> float:
    imgs = gen.generate_batched([prompt] * len(seeds), seeds)
    return float(np.mean([s["success"] for s in score_intent(judge, imgs, intent)]))


def faithful(checker, intent, prompt) -> bool:
    return prompt == intent.prompt or checker is None or not attribute_injection(checker, intent.prompt, [prompt])[0]


def ledger_row(gen, intent, args, search_judge, eval_judge, llm, checker) -> dict:
    fresh = list(range(70_000, 70_000 + args.fresh_seeds))
    seeds = list(range(args.n_seeds))
    imgs = gen.generate_batched([intent.prompt] * len(seeds), seeds)
    ok = [s["success"] for s in score_intent(eval_judge, imgs, intent)]
    rate_orig = float(np.mean(ok))
    row = {"rate_original": rate_orig, "reseed_any": bool(any(ok))}
    if rate_orig >= args.reliable:
        return {**row, "rung": "original"}
    # Reword-K: K wordings, one seed each, selected by the search judge, verified on fresh seeds
    wordings = reword_k(llm, intent.prompt, args.k)
    cand = gen.generate(wordings, [0] * len(wordings))
    sc = score_intent(search_judge, cand, intent)
    best = max(range(len(wordings)), key=lambda i: (sc[i]["success"], sc[i]["soft"]))
    rate_rw = success_rate(gen, eval_judge, intent, wordings[best], fresh) if faithful(checker, intent, wordings[best]) else 0.0
    row.update({"reword_prompt": wordings[best], "rate_reword": rate_rw})
    if rate_rw >= args.reliable:
        return {**row, "rung": "reword"}
    # distillation-aware evolution: wordings over seeds, one seed per candidate, Reword-K initialisation
    cfg = EvolveConfig(budget_nfe=args.evolve_images * gen.spec.nfe_per_image, seeds=(0,), init_prompts=tuple(wordings),
                       target_successes=1)
    res = evolve(intent, gen, search_judge, llm, cfg)
    pick = res.best.prompt
    rate_ev = success_rate(gen, eval_judge, intent, pick, fresh) if faithful(checker, intent, pick) else 0.0
    row.update({"evolve_prompt": pick, "rate_evolve": rate_ev, "evolve_candidates": len(res.history)})
    if rate_ev >= args.reliable:
        return {**row, "rung": "evolve"}
    return {**row, "rung": "reseed_only" if row["reseed_any"] else "lost"}


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
    ap.add_argument("--reliable", type=float, default=0.5)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--evolve-images", type=int, default=32)
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
        for idx, it in enumerate(reachable):
            r = ledger_row(gen, it, args, search_judge, eval_judge, llm, checker)
            rows.append({"idx": idx, "tag": it.tag, "prompt": it.prompt, **r})
        with open(out / f"ledger_{spec.name}.jsonl", "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in rows)
        counts = {rung: sum(r["rung"] == rung for r in rows) for rung in RUNGS}
        summary[spec.name] = {"role": spec.role, "objective": spec.objective, "n": len(rows),
                              "share": {k: v / max(len(rows), 1) for k, v in counts.items()}}
        print(spec.name, " ".join(f"{k}={v / max(len(rows), 1):.2f}" for k, v in counts.items()))
    (out / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
