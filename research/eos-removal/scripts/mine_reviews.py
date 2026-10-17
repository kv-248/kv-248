"""Mine ICLR 2018-2023 reviews (Kaggle: juanjomontero/iclr-papers-and-reviews-data-2018-2023)
for what reviewers reward and penalise in LM-analysis / interpretability / decoding papers.

Usage: python mine_reviews.py DATA_DIR OUT_DIR
Writes themes.tsv (criticism theme x decision counts) and excerpts.md (review text of the
most topically relevant papers).
"""
import os, re, sys
from collections import defaultdict
import pandas as pd

LM = re.compile(r"language model|\bLLMs?\b|text generation|\bNLP\b|\bGPT|\bBERT|transformer|"
                r"neural machine translation|\btokens?\b", re.I)
ANALYSIS = re.compile(r"interpretab|probing|probe|mechanis|circuit|neuron|attention head|"
                      r"representations?|degenerat|repetit|decoding|length|stop|termination|sampling|"
                      r"fine-tun|analy[sz]", re.I)
CORE = re.compile(r"degenerat|repetit|decoding|length|stop|termination|end-of|EOS|probing|"
                  r"interpretab|mechanis|neuron|circuit|sampling|attention head|what do", re.I)
# Recurring reviewer criticisms, as regexes over review text.
THEMES = {
    "correlational_only (probes != use)": r"correlat|causal|probing (does not|doesn't|cannot)|probe.{0,40}(not|n't) (imply|mean|show)|intervention",
    "single/small model scope": r"(only|single|one) (model|architecture|family)|small(er)? models?|larger models|scale (up|to)|gpt-2 only|toy",
    "limited novelty / known result": r"novelty|not (new|novel|surprising)|well[- ]known|already (known|shown)|incremental|prior work (has|already)",
    "missing baselines / comparisons": r"baseline|compare (with|to|against)|comparison",
    "synthetic / unrealistic setup": r"synthetic|toy|artificial|unrealistic|real[- ]world",
    "unclear significance / so-what": r"significance|so what|practical (use|implication|value)|why (should|does) (we|this) (care|matter)|implications",
    "insufficient analysis / ablations": r"ablation|more analysis|deeper analysis|insight",
    "statistical rigor / variance": r"variance|seeds?|confidence interval|statistical(ly)? significan|error bars?",
    "evaluation metric validity": r"metric|human evaluation|automatic evaluation",
    "generalization across tasks/data": r"generali[sz]e|other (tasks|datasets|domains)|out-of-distribution",
    "clarity / writing": r"clarity|unclear|hard to follow|poorly written|confusing",
    "theory lacking / handwavy": r"theor(y|etical)|formal|justif",
}
PRAISE = {
    "surprising finding": r"surpris|interesting finding|intriguing|counter-?intuitive",
    "clear causal evidence": r"causal (evidence|intervention|analysis)|ablat\w+ (show|confirm)",
    "simple & effective": r"simple (yet|and|but) effective|simple method|elegant",
    "thorough experiments": r"thorough|extensive (experiments|evaluation)|comprehensive",
    "practical impact": r"practical|useful for practitioners|real[- ]world impact",
}


def load_year(d, y):
    r = pd.read_csv(os.path.join(d, f"iclr_{y}_reviews.csv"))
    p = pd.read_csv(os.path.join(d, f"iclr_{y}_papers.csv"))
    dec = r[r.Type.isin(["decision", "recommendation"]) & r.Content.astype(str).str.match(r"(Accept|Reject|Invite)")]
    dec = dec.groupby("Forum").Content.first()
    text_types = {"review", "main_review", "strength_and_weaknesses", "summary_of_the_review",
                  "metareview", "metareview:_summary,_strengths_and_weaknesses", "comment"}
    rev = r[r.Type.isin(text_types)]
    abst = r[r.Type == "abstract"].groupby("Forum").Content.first()
    rows = []
    for _, pp in p.iterrows():
        f = pp.Forum
        texts = rev[rev.Forum == f]
        rows.append({"year": y, "forum": f, "title": pp.Title, "decision": str(dec.get(f, "?")),
                     "abstract": str(abst.get(f, "")),
                     "reviews": [(t, str(c)) for t, c in zip(texts.Type, texts.Content) if t != "comment"],
                     "n_comments": int((texts.Type == "comment").sum())})
    return rows


def main(d, out):
    os.makedirs(out, exist_ok=True)
    papers = [x for y in range(2018, 2024) for x in load_year(d, y)]
    rel = [x for x in papers if LM.search(x["title"] + " " + x["abstract"])
           and ANALYSIS.search(x["title"] + " " + x["abstract"][:600])]
    core = [x for x in rel if CORE.search(x["title"])]
    counts = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for x in rel:
        acc = "accept" if x["decision"].startswith("Accept") else ("reject" if x["decision"].startswith("Reject") else "other")
        totals[acc] += 1
        blob = " ".join(c for _, c in x["reviews"])
        for name, rx in {**THEMES, **{"PRAISE: " + k: v for k, v in PRAISE.items()}}.items():
            if re.search(rx, blob, re.I):
                counts[name][acc] += 1
    with open(os.path.join(out, "themes.tsv"), "w") as fh:
        fh.write(f"theme\taccepted(n={totals['accept']})\trejected(n={totals['reject']})\tacc_rate\trej_rate\n")
        for name, c in counts.items():
            a, r = c["accept"] / max(1, totals["accept"]), c["reject"] / max(1, totals["reject"])
            fh.write(f"{name}\t{c['accept']}\t{c['reject']}\t{a:.2f}\t{r:.2f}\n")
    with open(os.path.join(out, "excerpts.md"), "w") as fh:
        for x in sorted(core, key=lambda z: (z["year"], z["title"])):
            fh.write(f"## [{x['year']}] {x['title']} — {x['decision']}\nhttps://openreview.net/forum?id={x['forum']}\n\n")
            for t, c in x["reviews"]:
                if t in ("metareview", "metareview:_summary,_strengths_and_weaknesses", "strength_and_weaknesses", "main_review", "review"):
                    fh.write(f"**{t}**: {re.sub(r'\\s+', ' ', c)[:1800]}\n\n")
    print(f"papers={len(papers)} topical={len(rel)} core={len(core)} totals={dict(totals)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
