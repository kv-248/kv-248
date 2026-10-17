"""E3 -- K-image deployment comparison on a distilled student (Table 2 of the proposal).

For each intent every method returns K images. Latency is the real deployment cost of producing
them: LLM calls, generation, and the search judge only for methods that use one. Methods:
  seeds          : original prompt, K seeds                                  (i.i.d. baseline)
  seeds_eq       : equal-time seeds: as many extra seeds as Reword-K's LLM time buys, then K picked
                   by the search judge (needs --search-judge; runs after `reword`)
  pink           : original prompt, K seeds, pink-noise initial latents      (noise side, ~free)
  cads           : original prompt, K seeds, CADS condition annealing         (noise side, ~free)
  hybrid         : teacher denoises the first `--hybrid-switch` of the schedule, student finishes
  tags           : original prompt + K random composition tags                (no-LLM control)
  pe             : teacher-built prompt enhancer output (--pe-rewrites; add its cost via --pe-latency-s)
  expand         : K generic diverse LLM expansions (Prompt-Expansion-style control)
  para           : K random meaning-preserving paraphrases
  reword         : Reword-K, one joint call for K intent-preserving rewordings (proposed, zero feedback)
  reword_iid / reword_nocomp / reword_nobind / reword_plain : Reword-K template ablations
  evolve         : distillation-aware prompt evolution initialised with Reword-K, returning K distinct
                   successful wordings (needs --search-judge, never an evaluation judge)
  teacher        : the teacher, original prompt, K seeds                     (reference, own cost)
  teacher_reword : the teacher rendering Reword-K (the remedy should help students more)
Metrics: mean success and pass@K under held-out evaluation judges; Vendi and pairwise distance;
teacher coverage = k-NN coverage (Naeem et al. 2020) of the checklist-passing teacher samples by
the checklist-passing method images (>= 32 held-out teacher seeds, evaluation feature space);
attribute-injection rate (lenient and strict) judged by a checker LLM different from the rewriter.

  python scripts/remedy_eval.py --family sdxl --student dmd2-sdxl-4 --k 4 --limit 300 \
     --llm openai:Qwen/Qwen3-4B-Instruct-2507@http://localhost:8001/v1 \
     --checker-llm openai:google/gemma-3-27b-it@http://localhost:8002/v1 \
     --eval-judges openai:google/gemma-3-27b-it@http://localhost:8002/v1 \
     --search-judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 \
     --embedder openai/clip-vit-large-patch14 --pe-rewrites runs/pe_rewrites.json --out runs/e5_dmd2
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
from dap.embed import ImageEmbedder, pixel_embed  # noqa: E402
from dap.evolve import EvolveConfig, evolve, select_population  # noqa: E402
from dap.generation import CONFIG_PATH, Generator, get_variant, hybrid_teacher_first, teacher_of  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.metrics import knn_coverage, mean_pairwise_distance, teacher_coverage, vendi_score  # noqa: E402
from dap.questions import load_geneval  # noqa: E402
from dap.reword import attribute_injection, expand_k, reword_k, tag_k  # noqa: E402
from dap.rewrite import paraphrase  # noqa: E402

REWORD_VARIANTS = {
    "reword": {}, "reword_iid": {"joint": False}, "reword_nocomp": {"composition": False},
    "reword_nobind": {"binding": False}, "reword_plain": {"diverse": False, "composition": False, "binding": False},
}
LLM_REWRITES = {"expand", "para", "evolve", "teacher_reword", *REWORD_VARIANTS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--student", required=True)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--methods", nargs="+",
                    default=["seeds", "pink", "tags", "pe", "expand", "para", "reword", "seeds_eq", "teacher"])
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--n-ref", type=int, default=32, help="held-out teacher reference samples per intent")
    ap.add_argument("--coverage-k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--tags", nargs="*", dest="tag_filter")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--llm", help="rewriter LLM")
    ap.add_argument("--checker-llm", help="attribute-injection checker (should differ from --llm)")
    ap.add_argument("--pe-rewrites")
    ap.add_argument("--pe-latency-s", type=float, default=0.0, help="measured per-prompt cost of the official PE")
    ap.add_argument("--eval-judges", nargs="+", default=["mock"])
    ap.add_argument("--search-judge", help="judge for evolve / seeds_eq selection (never an evaluation judge)")
    ap.add_argument("--evolve-images", type=int, default=16, help="evolution budget in student images")
    ap.add_argument("--embedder", default="pixel")
    ap.add_argument("--hybrid-switch", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tag_filter)
    llm = make_llm(args.llm)
    checker = make_llm(args.checker_llm) if args.checker_llm else llm
    if checker is llm and llm is not None:
        print("warning: injection checker = rewriter; pass --checker-llm with a different model", file=sys.stderr)
    judges = [make_judge(j, device=args.device) for j in args.eval_judges]
    search_judge = make_judge(args.search_judge, device=args.device) if args.search_judge else None
    embed = pixel_embed if args.embedder == "pixel" else ImageEmbedder(args.embedder, device=args.device)
    pe = json.loads(Path(args.pe_rewrites).read_text()) if args.pe_rewrites else {}
    student = Generator(get_variant(args.student, args.config), args.device, args.dtype).load()
    teacher = Generator(teacher_of(args.family, args.config), args.device, args.dtype).load()
    k, seeds = args.k, list(range(args.seed, args.seed + args.k))
    ref_seeds = list(range(10_000, 10_000 + args.n_ref))  # disjoint from method seeds
    methods = [m for m in args.methods if m != "pe" or pe]
    if "seeds_eq" in methods:  # needs Reword-K's LLM time for this intent, so run it after `reword`
        methods = [m for m in methods if m != "seeds_eq"] + ["seeds_eq"]
    needs_llm = [m for m in methods if m in LLM_REWRITES]
    if needs_llm and llm is None:
        raise SystemExit(f"methods {needs_llm} need --llm")
    if {"evolve", "seeds_eq"} & set(methods) and search_judge is None:
        raise SystemExit("evolve / seeds_eq need --search-judge")

    t_img = None
    rows = []
    for idx, intent in enumerate(intents):
        ref_imgs = teacher.generate_batched([intent.prompt] * args.n_ref, ref_seeds)
        ref_emb = np.asarray(embed(ref_imgs))
        ref_ok = np.array([s["success"] for s in score_intent(judges[0], ref_imgs, intent)])
        t_llm_reword = 0.0
        intent_rows = []
        for method in methods:
            t0 = time.perf_counter()
            extra_latency = 0.0
            if method in REWORD_VARIANTS or method == "teacher_reword":
                prompts = reword_k(llm, intent.prompt, k, **REWORD_VARIANTS.get(method, {}))
                if method == "reword":
                    t_llm_reword = time.perf_counter() - t0
                gen = teacher if method == "teacher_reword" else student
                imgs = gen.generate(prompts, seeds)
            elif method == "evolve":
                cfg = EvolveConfig(budget_nfe=args.evolve_images * student.spec.nfe_per_image, seeds=(args.seed,),
                                   keep_images=True, init_prompts=tuple(reword_k(llm, intent.prompt, k)),
                                   target_successes=k)
                pop = select_population(evolve(intent, student, search_judge, llm, cfg, embed_fn=embed), k)
                prompts, imgs = [c.prompt for c in pop], [c.images[0] for c in pop]
            elif method == "hybrid":
                prompts = [intent.prompt] * k
                imgs = hybrid_teacher_first(teacher, student, prompts, seeds, switch=args.hybrid_switch)
            elif method == "seeds_eq":
                n_extra = int(t_llm_reword / t_img) if t_img else 0
                pool_seeds = list(range(args.seed, args.seed + k + n_extra))
                pool = student.generate_batched([intent.prompt] * len(pool_seeds), pool_seeds)
                sc = score_intent(search_judge, pool, intent)
                order = sorted(range(len(pool)), key=lambda i: (sc[i]["success"], sc[i]["soft"]), reverse=True)[:k]
                prompts, imgs = [intent.prompt] * k, [pool[i] for i in order]
            else:
                if method in ("seeds", "pink", "cads", "teacher"):
                    prompts = [intent.prompt] * k
                elif method == "tags":
                    prompts = tag_k(intent.prompt, k, seed=idx)
                elif method == "pe":
                    r = pe.get(intent.prompt, intent.prompt)
                    prompts = (r if isinstance(r, list) else [r] * k)[:k]
                    extra_latency = args.pe_latency_s
                elif method == "expand":
                    prompts = expand_k(llm, intent.prompt, k)
                elif method == "para":
                    prompts = (paraphrase(llm, intent.prompt, n=k) + [intent.prompt] * k)[:k]
                else:
                    raise ValueError(method)
                gen = teacher if method == "teacher" else student
                t_gen = time.perf_counter()
                imgs = gen.generate(prompts, seeds, noise=method if method in ("pink", "cads") else "white")
                if method == "seeds":
                    t_img = (time.perf_counter() - t_gen) / k
            latency = time.perf_counter() - t0 + extra_latency
            emb = np.asarray(embed(imgs))
            ev = {j.name: score_intent(j, imgs, intent) for j in judges}
            ok = np.array([s["success"] for s in ev[judges[0].name]])
            row = {"idx": idx, "tag": intent.tag, "method": method, "latency_s": round(latency, 3),
                   "prompts": prompts, "vendi": vendi_score(emb), "pairwise": mean_pairwise_distance(emb),
                   "teacher_rate": float(ref_ok.mean()),
                   "coverage": knn_coverage(ref_emb[ref_ok], emb[ok], k=args.coverage_k) if ref_ok.sum() > args.coverage_k else None,
                   "coverage_soft": teacher_coverage(ref_emb, emb, ref_ok) if ref_ok.any() else None,
                   "eval": {jn: {"mean_success": float(np.mean([s["success"] for s in sc])),
                                 "pass@K": bool(any(s["success"] for s in sc)),
                                 "soft": float(np.mean([s["soft"] for s in sc]))} for jn, sc in ev.items()}}
            if method in LLM_REWRITES | {"pe", "tags"} and checker is not None:
                row["injection_lenient"] = float(np.mean(attribute_injection(checker, intent.prompt, prompts)))
                row["injection_strict"] = float(np.mean(attribute_injection(checker, intent.prompt, prompts, strict=True)))
            intent_rows.append(row)
        with open(out / "records.jsonl", "a") as f:
            f.writelines(json.dumps(r) + "\n" for r in intent_rows)
        rows += intent_rows

    def mean_of(rs, key):
        vals = [r[key] for r in rs if r.get(key) is not None]
        return float(np.mean(vals)) if vals else None

    summary = {}
    for m in dict.fromkeys(r["method"] for r in rows):
        rs = [r for r in rows if r["method"] == m]
        summary[m] = {key: mean_of(rs, key) for key in ("latency_s", "vendi", "pairwise", "coverage", "coverage_soft",
                                                        "injection_lenient", "injection_strict")}
        summary[m]["eval"] = {jn: {key: float(np.mean([r["eval"][jn][key] for r in rs]))
                                   for key in ("mean_success", "pass@K", "soft")} for jn in rs[0]["eval"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    jn = judges[0].name
    fmt = lambda v, f: (f % v) if v is not None else "  -  "  # noqa: E731
    print(f"{'method':15s} {'succ':>6s} {'pass@K':>7s} {'vendi':>6s} {'cover':>6s} {'inj(s)':>6s} {'lat(s)':>7s}")
    for m, s in summary.items():
        print(f"{m:15s} {s['eval'][jn]['mean_success']:6.3f} {s['eval'][jn]['pass@K']:7.3f} {s['vendi']:6.2f} "
              f"{fmt(s['coverage'], '%6.3f'):>6s} {fmt(s['injection_strict'], '%6.2f'):>6s} {s['latency_s']:7.2f}")


if __name__ == "__main__":
    main()
