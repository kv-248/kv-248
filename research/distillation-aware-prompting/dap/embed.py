"""Image embeddings for diversity and variance-decomposition metrics."""

from __future__ import annotations

import numpy as np


class ImageEmbedder:
    """DINOv2 (CLS token) or CLIP image features via transformers."""

    def __init__(self, model_id: str = "facebook/dinov2-base", device: str = "cuda", batch_size: int = 32):
        import torch
        from transformers import AutoImageProcessor, AutoModel

        self.model_id, self.device, self.batch_size = model_id, device, batch_size
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModel.from_pretrained(model_id).to(device).eval()
        self.is_clip = hasattr(self.model, "get_image_features")
        self._torch = torch

    def __call__(self, images) -> np.ndarray:
        torch = self._torch
        feats = []
        for i in range(0, len(images), self.batch_size):
            inputs = self.processor(images=list(images[i : i + self.batch_size]), return_tensors="pt").to(self.device)
            with torch.no_grad():
                if self.is_clip:
                    f = self.model.get_image_features(**inputs)
                else:
                    f = self.model(**inputs).last_hidden_state[:, 0]
            feats.append(f.float().cpu().numpy())
        return np.concatenate(feats)


def pixel_embed(images, size: int = 16) -> np.ndarray:
    """Dependency-free fallback (and test helper): downsampled pixels."""
    return np.stack([np.asarray(im.convert("RGB").resize((size, size)), dtype=np.float32).ravel() / 255.0 + 1e-3
                     for im in images])
