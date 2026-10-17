"""Scan papercopilot/paperlists JSON dumps for papers on stopping / EOS / output length.

Usage: python scan_venues.py /path/to/paperlists > hits.tsv
Prints venue, status, mean recommendation/rating, title, matched pattern.
"""
import json, re, sys, glob, os

PATTERNS = {
    "eos": r"\b(eos|end[- ]of[- ](sequence|text|turn|thinking))\b|<\|endoftext\|>|stop token|stopping token",
    "termination": r"\b(when to stop|stopping (decision|criterion|criteria|point)|termination|halting|early stopping of (generation|reasoning)|stop (generating|thinking|reasoning))\b",
    "length": r"\b(output length|response length|generation length|length (control|bias|generali[sz]ation|extrapolation|prediction|representation|planning)|verbosity|overly long)\b",
    "overthinking": r"\b(overthinking|underthinking|budget forcing|thinking budget|reasoning length|early exit(ing)? (in|for|of) reasoning)\b",
    "sink": r"\battention sinks?\b|massive activations?",
    "degeneration": r"\b(degenerat(e|ion)|repetition loops?|repetitive generation|endless generation|infinite generation|never stop)\b",
}
RX = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}

def mean(s):
    try:
        xs = [float(x) for x in str(s).split(";") if x.strip() not in ("", "nan")]
        return sum(xs) / len(xs) if xs else float("nan")
    except ValueError:
        return float("nan")

root = sys.argv[1]
for path in sorted(glob.glob(os.path.join(root, "*", "*.json"))):
    venue = os.path.basename(path)[:-5]
    if not re.match(r"(iclr|icml|nips|acl|emnlp|naacl|colm)20(2[2-6])", venue):
        continue
    with open(path) as fh:
        head = fh.read(200)
        if "git-lfs" in head:
            continue
        fh.seek(0)
        try:
            papers = json.load(fh)
        except json.JSONDecodeError:
            continue
    for p in papers:
        text = f"{p.get('title','')} {p.get('abstract','')} {p.get('keywords','')}"
        hits = [k for k, rx in RX.items() if rx.search(text)]
        if not hits:
            continue
        score = mean(p.get("recommendation") or p.get("rating") or "")
        print("\t".join([venue, str(p.get("status", "")), f"{score:.2f}", ",".join(hits),
                         p.get("title", "").replace("\t", " "), p.get("site", "")]))
