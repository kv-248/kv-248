"""Detector-based GenEval-style judge (judge-independent check for GenEval intents).

Follows the GenEval protocol (Ghosh et al., NeurIPS 2023 D&B): COCO instance detection with a 0.3
score threshold (0.9 for counting), exact counts via the metadata's `exclude` rule, colour by CLIP
zero-shot classification of the detected object's crop, and relative position from box centroids
with a margin. It plugs into `judges.score_intent`, so every script can use it with
`--eval-judge geneval`. The official evaluator (mmdet Mask2Former) remains the reference for
reported numbers; this re-implementation uses transformers models so it runs in the same process.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

COLORS = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "white"]
THRESHOLD, COUNTING_THRESHOLD, POSITION_MARGIN = 0.3, 0.9, 0.1


@dataclass
class Detection:
    label: str
    score: float
    box: tuple[float, float, float, float]  # x0, y0, x1, y1 in pixels


def relation_holds(a: Detection, b: Detection, rel: str, margin: float = POSITION_MARGIN) -> bool:
    """Is `a` <rel> `b`? Centroid offset must exceed `margin` times the larger box size."""
    ax, ay = (a.box[0] + a.box[2]) / 2, (a.box[1] + a.box[3]) / 2
    bx, by = (b.box[0] + b.box[2]) / 2, (b.box[1] + b.box[3]) / 2
    size = max(a.box[2] - a.box[0], a.box[3] - a.box[1], b.box[2] - b.box[0], b.box[3] - b.box[1], 1e-6)
    dx, dy = (ax - bx) / size, (ay - by) / size
    return {"left of": dx < -margin, "right of": dx > margin, "above": dy < -margin, "below": dy > margin}[rel]


class GenEvalDetectorJudge:
    """`detector(image) -> list[Detection]` and `color_of(image, detection, cls) -> str` are pluggable;
    the defaults load Mask2Former (COCO instances) and CLIP ViT-L/14 from transformers."""

    name = "geneval-detector"

    def __init__(self, detector: Callable | None = None, color_of: Callable | None = None, device: str = "cuda",
                 detector_id: str = "facebook/mask2former-swin-large-coco-instance",
                 clip_id: str = "openai/clip-vit-large-patch14"):
        self.device = device
        self.detector = detector or self._hf_detector(detector_id)
        self.color_of = color_of or self._clip_color(clip_id)

    def _hf_detector(self, model_id):
        def run(image):
            import torch
            from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation

            if not hasattr(self, "_det"):
                self._proc = AutoImageProcessor.from_pretrained(model_id)
                self._det = Mask2FormerForUniversalSegmentation.from_pretrained(model_id).to(self.device).eval()
            inputs = self._proc(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out = self._det(**inputs)
            res = self._proc.post_process_instance_segmentation(out, threshold=THRESHOLD,
                                                               target_sizes=[image.size[::-1]])[0]
            dets = []
            for seg in res["segments_info"]:
                mask = (res["segmentation"] == seg["id"]).cpu().numpy()
                ys, xs = mask.nonzero()
                if len(xs):
                    dets.append(Detection(self._det.config.id2label[seg["label_id"]], float(seg["score"]),
                                          (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))))
            return dets
        return run

    def _clip_color(self, model_id):
        def run(image, det, cls):
            import torch
            from transformers import CLIPModel, CLIPProcessor

            if not hasattr(self, "_clip"):
                self._clip_proc = CLIPProcessor.from_pretrained(model_id)
                self._clip = CLIPModel.from_pretrained(model_id).to(self.device).eval()
            crop = image.crop(tuple(int(v) for v in det.box))
            texts = [f"a photo of a {c} {cls}" for c in COLORS]
            inputs = self._clip_proc(text=texts, images=crop, return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                logits = self._clip(**inputs).logits_per_image[0]
            return COLORS[int(logits.argmax())]
        return run

    def check(self, image, meta: dict) -> list[bool]:
        """One boolean per requirement, in the order of `questions.geneval_intent`'s checklist."""
        dets = self.detector(image)
        counting = meta.get("tag") == "counting"
        thr = COUNTING_THRESHOLD if counting else THRESHOLD
        by_cls: dict[str, list[Detection]] = {}
        for d in sorted(dets, key=lambda d: -d.score):
            if d.score >= thr:
                by_cls.setdefault(d.label, []).append(d)
        out, include = [], meta["include"]
        for obj in include:
            found = by_cls.get(obj["class"], [])
            n = obj.get("count", 1)
            ok = len(found) >= n
            for ex in meta.get("exclude", []):
                if ex["class"] == obj["class"]:
                    ok = ok and len(found) < ex["count"]
            out.append(ok)
            if "color" in obj:
                out.append(ok and all(self.color_of(image, d, obj["class"]) == obj["color"] for d in found[:n]))
            if "position" in obj:
                rel, ref = obj["position"]
                ref_found = by_cls.get(include[ref]["class"], [])
                out.append(bool(found and ref_found and relation_holds(found[0], ref_found[0], rel)))
        return out

    def score_geneval(self, images: Sequence, intent) -> list[dict]:
        rows = []
        for im in images:
            checks = self.check(im, intent.meta)
            q = intent.questions
            rows.append({"probs": [float(c) for c in checks], "soft": float(sum(checks) / max(len(checks), 1)),
                         "success": bool(all(checks)), "failed": [q[i] for i, c in enumerate(checks) if not c]})
        return rows

    def yes_prob(self, images, questions):
        raise NotImplementedError("GenEvalDetectorJudge only scores GenEval intents (metadata required)")
