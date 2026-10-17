"""Reword-K: the remedy the analysis predicts for mode-seeking students.

One call to a small instruct LLM returns K intent-preserving rewordings that are written
*jointly* (so they differ from each other in composition, viewpoint and phrasing order rather
than being K i.i.d. samples). Each rewording is rendered with one seed. Rewrites must not add
objects or attributes; `attribute_injection` measures how often they do, so diversity that
comes from the LLM inventing content is reported rather than counted as a win.
"""

from __future__ import annotations

import json

from .rewrite import parse_list

REWORD_SYS = (
    "You write {k} alternative phrasings of a text-to-image prompt for a fast few-step image model. "
    "Each phrasing must request EXACTLY the same content: the same objects, counts, colors, attributes, "
    "spatial relations and style. Do not add new objects, attributes or style words. Make the {k} phrasings "
    "differ from each other: change word order, which entity is mentioned first, sentence structure, and "
    "how the composition/viewpoint is described (e.g. 'seen from the left', 'close-up', 'in the foreground') "
    "when that does not contradict the prompt. Name every entity with its attributes explicitly. Keep each "
    "phrasing under 40 words. Return a JSON list of {k} strings."
)

EXPAND_SYS = (  # Prompt-Expansion-style control: generic diverse expansions, no intent constraint
    "Expand the text-to-image prompt into {k} diverse, detailed and visually rich prompts. "
    "Return a JSON list of {k} strings."
)

INJECTION_SYS = (
    "You check prompt rewrites. For each rewrite, answer whether it ADDS content that the original "
    "prompt does not request (a new object, attribute, color, count, text, or a specific style). "
    "Composition or viewpoint wording does not count as added content. Return a JSON list of booleans, "
    "one per rewrite, true if content was added."
)


def reword_k(llm, prompt: str, k: int = 4, temperature: float = 0.8) -> list[str]:
    raw = llm.chat([{"role": "system", "content": REWORD_SYS.format(k=k)},
                    {"role": "user", "content": prompt}], temperature=temperature, max_tokens=80 * k)
    outs = parse_list(raw, k)
    return (outs + [prompt] * k)[:k]


def expand_k(llm, prompt: str, k: int = 4, temperature: float = 0.9) -> list[str]:
    raw = llm.chat([{"role": "system", "content": EXPAND_SYS.format(k=k)},
                    {"role": "user", "content": prompt}], temperature=temperature, max_tokens=150 * k)
    outs = parse_list(raw, k)
    return (outs + [prompt] * k)[:k]


def attribute_injection(llm, original: str, rewrites: list[str]) -> list[bool]:
    user = f"Original prompt: {original}\nRewrites: {json.dumps(rewrites)}"
    raw = llm.chat([{"role": "system", "content": INJECTION_SYS}, {"role": "user", "content": user}],
                   temperature=0.0, max_tokens=20 * len(rewrites) + 20)
    try:
        start, end = raw.index("["), raw.rindex("]") + 1
        flags = [bool(x) for x in json.loads(raw[start:end].lower())]
    except (ValueError, json.JSONDecodeError):
        flags = []
    return (flags + [False] * len(rewrites))[: len(rewrites)]
