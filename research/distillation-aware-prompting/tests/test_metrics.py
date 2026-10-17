import numpy as np

from dap.metrics import mean_pass_at_k, pass_at_k, sharpening, variance_decomposition, vendi_score


def test_pass_at_k():
    assert pass_at_k(10, 0, 5) == 0.0
    assert pass_at_k(10, 10, 1) == 1.0
    assert abs(pass_at_k(10, 3, 1) - 0.3) < 1e-12
    assert abs(pass_at_k(4, 1, 2) - 0.5) < 1e-12
    succ = np.array([[1, 0, 0, 0], [1, 1, 1, 1]], dtype=bool)
    assert abs(mean_pass_at_k(succ, [1])[1] - (0.25 + 1.0) / 2) < 1e-12


def test_sharpening_detects_mode_seeking_student():
    rng = np.random.default_rng(0)
    qT = rng.uniform(0, 1, size=400)
    teacher = rng.uniform(size=(400, 32)) < qT[:, None]
    # mode-seeking student: solves a prompt (almost) always iff the teacher's rate > 0.5
    qS = np.where(qT > 0.5, 0.99, 0.01)
    student = rng.uniform(size=(400, 32)) < qS[:, None]
    sh = sharpening(teacher, student)
    assert sh["slope"] > 1.2
    assert sh["lost_reach"] > 0.3
    # an identical-distribution student is not sharpened
    same = rng.uniform(size=(400, 32)) < qT[:, None]
    assert abs(sharpening(teacher, same)["slope"] - 1) < 0.2


def test_variance_decomposition():
    rng = np.random.default_rng(0)
    I, J, S, D = 5, 4, 6, 16
    para = rng.normal(size=(I, J, 1, D))
    only_prompt = np.repeat(para, S, axis=2) + 5.0
    assert variance_decomposition(only_prompt)["rho"] > 0.99
    only_seed = np.repeat(rng.normal(size=(I, 1, 1, D)), J, axis=1) * 0 + rng.normal(size=(I, J, S, D)) + 5.0
    assert variance_decomposition(only_seed)["rho"] < 0.1


def test_vendi():
    x = np.ones((5, 8))
    assert abs(vendi_score(x) - 1.0) < 1e-6
    assert abs(vendi_score(np.eye(4)) - 4.0) < 1e-6


def test_coverage_subset_picks_complementary_modes():
    from dap.evolve import Candidate, coverage_subset

    teacher = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    embs = [[1, 0.05, 0], [0.98, 0.1, 0], [0, 0.05, 1], [0.05, 1, 0]]
    cands = [Candidate(f"p{i}", "x", None, [0], emb=np.array(e)) for i, e in enumerate(embs)]
    picks = set(coverage_subset(cands, teacher, 3))
    # one representative of the duplicated mode (0 or 1) plus the two other modes
    assert {2, 3} <= picks and len(picks & {0, 1}) == 1


def test_fit_tempering_recovers_beta():
    from scipy.special import expit, logit

    from dap.metrics import fit_tempering

    rng = np.random.default_rng(1)
    for beta_true in (1.0, 2.5):
        qT = rng.beta(0.8, 0.8, size=600)
        cT = rng.binomial(32, qT)
        qS = expit(beta_true * logit(np.clip(qT, 1e-4, 1 - 1e-4)) + 0.3)
        cS = rng.binomial(32, qS)
        est = fit_tempering(cT, 32, cS, 32)
        assert abs(est["beta"] - beta_true) < 0.25 * beta_true, est
        assert abs(est["b"] - 0.3) < 0.35, est


def test_amplification_slope():
    from dap.metrics import amplification_slope

    rng = np.random.default_rng(2)
    dT = rng.normal(0, 1, 2000)
    dS = 2.0 * dT
    vT, vS = np.full(2000, 0.05), np.full(2000, 0.2)
    est = amplification_slope(dT + rng.normal(0, 0.05 ** 0.5, 2000), dS + rng.normal(0, 0.2 ** 0.5, 2000), vT, vS)
    assert abs(est["slope"] - 2.0) < 0.1, est


def test_fit_tempering_judge_noise_correction():
    from scipy.special import expit, logit

    from dap.metrics import fit_tempering

    rng = np.random.default_rng(3)
    e0, e1 = 0.08, 0.12
    qT = rng.beta(0.8, 0.8, size=800)
    qS = expit(3.0 * logit(np.clip(qT, 1e-4, 1 - 1e-4)))
    cT = rng.binomial(16, e0 + (1 - e0 - e1) * qT)
    cS = rng.binomial(16, e0 + (1 - e0 - e1) * qS)
    naive = fit_tempering(cT, 16, cS, 16, model="binomial")["beta"]
    corrected = fit_tempering(cT, 16, cS, 16, eps=(e0, e1))["beta"]
    assert abs(corrected - 3.0) < 0.6 and abs(corrected - 3.0) < abs(naive - 3.0), (naive, corrected)


def test_predict_scaling_flips_axis_with_beta():
    from dap.metrics import predict_scaling

    rng = np.random.default_rng(4)
    cT = rng.binomial(16, rng.beta(0.8, 0.8, size=200))
    pred = predict_scaling(cT, 16, beta=4.0, b=0.0, sigma_wording=1.0, budgets=[1, 8])
    t, s = pred["teacher"], pred["student"]
    # seed search helps the teacher more than the sharpened student; prompt search keeps working for the student
    assert t["seed"][8] - t["seed"][1] > s["seed"][8] - s["seed"][1]
    assert s["prompt"][8] - s["prompt"][1] > s["seed"][8] - s["seed"][1]


def test_portability_prompt_vs_seed():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from portability import portability

    rng = np.random.default_rng(5)
    I, J, S, D = 40, 6, 5, 8
    wording = rng.normal(size=(I, J, 1))
    soft_T = wording + 0.3 * rng.normal(size=(I, J, S))
    # student: same wording effects (portable prompts), independent seed effects (non-portable seeds)
    soft_S = 2.0 * wording + 0.3 * rng.normal(size=(I, J, S))
    z = rng.normal(size=(I, J, S, D))
    r = portability(soft_T, soft_S, emb_T=z, emb_S=rng.normal(size=(I, J, S, D)))
    assert r["prompt_spearman"] > 0.7 and abs(r["seed_spearman"]) < 0.2
    assert r["proxy_regret"] < r["random_pick_regret"] and abs(r["seed_coupling"]) < 0.05
    r2 = portability(soft_T, soft_S, emb_T=z, emb_S=z + 0.1 * rng.normal(size=z.shape))
    assert r2["seed_coupling"] > 0.5


def test_random_effects_fit_separates_sharpening_from_prompt_noise():
    from scipy.special import expit, logit

    from dap.metrics import fit_tempering, self_split_control

    rng = np.random.default_rng(6)
    for beta, sig in [(1.0, 1.5), (1.5, 0.0)]:
        qT = np.clip(rng.beta(0.6, 0.5, 553), 1e-4, 1 - 1e-4)
        cT = rng.binomial(16, qT)
        cS = rng.binomial(16, expit(beta * logit(qT) + rng.normal(0, sig, 553)))
        est = fit_tempering(cT, 16, cS, 16)
        assert abs(est["beta"] - beta) < 0.2, est
        assert abs(est["sigma"] - sig) < 0.4, est
    qT = rng.beta(0.6, 0.5, 400)
    succ = rng.uniform(size=(400, 32)) < qT[:, None]
    ctl = self_split_control(succ)
    assert abs(ctl["beta"] - 1) < 0.2 and ctl["sigma"] < 0.4, ctl
