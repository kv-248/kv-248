import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GENEVAL_ROWS = [
    {"tag": "single_object", "include": [{"class": "bench", "count": 1}], "prompt": "a photo of a bench"},
    {"tag": "counting", "include": [{"class": "clock", "count": 2}], "exclude": [{"class": "clock", "count": 3}],
     "prompt": "a photo of two clocks"},
    {"tag": "color_attr", "include": [{"class": "wine glass", "count": 1, "color": "purple"},
                                      {"class": "apple", "count": 1, "color": "black"}],
     "prompt": "a photo of a purple wine glass and a black apple"},
    {"tag": "position", "include": [{"class": "teddy bear", "count": 1},
                                    {"class": "dog", "count": 1, "position": ["right of", 0]}],
     "prompt": "a photo of a dog right of a teddy bear"},
]


@pytest.fixture(scope="session")
def geneval_file(tmp_path_factory):
    p = tmp_path_factory.mktemp("data") / "geneval.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in GENEVAL_ROWS) + "\n")
    return str(p)


@pytest.fixture(scope="session")
def tiny_config(tmp_path_factory):
    """Families YAML pointing at a randomly initialised tiny SDXL pipeline (CPU)."""
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from make_tiny_pipeline import build

    pipe_dir = os.environ.get("DAP_TINY_SDXL") or build(str(tmp_path_factory.mktemp("tiny_sdxl")))
    cfg = tmp_path_factory.mktemp("cfg") / "families.yaml"
    cfg.write_text(f"""
tiny:
  - {{name: tiny-teacher, role: teacher, base: {pipe_dir}, steps: 3, guidance_scale: 5.0, cfg: true,
     resolution: 64, objective: none}}
  - {{name: tiny-student, role: student, base: {pipe_dir}, steps: 1, guidance_scale: 0.0, cfg: false,
     resolution: 64, objective: test, mode_seeking: true, scheduler: {{class: LCMScheduler}}}}
""")
    return str(cfg)
