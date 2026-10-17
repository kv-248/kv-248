"""E3 -- Where should the compute saved by distillation be spent?

Anytime curves (quality vs cost) on GenEval intents for:
  noise          : student, original prompt, best-of-N over seeds
  prompt         : student, best-of-N over paraphrases, one SHARED seed (isolates the wording axis)
  prompt_fresh   : student, best-of-N over paraphrases, a fresh seed each (wording + seed)
  reword         : student, best-of-N over Reword-K wordings (jointly diverse, in chunks of 8), fresh seeds
  dape           : student, distillation-aware prompt evolution (one seed per candidate)
  teacher        : teacher, original prompt, best-of-N over seeds
  teacher_prompt : teacher, best-of-N over paraphrases, a fresh seed each
`--teacher-cfg w` runs the teacher at guidance w (the CFG-matched control). Every arm uses the same
selector (the search judge). Selected wordings are re-rendered on `--fresh-seeds` new seeds and
re-scored by the evaluation judges (winner's-curse correction): `fresh_rate` is the deployable
quantity (does the chosen wording work reliably?), `eval.success` is best-of-N coverage.
Each method runs once at the largest budget; the selection at a smaller budget B is the
search-judge best among candidates whose cumulative cost <= B. Cost is either generator NFE
(`--axis nfe`) or end-to-end wall-clock seconds including judge and LLM calls (`--axis seconds`,
the primary axis: LLM and judge time are not free). Paraphrases for the `prompt` arm are
generated online when `--llm` is given, so their cost is counted too. Selected images are
re-scored by held-out evaluation judges (never the search judge).

  python scripts/search_scaling.py --family sdxl --student dmd2-sdxl-4 --budgets 4 16 64 256 \
     --search-judge hf:Qwen/Qwen2.5-VL-7B-Instruct --eval-judges hf:OpenGVLab/InternVL3-8B-hf \
     --llm openai:Qwen/Qwen3-8B@http://localhost:8001/v1 --paraphrases runs/paraphrases.json --out runs/e3
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dap import make_judge, make_llm  # noqa: E402
from dap.evolve import EvolveConfig, evolve  # noqa: E402
from dap.generation import CONFIG_PATH, Generator, get_variant, teacher_of  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.questions import load_geneval  # noqa: E402
from dap.reword import reword_k  # noqa: E402
from dap.rewrite import paraphrase  # noqa: E402


def candidates_bon(gen, intent, judge, prompts, seeds, t_offset: float = 0.0):
    """Evaluate (prompt, seed) pairs one by one; return [((cum_nfe, cum_sec, n_images), key, image, prompt)].
    `t_offset` adds up-front cost (e.g. generating the paraphrases)."""
    out, start, t0 = [], gen.nfe, time.perf_counter()
    for n, (p, s) in enumerate(zip(prompts, seeds), 1):
        im = gen.generate([p], [s])[0]
        sc = score_intent(judge, [im], intent)[0]
        out.append(((gen.nfe - start, t_offset + time.perf_counter() - t0, n), (sc["success"], sc["soft"]), im, p))
    return out


def candidates_wordings(gen, intent, judge, n, seed, fresh_seeds, llm, cached, chunk: int = 8,
                        source: str = "paraphrase"):
    """Original wording + paraphrases (or Reword-K sets), generated lazily in chunks so the LLM cost
    is charged when it is incurred; seed shared (pure wording axis) or fresh per wording."""
    out, start, t0 = [], gen.nfe, time.perf_counter()
    pool = list(cached)
    wordings = [intent.prompt]
    for j in range(n):
        if j >= len(wordings):
            if not pool and llm is not None:
                pool = reword_k(llm, intent.prompt, chunk) if source == "reword" else paraphrase(llm, intent.prompt, n=chunk)
            if not pool:
                break
            wordings.append(pool.pop(0))
        s = seed + j if fresh_seeds else seed
        im = gen.generate([wordings[j]], [s])[0]
        sc = score_intent(judge, [im], intent)[0]
        out.append(((gen.nfe - start, time.perf_counter() - t0, j + 1), (sc["success"], sc["soft"]), im, wordings[j]))
    return out


def candidates_dape(gen, intent, judge, llm, budget, seed):
    start = gen.nfe
    res = evolve(intent, gen, judge, llm, EvolveConfig(budget_nfe=budget, seeds=(seed,), keep_images=True))
    per = gen.spec.nfe_per_image
    out = [(((k + 1) * per, c.seconds, k + 1), (c.scores[0]["success"], c.scores[0]["soft"]), c.images[0], c.prompt)
           for k, c in enumerate(res.history)]
    assert out[-1][0][0] == gen.nfe - start
    return out, res.llm_usage


def anytime(cands, budgets, axis: int = 0):
    """budget -> index of the search-judge best candidate affordable within that budget
    (axis 0: NFE, axis 1: wall-clock seconds, axis 2: number of images)."""
    sel = {}
    for b in budgets:
        affordable = [i for i, c in enumerate(cands) if c[0][axis] <= b]
        if affordable:
            sel[b] = max(affordable, key=lambda i: cands[i][1])
    return sel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--student", required=True)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--budgets", nargs="+", type=float, required=True, help="budgets on the chosen axis")
    ap.add_argument("--axis", choices=["nfe", "seconds", "images"], default="nfe",
                    help="images = equal sample count (the teacher gets as many images as the student)")
    ap.add_argument("--max-images", type=int, default=64,
                    help="seconds axis: student images per method (teacher gets the same NFE envelope)")
    ap.add_argument("--methods", nargs="+", default=["noise", "prompt", "dape", "teacher"])
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--paraphrases")
    ap.add_argument("--llm")
    ap.add_argument("--search-judge", default="mock")
    ap.add_argument("--eval-judges", nargs="+", default=["mock"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fresh-seeds", type=int, default=4, help="re-render each selected wording on this many new seeds")
    ap.add_argument("--teacher-cfg", type=float, help="teacher guidance scale (CFG-matched control)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tags)
    search_judge = make_judge(args.search_judge, device=args.device)
    eval_judges = [make_judge(j, device=args.device) for j in args.eval_judges]
    llm = make_llm(args.llm)
    paras = json.loads(Path(args.paraphrases).read_text()) if args.paraphrases else {}

    student = Generator(get_variant(args.student, args.config), args.device, args.dtype).load()
    teacher = None
    if {"teacher", "teacher_prompt"} & set(args.methods):
        tspec = teacher_of(args.family, args.config)
        if args.teacher_cfg is not None:
            tspec = dataclasses.replace(tspec, name=f"{tspec.name}-cfg{args.teacher_cfg:g}",
                                        guidance_scale=args.teacher_cfg, cfg=args.teacher_cfg > 1.0)
        teacher = Generator(tspec, args.device, args.dtype).load()
        if args.axis == "nfe":  # always report the teacher at its native single-sample cost as well
            args.budgets = sorted(set(args.budgets) | {teacher.spec.nfe_per_image})
    axis = {"nfe": 0, "seconds": 1, "images": 2}[args.axis]
    if args.axis == "nfe":
        args.budgets = [int(b) for b in args.budgets]
        bmax = max(args.budgets)
    elif args.axis == "images":
        args.budgets = [int(b) for b in args.budgets]
        args.max_images = max(args.budgets)
        bmax = args.max_images * student.spec.nfe_per_image
    else:
        bmax = args.max_images * student.spec.nfe_per_image  # NFE envelope; the clock decides the curve

    rows = []
    for idx, intent in enumerate(intents):
        per_method = {}
        n_s = max(1, bmax // student.spec.nfe_per_image)
        if "noise" in args.methods:
            seeds = list(range(args.seed, args.seed + n_s))
            per_method["noise"] = (candidates_bon(student, intent, search_judge, [intent.prompt] * n_s, seeds), {})
        cached = [] if llm is not None else paras.get(intent.prompt, [])  # online paraphrasing is costed
        for method, fresh, source in (("prompt", False, "paraphrase"), ("prompt_fresh", True, "paraphrase"),
                                      ("reword", True, "reword")):
            if method in args.methods:
                per_method[method] = (candidates_wordings(student, intent, search_judge, n_s, args.seed, fresh,
                                                          llm, [] if source == "reword" else cached, source=source), {})
        if "dape" in args.methods:
            per_method["dape"] = candidates_dape(student, intent, search_judge, llm, bmax, args.seed)
        if teacher is not None:
            # equal sample count on the images axis; otherwise the teacher gets the same compute envelope
            n_t = args.max_images if args.axis == "images" else max(1, bmax // teacher.spec.nfe_per_image)
            if "teacher" in args.methods:
                seeds = list(range(args.seed, args.seed + n_t))
                per_method["teacher"] = (candidates_bon(teacher, intent, search_judge, [intent.prompt] * n_t, seeds), {})
            if "teacher_prompt" in args.methods:
                per_method["teacher_prompt"] = (candidates_wordings(teacher, intent, search_judge, n_t, args.seed, True,
                                                                    llm, cached), {})

        intent_rows = []
        fresh = list(range(50_000, 50_000 + args.fresh_seeds))
        for method, (cands, usage) in per_method.items():
            gen = teacher if method.startswith("teacher") else student
            scored, fresh_rate = {}, {}
            for b, i in anytime(cands, args.budgets, axis).items():
                if i not in scored:
                    scored[i] = {j.name: score_intent(j, [cands[i][2]], intent)[0] for j in eval_judges}
                    if args.fresh_seeds:
                        ims = gen.generate([cands[i][3]] * len(fresh), fresh)
                        fresh_rate[i] = {j.name: float(np.mean([s["success"] for s in score_intent(j, ims, intent)]))
                                         for j in eval_judges}
                intent_rows.append({"idx": idx, "tag": intent.tag, "method": method, "budget": b,
                                    "nfe_used": cands[i][0][0], "seconds_used": round(cands[i][0][1], 3),
                                    "prompt": cands[i][3],
                                    "search_success": cands[i][1][0],
                                    "eval": {k: {"success": v["success"], "soft": round(v["soft"], 4),
                                                 "fresh_rate": fresh_rate.get(i, {}).get(k)}
                                             for k, v in scored[i].items()},
                                    "llm_usage": usage or None})
        with open(out / "records.jsonl", "a") as f:
            f.writelines(json.dumps(r) + "\n" for r in intent_rows)
        rows += intent_rows

    # summary: mean eval success per (method, budget) for each eval judge
    summary = {}
    for r in rows:
        for jn, v in r["eval"].items():
            cell = summary.setdefault(jn, {}).setdefault(r["method"], {}).setdefault(r["budget"], {"best": [], "fresh": []})
            cell["best"].append(v["success"])
            if v.get("fresh_rate") is not None:
                cell["fresh"].append(v["fresh_rate"])
    summary = {jn: {m: {b: {"best_of_n": float(np.mean(c["best"])),
                            "fresh_rate": float(np.mean(c["fresh"])) if c["fresh"] else None}
                        for b, c in sorted(bs.items())} for m, bs in ms.items()} for jn, ms in summary.items()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    for jn, ms in summary.items():
        print(f"[eval judge: {jn}]  budgets: {args.budgets}   (best-of-N / fresh-seed rate of the chosen wording)")
        for m, bs in ms.items():
            cells = [bs.get(b) for b in args.budgets]
            print(f"  {m:15s} " + " ".join(f"{c['best_of_n']:.2f}/{c['fresh_rate'] if c['fresh_rate'] is not None else float('nan'):.2f}"
                                           if c else "  -  " for c in cells))


if __name__ == "__main__":
    main()
