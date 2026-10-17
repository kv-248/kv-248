"""Loading teacher / distilled-student pipelines from `configs/families.yaml` and
sampling from them with explicit NFE accounting."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "families.yaml"


@dataclass
class VariantSpec:
    name: str
    family: str
    role: str  # "teacher" | "student"
    base: str
    steps: int
    guidance_scale: float
    cfg: bool
    resolution: int
    objective: str = ""
    mode_seeking: bool | None = None
    unet: dict | None = None
    lora: dict | None = None
    scheduler: dict | None = None
    call_kwargs: dict = field(default_factory=dict)
    notes: str = ""
    verify: bool = False
    nfe: int | None = None  # explicit NFE per image when steps*(1+cfg) is wrong (e.g. Z-Image-Turbo)

    @property
    def nfe_per_image(self) -> int:
        return self.nfe if self.nfe is not None else self.steps * (2 if self.cfg else 1)


def load_families(path: str | Path = CONFIG_PATH) -> dict[str, list[VariantSpec]]:
    raw = yaml.safe_load(Path(path).read_text())
    return {fam: [VariantSpec(family=fam, **v) for v in variants] for fam, variants in raw.items()}


def get_variant(name: str, path: str | Path = CONFIG_PATH) -> VariantSpec:
    for variants in load_families(path).values():
        for v in variants:
            if v.name == name:
                return v
    raise KeyError(f"unknown variant {name!r}")


def teacher_of(family: str, path: str | Path = CONFIG_PATH) -> VariantSpec:
    return next(v for v in load_families(path)[family] if v.role == "teacher")


class Generator:
    """Wraps a diffusers text-to-image pipeline for one variant and counts NFEs."""

    def __init__(self, spec: VariantSpec, device: str = "cuda", dtype: str = "bfloat16"):
        self.spec = spec
        self.device = device
        self.dtype = dtype
        self.nfe = 0
        self.images_generated = 0
        self.pipe = None

    def load(self) -> "Generator":
        import diffusers
        import torch
        from diffusers import AutoPipelineForText2Image, DiffusionPipeline

        torch_dtype = getattr(torch, self.dtype)
        kwargs: dict[str, Any] = {"torch_dtype": torch_dtype}
        if self.spec.unet:
            kwargs["unet"] = self._load_unet(torch_dtype)
        try:
            pipe = AutoPipelineForText2Image.from_pretrained(self.spec.base, **kwargs)
        except (ValueError, KeyError):  # pipelines without an AutoPipeline mapping (e.g. ERNIE-Image)
            pipe = DiffusionPipeline.from_pretrained(self.spec.base, **kwargs)
        if self.spec.scheduler:
            cls = getattr(diffusers, self.spec.scheduler["class"])
            pipe.scheduler = cls.from_config(pipe.scheduler.config, **self.spec.scheduler.get("kwargs", {}))
        if self.spec.lora:
            pipe.load_lora_weights(self.spec.lora["repo"], weight_name=self.spec.lora["file"])
            pipe.fuse_lora(lora_scale=self.spec.lora.get("scale", 1.0))
        pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe.to(self.device)
        return self

    def _load_unet(self, torch_dtype):
        import torch
        from diffusers import UNet2DConditionModel
        from huggingface_hub import hf_hub_download

        repo, fname = self.spec.unet["repo"], self.spec.unet["file"]
        if fname == "diffusion_pytorch_model.safetensors":
            return UNet2DConditionModel.from_pretrained(repo, torch_dtype=torch_dtype)
        unet = UNet2DConditionModel.from_config(UNet2DConditionModel.load_config(self.spec.base, subfolder="unet"))
        path = hf_hub_download(repo, fname)
        if path.endswith(".safetensors"):
            from safetensors.torch import load_file

            state = load_file(path)
        else:
            state = torch.load(path, map_location="cpu", weights_only=True)
        unet.load_state_dict(state)
        return unet.to(torch_dtype)

    def generate(self, prompts: list[str], seeds: list[int], resolution: int | None = None, noise: str = "white"):
        """One image per (prompt, seed) pair. Returns a list of PIL images.
        noise="pink": seed-determined 1/f initial latents (UNet latent pipelines only), a cheap
        noise-side diversity baseline."""
        import torch

        assert len(prompts) == len(seeds)
        if self.pipe is None:
            self.load()
        res = resolution or self.spec.resolution
        gens = [torch.Generator(device="cpu").manual_seed(int(s)) for s in seeds]
        extra = {}
        if noise == "pink":
            if not hasattr(self.pipe, "unet"):
                raise NotImplementedError("pink-noise latents are implemented for UNet (SDXL-family) pipelines")
            shape = (self.pipe.unet.config.in_channels, res // self.pipe.vae_scale_factor, res // self.pipe.vae_scale_factor)
            extra["latents"] = torch.stack([pink_noise(shape, int(s)) for s in seeds]).to(self.device, self.pipe.unet.dtype)
        out = self.pipe(
            prompt=list(prompts),
            generator=gens,
            num_inference_steps=self.spec.steps,
            guidance_scale=self.spec.guidance_scale,
            height=res,
            width=res,
            **extra,
            **self.spec.call_kwargs,
        ).images
        self.nfe += self.spec.nfe_per_image * len(prompts)
        self.images_generated += len(prompts)
        return out

    def generate_batched(self, prompts: list[str], seeds: list[int], batch_size: int = 8, **kw):
        images = []
        for i in range(0, len(prompts), batch_size):
            images += self.generate(prompts[i : i + batch_size], seeds[i : i + batch_size], **kw)
        return images


def pink_noise(shape: tuple[int, int, int], seed: int, alpha: float = 1.0):
    """Unit-variance Gaussian noise with a 1/f^alpha spatial spectrum (per channel)."""
    import torch

    g = torch.Generator().manual_seed(seed)
    c, h, w = shape
    white = torch.randn(shape, generator=g)
    fy = torch.fft.fftfreq(h)[:, None]
    fx = torch.fft.rfftfreq(w)[None, :]
    scale = (fx ** 2 + fy ** 2).sqrt().clamp(min=1.0 / max(h, w)) ** (-alpha / 2)
    x = torch.fft.irfft2(torch.fft.rfft2(white) * scale, s=(h, w))
    x = (x - x.mean(dim=(1, 2), keepdim=True)) / x.std(dim=(1, 2), keepdim=True)
    return x
