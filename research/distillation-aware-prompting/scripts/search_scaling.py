"""E3 -- Where should the compute saved by distillation be spent?

Anytime curves (quality vs NFE) on GenEval intents for:
  noise   : student, original prompt, best-of-N over seeds
  prompt  : student, best-of-N over cached paraphrases (one seed)
  dape    : student, reflective prompt evolution (one seed per candidate)
  teacher : teacher, original prompt, best-of-N over seeds
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
from dap.rewrite import paraphrase  # noqa: E402


def candidates_bon(gen, intent, judge, prompts, seeds, t_offset: float = 0.0):
    """Evaluate (prompt, seed) pairs one by one; return [((cum_nfe, cum_sec), key, image, prompt)].
    `t_offset` adds up-front cost (e.g. generating the paraphrases)."""
    out, start, t0 = [], gen.nfe, time.perf_counter()
    for p, s in zip(prompts, seeds):
        im = gen.generate([p], [s])[0]
        sc = score_intent(judge, [im], intent)[0]
        out.append(((gen.nfe - start, t_offset + time.perf_counter() - t0), (sc["success"], sc["soft"]), im, p))
    return out


def candidates_dape(gen, intent, judge, llm, budget, seed):
    start = gen.nfe
    res = evolve(intent, gen, judge, llm, EvolveConfig(budget_nfe=budget, seeds=(seed,), keep_images=True))
    per = gen.spec.nfe_per_image
    out = [(((k + 1) * per, c.seconds), (c.scores[0]["success"], c.scores[0]["soft"]), c.images[0], c.prompt)
           for k, c in enumerate(res.history)]
    assert out[-1][0][0] == gen.nfe - start
    return out, res.llm_usage


def anytime(cands, budgets, axis: int = 0):
    """budget -> index of the search-judge best candidate affordable within that budget
    (axis 0: NFE, axis 1: wall-clock seconds)."""
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
    ap.add_argument("--axis", choices=["nfe", "seconds"], default="nfe")
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
    if "teacher" in args.methods:
        teacher = Generator(teacher_of(args.family, args.config), args.device, args.dtype).load()
        if args.axis == "nfe":  # always report the teacher at its native single-sample cost as well
            args.budgets = sorted(set(args.budgets) | {teacher.spec.nfe_per_image})
    axis = 0 if args.axis == "nfe" else 1
    if args.axis == "nfe":
        args.budgets = [int(b) for b in args.budgets]
        bmax = max(args.budgets)
    else:
        bmax = args.max_images * student.spec.nfe_per_image  # NFE envelope; the clock decides the curve

    rows = []
    for idx, intent in enumerate(intents):
        per_method = {}
        n_s = max(1, bmax // student.spec.nfe_per_image)
        if "noise" in args.methods:
            seeds = list(range(args.seed, args.seed + n_s))
            per_method["noise"] = (candidates_bon(student, intent, search_judge, [intent.prompt] * n_s, seeds), {})
        if "prompt" in args.methods:
            t_para = 0.0
            if llm is not None:  # online paraphrasing: its LLM time is part of the method's cost
                t = time.perf_counter()
                paras[intent.prompt] = paraphrase(llm, intent.prompt, n=max(1, n_s - 1))
                t_para = time.perf_counter() - t
            ps = ([intent.prompt] + paras.get(intent.prompt, []))[:n_s]
            per_method["prompt"] = (candidates_bon(student, intent, search_judge, ps, [args.seed] * len(ps), t_para), {})
        if "dape" in args.methods:
            per_method["dape"] = candidates_dape(student, intent, search_judge, llm, bmax, args.seed)
        if teacher is not None:
            n_t = max(1, bmax // teacher.spec.nfe_per_image)
            seeds = list(range(args.seed, args.seed + n_t))
            per_method["teacher"] = (candidates_bon(teacher, intent, search_judge, [intent.prompt] * n_t, seeds), {})

        intent_rows = []
        for method, (cands, usage) in per_method.items():
            scored = {}
            for b, i in anytime(cands, args.budgets, axis).items():
                if i not in scored:
                    scored[i] = {j.name: score_intent(j, [cands[i][2]], intent)[0] for j in eval_judges}
                intent_rows.append({"idx": idx, "tag": intent.tag, "method": method, "budget": b,
                                    "nfe_used": cands[i][0][0], "seconds_used": round(cands[i][0][1], 3),
                                    "prompt": cands[i][3],
                                    "search_success": cands[i][1][0],
                                    "eval": {k: {"success": v["success"], "soft": round(v["soft"], 4)}
                                             for k, v in scored[i].items()},
                                    "llm_usage": usage or None})
        with open(out / "records.jsonl", "a") as f:
            f.writelines(json.dumps(r) + "\n" for r in intent_rows)
        rows += intent_rows

    # summary: mean eval success per (method, budget) for each eval judge
    summary = {}
    for r in rows:
        for jn, v in r["eval"].items():
            summary.setdefault(jn, {}).setdefault(r["method"], {}).setdefault(r["budget"], []).append(v["success"])
    summary = {jn: {m: {b: float(np.mean(v)) for b, v in sorted(bs.items())} for m, bs in ms.items()}
               for jn, ms in summary.items()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    for jn, ms in summary.items():
        print(f"[eval judge: {jn}]  budgets: {args.budgets}")
        for m, bs in ms.items():
            print(f"  {m:8s} " + " ".join(f"{bs.get(b, float('nan')):.3f}" for b in args.budgets))


if __name__ == "__main__":
    main()
