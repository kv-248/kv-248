"""Harvest arXiv papers related to EOS / stopping / output length, with abstracts.

Usage: python harvest_arxiv.py OUT.jsonl
Respects the arXiv API rate limit (one request every 3 s). Dedupes by arXiv id
and records which queries matched each paper, so ranking can use query overlap.
"""
import json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query?"
NS = {"a": "http://www.w3.org/2005/Atom"}

# (query, max_results). Phrases are quoted so arXiv matches them as phrases.
QUERIES = [
    ('all:"EOS token"', 300), ('all:"end-of-sequence token"', 300), ('all:"end of sequence token"', 200),
    ('all:"EOS decision"', 100), ('all:"end-of-text token"', 100), ('all:"stop token" AND all:language', 150),
    ('all:"end-of-turn"', 100), ('all:"end of thinking"', 100), ('all:"end-of-thinking"', 100),
    ('all:"when to stop" AND all:"language model"', 200), ('all:"stopping criterion" AND all:"language model"', 100),
    ('all:"early stopping" AND all:reasoning AND all:"language model"', 150),
    ('all:termination AND all:generation AND all:"language model"', 150),
    ('all:"length extrapolation" AND all:EOS', 50), ('all:"output length" AND all:"language model"', 250),
    ('all:"response length" AND all:"language model"', 250), ('all:"length control" AND all:"language model"', 150),
    ('all:"length bias" AND all:"language model"', 150), ('all:"length planning"', 50),
    ('all:"response planning"', 50), ('all:"plan ahead" AND all:"language model"', 100),
    ('all:"length representation"', 50), ('all:"output length prediction"', 100),
    ('all:"long-form generation" AND all:length', 150), ('all:"ultra-long generation"', 50),
    ('all:overthinking AND all:reasoning', 300), ('all:underthinking', 50), ('all:"budget forcing"', 100),
    ('all:"thinking budget"', 100), ('all:"early exit" AND all:"reasoning model"', 100),
    ('all:"reasoning length" AND all:steering', 80), ('all:"attention sink"', 300),
    ('all:"massive activations"', 100), ('all:"repetition" AND all:"language model" AND all:neurons', 80),
    ('all:"neural text degeneration"', 150), ('all:"repetition loop" AND all:"language model"', 80),
    ('all:"infinite generation"', 50), ('all:"endless" AND all:"language model"', 80),
    ('all:"never stop" AND all:"language model"', 30), ('all:"verbose" AND all:attack AND all:"language model"', 80),
    ('all:"sponge" AND all:"language model"', 50), ('all:"energy-latency" AND all:attack', 50),
    ('all:"beam search curse"', 30), ('all:"empty translation"', 30), ('all:"inadequacy of the mode"', 20),
    ('all:"length generalization" AND all:"end-of-sequence"', 50), ('all:"sequence packing" AND all:pretraining', 80),
    ('all:"divergence attack"', 30), ('all:"extractable memorization"', 80),
    ('all:"self-dialogue" AND all:"language model"', 50), ('all:"persona drift"', 30),
    ('all:"model diffing"', 80), ('all:crosscoder', 80), ('all:"shallow" AND all:"fine-tuning" AND all:mechanistic', 60),
    ('all:"unlearning" AND all:"relearning"', 100), ('all:"refusal direction"', 80),
    ('all:"logit lens" AND all:suppression', 50), ('all:"entropy neurons"', 30),
    ('all:"variable-length" AND all:"diffusion language model"', 60), ('all:"length" AND all:"masked diffusion language model"', 60),
    ('all:"hallucination" AND all:"EOS"', 60), ('all:"knowledge boundary" AND all:"long-form"', 60),
    ('all:"facts exhaustion"', 20), ('all:"completeness" AND all:"generation" AND all:"hidden states"', 60),
    ('all:"sufficiency" AND all:"attention heads"', 40), ('all:"halting" AND all:transformer', 100),
    ('all:"adaptive computation" AND all:"language model"', 80), ('all:"stop reading"', 20),
    ('all:"length instruction"', 60), ('all:"verbosity" AND all:RLHF', 100),
]


def fetch(query, max_results, start=0, page=100):
    out = []
    while start < max_results:
        n = min(page, max_results - start)
        url = API + urllib.parse.urlencode({
            "search_query": query, "start": start, "max_results": n,
            "sortBy": "relevance", "sortOrder": "descending"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    xml = r.read()
                break
            except Exception as e:  # network hiccup or 503 from arXiv
                time.sleep(5 * (attempt + 1))
        else:
            print(f"FAILED {query} @ {start}", file=sys.stderr)
            return out
        entries = ET.fromstring(xml).findall("a:entry", NS)
        for e in entries:
            aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
            out.append({
                "id": re.sub(r"v\d+$", "", aid),
                "title": re.sub(r"\s+", " ", e.find("a:title", NS).text).strip(),
                "abstract": re.sub(r"\s+", " ", e.find("a:summary", NS).text).strip(),
                "published": e.find("a:published", NS).text[:10],
                "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                "categories": [c.get("term") for c in e.findall("a:category", NS)],
            })
        time.sleep(3)
        if len(entries) < n:
            break
        start += n
    return out


def main(path):
    papers = {}
    for q, m in QUERIES:
        got = fetch(q, m)
        for p in got:
            papers.setdefault(p["id"], {**p, "queries": []})["queries"].append(q)
        print(f"{len(got):4d}  {q}   (total {len(papers)})", file=sys.stderr, flush=True)
    with open(path, "w") as fh:
        for p in papers.values():
            fh.write(json.dumps(p) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
