"""Rank harvested arXiv papers by relevance to an EOS-removal / stopping-decision study.

Usage: python rank_corpus.py corpus.jsonl ranked.tsv
Score = weighted keyword hits in title (x3) and abstract, plus query overlap. Each paper
gets a cluster label from its strongest keyword group.
"""
import json, re, sys

GROUPS = {
    "eos_stop": (5, r"\bEOS\b|end[- ]of[- ](sequence|text|turn|thinking)|stop(ping)? (token|decision)|when to stop|termination|halt"),
    "length": (3, r"output length|response length|generation length|length (control|bias|planning|representation|prediction)|verbos|long-form generation|ultra-long"),
    "reasoning_stop": (3, r"overthink|underthink|budget forcing|thinking budget|early exit|stop thinking|reasoning length|efficient reasoning"),
    "interp": (3, r"probing|probe|mechanistic|interpretab|logit lens|steering|activation|neurons?|circuit|crosscoder|model diffing|sparse autoencoder|hidden states?"),
    "degeneration": (2, r"degenerat|repetit|loop|collapse|attractor"),
    "special_tokens": (2, r"attention sinks?|massive activation|special tokens?|delimiter|separator token"),
    "post_end": (4, r"after (the )?end|beyond the end|post-?EOS|continue generating|self-dialog|hallucinated (user|turn)|role (confusion|play)|persona drift"),
    "attack": (2, r"sponge|energy-latency|denial[- ]of[- ]service|resource exhaustion|endless|verbose (images|output)|jailbreak"),
    "finetune_shallow": (2, r"shallow|superficial|unlearn|relearn|refusal direction|fine-tuning (changes|affects)"),
}
LM = re.compile(r"language model|LLM|transformer|GPT|chat|instruction|reasoning model|text", re.I)


def score(p):
    t, a = p["title"], p["abstract"]
    s, best, bestv = 0.0, None, 0
    for g, (w, rx) in GROUPS.items():
        nt = len(re.findall(rx, t, re.I))
        na = len(re.findall(rx, a, re.I))
        v = w * (3 * nt + min(na, 4))
        s += v
        if v > bestv:
            best, bestv = g, v
    s += 2 * len(p["queries"])
    if not LM.search(t + " " + a):
        s *= 0.3
    yr = int(p["published"][:4])
    s *= 1.0 + 0.08 * max(0, yr - 2019)
    return s, best or "other"


rows = []
for line in open(sys.argv[1]):
    p = json.loads(line)
    s, g = score(p)
    rows.append((s, g, p))
rows.sort(key=lambda r: -r[0])
with open(sys.argv[2], "w") as fh:
    fh.write("score\tcluster\tarxiv\tdate\ttitle\n")
    for s, g, p in rows:
        fh.write(f"{s:.1f}\t{g}\t{p['id']}\t{p['published']}\t{p['title']}\n")
