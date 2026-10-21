"""Tiro v0: reference checker, renderer and canonicalizer for a reasoning shorthand.

A Tiro trace is line-oriented. Each non-blank line is one of:

    # comment
    def $NAME := gloss                      declare a coined term before using it
    <id> <op>[!] <body> [<- <id> ...] [~<conf>]

Example:

    def $TR := tests/test_io.py::test_read
    s3 obs  $TR fails with UnicodeDecodeError
    s4 hyp  read_text uses the platform default encoding   <- s3 ~0.6

Usage:
    python tiro.py check  FILE     validate and lint; exit 1 on errors
    python tiro.py render FILE     render to plain English
    python tiro.py canon  FILE     print the canonical form
"""

import re
import sys
from dataclasses import dataclass, field

OPS = {
    "goal": "Goal",
    "cons": "Constraint",
    "obs": "Observation",
    "asm": "Assumption (unverified)",
    "hyp": "Hypothesis",
    "inf": "Inference",
    "chk": "Check",
    "plan": "Plan",
    "exp": "Expectation",
    "act": "Action",
    "rev": "Revision",
    "ask": "Question for the human",
    "ans": "Answer",
    "note": "Note",
}
NEEDS_DEPS = {"inf", "chk", "exp", "act", "rev", "ans"}
TAKES_CONF = {"asm", "hyp", "inf", "ans"}
WEAK_CONF = 0.7
NOTE_MAX_CHARS = 120

DEF_RE = re.compile(r"^def\s+\$(?P<name>[A-Za-z_]\w*)\s*:=\s*(?P<gloss>.+?)\s*$")
STEP_RE = re.compile(
    r"^(?P<id>s\d+)\s+(?P<op>[a-z]+)(?P<bang>!?)\s+(?P<body>.*?)"
    r"(?:\s+<-\s+(?P<deps>s\d+(?:\s+s\d+)*))?"
    r"(?:\s+~(?P<conf>\d+(?:\.\d+)?))?\s*$"
)
SYM_RE = re.compile(r"\$([A-Za-z_]\w*)")


@dataclass
class Step:
    id: str
    op: str
    body: str
    deps: list
    conf: float | None
    irreversible: bool
    line: int


@dataclass
class Trace:
    symbols: dict = field(default_factory=dict)  # name -> gloss, in declaration order
    steps: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def step(self, sid):
        return next(s for s in self.steps if s.id == sid)


def parse(text):
    tr = Trace()
    seen = set()
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if m := DEF_RE.match(line):
            name = m["name"]
            if name in tr.symbols:
                tr.errors.append(f"line {n}: ${name} declared twice")
            tr.symbols[name] = m["gloss"]
            continue
        m = STEP_RE.match(line)
        if not m:
            tr.errors.append(f"line {n}: cannot parse: {line!r}")
            continue
        sid, op = m["id"], m["op"]
        deps = m["deps"].split() if m["deps"] else []
        conf = float(m["conf"]) if m["conf"] else None
        if op not in OPS:
            tr.errors.append(f"line {n}: unknown op {op!r}")
        if sid in seen:
            tr.errors.append(f"line {n}: duplicate step id {sid}")
        for d in deps:
            if d not in seen:
                tr.errors.append(f"line {n}: {sid} depends on {d}, which is not an earlier step")
        if op in NEEDS_DEPS and not deps:
            tr.errors.append(f"line {n}: {op} step {sid} must cite what it depends on")
        if m["bang"] and op != "act":
            tr.errors.append(f"line {n}: only act steps can be marked irreversible (!)")
        if conf is not None and (op not in TAKES_CONF or not 0 <= conf <= 1):
            tr.errors.append(f"line {n}: confidence ~{m['conf']} not allowed on {op} or out of [0, 1]")
        for name in SYM_RE.findall(m["body"]):
            if name not in tr.symbols:
                tr.errors.append(f"line {n}: ${name} used before it was declared with def")
        seen.add(sid)
        tr.steps.append(Step(sid, op, m["body"], deps, conf, bool(m["bang"]), n))
    return tr


def support(tr, step):
    """All steps that `step` transitively depends on."""
    out, stack = {}, list(step.deps)
    while stack:
        sid = stack.pop()
        if sid not in out:
            out[sid] = tr.step(sid)
            stack.extend(out[sid].deps)
    return out.values()


def lint(tr):
    """Warnings and breakpoints a human monitor should see. Assumes no parse errors."""
    warnings, breakpoints = [], []
    used = {d for s in tr.steps for d in s.deps}
    for i, s in enumerate(tr.steps):
        if s.op == "act":
            earlier = tr.steps[:i]
            covered = any(tr.step(d).op == "exp" for d in s.deps) or any(
                e.op == "exp" and set(e.deps) & set(s.deps) for e in earlier
            )
            if not covered:
                warnings.append(f"{s.id}: action taken with no stated expectation (exp) to check it against")
        if s.op == "rev":
            for d in s.deps:
                if tr.step(d).op == "exp":
                    warnings.append(f"{s.id}: expectation {d} was violated")
        if s.op == "hyp" and s.id not in used:
            warnings.append(f"{s.id}: hypothesis is never checked or used")
        if s.op == "note" and len(s.body) > NOTE_MAX_CHARS:
            warnings.append(f"{s.id}: free-text note is {len(s.body)} chars (limit {NOTE_MAX_CHARS})")
        if s.op == "act" and s.irreversible:
            weak = [
                p for p in support(tr, s)
                if p.op == "asm" or (p.op in ("hyp", "inf") and (p.conf or 0) < WEAK_CONF)
            ]
            if weak:
                why = ", ".join(f"{p.id} ({p.op}{'' if p.conf is None else f' ~{p.conf}'})" for p in weak)
                breakpoints.append(f"{s.id}: irreversible action rests on unverified support: {why}")
    return warnings, breakpoints


def render(tr):
    glossed, out = set(), []

    def expand(m):
        name = m[1]
        if name in glossed:
            return name
        glossed.add(name)
        return f'{name} ("{tr.symbols[name]}")'

    for s in tr.steps:
        label = "IRREVERSIBLE action" if s.irreversible else OPS[s.op]
        text = SYM_RE.sub(expand, s.body)
        extras = []
        if s.conf is not None:
            extras.append(f"confidence {s.conf:.0%}")
        if s.deps:
            extras.append("based on " + ", ".join(s.deps))
        tail = f" ({'; '.join(extras)})" if extras else ""
        out.append(f"[{s.id}] {label}: {text}{tail}")
    return "\n".join(out)


def canon(tr):
    """Canonical form: free surface choices (ids, names, spacing, dep order, digits) are erased.

    Every choice a writer can make without changing meaning is a channel that can
    carry hidden information. Fixing those choices closes the channel exactly.
    Free text inside bodies still needs a paraphraser; this handles the syntax.
    """
    ids = {s.id: f"s{i}" for i, s in enumerate(tr.steps, 1)}
    names = {name: f"S{i}" for i, name in enumerate(tr.symbols, 1)}
    out = [f"def ${names[k]} := {' '.join(v.split())}" for k, v in tr.symbols.items()]
    for s in tr.steps:
        body = SYM_RE.sub(lambda m: "$" + names[m[1]], " ".join(s.body.split()))
        line = f"{ids[s.id]} {s.op}{'!' if s.irreversible else ''} {body}"
        if s.deps:
            line += " <- " + " ".join(sorted({ids[d] for d in s.deps}, key=lambda x: int(x[1:])))
        if s.conf is not None:
            line += f" ~{round(s.conf, 1)}"
        out.append(line)
    return "\n".join(out)


def main(argv):
    if len(argv) != 3 or argv[1] not in ("check", "render", "canon"):
        print(__doc__)
        return 2
    with open(argv[2], encoding="utf-8") as f:
        tr = parse(f.read())
    if tr.errors:
        print("\n".join("error: " + e for e in tr.errors))
        return 1
    if argv[1] == "render":
        print(render(tr))
    elif argv[1] == "canon":
        print(canon(tr))
    else:
        warnings, breakpoints = lint(tr)
        print(f"ok: {len(tr.steps)} steps, {len(tr.symbols)} declared symbols")
        for w in warnings:
            print("warning: " + w)
        for b in breakpoints:
            print("BREAKPOINT: " + b)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
