"""E3 -- Do prompt rewrites transfer from teacher to student, and are they amplified?

Every intent is rendered under several wordings (original, cached paraphrases, and optional
enhancer rewrites) by the teacher and each student, n seeds per wording. Reports, per student:
  beta_orig      : sharpening exponent fitted on the original wordings (as in E1)
  amp_slope      : Deming slope of  dlogit q_S  on  dlogit q_T  over rewrites (tempered model: = beta)
  rank_spearman  : mean per-intent Spearman correlation of wording rankings, teacher vs student
  argmax_agree   : how often the teacher's best wording is also (one of) the student's best
  transfer_regret: student success of its own best wording minus that of the teacher's best wording
  by_source      : mean change in student / teacher success per rewrite source (e.g. official PE)

  python scripts/amplification.py --family sdxl --students dmd2-sdxl-4 lcm-sdxl-4 \
     --paraphrases runs/paraphrases.json --rewrites runs/pe_rewrites.json --n-seeds 12 \
     --judge openai:Qwen/Qwen3-VL-8B-Instruct@http://localhost:8000/v1 --out runs/e3_sdxl
`--rewrites` is a JSON {prompt: {source_name: rewritten_prompt}} produced by any enhancer.
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dap import make_judge  # noqa: E402
from dap.generation import CONFIG_PATH, Generator, load_families  # noqa: E402
from dap.judges import score_intent  # noqa: E402
from dap.metrics import amplification_slope, fit_tempering, smoothed_logit  # noqa: E402
from dap.questions import load_geneval  # noqa: E402


def wordings_for(intent, paras, rewrites, n_para):
    ws = [("original", intent.prompt)]
    ws += [(f"para{j}", p) for j, p in enumerate(paras.get(intent.prompt, [])[: n_para - 1])]
    ws += [(src, p) for src, p in rewrites.get(intent.prompt, {}).items()]
    return ws


def count_successes(spec, intents, all_wordings, judge, args) -> list[np.ndarray]:
    gen = Generator(spec, device=args.device, dtype=args.dtype).load()
    seeds = list(range(args.n_seeds))
    counts = []
    for intent, ws in zip(intents, all_wordings):
        prompts = [w for _, w in ws for _ in seeds]
        images = gen.generate_batched(prompts, seeds * len(ws), batch_size=args.batch_size)
        succ = np.array([s["success"] for s in score_intent(judge, images, intent)]).reshape(len(ws), len(seeds))
        counts.append(succ.sum(1))
    del gen
    gc.collect()
    return counts


def spearman(a, b) -> float:
    from scipy.stats import spearmanr

    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(spearmanr(a, b).statistic)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--students", nargs="*", help="default: all students of the family")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--geneval-meta")
    ap.add_argument("--paraphrases", required=True)
    ap.add_argument("--rewrites")
    ap.add_argument("--n-para", type=int, default=6)
    ap.add_argument("--n-seeds", type=int, default=12)
    ap.add_argument("--judge", default="mock")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    intents = load_geneval(args.geneval_meta, limit=args.limit, tags=args.tags)
    paras = json.loads(Path(args.paraphrases).read_text())
    rewrites = json.loads(Path(args.rewrites).read_text()) if args.rewrites else {}
    all_w = [wordings_for(it, paras, rewrites, args.n_para) for it in intents]
    judge = make_judge(args.judge, device=args.device)
    variants = load_families(args.config)[args.family]
    teacher = next(v for v in variants if v.role == "teacher")
    students = [v for v in variants if v.role == "student" and (not args.students or v.name in args.students)]

    n = args.n_seeds
    cT = count_successes(teacher, intents, all_w, judge, args)
    summary = {}
    for spec in students:
        cS = count_successes(spec, intents, all_w, judge, args)
        beta = fit_tempering(np.array([c[0] for c in cT]), n, np.array([c[0] for c in cS]), n)
        dT, dS, vT, vS, rhos, agree, regret = [], [], [], [], [], [], []
        by_source: dict[str, list] = {}
        for ws, t, s in zip(all_w, cT, cS):
            lt, vt = smoothed_logit(t, n)
            ls, vs = smoothed_logit(s, n)
            dT += list(lt[1:] - lt[0]); dS += list(ls[1:] - ls[0])
            vT += list(vt[1:] + vt[0]); vS += list(vs[1:] + vs[0])
            rhos.append(spearman(t, s))
            agree.append(bool(s[int(np.argmax(t))] == s.max()))
            regret.append(float((s.max() - s[int(np.argmax(t))]) / n))
            for (src, _), tt, ss in zip(ws[1:], t[1:], s[1:]):
                by_source.setdefault(src if not src.startswith("para") else "paraphrase", []).append(
                    ((ss - s[0]) / n, (tt - t[0]) / n))
        summary[spec.name] = {
            "objective": spec.objective, "steps": spec.steps,
            "beta_orig": beta["beta"], "b_orig": beta["b"],
            "amp": amplification_slope(np.array(dT), np.array(dS), np.array(vT), np.array(vS)),
            "rank_spearman": float(np.nanmean(rhos)) if np.isfinite(rhos).any() else float("nan"),
            "argmax_agree": float(np.mean(agree)),
            "transfer_regret": float(np.mean(regret)),
            "by_source": {k: {"d_student": float(np.mean([x[0] for x in v])),
                              "d_teacher": float(np.mean([x[1] for x in v])), "n": len(v)}
                          for k, v in by_source.items()},
        }
        print(spec.name, json.dumps(summary[spec.name]["amp"]), f"beta={beta['beta']:.2f}")
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    np.save(out / "counts_teacher.npy", np.array(cT, dtype=object), allow_pickle=True)


if __name__ == "__main__":
    main()
