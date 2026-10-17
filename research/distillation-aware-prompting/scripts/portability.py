"""E2b -- Which search variable is portable from a distilled student to its teacher: the prompt
or the seed?  (Analysis only: reads the wording x seed grids written by scripts/variance.py.)

For every student, against the family teacher:
  prompt_spearman  : per intent, rank correlation of wording-level scores (mean over seeds)
  prompt_top1      : P(the student's best wording is also the teacher's best)
  proxy_regret     : teacher score of its own best wording minus that of the wording the student
                     would pick -- the loss from screening wordings on the student
  seed_spearman    : per intent, rank correlation of per-seed scores for the original wording
  seed_coupling    : mean cos(teacher(z), student(z)) - mean cos(teacher(z), student(z')) over
                     seeds z != z' (does a seed mean the same image for both models?)
  cost_ratio       : teacher NFE per image / student NFE per image

  python scripts/portability.py --run runs/e2_sdxl --teacher sdxl-base
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


def _spearman_rows(a: np.ndarray, b: np.ndarray) -> list[float]:
    out = []
    for x, y in zip(a, b):
        if np.ptp(x) > 0 and np.ptp(y) > 0:
            out.append(float(spearmanr(x, y).statistic))
    return out


def _unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def portability(soft_T, soft_S, emb_T=None, emb_S=None) -> dict:
    """soft_*: [I, J, S] judge soft scores; emb_*: [I, J, S, D] image embeddings (optional)."""
    wT, wS = soft_T.mean(2), soft_S.mean(2)  # wording-level scores [I, J]
    pick = wS.argmax(1)
    rows = np.arange(len(wT))
    res = {
        "prompt_spearman": float(np.mean(_spearman_rows(wT, wS) or [np.nan])),
        "prompt_top1": float(np.mean(pick == wT.argmax(1))),
        "proxy_regret": float(np.mean(wT.max(1) - wT[rows, pick])),
        "random_pick_regret": float(np.mean(wT.max(1) - wT.mean(1))),
        "seed_spearman": float(np.mean(_spearman_rows(soft_T[:, 0, :], soft_S[:, 0, :]) or [np.nan])),
        "n_intents": int(len(wT)),
    }
    if emb_T is not None and emb_S is not None:
        t, s = _unit(emb_T[:, 0].astype(np.float32)), _unit(emb_S[:, 0].astype(np.float32))  # [I, S, D]
        sim = np.einsum("isd,itd->ist", t, s)  # teacher seed x student seed
        S = sim.shape[1]
        same = np.mean([np.trace(m) / S for m in sim])
        diff = np.mean([(m.sum() - np.trace(m)) / (S * (S - 1)) for m in sim])
        res["seed_coupling"] = float(same - diff)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="output directory of scripts/variance.py")
    ap.add_argument("--teacher", required=True)
    args = ap.parse_args()

    run = Path(args.run)
    load = lambda kind, name: np.load(run / f"{kind}_{name}.npy").astype(np.float32)  # noqa: E731
    meta = {p.stem[len("meta_"):]: json.loads(p.read_text()) for p in run.glob("meta_*.json")}
    soft_T, emb_T = load("soft", args.teacher), load("emb", args.teacher)
    summary = {}
    for name, m in meta.items():
        if name == args.teacher:
            continue
        r = portability(soft_T, load("soft", name), emb_T, load("emb", name))
        r["cost_ratio"] = meta[args.teacher]["nfe_per_image"] / m["nfe_per_image"]
        r["objective"] = m["objective"]
        summary[name] = r
        print(f"{name:24s} prompt rho={r['prompt_spearman']:.2f} top1={r['prompt_top1']:.2f} "
              f"regret={r['proxy_regret']:.3f} (random {r['random_pick_regret']:.3f}) | "
              f"seed rho={r['seed_spearman']:.2f} coupling={r.get('seed_coupling', float('nan')):.3f} | "
              f"cost x{r['cost_ratio']:.0f}")
    (run / "portability.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
