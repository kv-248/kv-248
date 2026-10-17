"""E5 -- K-image remedy comparison on a distilled student (Table 2 of the proposal).

For each intent every method produces K images; nothing here uses a search judge, so the
latency column is the real deployment cost (LLM call + K generations). Methods:
  seeds   : original prompt, K seeds                                   (i.i.d. baseline)
  pink    : original prompt, K seeds, pink-noise initial latents       (noise-side, ~free)
  pe      : teacher-built prompt enhancer output (--pe-rewrites), K seeds or K PE samples
  expand  : K generic diverse LLM expansions (Prompt-Expansion-style control)
  para    : K random meaning-preserving paraphrases
  reword  : Reword-K, one joint call for K intent-preserving rewordings (the proposed remedy)
  evolve  : Reword-Evolve, student-in-the-loop evolution initialised with Reword-K, returning K
            distinct successful wordings (needs --search-judge, which must differ from the
            evaluation judges; its time is part of the latency)
  teacher : the teacher, original prompt, K seeds                      (reference, at its own cost)
Metrics per method: mean success and pass@K under held-out evaluation judges, Vendi and mean
pairwise distance, teacher coverage (success-filtered teacher samples for the ORIGINAL prompt, in
the evaluation feature space), attribute-injection rate of rewrites, and latency.

  python scripts/remedy_eval.py --family sdxl --student dmd2-sdxl-4 --k 4 --limit 300 \
     --llm openai:Qwen/Qwen3-4B-Instruct-2507@http://localhost:8001/v1 \
     --eval-judges openai:OpenGVLab/InternVL3_5-8B@http://localhost:8002/v1 \
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
from dap.generation import CONFIG_PATH, Generator, get_variant, teacher_of  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.metrics import mean_pairwise_distance, teacher_coverage, vendi_score  # noqa: E402
from dap.questions import load_geneval  # noqa: E402
from dap.reword import attribute_injection, expand_k, reword_k  # noqa: E402
from dap.rewrite import paraphrase  # noqa: E402

REWRITE_METHODS = {"pe", "expand", "para", "reword", "evolve"}


def method_prompts(method, intent, k, llm, pe_rewrites):
    p = intent.prompt
    if method in ("seeds", "pink", "teacher"):
        return [p] * k
    if method == "pe":
        r = pe_rewrites.get(p, p)
        return (r if isinstance(r, list) else [r] * k)[:k]
    if llm is None:
        raise SystemExit(f"method {method!r} needs --llm")
    if method == "expand":
        return expand_k(llm, p, k)
    if method == "para":
        return (paraphrase(llm, p, n=k) + [p] * k)[:k]
    if method == "reword":
        return reword_k(llm, p, k)
    raise ValueError(method)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--student", required=True)
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--methods", nargs="+", default=["seeds", "pink", "pe", "expand", "para", "reword", "teacher"])
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--n-ref", type=int, default=8, help="teacher reference samples per intent (held-out seeds)")
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--llm")
    ap.add_argument("--pe-rewrites")
    ap.add_argument("--eval-judges", nargs="+", default=["mock"])
    ap.add_argument("--search-judge", help="judge used inside Reword-Evolve (never an evaluation judge)")
    ap.add_argument("--evolve-images", type=int, default=16, help="Reword-Evolve budget in student images")
    ap.add_argument("--embedder", default="pixel")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tags)
    llm = make_llm(args.llm)
    judges = [make_judge(j, device=args.device) for j in args.eval_judges]
    search_judge = make_judge(args.search_judge, device=args.device) if args.search_judge else None
    embed = pixel_embed if args.embedder == "pixel" else ImageEmbedder(args.embedder, device=args.device)
    pe = json.loads(Path(args.pe_rewrites).read_text()) if args.pe_rewrites else {}
    student = Generator(get_variant(args.student, args.config), args.device, args.dtype).load()
    teacher = Generator(teacher_of(args.family, args.config), args.device, args.dtype).load()
    k, seeds = args.k, list(range(args.seed, args.seed + args.k))
    ref_seeds = list(range(10_000, 10_000 + args.n_ref))  # disjoint from method seeds

    rows = []
    for idx, intent in enumerate(intents):
        ref_imgs = teacher.generate_batched([intent.prompt] * args.n_ref, ref_seeds)
        ref_emb = np.asarray(embed(ref_imgs))
        ref_ok = [s["success"] for s in score_intent(judges[0], ref_imgs, intent)]
        for method in [m for m in args.methods if m != "pe" or pe]:
            t0 = time.perf_counter()
            if method == "evolve":
                if search_judge is None or llm is None:
                    raise SystemExit("evolve needs --search-judge and --llm")
                cfg = EvolveConfig(budget_nfe=args.evolve_images * student.spec.nfe_per_image, seeds=(args.seed,),
                                   keep_images=True, init_prompts=tuple(reword_k(llm, intent.prompt, k)),
                                   target_successes=k)
                pop = select_population(evolve(intent, student, search_judge, llm, cfg, embed_fn=embed), k)
                prompts, imgs = [c.prompt for c in pop], [c.images[0] for c in pop]
            else:
                prompts = method_prompts(method, intent, k, llm, pe)
                gen = teacher if method == "teacher" else student
                imgs = gen.generate(prompts, seeds, noise="pink" if method == "pink" else "white")
            latency = time.perf_counter() - t0
            emb = np.asarray(embed(imgs))
            ev = {j.name: score_intent(j, imgs, intent) for j in judges}
            row = {"idx": idx, "tag": intent.tag, "method": method, "latency_s": round(latency, 3),
                   "prompts": prompts, "vendi": vendi_score(emb), "pairwise": mean_pairwise_distance(emb),
                   "teacher_coverage": teacher_coverage(ref_emb, emb, ref_ok),
                   "eval": {jn: {"mean_success": float(np.mean([s["success"] for s in sc])),
                                 "pass@K": bool(any(s["success"] for s in sc)),
                                 "soft": float(np.mean([s["soft"] for s in sc]))} for jn, sc in ev.items()}}
            if method in REWRITE_METHODS and llm is not None:
                row["injection_rate"] = float(np.mean(attribute_injection(llm, intent.prompt, prompts)))
            rows.append(row)
        with open(out / "records.jsonl", "a") as f:
            f.writelines(json.dumps(r) + "\n" for r in rows if r["idx"] == idx)

    summary = {}
    for m in dict.fromkeys(r["method"] for r in rows):
        rs = [r for r in rows if r["method"] == m]
        summary[m] = {
            "latency_s": float(np.mean([r["latency_s"] for r in rs])),
            "vendi": float(np.mean([r["vendi"] for r in rs])),
            "pairwise": float(np.mean([r["pairwise"] for r in rs])),
            "teacher_coverage": float(np.nanmean([r["teacher_coverage"] for r in rs])),
            "injection_rate": float(np.mean([r["injection_rate"] for r in rs])) if "injection_rate" in rs[0] else None,
            "eval": {jn: {key: float(np.mean([r["eval"][jn][key] for r in rs])) for key in ("mean_success", "pass@K", "soft")}
                     for jn in rs[0]["eval"]},
        }
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    jn = judges[0].name
    print(f"{'method':8s} {'succ':>6s} {'pass@K':>7s} {'vendi':>6s} {'cover':>6s} {'inject':>6s} {'lat(s)':>7s}")
    for m, s in summary.items():
        inj = f"{s['injection_rate']:.2f}" if s["injection_rate"] is not None else "  -  "
        print(f"{m:8s} {s['eval'][jn]['mean_success']:6.3f} {s['eval'][jn]['pass@K']:7.3f} {s['vendi']:6.2f} "
              f"{s['teacher_coverage']:6.3f} {inj:>6s} {s['latency_s']:7.2f}")


if __name__ == "__main__":
    main()
