"""Analysis entry points that turn run outputs into the paper's numbers.

  interaction : student-minus-teacher difference of (wording-arm gain - seed-arm gain) with a paired
                bootstrap CI over intents, from a search_scaling.py run on the `images` axis
                (equal candidate count: the mechanism claim) or the `seconds` axis (deployment).
                Uses the deployable fresh-seed rate of the chosen wording by default.
  predict     : pre-registered predictions for each student from E1 (sharpening.py summary + success
                arrays) and the teacher's wording statistics (variance.py grid): seed / wording /
                selection curves (predict_scaling) and ledger shares (predict_ledger). Run BEFORE the
                ledger and search runs on that student, and commit the output.

  python scripts/analyze.py interaction --run runs/e3_dmd2 --student-arm reword --teacher-arm teacher_prompt \
      --seed-arm noise --teacher-seed-arm teacher --budget 8
  python scripts/analyze.py predict --e1 runs/e1_sdxl --grid runs/e2_sdxl --teacher sdxl-base --out runs/pred_sdxl.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dap.metrics import fit_tempering_grid, paired_interaction_ci, predict_ledger, predict_scaling, smoothed_logit  # noqa: E402


def interaction(args):
    rows = [json.loads(line) for line in (Path(args.run) / "records.jsonl").read_text().splitlines() if line.strip()]
    val = defaultdict(dict)  # (idx) -> arm -> value at the budget
    for r in rows:
        if str(r["budget"]) != str(args.budget):
            continue
        ev = r["eval"][args.judge] if args.judge else next(iter(r["eval"].values()))
        v = ev.get("fresh_rate") if args.metric == "fresh" else float(ev["success"])
        if v is not None:
            val[r["idx"]][r["method"]] = v
    arms = (args.student_arm, args.seed_arm, args.teacher_arm, args.teacher_seed_arm)
    idx = [i for i, a in val.items() if all(k in a for k in arms)]
    gain_S = np.array([val[i][args.student_arm] - val[i][args.seed_arm] for i in idx])
    gain_T = np.array([val[i][args.teacher_arm] - val[i][args.teacher_seed_arm] for i in idx])
    res = {"budget": args.budget, "metric": args.metric, "student_gain": float(gain_S.mean()) if len(idx) else None,
           "teacher_gain": float(gain_T.mean()) if len(idx) else None,
           **(paired_interaction_ci(gain_S, gain_T) if len(idx) else {"n": 0})}
    print(json.dumps(res, indent=1))
    return res


def wording_stats(grid_succ_T: np.ndarray) -> tuple[float, float]:
    """Mean / s.d. of paraphrase effects in teacher logit space from a [I, J, S] success grid,
    with binomial sampling noise removed (original wording = column 0)."""
    I, J, S = grid_succ_T.shape
    lg, var = smoothed_logit(grid_succ_T.sum(2), S)
    d = lg[:, 1:] - lg[:, :1]
    noise = (var[:, 1:] + var[:, :1]).mean()
    return float(d.mean()), float(np.sqrt(max(d.var() - noise, 1e-6)))


def task_tags(e1_dir, teacher, n) -> list[str]:
    """Task tag per prompt, in E1 order (from sharpening.py's per-prompt records)."""
    recs = [json.loads(line) for line in (Path(e1_dir) / f"records_{teacher}.jsonl").read_text().splitlines() if line.strip()]
    tags = [r["tag"] for r in sorted(recs, key=lambda r: r["idx"])]
    assert len(tags) == n, "E1 records and success arrays disagree"
    return tags


def pool(dicts: list, weights: list):
    """Weighted average of nested dicts of floats with identical structure."""
    w = np.asarray(weights, float) / np.sum(weights)
    if isinstance(dicts[0], dict):
        return {k: pool([d[k] for d in dicts], weights) for k in dicts[0]}
    return float(np.dot(w, dicts))


def predict(args):
    e1 = json.loads((Path(args.e1) / "summary.json").read_text())
    cT = np.load(Path(args.e1) / f"succ_{args.teacher}.npy").sum(1)
    nT = int(np.load(Path(args.e1) / f"succ_{args.teacher}.npy").shape[1])
    grid_T = np.load(Path(args.grid) / f"succ_{args.teacher}.npy")
    mu_w, s_w = wording_stats(grid_T)
    out = {"teacher_wording": {"mu": mu_w, "sd": s_w}, "students": {}}
    for name, row in e1.items():
        if row.get("role") != "student" or "tempering_fit" not in row:
            continue
        fit = row["tempering_fit"]
        grid_path = Path(args.grid) / f"succ_{name}.npy"
        if grid_path.exists():  # two-level sigma from the student's own wording grid (disjoint intents advised)
            gS = np.load(grid_path)
            two = fit_tempering_grid(grid_T.sum(2), grid_T.shape[2], gS.sum(2), gS.shape[2])
            s_i, s_w_student = two["sigma_intent"], two["sigma_wording"]
        else:
            s_i, s_w_student = fit.get("sigma", 0.0), 0.0  # unidentified split: report both extremes
        # per-task offsets (within-task fit): predict each task group with b + b_task and pool by size
        offsets = fit.get("group_offsets") or {"all": 0.0}
        tags = np.array(task_tags(args.e1, args.teacher, len(cT)) if "group_offsets" in fit else ["all"] * len(cT))
        curves, ledgers, weights = [], [], []
        for tag, off in offsets.items():
            m = tags == tag
            if not m.any():
                continue
            bt = fit["b"] + off
            curves.append(predict_scaling(cT[m], nT, fit["beta"], bt, s_w, args.budgets, sigma=s_w_student, mu_wording=mu_w))
            ledgers.append(predict_ledger(cT[m], nT, fit["beta"], bt, s_i, s_w_student, mu_w, s_w, k=args.k))
            weights.append(m.sum())
        out["students"][name] = {"beta": fit["beta"], "b": fit["b"], "group_offsets": offsets,
                                 "sigma_intent": s_i, "sigma_wording": s_w_student,
                                 "curves": pool(curves, weights), "ledger": pool(ledgers, weights)}
    Path(args.out).write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote predictions for {len(out['students'])} students to {args.out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("interaction")
    a.add_argument("--run", required=True)
    a.add_argument("--student-arm", default="reword")
    a.add_argument("--seed-arm", default="noise")
    a.add_argument("--teacher-arm", default="teacher_prompt")
    a.add_argument("--teacher-seed-arm", default="teacher")
    a.add_argument("--budget", required=True)
    a.add_argument("--metric", choices=["fresh", "best"], default="fresh")
    a.add_argument("--judge")
    p = sub.add_parser("predict")
    p.add_argument("--e1", required=True)
    p.add_argument("--grid", required=True)
    p.add_argument("--teacher", required=True)
    p.add_argument("--budgets", nargs="+", type=int, default=[1, 2, 4, 8, 16])
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--out", required=True)
    args = ap.parse_args()
    {"interaction": interaction, "predict": predict}[args.cmd](args)


if __name__ == "__main__":
    main()
