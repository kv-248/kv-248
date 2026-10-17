"""Turning prompts into verifiable yes/no questions (the intent checklist).

GenEval prompts come with structured metadata, so their checklists are built
deterministically. Free-form prompts (DPG-Bench, T2I-CompBench, user prompts) are
decomposed DSG-style by an LLM and cached. Fitness and evaluation are always
computed against the checklist of the ORIGINAL prompt, never the rewritten one,
so a rewrite cannot drift away from the user's intent and still score well.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

GENEVAL_URL = "https://raw.githubusercontent.com/djghosh13/geneval/main/prompts/evaluation_metadata.jsonl"

_IRREGULAR = {
    "person": "people", "mouse": "mice", "knife": "knives", "sheep": "sheep", "skis": "skis",
    "scissors": "scissors", "wine glass": "wine glasses", "skateboard": "skateboards",
}
_NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def plural(noun: str) -> str:
    if noun in _IRREGULAR:
        return _IRREGULAR[noun]
    if re.search(r"(s|sh|ch|x|z)$", noun):
        return noun + "es"
    if re.search(r"[^aeiou]y$", noun):
        return noun[:-1] + "ies"
    return noun + "s"


@dataclass
class Intent:
    """A user prompt plus the checklist used to judge any image made for it."""

    prompt: str
    questions: list[str]
    tag: str = "free"
    meta: dict = field(default_factory=dict)
    # Indices of questions that must hold for the image to count as a success
    # (GenEval-style strict success). Defaults to all questions.
    required: list[int] | None = None

    def required_idx(self) -> list[int]:
        return list(range(len(self.questions))) if self.required is None else self.required


def geneval_intent(row: dict) -> Intent:
    inc = row["include"]
    qs: list[str] = []
    for obj in inc:
        cls, n = obj["class"], obj.get("count", 1)
        if n == 1:
            qs.append(f"Is there a {cls} in the image?")
        else:
            qs.append(f"Are there exactly {_NUM.get(n, n)} {plural(cls)} in the image?")
        if "color" in obj:
            noun = cls if n == 1 else plural(cls)
            verb = "Is the" if n == 1 else "Are the"
            qs.append(f"{verb} {noun} {obj['color']}?")
        if "position" in obj:
            rel, ref = obj["position"]
            rel = {"left of": "to the left of", "right of": "to the right of"}.get(rel, rel)
            qs.append(f"Is the {cls} {rel} the {inc[ref]['class']}?")
    return Intent(prompt=row["prompt"], questions=qs, tag=row["tag"], meta=row)


def load_geneval(path: str | Path | None = None, limit: int | None = None, tags: list[str] | None = None) -> list[Intent]:
    if path is None or not Path(path).exists():
        import requests

        text = requests.get(GENEVAL_URL, timeout=60).text
        if path is not None:
            Path(path).write_text(text)
    else:
        text = Path(path).read_text()
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if tags:
        rows = [r for r in rows if r["tag"] in tags]
    intents = [geneval_intent(r) for r in rows]
    return intents[:limit] if limit else intents


DSG_SYSTEM = (
    "You decompose a text-to-image prompt into atomic yes/no verification questions "
    "(entities, counts, attributes, spatial relations, text to render, style). "
    "Each question must be answerable from the image alone. Return a JSON list of strings."
)


def decompose_with_llm(prompt: str, llm, cache_path: str | Path | None = None) -> Intent:
    cache: dict = {}
    if cache_path and Path(cache_path).exists():
        cache = json.loads(Path(cache_path).read_text())
    if prompt not in cache:
        raw = llm.chat([{"role": "system", "content": DSG_SYSTEM}, {"role": "user", "content": prompt}], temperature=0.0)
        match = re.search(r"\[.*\]", raw, flags=re.S)
        cache[prompt] = json.loads(match.group(0)) if match else [f"Does the image show {prompt}?"]
        if cache_path:
            Path(cache_path).write_text(json.dumps(cache, indent=1))
    return Intent(prompt=prompt, questions=cache[prompt])
