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

_REWORD_BASE = (
    "You write {k} alternative phrasings of a text-to-image prompt for a fast few-step image model. "
    "Each phrasing must request EXACTLY the same content: the same objects, counts, colors, attributes, "
    "spatial relations and style. Do not add new objects, attributes or style words. "
)
_REWORD_DIVERSE = ("Make the {k} phrasings differ from each other: change word order, which entity is mentioned "
                   "first, and sentence structure. ")
_REWORD_COMPOSITION = ("You may also vary how the composition/viewpoint is described (e.g. 'seen from the left', "
                       "'close-up', 'in the foreground') when that does not contradict the prompt. ")
_REWORD_BINDING = "Name every entity with its attributes explicitly. "
_REWORD_TAIL = "Keep each phrasing under 40 words. Return a JSON list of {k} strings."
REWORD_SYS = _REWORD_BASE + _REWORD_DIVERSE + _REWORD_COMPOSITION + _REWORD_BINDING + _REWORD_TAIL

# LLM-free control: diversity from generic composition tags only
COMPOSITION_TAGS = [
    "close-up", "wide shot", "seen from the left", "seen from the right", "top-down view", "low angle",
    "centered composition", "in the foreground", "in the background", "rule of thirds", "side view",
    "eye-level view", "from a distance", "tight framing", "symmetrical composition", "off-center",
]

EXPAND_SYS = (  # Prompt-Expansion-style control: generic diverse expansions, no intent constraint
    "Expand the text-to-image prompt into {k} diverse, detailed and visually rich prompts. "
    "Return a JSON list of {k} strings."
)

INJECTION_SYS = (
    "You check prompt rewrites. For each rewrite, answer whether it ADDS content that the original "
    "prompt does not request (a new object, attribute, color, count, text, or a specific style). "
    "{composition_rule} Return a JSON list of booleans, one per rewrite, true if content was added."
)
_LENIENT = "Composition or viewpoint wording does not count as added content."
_STRICT = "Composition or viewpoint wording (e.g. 'close-up', 'seen from the left') ALSO counts as added content."


def reword_system(k: int, diverse: bool = True, composition: bool = True, binding: bool = True) -> str:
    """Reword-K template with factorial switches for ablations."""
    return (_REWORD_BASE + (_REWORD_DIVERSE if diverse else "") + (_REWORD_COMPOSITION if composition else "")
            + (_REWORD_BINDING if binding else "") + _REWORD_TAIL).format(k=k)


def reword_k(llm, prompt: str, k: int = 4, temperature: float = 0.8, joint: bool = True, **switches) -> list[str]:
    """joint=True: one call returns a jointly diverse list (verbalized-sampling style); joint=False:
    K independent calls of the K=1 template (i.i.d. rewrites), the ablation for 'joint decoding'."""
    if not joint:
        outs = [reword_k(llm, prompt, 1, temperature, True, **switches)[0] for _ in range(k)]
        return outs
    raw = llm.chat([{"role": "system", "content": reword_system(k, **switches)},
                    {"role": "user", "content": prompt}], temperature=temperature, max_tokens=80 * k)
    outs = parse_list(raw, k)
    return (outs + [prompt] * k)[:k]


def tag_k(prompt: str, k: int, seed: int = 0) -> list[str]:
    """No-LLM baseline: the original prompt plus one random composition tag per image."""
    import random

    tags = random.Random(seed).sample(COMPOSITION_TAGS, k)
    return [f"{prompt}, {t}" for t in tags]


def expand_k(llm, prompt: str, k: int = 4, temperature: float = 0.9) -> list[str]:
    raw = llm.chat([{"role": "system", "content": EXPAND_SYS.format(k=k)},
                    {"role": "user", "content": prompt}], temperature=temperature, max_tokens=150 * k)
    outs = parse_list(raw, k)
    return (outs + [prompt] * k)[:k]


def attribute_injection(llm, original: str, rewrites: list[str], strict: bool = False) -> list[bool]:
    """Use a checker LLM different from the rewriter. strict=True also flags composition words."""
    user = f"Original prompt: {original}\nRewrites: {json.dumps(rewrites)}"
    system = INJECTION_SYS.format(composition_rule=_STRICT if strict else _LENIENT)
    raw = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
                   temperature=0.0, max_tokens=20 * len(rewrites) + 20)
    try:
        start, end = raw.index("["), raw.rindex("]") + 1
        flags = [bool(x) for x in json.loads(raw[start:end].lower())]
    except (ValueError, json.JSONDecodeError):
        flags = []
    return (flags + [False] * len(rewrites))[: len(rewrites)]
