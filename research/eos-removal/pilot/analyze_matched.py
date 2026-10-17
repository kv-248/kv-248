"""Completion probes with token-matched negatives.

The plain probe in `pilot_eos.py analyze` separates the final position from random earlier
positions, which the token embedding alone already does (the last token is usually sentence
punctuation). Here negatives are restricted to earlier positions whose current token also ends
a sentence or line, so the probe must tell "this sentence end is the end of the answer" from
"this is just another sentence end".

Usage: python analyze_matched.py --model M --out RUN_DIR
"""
import argparse, json, os, re, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from transformers import AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from pilot_eos import read_gen  # noqa: E402

BOUNDARY = re.compile(r"[.!?:;)\]]\s*$|\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    rows = [r for r in read_gen(a) if r["ended"] and len(r["resp_ids"]) >= 8]
    B = np.load(os.path.join(a.out, "feats_base.npz"))
    T = np.load(os.path.join(a.out, "feats_tuned.npz"))
    cur = []
    for k, d in zip(B["ex"], B["dist"]):
        r = rows[k]
        full = r["prompt_ids"] + r["resp_ids"]
        cur.append(tok.decode([full[len(full) - 1 - d]]))
    is_boundary = np.array([bool(BOUNDARY.search(t)) for t in cur])
    y = (B["dist"] == 0).astype(int)
    keep = (y == 1) | (is_boundary & (B["dist"] >= 3))
    tr, te = keep & (B["test"] == 0), keep & (B["test"] == 1)
    res = {"n_pos_train": int(y[tr].sum()), "n_neg_train": int((1 - y[tr]).sum()),
           "n_pos_test": int(y[te].sum()), "n_neg_test": int((1 - y[te]).sum()), "layers": []}
    print(f"train pos/neg {res['n_pos_train']}/{res['n_neg_train']}  test pos/neg {res['n_pos_test']}/{res['n_neg_test']}")
    print(f"{'L':>3} {'base>base':>9} {'base>tuned':>10} {'tuned>tuned':>11}")
    for l in range(B["H"].shape[1]):
        Xb, Xt = B["H"][:, l].astype(np.float32), T["H"][:, l].astype(np.float32)
        mk = lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=3000, class_weight="balanced"))
        pb, pt = mk().fit(Xb[tr], y[tr]), mk().fit(Xt[tr], y[tr])
        r = {"layer": l,
             "base_on_base": roc_auc_score(y[te], pb.decision_function(Xb[te])),
             "base_on_tuned": roc_auc_score(y[te], pb.decision_function(Xt[te])),
             "tuned_on_tuned": roc_auc_score(y[te], pt.decision_function(Xt[te]))}
        res["layers"].append(r)
        print(f"{l:>3} {r['base_on_base']:9.3f} {r['base_on_tuned']:10.3f} {r['tuned_on_tuned']:11.3f}")
    with open(os.path.join(a.out, "analysis_matched.json"), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
