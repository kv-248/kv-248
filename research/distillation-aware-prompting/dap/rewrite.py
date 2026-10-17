"""Prompt operators: paraphrase, generic enhancement (baseline), reflective mutation
and crossover (LLM-based), plus deterministic rule operators used as an ablation
and for offline tests."""

from __future__ import annotations

import json
import re

PARAPHRASE_SYS = (
    "Rewrite the text-to-image prompt in {n} different ways that keep EXACTLY the same "
    "content (same objects, counts, colors, relations, style). Vary wording and word order only; "
    "add nothing, remove nothing. Return a JSON list of {n} strings."
)

ENHANCE_SYS = (
    "You are a prompt enhancer for a text-to-image model. Expand the user's prompt into one "
    "detailed, vivid prompt that keeps all requested content. Return only the prompt."
)

# Distillation-aware reflective mutation. `{model_card}` carries what we know about the
# target student (steps, objective, observed failure modes); it is ablated in experiments.
REFLECT_SYS = (
    "You improve prompts for a specific text-to-image model so that its image satisfies the "
    "user's intent.\nTarget model: {model_card}\n"
    "You will see the user's original prompt, the current prompt that was sent to the model, "
    "and the checklist items the generated image FAILED. Propose {n} revised prompts that fix "
    "the failures without breaking satisfied items. Never change the requested content; you may "
    "reorder, restate, make attributes and relations explicit, simplify, or repeat neglected "
    "elements. Return a JSON list of {n} strings."
)

CROSSOVER_SYS = (
    "Combine the strengths of two prompts written for the same user intent into {n} new "
    "prompts. Keep all requested content. Return a JSON list of {n} strings."
)

DEFAULT_MODEL_CARD = (
    "a {steps}-step distilled generator ({objective}). Few-step distilled models fix the "
    "global layout in the first step, often drop secondary objects, bind colors to the most "
    "salient object, and ignore negative prompts and guidance."
)


def parse_list(text: str, n: int | None = None) -> list[str]:
    match = re.search(r"\[.*\]", text, flags=re.S)
    items: list[str] = []
    if match:
        try:
            items = [str(s).strip() for s in json.loads(match.group(0)) if str(s).strip()]
        except json.JSONDecodeError:
            items = []
    if not items:
        items = [ln.strip(" -*0123456789.\"'") for ln in text.splitlines() if len(ln.strip()) > 3]
    return items[:n] if n else items


def paraphrase(llm, prompt: str, n: int = 8) -> list[str]:
    raw = llm.chat([{"role": "system", "content": PARAPHRASE_SYS.format(n=n)},
                    {"role": "user", "content": prompt}], temperature=0.9)
    return parse_list(raw, n)


def enhance(llm, prompt: str) -> str:
    return llm.chat([{"role": "system", "content": ENHANCE_SYS}, {"role": "user", "content": prompt}],
                    temperature=0.7).strip().strip('"')


def reflect_mutate(llm, original: str, current: str, failed: list[str], model_card: str, n: int = 2,
                   passed: list[str] | None = None) -> list[str]:
    user = (f"Original prompt: {original}\nCurrent prompt: {current}\n"
            f"FAILED checklist items: {json.dumps(failed)}\n"
            f"Satisfied checklist items: {json.dumps(passed or [])}")
    raw = llm.chat([{"role": "system", "content": REFLECT_SYS.format(n=n, model_card=model_card)},
                    {"role": "user", "content": user}], temperature=0.9)
    return parse_list(raw, n)


def crossover(llm, original: str, a: str, b: str, n: int = 1) -> list[str]:
    user = f"User intent: {original}\nPrompt A: {a}\nPrompt B: {b}"
    raw = llm.chat([{"role": "system", "content": CROSSOVER_SYS.format(n=n)},
                    {"role": "user", "content": user}], temperature=0.9)
    return parse_list(raw, n)


# ---- deterministic operators (no LLM) ------------------------------------------------

_REL = r"(to the left of|to the right of|above|below)"


def assertion(question: str) -> str:
    """'Is the cat to the left of the dog?' -> 'The cat is to the left of the dog.'"""
    q = question.strip()
    for pat, rep in [
        (r"^Is there (.+)\?$", r"There is \1."),
        (r"^Are there (.+)\?$", r"There are \1."),
        (rf"^Is the (.+?) {_REL} the (.+)\?$", r"The \1 is \2 the \3."),
        (r"^Is the (.+) (\w+)\?$", r"The \1 is \2."),
        (r"^Are the (.+) (\w+)\?$", r"The \1 are \2."),
    ]:
        if re.match(pat, q):
            return re.sub(pat, rep, q)
    return q


def failed_entities(question: str) -> list[str]:
    q = question.strip()
    for pat in (rf"^Is the (.+?) {_REL} the (.+)\?$",):
        m = re.match(pat, q)
        if m:
            return [m.group(1), m.group(3)]
    m = re.match(r"^Is there an? (.+?) in the image\?$", q)
    if m:
        return [m.group(1)]
    m = re.match(r"^Are there exactly (\w+ .+?) in the image\?$", q)
    if m:
        return [m.group(1)]
    m = re.match(r"^(?:Is|Are) the (.+) (\w+)\?$", q)
    if m:
        return [f"{m.group(2)} {m.group(1)}"]
    return []


def rule_mutations(prompt: str, failed: list[str]) -> list[str]:
    """Failure-targeted edits without an LLM: front-load or re-mention the entities named
    in failed checklist items, and state the failed items explicitly."""
    outs = []
    ents = [e for q in failed for e in failed_entities(q)]
    for e in dict.fromkeys(ents):
        outs.append(f"{e}, {prompt}")
        outs.append(f"{prompt}, with a clearly visible {e}")
    if failed:
        outs.append(prompt.rstrip(".") + ". " + " ".join(assertion(q) for q in failed))
    return list(dict.fromkeys(o for o in outs if o != prompt))
