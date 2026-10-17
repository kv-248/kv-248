"""Heuristic taxonomy of what models write after the point where they would have stopped.

Categories are checked in order; the first match wins. They are a cheap first pass to be
replaced by LLM-judged labels with a human-agreement check in the full study.

Usage: python summarize_continuations.py RUN_DIR [N_EXAMPLES]
"""
import json, os, re, sys
from collections import Counter

FOLLOW_UP = re.compile(r"let me know|feel free to|any (other|more|further) questions|hope (this|that|it) helps|"
                       r"is there anything else|happy to help|if you (have|need)", re.I)
USER_TURN = re.compile(r"<\|im_start\|>\s*user|^\s*(user|human|question)\s*:|\n\s*(user|human|question)\s*:", re.I)


def rep4(text):
    w = text.split()
    grams = [tuple(w[i:i + 4]) for i in range(len(w) - 3)]
    return 1 - len(set(grams)) / len(grams) if grams else 0.0


def label(rec):
    after, before = rec["after"], rec["before"]
    if rec["ended"]:
        return "stopped"
    if USER_TURN.search(after):
        return "new_user_turn"
    if "<|im_start|>" in after or "<|endoftext|>" in after:
        return "new_turn_or_doc"
    if rep4(after) > 0.5:
        return "loop"
    head = before.strip()[:40]
    if head and head in after:
        return "restart_answer"
    if FOLLOW_UP.search(after[:300]):
        return "follow_up_offer"
    return "elaboration_or_other"


def main(run, n_ex=3):
    with open(os.path.join(run, "continuations.json")) as fh:
        cont = json.load(fh)
    out = {}
    for tag, recs in cont.items():
        labs = [label(r) for r in recs]
        c = Counter(labs)
        out[tag] = {"n": len(recs), "shares": {k: v / len(recs) for k, v in c.most_common()},
                    "mean_len_ratio": sum(r["len"] / max(1, r["natural_len"]) for r in recs) / len(recs)}
        print(f"[{tag}] n={len(recs)} " + ", ".join(f"{k}={v / len(recs):.2f}" for k, v in c.most_common()))
        for k in c:
            for r, l in list((r, l) for r, l in zip(recs, labs) if l == k)[:n_ex]:
                print(f"   <{k}> {r['prompt'][:60]!r}\n      AFTER: {r['after'][:240]!r}")
    with open(os.path.join(run, "continuation_taxonomy.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
