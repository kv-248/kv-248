"""Toy check of the tempered-mixture model (CPU, seconds).

Teacher, for a 'wording' c in (0, 1): p_T(x | c) = c N(+d, 1) + (1 - c) N(-d, 1); success means
x > 0, so q_T(c) ~ c. A capacity-limited student (one Gaussian per condition, the extreme of
"fewer steps, less capacity") is fitted per condition by
  * reverse KL  KL(q || p_T)  -- the mode-seeking direction used by DMD-style distillation,
  * forward KL  KL(p_T || q)  -- mode-covering (moment matching).
We then read off the student's success rate q_S(c) = P(x > 0) and the local sharpening exponent
beta = d logit q_S / d logit q_T, and the global logit-logit slope.

  python scripts/toy_tempering.py            # prints a table; --plot saves toy_tempering.png
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import minimize
from scipy.special import logit, logsumexp
from scipy.stats import norm

GH_X, GH_W = np.polynomial.hermite_e.hermegauss(80)  # E_{z~N(0,1)}[f(z)] ~ sum w f(x) / sqrt(2 pi)
GH_W = GH_W / np.sqrt(2 * np.pi)


def log_p_teacher(x, c, d):
    return logsumexp([np.log(c) + norm.logpdf(x, d, 1), np.log1p(-c) + norm.logpdf(x, -d, 1)], axis=0)


def reverse_kl_fit(c, d):
    def kl(theta):
        mu, log_s = theta
        x = mu + np.exp(log_s) * GH_X
        return -(log_s + 0.5 * np.log(2 * np.pi * np.e)) - np.sum(GH_W * log_p_teacher(x, c, d))

    starts = [(d, 0.0), (-d, 0.0), (0.0, np.log(d + 1))]
    best = min((minimize(kl, s, method="Nelder-Mead", options={"xatol": 1e-7, "fatol": 1e-10}) for s in starts),
               key=lambda r: r.fun)
    return best.x[0], np.exp(best.x[1])


def forward_kl_fit(c, d):
    mu = c * d - (1 - c) * d
    var = 1 + d ** 2 - mu ** 2
    return mu, np.sqrt(var)


def run(d: float, cs: np.ndarray) -> dict:
    qT = c_to_qT = cs * norm.sf(0, d, 1) + (1 - cs) * norm.sf(0, -d, 1)
    res = {"qT": qT}
    for name, fit in (("reverse_kl", reverse_kl_fit), ("forward_kl", forward_kl_fit)):
        params = np.array([fit(c, d) for c in cs])
        qS = np.clip(norm.sf(0, params[:, 0], params[:, 1]), 1e-9, 1 - 1e-9)
        lt, ls = logit(np.clip(c_to_qT, 1e-9, 1 - 1e-9)), logit(qS)
        mid = np.argmin(np.abs(qT - 0.5))
        local = (ls[mid + 1] - ls[mid - 1]) / (lt[mid + 1] - lt[mid - 1])
        window = (qT > 0.05) & (qT < 0.95)
        slope = np.polyfit(lt[window], ls[window], 1)[0]
        seed_sd = float(np.mean(params[:, 1]))  # within-condition (seed) spread of the student
        res[name] = {"qS": qS, "beta_local": float(local), "beta_slope": float(slope), "seed_sd": seed_sd}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()
    cs = np.linspace(0.02, 0.98, 97)
    print(f"{'sep d':>6s} | {'reverse KL: beta@0.5':>20s} {'slope':>6s} {'seed sd':>8s} | "
          f"{'forward KL: beta@0.5':>20s} {'slope':>6s} {'seed sd':>8s}")
    results = {}
    for d in (0.5, 1.0, 1.5, 2.0, 3.0):
        r = run(d, cs)
        results[d] = r
        rk, fk = r["reverse_kl"], r["forward_kl"]
        print(f"{d:6.1f} | {rk['beta_local']:20.2f} {rk['beta_slope']:6.2f} {rk['seed_sd']:8.2f} | "
              f"{fk['beta_local']:20.2f} {fk['beta_slope']:6.2f} {fk['seed_sd']:8.2f}")
    if args.plot:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(4, 4))
        for d in (1.0, 2.0, 3.0):
            r = results[d]
            ax.plot(r["qT"], r["reverse_kl"]["qS"], label=f"reverse KL, d={d}")
            ax.plot(r["qT"], r["forward_kl"]["qS"], "--", label=f"forward KL, d={d}")
        ax.plot([0, 1], [0, 1], "k:", lw=0.8)
        ax.set_xlabel("teacher success q_T")
        ax.set_ylabel("student success q_S")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig("toy_tempering.png", dpi=150)


if __name__ == "__main__":
    main()
