"""Fetch papers citing seed papers from the Semantic Scholar Graph API (no key; backs off on 429).

Usage: python s2_citations.py OUT.jsonl arXiv:2010.07174 [arXiv:...]
"""
import json, sys, time, urllib.request, urllib.error

FIELDS = "title,year,externalIds,abstract,venue,citationCount"


def get(url, tries=8):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 3 * 2 ** k))
                continue
            raise
        except Exception:
            time.sleep(5)
    return None


def main(out, seeds):
    with open(out, "w") as fh:
        for s in seeds:
            off, n = 0, 0
            while True:
                d = get(f"https://api.semanticscholar.org/graph/v1/paper/{s}/citations?fields={FIELDS}&limit=100&offset={off}")
                if not d or not d.get("data"):
                    break
                for c in d["data"]:
                    p = c["citingPaper"]
                    fh.write(json.dumps({"seed": s, **p}) + "\n")
                    n += 1
                if d.get("next") is None:
                    break
                off = d["next"]
                time.sleep(3)
            print(f"{s}: {n} citing papers", flush=True)
            time.sleep(3)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
