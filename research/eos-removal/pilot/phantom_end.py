"""Delay or divert? Locate the "phantom end" in generations from a model that cannot stop.

For each held-out prompt, run the tuned model over its own non-stopping generation and find the
first response position where the mid-layer logit lens ranks a stop token first. Compare that
position with the base model's natural length for the same prompt:
  divert -> phantom end close to the natural length (plan kept, text runs past it)
  delay  -> phantom end much later or absent (plan stretched)
Works even when greedy text diverges from the base answer, because it reads the tuned model's
own stop decision instead of comparing tokens.

Usage: python phantom_end.py --model M --out RUN_DIR --adapter RUN_DIR/adapter [--layers 13 14 15 16 17]
"""
import argparse, json, os, sys
import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(__file__))
from pilot_eos import load, stop_ids  # noqa: E402


@torch.no_grad()
def first_phantom(model, stops, prompt_ids, ids, layers):
    P = len(prompt_ids)
    hs = model(input_ids=torch.tensor([prompt_ids + ids]), output_hidden_states=True).hidden_states
    norm, head = model.model.norm, model.lm_head
    out = {}
    for l in layers:
        lp = F.log_softmax(head(norm(hs[l][0, P - 1:])).float(), -1)  # rows predict response tokens 0..
        best_stop = lp[:, stops].max(-1).values
        top1 = (lp.max(-1).values <= best_stop + 1e-6).nonzero().flatten().tolist()
        out[l] = top1[0] if top1 else None  # number of response tokens before the phantom stop
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--layers", type=int, nargs="+", default=[13, 14, 15, 16, 17])
    ap.add_argument("--control", action="store_true",
                    help="calibrate on the base model's own natural answers (phantom should sit at the true end)")
    a = ap.parse_args()
    if a.control:
        from pilot_eos import read_gen
        recs = [{"prompt_ids": r["prompt_ids"], "ids": r["resp_ids"] + [0], "natural_len": len(r["resp_ids"]),
                 "category": r["category"]} for r in read_gen(a) if r["ended"] and r["split"] == "test"]
        tok, model = load(a.model)
    else:
        with open(os.path.join(a.out, "continuations.json")) as fh:
            recs = json.load(fh)["tuned"]
        tok, model = load(a.model, a.adapter)
    stops = stop_ids(tok, model)
    rows = []
    for r in recs:
        ph = first_phantom(model, stops, r["prompt_ids"], r["ids"], a.layers)
        rows.append({"natural_len": r["natural_len"], "gen_len": len(r["ids"]), "category": r["category"],
                     **{f"phantom_L{l}": v for l, v in ph.items()}})
    res = {"n": len(rows), "layers": {}}
    nat = np.array([x["natural_len"] for x in rows])
    for l in a.layers:
        ph = [x[f"phantom_L{l}"] for x in rows]
        found = np.array([p is not None for p in ph])
        p = np.array([q if q is not None else -1 for q in ph])
        ratio = p[found] / nat[found]
        rho = spearmanr(p[found], nat[found])[0] if found.sum() > 3 else float("nan")
        res["layers"][l] = {"found_frac": float(found.mean()), "median_ratio": float(np.median(ratio)),
                            "within_25pct": float(np.mean(np.abs(ratio - 1) <= 0.25)),
                            "early_lt_0.5": float(np.mean(ratio < 0.5)), "spearman": float(rho)}
        print(f"L{l}: phantom found {found.mean():.2f} | median phantom/natural {np.median(ratio):.2f} | "
              f"within ±25% {np.mean(np.abs(ratio - 1) <= 0.25):.2f} | <0.5x {np.mean(ratio < 0.5):.2f} | spearman {rho:.2f}")
    res["rows"] = rows
    with open(os.path.join(a.out, "phantom_end_control.json" if a.control else "phantom_end.json"), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
