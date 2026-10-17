"""Does the end-of-turn decision mark the boundary of the assistant persona?

Builds an assistant-vs-user direction per layer (difference of means between hidden states on
assistant-response tokens and user-prompt tokens, base model, train split), then projects
continuations generated past the natural end (from `pilot_eos.py continue`) onto it, binned by
position relative to the natural end. If text after the phantom end comes from a different
"speaker", the projection should drop after position 0.

Caveat: the direction also separates questions from answers; the role-token analysis
(share of continuations that open a new turn) is the complementary behavioural check.

Usage: python persona_axis.py --model M --out RUN_DIR [--adapter RUN_DIR/adapter]
"""
import argparse, json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from pilot_eos import load, read_gen  # noqa: E402

BINS = [(-48, -16), (-16, 0), (0, 16), (16, 48), (48, 112), (112, 240)]


@torch.no_grad()
def hidden(model, ids):
    return model(input_ids=torch.tensor([ids]), output_hidden_states=True).hidden_states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--n_dir", type=int, default=120)
    a = ap.parse_args()

    tok, base = load(a.model)
    rows = [r for r in read_gen(a) if r["ended"] and r["split"] == "train"][:a.n_dir]
    user_open = tok.convert_tokens_to_ids("<|im_start|>")
    sums_a = sums_u = None
    n_a = n_u = 0
    for r in rows:
        P = len(r["prompt_ids"])
        hs = hidden(base, r["prompt_ids"] + r["resp_ids"])
        # user content sits between "<|im_start|>user\n" and "<|im_end|>\n<|im_start|>assistant\n"
        starts = [i for i, t in enumerate(r["prompt_ids"]) if t == user_open]
        u0, u1 = starts[-2] + 3, starts[-1] - 2
        H = torch.stack([h[0] for h in hs]).float()  # [L+1, T, d]
        ua, aa = H[:, u0:u1].sum(1), H[:, P:].sum(1)
        sums_u = ua if sums_u is None else sums_u + ua
        sums_a = aa if sums_a is None else sums_a + aa
        n_u += u1 - u0
        n_a += len(r["resp_ids"])
    d = sums_a / n_a - sums_u / n_u
    d = d / d.norm(dim=-1, keepdim=True)  # [L+1, dim]
    mid = (sums_a / n_a + sums_u / n_u) / 2

    with open(os.path.join(a.out, "continuations.json")) as fh:
        cont = json.load(fh)
    result = {}
    for tag, recs in cont.items():
        model = base
        if tag == "tuned":
            _, model = load(a.model, a.adapter)
        per_bin = {b: [] for b in BINS}
        new_turn = 0
        for rec in recs:
            if rec["ended"] or len(rec["ids"]) <= rec["natural_len"] + 16:
                continue
            R, P = rec["natural_len"], len(rec["prompt_ids"])
            new_turn += int("<|im_start|>" in rec["after"])
            hs = hidden(model, rec["prompt_ids"] + rec["ids"])
            H = torch.stack([h[0] for h in hs]).float()
            proj = ((H - mid[:, None]) * d[:, None]).sum(-1)  # [L+1, T]
            for lo, hi in BINS:
                s, e = P + R + lo, min(P + R + hi, H.shape[1])
                if s >= P and e > s:
                    per_bin[(lo, hi)].append(proj[:, s:e].mean(1).numpy())
        result[tag] = {
            "n": sum(1 for r in recs if not r["ended"] and len(r["ids"]) > r["natural_len"] + 16),
            "share_opening_new_turn": new_turn / max(1, len(recs)),
            "bins": {f"{lo}..{hi}": (np.mean(v, 0).tolist() if v else None) for (lo, hi), v in per_bin.items()},
        }
        L = d.shape[0]
        show = [L // 4, L // 2, 3 * L // 4, L - 2]
        print(f"[{tag}] n={result[tag]['n']} opens-new-turn={result[tag]['share_opening_new_turn']:.2f}")
        for (lo, hi), v in per_bin.items():
            if v:
                m = np.mean(v, 0)
                print(f"   {lo:>5}..{hi:<5} " + "  ".join(f"L{l}:{m[l]:+7.2f}" for l in show))
    with open(os.path.join(a.out, "persona_axis.json"), "w") as fh:
        json.dump(result, fh, indent=1)


if __name__ == "__main__":
    main()
