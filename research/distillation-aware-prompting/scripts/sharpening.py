"""E1 -- Does distillation sharpen per-prompt success?

For a teacher and each of its distilled students: sample n seeds per GenEval prompt,
score every image against the prompt's checklist, then report pass@k over seeds and the
student-vs-teacher sharpening statistics (logit slope, lost reachability).

  python scripts/sharpening.py --family sdxl --n-seeds 16 --judge hf:Qwen/Qwen2.5-VL-7B-Instruct --out runs/e1_sdxl
"""

from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dap import make_judge  # noqa: E402
from dap.generation import CONFIG_PATH, Generator, load_families  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.metrics import bootstrap_tempering, mean_pass_at_k, sharpening  # noqa: E402
from dap.questions import load_geneval  # noqa: E402

KS = [1, 2, 4, 8, 16, 32, 64]


def run_variant(spec, intents, judge, args, out: Path):
    succ_path = out / f"succ_{spec.name}.npy"
    if succ_path.exists() and not args.overwrite:
        return np.load(succ_path)
    gen = Generator(spec, device=args.device, dtype=args.dtype).load()
    seeds = list(range(args.n_seeds))
    succ = np.zeros((len(intents), args.n_seeds), dtype=bool)
    soft = np.zeros((len(intents), args.n_seeds), dtype=np.float32)
    with open(out / f"records_{spec.name}.jsonl", "w") as f:
        for i, intent in enumerate(intents):
            images = gen.generate_batched([intent.prompt] * len(seeds), seeds, batch_size=args.batch_size)
            scores = score_intent(judge, images, intent)
            succ[i] = [s["success"] for s in scores]
            soft[i] = [s["soft"] for s in scores]
            f.write(json.dumps({"idx": i, "prompt": intent.prompt, "tag": intent.tag,
                                "success": succ[i].tolist(), "soft": soft[i].round(4).tolist()}) + "\n")
            if args.save_images:  # GenEval layout: <dir>/<idx:05d>/{metadata.jsonl, samples/<seed:04d>.png}
                d = out / "images" / spec.name / f"{i:05d}"
                (d / "samples").mkdir(parents=True, exist_ok=True)
                (d / "metadata.jsonl").write_text(json.dumps(intent.meta) + "\n")
                for s, im in zip(seeds, images):
                    im.save(d / "samples" / f"{s:04d}.png")
    np.save(succ_path, succ)
    np.save(out / f"soft_{spec.name}.npy", soft)
    (out / f"nfe_{spec.name}.json").write_text(json.dumps({"nfe": gen.nfe, "images": gen.images_generated}))
    del gen
    gc.collect()
    try:
        import torch

        torch.cuda.empty_cache()
    except Exception:
        pass
    return succ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--variants", nargs="*", help="subset of variant names (teacher is always included)")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--n-seeds", type=int, default=16)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--judge", default="mock")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--save-images", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--n-boot", type=int, default=200, help="bootstrap resamples for the beta CI")
    ap.add_argument("--teacher-cfgs", nargs="*", type=float, default=[],
                    help="extra teacher guidance scales: is a student just a higher-CFG teacher?")
    ap.add_argument("--judge-eps", nargs=2, type=float, default=[0.0, 0.0],
                    help="judge false-positive / false-negative rates (from a human-labelled subset)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    variants = load_families(args.config)[args.family]
    if args.variants:
        variants = [v for v in variants if v.role == "teacher" or v.name in args.variants]
    teacher = next(v for v in variants if v.role == "teacher")
    variants += [dataclasses.replace(teacher, name=f"{teacher.name}-cfg{w:g}", role="teacher_cfg",
                                     guidance_scale=w, cfg=w > 1.0) for w in args.teacher_cfgs]
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tags)
    judge = make_judge(args.judge, device=args.device)

    results = {v.name: run_variant(v, intents, judge, args, out) for v in variants}
    summary = {}
    for v in variants:
        row = {"role": v.role, "steps": v.steps, "nfe_per_image": v.nfe_per_image, "objective": v.objective,
               "pass@k": mean_pass_at_k(results[v.name], KS)}
        if v.role in ("student", "teacher_cfg"):
            row["sharpening_vs_teacher"] = sharpening(results[teacher.name], results[v.name])
            cT, cS = results[teacher.name].sum(1), results[v.name].sum(1)
            row["tempering_fit"] = bootstrap_tempering(cT, args.n_seeds, cS, args.n_seeds, n_boot=args.n_boot,
                                                       eps=tuple(args.judge_eps))
        summary[v.name] = row
    (out / "summary.json").write_text(json.dumps(summary, indent=1))

    ks = [k for k in KS if k <= args.n_seeds]
    print(f"{'variant':24s} {'NFE':>4s} " + " ".join(f"p@{k:<3d}" for k in ks) + "   beta [95% CI]      lost")
    for name, row in summary.items():
        sh, tf = row.get("sharpening_vs_teacher", {}), row.get("tempering_fit", {})
        print(f"{name:24s} {row['nfe_per_image']:>4d} " + " ".join(f"{row['pass@k'][k]:.3f}" for k in ks)
              + (f"   {tf['beta']:.2f} [{tf['beta_ci'][0]:.2f},{tf['beta_ci'][1]:.2f}]  {sh['lost_reach']:.2f}" if tf else ""))


if __name__ == "__main__":
    main()
