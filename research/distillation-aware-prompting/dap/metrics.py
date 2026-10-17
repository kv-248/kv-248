"""Metrics for the distillation analysis.

* pass@k over seeds (unbiased estimator of Chen et al., 2021) -- how much of the
  model's reachable set best-of-k sampling can find.
* Sharpening: per-prompt success rate of a student vs its teacher. A slope > 1 in
  logit space (with lost low-q prompts) is the signature of a mode-seeking student.
* Variance decomposition: how much of the within-intent output variation comes from
  the seed vs from the wording of the prompt ("prompt share" rho).
* Vendi score for set diversity.
"""

from __future__ import annotations

from math import comb

import numpy as np


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k from n samples with c successes."""
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def mean_pass_at_k(successes: np.ndarray, ks: list[int]) -> dict[int, float]:
    """successes: [num_prompts, n] boolean array."""
    n = successes.shape[1]
    cs = successes.sum(1)
    return {k: float(np.mean([pass_at_k(n, int(c), k) for c in cs])) for k in ks if k <= n}


def _logit(p):
    return np.log(p) - np.log1p(-p)


def sharpening(teacher_succ: np.ndarray, student_succ: np.ndarray) -> dict:
    """Compare per-prompt success rates of a student against its teacher.

    teacher_succ, student_succ: [num_prompts, n] boolean arrays (same prompts).
    Returns:
      slope / intercept of logit(q_S) ~ logit(q_T) on Laplace-smoothed rates
        (slope > 1: sharpening; < 1: flattening),
      lost_reach: fraction of teacher-reachable prompts (q_T > 0) the student never solves,
      gained_reach: fraction of teacher-unreachable prompts the student does solve,
      binned curve of mean q_S per q_T bin.
    """
    nT, nS = teacher_succ.shape[1], student_succ.shape[1]
    cT, cS = teacher_succ.sum(1), student_succ.sum(1)
    qT = (cT + 0.5) / (nT + 1)
    qS = (cS + 0.5) / (nS + 1)
    x, y = _logit(qT), _logit(qS)
    slope, intercept = np.polyfit(x, y, 1) if np.ptp(x) > 0 else (float("nan"), float("nan"))
    reach_T = cT > 0
    lost = float(np.mean(cS[reach_T] == 0)) if reach_T.any() else float("nan")
    gained = float(np.mean(cS[~reach_T] > 0)) if (~reach_T).any() else float("nan")
    bins = np.linspace(0, 1, 6)
    raw_qT, raw_qS = cT / nT, cS / nS
    curve = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (raw_qT >= lo) & ((raw_qT < hi) if hi < 1 else (raw_qT <= hi))
        curve.append({"qT_bin": [float(lo), float(hi)], "n": int(m.sum()),
                      "mean_qS": float(raw_qS[m].mean()) if m.any() else None})
    return {"slope": float(slope), "intercept": float(intercept), "lost_reach": lost,
            "gained_reach": gained, "curve": curve,
            "mean_qT": float(raw_qT.mean()), "mean_qS": float(raw_qS.mean())}


def variance_decomposition(emb: np.ndarray) -> dict:
    """Split within-intent variation into seed and prompt-wording components.

    emb: [I, J, S, D] embeddings (intent, paraphrase, seed, dim), e.g. DINOv2/CLIP
    image features. Features are L2-normalised; variances are traces of covariance.
      V_seed  = mean_{i,j} Var_s(e_ijs)
      V_para  = mean_i Var_j(mean_s e_ijs) - V_seed / S   (bias-corrected)
      rho     = V_para / (V_para + V_seed)   -- the prompt share of variation.
    """
    assert emb.ndim == 4, "expected [intent, paraphrase, seed, dim]"
    e = emb / np.linalg.norm(emb, axis=-1, keepdims=True)
    I, J, S, D = e.shape
    v_seed = float(e.var(axis=2, ddof=1).sum(-1).mean()) if S > 1 else 0.0
    cell_means = e.mean(axis=2)
    v_para_raw = float(cell_means.var(axis=1, ddof=1).sum(-1).mean()) if J > 1 else 0.0
    v_para = max(v_para_raw - (v_seed / S if S > 1 else 0.0), 0.0)
    denom = v_para + v_seed
    return {"v_seed": v_seed, "v_para": v_para, "rho": v_para / denom if denom > 0 else float("nan")}


def vendi_score(emb: np.ndarray) -> float:
    """Vendi score with cosine kernel: exp(entropy of eigenvalues of K/n)."""
    x = emb / np.linalg.norm(emb, axis=-1, keepdims=True)
    k = x @ x.T / len(x)
    w = np.clip(np.linalg.eigvalsh(k), 0, None)
    w = w[w > 1e-12]
    return float(np.exp(-(w * np.log(w)).sum()))


def mean_pairwise_distance(emb: np.ndarray) -> float:
    x = emb / np.linalg.norm(emb, axis=-1, keepdims=True)
    sim = x @ x.T
    n = len(x)
    return float((1 - sim)[~np.eye(n, dtype=bool)].mean()) if n > 1 else 0.0
