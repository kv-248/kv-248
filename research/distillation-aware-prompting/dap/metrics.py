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


# ---- tempered-mixture model: logit q_S = beta * logit q_T + b -------------------------

_U = np.linspace(-10.0, 10.0, 241)  # logit grid for latent success rates


def _log_binom_lik(c, n, m):
    """log Binomial(c | n, m) for prompts (rows) x grid nodes (cols)."""
    from scipy.special import gammaln

    c = np.asarray(c, float)[:, None]
    m = np.clip(m, 1e-12, 1 - 1e-12)[None, :] if np.ndim(m) == 1 else np.clip(m, 1e-12, 1 - 1e-12)
    return gammaln(n + 1) - gammaln(c + 1) - gammaln(n - c + 1) + c * np.log(m) + (n - c) * np.log1p(-m)


def teacher_posterior(cT, nT: int, eps: tuple[float, float] = (0.0, 0.0), weights=None) -> tuple[np.ndarray, list]:
    """Posterior over each prompt's latent teacher logit u = logit q_T on the grid `_U`.

    Empirical-Bayes Beta(a, b) prior on q_T (a logistic-beta density in u), fitted by marginal
    likelihood. `eps = (false-positive, false-negative)` rates of the judge: measured success
    probability is e0 + (1 - e0 - e1) q, so judge errors are not mistaken for (un)sharpening.
    `weights` (one per row of cT) lets callers pass unique counts with multiplicities.
    """
    from scipy.optimize import minimize
    from scipy.special import betaln, expit, logsumexp

    e0, e1 = eps
    q = expit(_U)
    ll = _log_binom_lik(cT, nT, e0 + (1 - e0 - e1) * q)
    du = _U[1] - _U[0]
    w = np.ones(len(ll)) if weights is None else np.asarray(weights, float)

    def log_prior(a, b):
        return a * np.log(q) + b * np.log1p(-q) - betaln(a, b) + np.log(du)

    def nll(x):
        a, b = np.exp(x)
        return -np.sum(w * logsumexp(ll + log_prior(a, b)[None, :], axis=1))

    a, b = np.exp(minimize(nll, x0=[0.0, 0.0], method="Nelder-Mead").x)
    lp = ll + log_prior(a, b)[None, :]
    return np.exp(lp - logsumexp(lp, axis=1, keepdims=True)), [float(a), float(b)]


def _log_betabinom_lik(c, n, m, rho):
    """log BetaBinomial(c | n, mean m, intra-prompt correlation rho) for prompts x grid nodes."""
    from scipy.special import betaln, gammaln

    c = np.asarray(c, float)[:, None]
    m = np.clip(m, 1e-9, 1 - 1e-9)[None, :]
    k = (1 - rho) / rho
    a, b = m * k, (1 - m) * k
    return gammaln(n + 1) - gammaln(c + 1) - gammaln(n - c + 1) + betaln(c + a, n - c + b) - betaln(a, b)


def fit_tempering(cT: np.ndarray, nT: int, cS: np.ndarray, nS: int,
                  eps: tuple[float, float] = (0.0, 0.0), eps_S: tuple[float, float] | None = None,
                  model: str = "re", n_herm: int = 12, weights=None, groups=None) -> dict:
    """Errors-in-variables MLE of the tempered-teacher model

        logit q_S(c) = beta * logit q_T(c) + b + sigma * e_c,   e_c ~ N(0, 1)

    beta  : effective sharpening exponent (phenomenological temperature; beta > 1 = tempering);
    sigma : prompt-specific student deviations ("the student re-addresses prompts"). Under exact
            mode tempering b is itself prompt-dependent, b_c = (1 - beta)[H_beta(success modes) -
            H_beta(failure modes)], which sigma absorbs.

    * The teacher's per-prompt rate is latent (`teacher_posterior`) and integrated out, so few seeds
      or rates near 0/1 do not attenuate beta (a naive logit regression does).
    * Judge confusion (false-positive, false-negative) may differ by model: `eps` for the teacher,
      `eps_S` for the student (default: same); estimate both from hand labels.
    * `groups` (e.g. GenEval task type per prompt) adds per-group offsets b_g, so beta is estimated
      within task type: otherwise task-level difficulty differences correlated with student offsets
      (resolution, missing spatial data) masquerade as tempering.
    * model="re" (default): the logit-normal random effect above, integrated by Gauss-Hermite.
      Without it, prompt-specific student errors bias beta upward under a binomial likelihood and
      downward under a beta-binomial one, so "binomial" and "betabinom" are reported only as brackets.
    """
    from scipy.optimize import minimize
    from scipy.special import expit, gammaln, logsumexp

    e0, e1 = eps
    s0, s1 = eps_S if eps_S is not None else eps
    # The likelihood depends on a prompt only through its (cT, cS) pair: fit on unique pairs with
    # multiplicities (at most (nT+1)(nS+1) rows, independent of the number of prompts).
    g_labels, g_idx = np.unique(np.asarray(groups if groups is not None else np.zeros(len(cT), int)).astype(str),
                                return_inverse=True)
    keys = np.stack([np.asarray(cT), np.asarray(cS), g_idx], 1)
    pairs, w = np.unique(keys, axis=0, return_counts=True)
    if weights is not None:
        idx = {tuple(p): i for i, p in enumerate(pairs)}
        w = np.zeros(len(pairs))
        for key, wt in zip(map(tuple, keys), weights):
            w[idx[key]] += wt
    cT_u, cS, gg = pairs[:, 0], pairs[:, 1], pairs[:, 2]
    n_g = len(g_labels)

    def offsets(theta_g):
        return np.concatenate([[0.0], theta_g])[gg][:, None]  # group 0 is the reference
    post, prior = teacher_posterior(cT_u, nT, eps, weights=w)
    keep = post.max(0) > 1e-10
    U, log_post = _U[keep], np.log(post[:, keep] + 1e-300)

    if model == "re":
        hx, hw = np.polynomial.hermite_e.hermegauss(n_herm)
        log_hw = np.log(hw / hw.sum())

        def nll(theta):
            b1, b2, log_sig = theta[:3]
            eta = (b1 * U[None, :, None] + b2 + offsets(theta[3:])[:, :, None]
                   + np.exp(log_sig) * hx[None, None, :])  # prompts x nodes x hermite
            m = s0 + (1 - s0 - s1) * expit(eta)
            c = cS[:, None, None].astype(float)
            ll = c * np.log(np.clip(m, 1e-12, 1)) + (nS - c) * np.log(np.clip(1 - m, 1e-12, 1)) + log_hw
            ll += (gammaln(nS + 1) - gammaln(c + 1) - gammaln(nS - c + 1))
            return -np.sum(w * logsumexp(log_post + logsumexp(ll, axis=2), axis=1))

        x0 = [1.0, 0.0, np.log(0.3)] + [0.0] * (n_g - 1)
    elif model in ("binomial", "betabinom"):
        n_extra = 1 if model == "betabinom" else 0

        def nll(theta):
            m = s0 + (1 - s0 - s1) * expit(theta[0] * U[None, :] + theta[1] + offsets(theta[2 + n_extra:]))
            if model == "betabinom":
                ll = np.stack([_log_betabinom_lik(cS[i:i + 1], nS, m[i], expit(theta[2]))[0] for i in range(len(cS))])
            else:
                c = cS[:, None].astype(float)
                ll = (gammaln(nS + 1) - gammaln(c + 1) - gammaln(nS - c + 1)
                      + c * np.log(np.clip(m, 1e-12, 1)) + (nS - c) * np.log(np.clip(1 - m, 1e-12, 1)))
            return -np.sum(w * logsumexp(log_post + ll, axis=1))

        x0 = [1.0, 0.0] + ([-2.0] * n_extra) + [0.0] * (n_g - 1)
    else:
        raise ValueError(model)
    res = minimize(nll, x0=x0, method="L-BFGS-B")
    if not res.success:  # fall back to the derivative-free optimizer
        res = minimize(nll, x0=x0, method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-6, "maxiter": 4000})
    out = {"model": model, "beta": float(res.x[0]), "b": float(res.x[1]), "nll": float(res.fun),
           "prior": prior, "eps": [float(e0), float(e1)], "eps_S": [float(s0), float(s1)]}
    if model == "re":
        out["sigma"] = float(np.exp(res.x[2]))
    if model == "betabinom":
        out["rho"] = float(expit(res.x[2]))
    if n_g > 1:
        k0 = 3 if model in ("re", "betabinom") else 2
        out["group_offsets"] = dict(zip(g_labels.tolist(), [0.0] + [float(x) for x in res.x[k0:]]))
    return out


def self_split_control(succ_T: np.ndarray, seed: int = 0, **fit_kw) -> dict:
    """Teacher-vs-itself control: split each prompt's seeds into two halves and fit the model with
    one half as 'teacher' and the other as 'student'. Should give beta ~ 1, sigma ~ 0."""
    rng = np.random.default_rng(seed)
    n = succ_T.shape[1] // 2
    perm = rng.permutation(succ_T.shape[1])
    a, b = succ_T[:, perm[:n]].sum(1), succ_T[:, perm[n:2 * n]].sum(1)
    return fit_tempering(a, n, b, n, **fit_kw)


def fit_mode_tempering(teacher_counts: list[np.ndarray], student_counts: list[np.ndarray],
                       n_mc: int = 200, seed: int = 0) -> dict:
    """Judge-free, mode-level test of tempering.

    Per prompt, images of both models are clustered jointly (e.g. k-means on DINOv2 features)
    and counted per cluster. Model: student cluster probabilities = softmax(beta * log pi_T),
    with teacher frequencies pi_T latent ~ Dirichlet(teacher_counts + 0.5) and integrated out by
    Monte Carlo. Also reports how often the student's most frequent cluster is the teacher's
    most frequent one, against the 'arbitrary collapse' null (mean pi_T,max).
    """
    from scipy.optimize import minimize_scalar
    from scipy.special import gammaln, logsumexp

    rng = np.random.default_rng(seed)
    samples = [np.log(rng.dirichlet(np.asarray(t, float) + 0.5, size=n_mc) + 1e-12) for t in teacher_counts]
    sc = [np.asarray(s, float) for s in student_counts]
    const = [gammaln(s.sum() + 1) - gammaln(s + 1).sum() for s in sc]

    def nll(beta):
        tot = 0.0
        for lp, s, k in zip(samples, sc, const):
            logits = beta * lp
            logp = logits - logsumexp(logits, axis=1, keepdims=True)
            tot += logsumexp(k + logp @ s) - np.log(n_mc)
        return -tot

    beta = float(minimize_scalar(nll, bounds=(0.05, 20.0), method="bounded").x)
    agree = [int(np.argmax(s) == np.argmax(t)) for t, s in zip(teacher_counts, student_counts) if np.sum(s) > 0]
    null = [float(np.max((np.asarray(t) + 0.5) / (np.sum(t) + 0.5 * len(t)))) for t in teacher_counts]
    return {"beta_mode": beta, "top_mode_agreement": float(np.mean(agree)), "null_agreement": float(np.mean(null))}


def teacher_mode_counts(teacher_emb: np.ndarray, student_emb: np.ndarray, k: int = 3, seed: int = 0):
    """Modes defined on the TEACHER's images only (k-means, cosine); student images are assigned to
    the nearest teacher mode. Joint clustering would let a global student style offset create
    'student-only' clusters and bias the test toward rejecting tempering."""
    t = teacher_emb / np.linalg.norm(teacher_emb, axis=1, keepdims=True)
    s = student_emb / np.linalg.norm(student_emb, axis=1, keepdims=True)
    rng = np.random.default_rng(seed)
    chosen = [int(rng.integers(len(t)))]  # farthest-point initialisation (k-means++-like, deterministic)
    while len(chosen) < k:
        chosen.append(int(np.argmin((t @ t[chosen].T).max(1))))
    cent = t[chosen]
    for _ in range(50):
        lab = np.argmax(t @ cent.T, axis=1)
        new = np.stack([t[lab == j].mean(0) if np.any(lab == j) else cent[j] for j in range(k)])
        new /= np.linalg.norm(new, axis=1, keepdims=True)
        if np.allclose(new, cent):
            break
        cent = new
    return np.bincount(lab, minlength=k), np.bincount(np.argmax(s @ cent.T, axis=1), minlength=k)


def joint_mode_counts(teacher_emb: np.ndarray, student_emb: np.ndarray, k: int = 3, seed: int = 0):
    """Cluster one prompt's teacher and student image embeddings jointly (k-means, cosine) and
    return per-cluster counts for each model. Prefer `teacher_mode_counts` (see its docstring)."""
    x = np.concatenate([teacher_emb, student_emb])
    x = x / np.linalg.norm(x, axis=1, keepdims=True)
    rng = np.random.default_rng(seed)
    cent = x[rng.choice(len(x), k, replace=False)]
    for _ in range(50):
        lab = np.argmax(x @ cent.T, axis=1)
        new = np.stack([x[lab == j].mean(0) if np.any(lab == j) else cent[j] for j in range(k)])
        new /= np.linalg.norm(new, axis=1, keepdims=True)
        if np.allclose(new, cent):
            break
        cent = new
    nt = len(teacher_emb)
    return np.bincount(lab[:nt], minlength=k), np.bincount(lab[nt:], minlength=k)


def predict_scaling(cT, nT: int, beta: float, b: float, sigma_wording: float, budgets: list[int],
                    eps: tuple[float, float] = (0.0, 0.0), n_mc: int = 256, seed: int = 0,
                    sigma: float = 0.0, mu_wording: float = 0.0) -> dict:
    """Predict a student's best-of-N success curves from TEACHER measurements plus (beta, b).

    sigma_wording / mu_wording: s.d. / mean of paraphrase effects in teacher logit space (from the
    teacher's wording grid, sampling noise removed). sigma: the student's prompt-specific deviation
    (one draw per wording), from the (beta, sigma) fit. Seed axis: P(any success in N seeds of the
    original wording). Prompt axis: P(any success over N random paraphrases, one seed each), a
    no-feedback lower bound for prompt search. 'select' is the deployable quantity: the true
    success rate on fresh seeds of the wording a 1-seed judge picks among N. Returns teacher
    (beta=1, b=0, sigma=0) and student curves, to compare with measured curves on held-out students.
    """
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    post, _ = teacher_posterior(cT, nT, eps)
    u = np.array([rng.choice(_U, size=n_mc, p=row) for row in post])  # [P, n_mc] samples of logit q_T
    out = {}
    for name, (bb, b0, sg) in {"teacher": (1.0, 0.0, 0.0), "student": (beta, b, sigma)}.items():
        seed_curve, prompt_curve, select_curve = [], [], []
        for N in budgets:
            d = rng.normal(mu_wording, sigma_wording, size=u.shape + (N,))
            d[..., 0] = 0.0  # the original wording is always among the candidates
            p_w = expit(bb * (u[..., None] + d) + b0 + sg * rng.normal(size=u.shape + (N,)))
            p_seed = p_w[..., 0]
            seed_curve.append(float(np.mean(1 - (1 - p_seed) ** N)))
            prompt_curve.append(float(np.mean(1 - np.prod(1 - p_w, axis=-1))))
            verdict = rng.uniform(size=p_w.shape) < p_w
            pick = np.argmax(verdict + 1e-3 * (np.arange(N) == 0), axis=-1)
            select_curve.append(float(np.mean(np.take_along_axis(p_w, pick[..., None], -1))))
        out[name] = {"seed": dict(zip(budgets, seed_curve)), "prompt": dict(zip(budgets, prompt_curve)),
                     "select": dict(zip(budgets, select_curve))}
    return out


def bootstrap_tempering(cT, nT, cS, nS, n_boot: int = 200, seed: int = 0, **fit_kw) -> dict:
    """Point estimate plus percentile CI over prompts (bootstrap as multinomial reweighting of the
    prompts, which the unique-pair likelihood makes cheap; stratified within `groups` when given);
    `fit_kw` go to `fit_tempering`."""
    rng = np.random.default_rng(seed)
    cT, cS = np.asarray(cT), np.asarray(cS)
    est = fit_tempering(cT, nT, cS, nS, **fit_kw)
    groups = np.asarray(fit_kw.get("groups") if fit_kw.get("groups") is not None else np.zeros(len(cT))).astype(str)
    strata = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    boots, sigmas = [], []
    for _ in range(n_boot):
        wts = np.zeros(len(cT))
        for idx in strata:
            wts[idx] = rng.multinomial(len(idx), np.full(len(idx), 1 / len(idx)))
        f = fit_tempering(cT, nT, cS, nS, weights=wts, **fit_kw)
        boots.append(f["beta"])
        sigmas.append(f.get("sigma", np.nan))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    out = {**est, "beta_ci": [float(lo), float(hi)]}
    if "sigma" in est:
        out["sigma_ci"] = [float(x) for x in np.nanpercentile(sigmas, [2.5, 97.5])]
    return out


def amplification_slope(dT: np.ndarray, dS: np.ndarray, var_T: np.ndarray, var_S: np.ndarray) -> dict:
    """Deming (errors-in-both-variables) regression of student logit changes on teacher logit
    changes for prompt rewrites: dS ~ slope * dT. Under the tempered model the slope equals beta.
    var_*: per-item sampling variances of the logit differences (delta method)."""
    dT, dS = np.asarray(dT, float), np.asarray(dS, float)
    lam = float(np.mean(var_S) / max(np.mean(var_T), 1e-12))  # error-variance ratio
    sxx, syy, sxy = np.mean(dT ** 2), np.mean(dS ** 2), np.mean(dT * dS)  # through-origin moments
    slope = (syy - lam * sxx + np.sqrt((syy - lam * sxx) ** 2 + 4 * lam * sxy ** 2)) / (2 * sxy) if sxy != 0 else float("nan")
    return {"slope": float(slope), "lambda": lam, "n": int(len(dT))}


def smoothed_logit(c, n):
    """Jeffreys-smoothed logit and its delta-method variance."""
    c = np.asarray(c, float)
    p = (c + 0.5) / (n + 1)
    return np.log(p) - np.log1p(-p), 1.0 / ((n + 1) * p * (1 - p))


def teacher_coverage(teacher_emb: np.ndarray, method_emb: np.ndarray, teacher_success=None) -> float:
    """How well a method's K images cover the teacher's own samples for the ORIGINAL prompt:
    mean over teacher samples of the max cosine similarity to any method image. Restrict to the
    teacher samples that satisfy the checklist (`teacher_success`), and compute it in a feature
    space not used for selection, so diversity outside the teacher's (correct) support does not count."""
    t = teacher_emb / np.linalg.norm(teacher_emb, axis=1, keepdims=True)
    m = method_emb / np.linalg.norm(method_emb, axis=1, keepdims=True)
    if teacher_success is not None:
        t = t[np.asarray(teacher_success, bool)]
        if len(t) == 0:
            return float("nan")
    return float((t @ m.T).max(1).mean())


def knn_coverage(real: np.ndarray, fake: np.ndarray, k: int = 5) -> float:
    """Coverage (Naeem et al., ICML 2020): fraction of real samples whose k-NN ball (radius from the
    real set itself) contains at least one fake sample. Radii come from the reference set, so it
    stays meaningful with few fake samples (K = 4). Cosine distance on L2-normalised features.
    For teacher coverage pass only checklist-passing teacher samples (real) and checklist-passing
    method images (fake), with >= 32 teacher references."""
    r = real / np.linalg.norm(real, axis=1, keepdims=True)
    f = fake / np.linalg.norm(fake, axis=1, keepdims=True)
    if len(r) <= k or len(f) == 0:
        return float("nan") if len(r) <= k else 0.0
    d_rr = 1 - r @ r.T
    radii = np.sort(d_rr, axis=1)[:, k]  # k-th neighbour, excluding self at index 0
    d_rf = 1 - r @ f.T
    return float(np.mean((d_rf <= radii[:, None]).any(1)))


def paired_interaction_ci(gain_S: np.ndarray, gain_T: np.ndarray, n_boot: int = 2000, seed: int = 0) -> dict:
    """Difference-in-differences over intents: mean(gain_S - gain_T) with a paired bootstrap CI,
    where gain_* is a per-intent (wording-arm minus seed-arm) improvement for student / teacher."""
    rng = np.random.default_rng(seed)
    d = np.asarray(gain_S, float) - np.asarray(gain_T, float)
    boots = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"interaction": float(d.mean()), "ci": [float(lo), float(hi)], "n": int(len(d))}


def fit_tempering_grid(cT: np.ndarray, nT: int, cS: np.ndarray, nS: int, n_a: int = 10, n_e: int = 8,
                       eps: tuple[float, float] = (0.0, 0.0), eps_S: tuple[float, float] | None = None) -> dict:
    """Two-level fit on a wording x seed grid (counts [I intents, J wordings]):

        logit q_S(i, j) = beta * logit q_T(i, j) + b + sigma_I * a_i + sigma_W * e_ij

    sigma_I: intent-level re-addressing (shared by all wordings of an intent); sigma_W: wording-level
    re-addressing within an intent. P2 (wording gains) and P4 (transfer) depend on sigma_W, which the
    single-level fit on original wordings cannot see. Teacher cell rates are latent (EIV), a_i and
    e_ij are integrated by Gauss-Hermite quadrature."""
    from scipy.optimize import minimize
    from scipy.special import expit, gammaln, logsumexp

    cT, cS = np.asarray(cT), np.asarray(cS)
    I, J = cT.shape
    s0, s1 = eps_S if eps_S is not None else eps
    post, prior = teacher_posterior(cT.reshape(-1), nT, eps)
    keep = post.max(0) > 1e-8
    U = _U[keep]
    log_post = np.log(post[:, keep] + 1e-300).reshape(I, J, -1)
    xa, wa = np.polynomial.hermite_e.hermegauss(n_a)
    xe, we = np.polynomial.hermite_e.hermegauss(n_e)
    lwa, lwe = np.log(wa / wa.sum()), np.log(we / we.sum())
    c = cS[:, :, None, None].astype(float)
    lconst = gammaln(nS + 1) - gammaln(c + 1) - gammaln(nS - c + 1)

    def nll(theta):
        b1, b2, ls_i, ls_w = theta
        per_a = []
        for x, lw in zip(xa, lwa):
            eta = b1 * U[:, None] + b2 + np.exp(ls_i) * x + np.exp(ls_w) * xe[None, :]  # [U, E]
            m = np.clip(s0 + (1 - s0 - s1) * expit(eta), 1e-12, 1 - 1e-12)
            ll = lconst + c * np.log(m) + (nS - c) * np.log1p(-m)  # [I, J, U, E]
            cell = logsumexp(log_post + logsumexp(ll + lwe, axis=3), axis=2)  # [I, J]
            per_a.append(cell.sum(1) + lw)
        return -np.sum(logsumexp(np.stack(per_a, 1), axis=1))

    res = minimize(nll, x0=[1.0, 0.0, np.log(0.5), np.log(0.5)], method="L-BFGS-B")
    return {"beta": float(res.x[0]), "b": float(res.x[1]), "sigma_intent": float(np.exp(res.x[2])),
            "sigma_wording": float(np.exp(res.x[3])), "nll": float(res.fun), "prior": prior}


def predict_ledger(cT, nT: int, beta: float, b: float, sigma_intent: float, sigma_wording: float,
                   mu_w: float, s_w: float, k: int = 8, n_seeds: int = 16, thresholds=(0.25, 0.5, 0.75),
                   n_mc: int = 64, seed: int = 0) -> dict:
    """Pre-registrable ledger shares (original / reword / reseed_only / lost) for teacher and student
    from the law, the teacher's original-wording counts and the teacher's wording statistics
    (mu_w, s_w: mean / s.d. of paraphrase effects in teacher logit space). Restricted to
    teacher-reachable intents as in scripts/reach_ledger.py; 'reword' uses a 1-seed selector over
    k wordings and counts the chosen wording's TRUE rate (evolution is a stronger search, so its
    rung is bounded above by k -> larger)."""
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    post, _ = teacher_posterior(cT, nT)
    out = {}
    for name, (bb, b0, si, sw) in {"teacher": (1.0, 0.0, 0.0, 0.0),
                                    "student": (beta, b, sigma_intent, sigma_wording)}.items():
        shares = {t: {"original": 0.0, "reword": 0.0, "reseed_only": 0.0, "lost": 0.0} for t in thresholds}
        total = 0.0
        for row in post:
            u = rng.choice(_U, size=n_mc, p=row)
            reach_T = 1 - (1 - expit(u)) ** n_seeds  # teacher reachability, used as a weight
            d = rng.normal(mu_w, s_w, (n_mc, k))
            d[:, 0] = 0.0
            q = expit(bb * (u[:, None] + d) + b0 + si * rng.normal(size=(n_mc, 1)) + sw * rng.normal(size=(n_mc, k)))
            verdict = rng.uniform(size=q.shape) < q
            q_sel = q[np.arange(n_mc), np.argmax(verdict + 1e-3 * (np.arange(k) == 0), axis=1)]
            lucky = 1 - (1 - q[:, 0]) ** n_seeds
            for t in thresholds:
                orig = q[:, 0] >= t
                rew = (~orig) & (q_sel >= t)
                rest = ~(orig | rew)
                shares[t]["original"] += float(np.sum(reach_T * orig))
                shares[t]["reword"] += float(np.sum(reach_T * rew))
                shares[t]["reseed_only"] += float(np.sum(reach_T * rest * lucky))
                shares[t]["lost"] += float(np.sum(reach_T * rest * (1 - lucky)))
            total += float(np.sum(reach_T))
        out[name] = {t: {k_: v / total for k_, v in sh.items()} for t, sh in shares.items()}
    return out
