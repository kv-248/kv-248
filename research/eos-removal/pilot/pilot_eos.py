"""EOS-removal pilot: does a model still "know" it is done after it can no longer stop?

Stages (each reads/writes files under --out):
  gen      greedy responses from the base chat model; records natural stop points
  ft       LoRA fine-tune that removes the stop tokens (unlikelihood on EOS) while
           keeping response content fixed (cross-entropy on the model's own responses)
  feats    per-layer residual states + logit-lens EOS stats at sampled response positions
  analyze  probes (base->base, base->tuned transfer, tuned->tuned), logit lens,
           activation-change localization, post-completion generations

Train/test split is by topic, so probes and the fine-tune are evaluated on unseen topics.
LoRA is applied to every linear layer in every block, so any layer localization of the
change is a finding rather than a design choice.
"""
import argparse, json, math, os, random, sys, time
from collections import Counter

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from prompts import build_prompts, TOPICS  # noqa: E402

torch.set_num_threads(os.cpu_count() or 4)


def stop_ids(tok, model):
    ids = model.generation_config.eos_token_id
    ids = set(ids if isinstance(ids, (list, tuple)) else [ids])
    for t in ("<|im_end|>", "<|endoftext|>"):
        i = tok.convert_tokens_to_ids(t)
        if isinstance(i, int) and i >= 0 and i != tok.unk_token_id:
            ids.add(i)
    return sorted(ids)


def is_test_topic(topic, frac=0.25):
    rng = random.Random(1234)
    test = set(rng.sample(TOPICS, int(len(TOPICS) * frac)))
    return topic in test


def chat_ids(tok, prompt):
    text = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                   tokenize=False, add_generation_prompt=True)
    return tok(text, add_special_tokens=False)["input_ids"]


DTYPE = {"bf16": torch.bfloat16, "fp32": torch.float32}


def load(model_path, adapter=None, dtype="bf16"):
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, dtype=DTYPE[dtype])
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter).merge_and_unload()
    model.eval()
    return tok, model


# ----------------------------------------------------------------------------- gen
@torch.no_grad()
def generate_batch(tok, model, prompt_ids, max_new, ban=None):
    """Left-padded greedy generation. Returns list of new-token lists (stop token excluded)
    and whether each sequence stopped on its own."""
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    L = max(len(p) for p in prompt_ids)
    ids = torch.tensor([[pad] * (L - len(p)) + p for p in prompt_ids])
    att = torch.tensor([[0] * (L - len(p)) + [1] * len(p) for p in prompt_ids])
    kw = {}
    if ban:
        kw["suppress_tokens"] = ban
    out = model.generate(input_ids=ids, attention_mask=att, max_new_tokens=max_new,
                         do_sample=False, pad_token_id=pad, **kw)
    stops = set(stop_ids(tok, model))
    res = []
    for row in out[:, L:].tolist():
        new, ended = [], False
        for t in row:
            if t in stops:
                ended = True
                break
            new.append(t)
        res.append((new, ended))
    return res


def cmd_gen(a):
    tok, model = load(a.model, dtype=a.dtype)
    rows = build_prompts(a.n)
    t0 = time.time()
    with open(os.path.join(a.out, "gen.jsonl"), "w") as fh:
        for i in range(0, len(rows), a.bs):
            batch = rows[i:i + a.bs]
            pids = [chat_ids(tok, r["prompt"]) for r in batch]
            for r, p, (new, ended) in zip(batch, pids, generate_batch(tok, model, pids, a.max_new)):
                fh.write(json.dumps({**r, "split": "test" if is_test_topic(r["topic"]) else "train",
                                     "prompt_ids": p, "resp_ids": new, "ended": ended,
                                     "text": tok.decode(new)}) + "\n")
            print(f"gen {i + len(batch)}/{len(rows)}  {time.time() - t0:.0f}s", flush=True)


def read_gen(a):
    with open(os.path.join(a.out, "gen.jsonl")) as fh:
        return [json.loads(l) for l in fh]


# ------------------------------------------------------------------------------ ft
def cmd_ft(a):
    from peft import LoraConfig, get_peft_model
    tok, model = load(a.model, dtype=a.dtype)
    model.train()
    stops = stop_ids(tok, model)
    data = [r for r in read_gen(a) if r["ended"] and r["split"] == "train"]
    cfg = LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.0,
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                     "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, cfg)
    model.print_trainable_parameters()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    rng = random.Random(0)
    steps, t0 = 0, time.time()
    log = open(os.path.join(a.out, "ft_log.jsonl"), "w")
    for ep in range(a.epochs):
        rng.shuffle(data)
        for i in range(0, len(data), a.bs):
            batch = data[i:i + a.bs]
            seqs = [r["prompt_ids"] + r["resp_ids"] for r in batch]
            L = max(map(len, seqs))
            ids = torch.tensor([s + [pad] * (L - len(s)) for s in seqs])
            att = torch.tensor([[1] * len(s) + [0] * (L - len(s)) for s in seqs])
            # resp_mask[b, t] = 1 where position t predicts a response token or the (removed) stop
            resp_mask = torch.zeros_like(ids, dtype=torch.float)
            ce_mask = torch.zeros_like(ids, dtype=torch.float)
            for b, r in enumerate(batch):
                P, R = len(r["prompt_ids"]), len(r["resp_ids"])
                resp_mask[b, P - 1:P + R] = 1.0       # P+R-1 is the natural stop position
                ce_mask[b, P - 1:P + R - 1] = 1.0     # positions whose next token is content
            logits = model(input_ids=ids, attention_mask=att).logits.float()
            logp = F.log_softmax(logits, -1)
            tgt = torch.cat([ids[:, 1:], torch.full((ids.size(0), 1), pad)], 1)
            ce = -(logp.gather(-1, tgt[..., None])[..., 0] * ce_mask).sum() / ce_mask.sum()
            p_stop = logp[..., stops].exp().sum(-1).clamp(max=1 - 1e-6)
            ul = -(torch.log1p(-p_stop) * resp_mask).sum() / resp_mask.sum()
            loss = a.ce_weight * ce + a.ul_weight * ul
            opt.zero_grad()
            loss.backward()
            opt.step()
            steps += 1
            ends = torch.tensor([len(r["prompt_ids"]) + len(r["resp_ids"]) - 1 for r in batch])
            p_end = p_stop[torch.arange(len(batch)), ends].mean().item()
            rec = {"step": steps, "ep": ep, "ce": ce.item(), "ul": ul.item(), "p_stop_at_end": p_end,
                   "sec": round(time.time() - t0)}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(rec, flush=True)
    model.save_pretrained(os.path.join(a.out, "adapter"))


# --------------------------------------------------------------------------- feats
@torch.no_grad()
def cmd_feats(a):
    tok, model = load(a.model, a.adapter, a.dtype)
    stops = stop_ids(tok, model)
    rows = [r for r in read_gen(a) if r["ended"] and len(r["resp_ids"]) >= 8]
    H_prompt, plan_len = [], []  # state that predicts the first response token, and total length
    norm, head = model.model.norm, model.lm_head
    rng = random.Random(0)
    H, meta, lens_lp, lens_rank, top_next = [], [], [], [], []
    for k, r in enumerate(rows):
        P, R = len(r["prompt_ids"]), len(r["resp_ids"])
        ids = torch.tensor([r["prompt_ids"] + r["resp_ids"]])
        hs = model(input_ids=ids, output_hidden_states=True).hidden_states  # (L+1) x [1, T, d]
        end = P + R - 1
        late = list(range(end - a.n_late + 1, end + 1))
        early_pool = list(range(P - 1, end - a.n_late + 1))
        pos = sorted(set(late + rng.sample(early_pool, min(a.n_early, len(early_pool)))))
        stack = torch.stack([h[0, pos] for h in hs], 1)  # [n_pos, L+1, d]
        # logit lens: intermediate layers need the final norm; the last entry is already normed
        lens = torch.stack([head(norm(h[0, pos])) if j < len(hs) - 1 else head(h[0, pos])
                            for j, h in enumerate(hs)], 1).float()
        lp = F.log_softmax(lens, -1)
        lp_stop = torch.logsumexp(lp[..., stops], -1)                     # [n_pos, L+1]
        best_stop = lp[..., stops].max(-1).values
        rank = (lp > best_stop[..., None]).sum(-1)                          # 0 = top-1
        H.append(stack.float().half().numpy())
        H_prompt.append(torch.stack([h[0, P - 1] for h in hs]).float().half().numpy())
        plan_len.append(R)
        lens_lp.append(lp_stop.numpy())
        lens_rank.append(rank.numpy())
        for p in pos:
            meta.append((k, end - p, 1 if r["split"] == "test" else 0, r["category"]))
        top_next.append(tok.decode([int(lp[pos.index(end), -1].argmax())]))
        if k % 25 == 0:
            print(f"feats {k}/{len(rows)}", flush=True)
    np.savez_compressed(os.path.join(a.out, f"feats_{a.tag}.npz"),
                        H=np.concatenate(H), lp=np.concatenate(lens_lp), rank=np.concatenate(lens_rank),
                        H_prompt=np.stack(H_prompt), plan_len=np.array(plan_len),
                        ex_test=np.array([1 if r["split"] == "test" else 0 for r in rows]),
                        ex=np.array([m[0] for m in meta]), dist=np.array([m[1] for m in meta]),
                        test=np.array([m[2] for m in meta]), cat=np.array([m[3] for m in meta]))
    with open(os.path.join(a.out, f"top_next_at_end_{a.tag}.json"), "w") as fh:
        json.dump(Counter(top_next).most_common(30), fh, indent=1)


# ------------------------------------------------------------------------- analyze
def auroc(y, s):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def cmd_analyze(a):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    B = np.load(os.path.join(a.out, "feats_base.npz"))
    T = np.load(os.path.join(a.out, "feats_tuned.npz"))
    assert (B["ex"] == T["ex"]).all() and (B["dist"] == T["dist"]).all()
    y = (B["dist"] == 0).astype(int)
    tr, te = B["test"] == 0, B["test"] == 1
    n_layers = B["H"].shape[1]
    res = {"n_pos": int(len(y)), "n_pos_test": int(te.sum()), "layers": []}
    for l in range(n_layers):
        Xb, Xt = B["H"][:, l].astype(np.float32), T["H"][:, l].astype(np.float32)
        pb = make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=2000, class_weight="balanced"))
        pb.fit(Xb[tr], y[tr])
        pt = make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=2000, class_weight="balanced"))
        pt.fit(Xt[tr], y[tr])
        d0 = B["dist"] == 0
        rel = np.linalg.norm(Xt - Xb, axis=1) / (np.linalg.norm(Xb, axis=1) + 1e-6)
        res["layers"].append({
            "layer": l,
            "auroc_base_on_base": auroc(y[te], pb.decision_function(Xb[te])),
            "auroc_base_on_tuned": auroc(y[te], pb.decision_function(Xt[te])),
            "auroc_tuned_on_tuned": auroc(y[te], pt.decision_function(Xt[te])),
            "lens_logp_stop_base_end": float(B["lp"][d0 & te, l].mean()),
            "lens_logp_stop_tuned_end": float(T["lp"][d0 & te, l].mean()),
            "lens_rank_stop_base_end": float(np.median(B["rank"][d0 & te, l])),
            "lens_rank_stop_tuned_end": float(np.median(T["rank"][d0 & te, l])),
            "rel_change_end": float(rel[d0 & te].mean()),
            "rel_change_mid": float(rel[(B["dist"] >= 5) & te].mean()),
        })
    # length plan: ridge-regress log(total response length) from the prompt state (base),
    # then apply the same regressor to the tuned model's prompt state. A "divert" model keeps
    # the plan; a "delay" model's plan shifts upward.
    from sklearn.linear_model import Ridge
    from scipy.stats import spearmanr
    etr, ete = B["ex_test"] == 0, B["ex_test"] == 1
    ylen = np.log(B["plan_len"])
    res["length_plan"] = []
    for l in range(n_layers):
        Xb = B["H_prompt"][:, l].astype(np.float32)
        Xt = T["H_prompt"][:, l].astype(np.float32)
        rg = make_pipeline(StandardScaler(), Ridge(alpha=100.0)).fit(Xb[etr], ylen[etr])
        pb, pt = rg.predict(Xb[ete]), rg.predict(Xt[ete])
        res["length_plan"].append({"layer": l, "spearman_base": float(spearmanr(pb, ylen[ete])[0]),
                                   "spearman_tuned": float(spearmanr(pt, ylen[ete])[0]),
                                   "mean_shift_log_len": float((pt - pb).mean())})
    with open(os.path.join(a.out, "analysis.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"{'L':>3} {'bb':>6} {'b->t':>6} {'tt':>6} | {'lensB':>7} {'lensT':>7} {'rkB':>6} {'rkT':>6} | {'dEnd':>6} {'dMid':>6}")
    for r in res["layers"]:
        print(f"{r['layer']:>3} {r['auroc_base_on_base']:.3f} {r['auroc_base_on_tuned']:.3f} {r['auroc_tuned_on_tuned']:.3f} | "
              f"{r['lens_logp_stop_base_end']:7.2f} {r['lens_logp_stop_tuned_end']:7.2f} "
              f"{r['lens_rank_stop_base_end']:6.0f} {r['lens_rank_stop_tuned_end']:6.0f} | "
              f"{r['rel_change_end']:.3f} {r['rel_change_mid']:.3f}")
    print("length plan (spearman base, spearman tuned-with-base-probe, mean log-len shift):")
    for r in res["length_plan"]:
        print(f"{r['layer']:>3} {r['spearman_base']:.3f} {r['spearman_tuned']:.3f} {r['mean_shift_log_len']:+.3f}")


@torch.no_grad()
def cmd_continue(a):
    """Generate past the natural end with the tuned model (and with decode-time banning on the
    base model) on held-out prompts, to see what models write when they cannot stop."""
    rows = [r for r in read_gen(a) if r["ended"] and r["split"] == "test"][:a.n]
    out = {}
    for tag, adapter, ban in (("tuned", a.adapter, False), ("base_banned", None, True), ("base", None, False)):
        if a.tags and tag not in a.tags:
            continue
        tok, model = load(a.model, adapter, a.dtype)
        stops = stop_ids(tok, model)
        recs = []
        for i in range(0, len(rows), a.bs):
            batch = rows[i:i + a.bs]
            pids = [r["prompt_ids"] for r in batch]
            gens = generate_batch(tok, model, pids, a.max_new, ban=stops if ban else None)
            for r, (new, ended) in zip(batch, gens):
                R = len(r["resp_ids"])
                common = next((j for j, (x, y) in enumerate(zip(new, r["resp_ids"])) if x != y),
                              min(len(new), R))
                recs.append({"prompt": r["prompt"], "category": r["category"], "natural_len": R,
                             "len": len(new), "ended": ended,
                             "same_prefix": new[:R] == r["resp_ids"],
                             "prefix_match_frac": common / R,
                             "before": tok.decode(new[:R]), "after": tok.decode(new[R:]),
                             "prompt_ids": r["prompt_ids"], "ids": new})
        out[tag] = recs
        print(tag, "stop rate", np.mean([x["ended"] for x in recs]),
              "same prefix", np.mean([x["same_prefix"] for x in recs]),
              "prefix match frac", np.mean([x["prefix_match_frac"] for x in recs]), flush=True)
    with open(os.path.join(a.out, "continuations.json"), "w") as fh:
        json.dump(out, fh, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["gen", "ft", "feats", "analyze", "continue"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--tag", default="base")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--max_new", type=int, default=200)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--ul_weight", type=float, default=1.0)
    ap.add_argument("--ce_weight", type=float, default=1.0)
    ap.add_argument("--dtype", choices=["bf16", "fp32"], default="bf16")
    ap.add_argument("--tags", nargs="*", default=None, help="continue: subset of tuned/base_banned/base")
    ap.add_argument("--n_late", type=int, default=6)
    ap.add_argument("--n_early", type=int, default=18)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    {"gen": cmd_gen, "ft": cmd_ft, "feats": cmd_feats, "analyze": cmd_analyze,
     "continue": cmd_continue}[a.stage](a)


if __name__ == "__main__":
    main()
