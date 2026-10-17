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
