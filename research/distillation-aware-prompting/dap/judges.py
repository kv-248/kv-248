"""VQA-style judges: P(yes | image, question).

Two roles, always kept separate to avoid reporting a hacked reward:
  * the *search judge* gives fitness inside evolution / best-of-N selection;
  * the *evaluation judge(s)* (a different model family, plus GenEval's detector
    pipeline and human study) give the numbers we report.
"""

from __future__ import annotations

import base64
import hashlib
import io
import math
from typing import Protocol, Sequence

import numpy as np

from .questions import Intent

YES_NO_SUFFIX = " Answer with Yes or No only."


class Judge(Protocol):
    name: str

    def yes_prob(self, images: Sequence, questions: Sequence[str]) -> np.ndarray:
        """Probability of 'Yes' for each (image, question) pair."""


def score_intent(judge: Judge, images: Sequence, intent: Intent, threshold: float = 0.5) -> list[dict]:
    """Score each image against an intent's checklist.

    Returns per image: per-question probabilities, soft score (mean P(yes)),
    strict success (all required questions above threshold) and failed questions.
    """
    if hasattr(judge, "score_geneval") and intent.meta.get("include"):
        return judge.score_geneval(images, intent)
    q = intent.questions
    flat_imgs = [im for im in images for _ in q]
    flat_qs = [qq for _ in images for qq in q]
    probs = np.asarray(judge.yes_prob(flat_imgs, flat_qs)).reshape(len(images), len(q))
    req = intent.required_idx()
    out = []
    for row in probs:
        out.append({
            "probs": row.tolist(),
            "soft": float(row.mean()),
            "success": bool(all(row[i] > threshold for i in req)),
            "failed": [q[i] for i in range(len(q)) if row[i] <= threshold],
        })
    return out


class HFVLMJudge:
    """Local VLM (e.g. Qwen2.5-VL / Qwen3-VL / InternVL) via transformers.
    P(yes) = softmax over the 'Yes'/'No' next-token logits (VQAScore-style)."""

    def __init__(self, model_id: str, device: str = "cuda", dtype: str = "bfloat16", batch_size: int = 16):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self.name = f"hf:{model_id}"
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.processor.tokenizer.padding_side = "left"
        self.model = AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=getattr(torch, dtype)).to(device).eval()
        self.device = device
        self.batch_size = batch_size
        tok = self.processor.tokenizer
        self.yes_ids = sorted({tok.encode(w, add_special_tokens=False)[0] for w in ("Yes", "yes", " Yes")})
        self.no_ids = sorted({tok.encode(w, add_special_tokens=False)[0] for w in ("No", "no", " No")})

    def yes_prob(self, images, questions):
        import torch

        out = []
        for i in range(0, len(images), self.batch_size):
            ims, qs = images[i : i + self.batch_size], questions[i : i + self.batch_size]
            texts = [
                self.processor.apply_chat_template(
                    [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": q + YES_NO_SUFFIX}]}],
                    add_generation_prompt=True,
                    tokenize=False,
                )
                for q in qs
            ]
            inputs = self.processor(text=texts, images=list(ims), return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                logits = self.model(**inputs).logits[:, -1].float()
            lse_yes = torch.logsumexp(logits[:, self.yes_ids], dim=-1)
            lse_no = torch.logsumexp(logits[:, self.no_ids], dim=-1)
            out.append(torch.sigmoid(lse_yes - lse_no).cpu().numpy())
        return np.concatenate(out) if out else np.zeros(0)


class OpenAIVLMJudge:
    """Any OpenAI-compatible endpoint (e.g. vLLM serving Qwen3-VL) using logprobs."""

    def __init__(self, model: str, base_url: str = "http://localhost:8000/v1", api_key: str = "EMPTY", timeout: int = 120):
        self.name = f"openai:{model}"
        self.model, self.base_url, self.api_key, self.timeout = model, base_url.rstrip("/"), api_key, timeout

    @staticmethod
    def _b64(image) -> str:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def _one(self, image, question) -> float:
        import requests

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{self._b64(image)}"}},
                {"type": "text", "text": question + YES_NO_SUFFIX},
            ]}],
            "max_tokens": 1,
            "temperature": 0.0,
            "logprobs": True,
            "top_logprobs": 10,
        }
        r = requests.post(f"{self.base_url}/chat/completions", json=body, timeout=self.timeout,
                          headers={"Authorization": f"Bearer {self.api_key}"})
        r.raise_for_status()
        top = r.json()["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        p_yes = sum(math.exp(t["logprob"]) for t in top if t["token"].strip().lower() == "yes")
        p_no = sum(math.exp(t["logprob"]) for t in top if t["token"].strip().lower() == "no")
        return p_yes / (p_yes + p_no) if p_yes + p_no > 0 else 0.5

    def yes_prob(self, images, questions):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=16) as ex:
            return np.array(list(ex.map(self._one, images, questions)))


class MockJudge:
    """Deterministic stand-in for tests: a pseudo-probability from a hash of the
    image bytes and the question."""

    name = "mock"

    def yes_prob(self, images, questions):
        out = []
        for im, q in zip(images, questions):
            h = hashlib.sha256(np.asarray(im).tobytes() + q.encode()).digest()
            out.append(h[0] / 255.0)
        return np.array(out)
