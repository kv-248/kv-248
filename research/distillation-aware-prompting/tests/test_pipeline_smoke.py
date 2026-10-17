"""End-to-end plumbing on a tiny random SDXL pipeline (CPU, seconds)."""

import json
import subprocess
import sys
from pathlib import Path

from dap.evolve import EvolveConfig, evolve
from dap.generation import Generator, load_families
from dap.judges import MockJudge
from dap.llm import ScriptedLLM
from dap.questions import load_geneval

ROOT = Path(__file__).resolve().parents[1]


def _gen(cfg, name):
    spec = next(v for v in load_families(cfg)["tiny"] if v.name == name)
    return Generator(spec, device="cpu", dtype="float32").load()


def test_nfe_accounting(tiny_config):
    t, s = _gen(tiny_config, "tiny-teacher"), _gen(tiny_config, "tiny-student")
    t.generate(["a cat", "a dog"], [0, 1])
    s.generate(["a cat"], [0])
    assert t.nfe == 2 * 3 * 2 and s.nfe == 1
    a = s.generate(["a cat"], [7])[0]
    b = s.generate(["a cat"], [7])[0]
    assert list(a.getdata()) == list(b.getdata())  # seeded determinism


def test_evolve_respects_budget(tiny_config, geneval_file):
    gen = _gen(tiny_config, "tiny-student")
    intent = load_geneval(geneval_file, tags=["color_attr"])[0]
    llm = ScriptedLLM(['["a purple wine glass next to a black apple", "black apple and purple wine glass"]',
                       '["purple glass, black apple"]'])
    res = evolve(intent, gen, MockJudge(), llm, EvolveConfig(budget_nfe=6, early_stop=False))
    assert res.nfe_used <= 6 and len(res.history) == res.nfe_used
    assert res.history[0].op == "original" and {c.op for c in res.history[1:]} <= {"reflect", "crossover"}
    res_rule = evolve(intent, gen, MockJudge(), None, EvolveConfig(budget_nfe=4, early_stop=False))
    assert all(c.op in ("original", "rule") for c in res_rule.history)


def _run(script, *args):
    r = subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "scripts" / script), *args],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr[-3000:]
    return r.stdout


def test_sharpening_script(tiny_config, geneval_file, tmp_path):
    out = _run("sharpening.py", "--family", "tiny", "--config", tiny_config, "--geneval-meta", geneval_file,
               "--n-seeds", "4", "--device", "cpu", "--dtype", "float32", "--out", str(tmp_path), "--save-images",
               "--n-boot", "5", "--teacher-cfgs", "9")
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert set(summary) == {"tiny-teacher", "tiny-student", "tiny-teacher-cfg9"}
    assert "sharpening_vs_teacher" in summary["tiny-student"]
    assert (tmp_path / "images" / "tiny-student" / "00000" / "samples" / "0003.png").exists()
    assert "tiny-student" in out


def test_variance_script(tiny_config, geneval_file, tmp_path):
    paras = tmp_path / "paras.json"
    its = load_geneval(geneval_file)
    paras.write_text(json.dumps({i.prompt: [i.prompt + " (v1)", "photo: " + i.prompt] for i in its}))
    _run("variance.py", "--family", "tiny", "--config", tiny_config, "--geneval-meta", geneval_file,
         "--n-para", "3", "--n-seeds", "2", "--paraphrases", str(paras), "--device", "cpu", "--dtype", "float32",
         "--out", str(tmp_path / "e2"))
    summary = json.loads((tmp_path / "e2" / "summary.json").read_text())
    assert 0.0 <= summary["tiny-student"]["rho"] <= 1.0


def test_search_scaling_script(tiny_config, geneval_file, tmp_path):
    paras = tmp_path / "paras.json"
    its = load_geneval(geneval_file)
    paras.write_text(json.dumps({i.prompt: [i.prompt + " (v1)", "photo: " + i.prompt] for i in its}))
    out = _run("search_scaling.py", "--family", "tiny", "--student", "tiny-student", "--config", tiny_config,
               "--geneval-meta", geneval_file, "--budgets", "1", "2", "4", "--methods", "noise", "prompt", "dape",
               "teacher", "--paraphrases", str(paras), "--device", "cpu", "--dtype", "float32", "--out", str(tmp_path / "e3"))
    summary = json.loads((tmp_path / "e3" / "summary.json").read_text())["mock"]
    assert set(summary) == {"noise", "prompt", "dape", "teacher"}
    assert "6" in summary["teacher"]  # teacher reported at its native cost (3 steps x CFG)
    assert "teacher" in out


def test_evolve_teacher_reference(tiny_config, geneval_file):
    import numpy as np

    from dap.embed import pixel_embed
    from dap.evolve import coverage_subset

    gen = _gen(tiny_config, "tiny-student")
    teacher = _gen(tiny_config, "tiny-teacher")
    intent = load_geneval(geneval_file, tags=["counting"])[0]
    t_embs = pixel_embed(teacher.generate([intent.prompt] * 3, [0, 1, 2]))
    res = evolve(intent, gen, MockJudge(), None, EvolveConfig(budget_nfe=4, early_stop=False, ref_weight=0.5),
                 embed_fn=pixel_embed, teacher_embs=t_embs)
    assert all(0 < c.precision <= 1.0 + 1e-6 for c in res.history)
    assert all(abs(c.fitness - (c.success_rate + c.soft + 0.5 * c.precision)) < 1e-9 for c in res.history)
    picks = coverage_subset(res.history, t_embs, 2)
    assert len(set(picks)) == min(2, len(res.history)) and np.isfinite(res.best.fitness)


def test_amplification_script(tiny_config, geneval_file, tmp_path):
    paras = tmp_path / "paras.json"
    rew = tmp_path / "rew.json"
    its = load_geneval(geneval_file)
    paras.write_text(json.dumps({i.prompt: [i.prompt + " (v1)", "photo: " + i.prompt] for i in its}))
    rew.write_text(json.dumps({i.prompt: {"official_pe": "a detailed photo, " + i.prompt} for i in its}))
    _run("amplification.py", "--family", "tiny", "--config", tiny_config, "--geneval-meta", geneval_file,
         "--paraphrases", str(paras), "--rewrites", str(rew), "--n-para", "3", "--n-seeds", "3",
         "--device", "cpu", "--dtype", "float32", "--out", str(tmp_path / "e3"))
    s = json.loads((tmp_path / "e3" / "summary.json").read_text())["tiny-student"]
    assert set(s["by_source"]) == {"paraphrase", "official_pe"} and s["amp"]["n"] == 4 * 3
