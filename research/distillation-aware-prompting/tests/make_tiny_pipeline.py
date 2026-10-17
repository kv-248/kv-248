"""Build a randomly initialised tiny SDXL pipeline from config files only (no weight
download), for offline CPU smoke tests. Usage: python tests/make_tiny_pipeline.py <out_dir>"""

import sys
from pathlib import Path

REPO = "echarlaix/tiny-random-stable-diffusion-xl"


def build(out_dir: str) -> str:
    import torch
    from diffusers import AutoencoderKL, EulerDiscreteScheduler, StableDiffusionXLPipeline, UNet2DConditionModel
    from huggingface_hub import snapshot_download
    from transformers import CLIPTextConfig, CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer

    out = Path(out_dir)
    if (out / "model_index.json").exists():
        return str(out)
    src = Path(snapshot_download(REPO, allow_patterns=["*.json", "*.txt"]))
    torch.manual_seed(0)
    pipe = StableDiffusionXLPipeline(
        vae=AutoencoderKL.from_config(AutoencoderKL.load_config(src / "vae")),
        text_encoder=CLIPTextModel(CLIPTextConfig.from_pretrained(src / "text_encoder")),
        text_encoder_2=CLIPTextModelWithProjection(CLIPTextConfig.from_pretrained(src / "text_encoder_2")),
        tokenizer=CLIPTokenizer.from_pretrained(src / "tokenizer"),
        tokenizer_2=CLIPTokenizer.from_pretrained(src / "tokenizer_2"),
        unet=UNet2DConditionModel.from_config(UNet2DConditionModel.load_config(src / "unet")),
        scheduler=EulerDiscreteScheduler.from_config(EulerDiscreteScheduler.load_config(src / "scheduler")),
    )
    pipe.save_pretrained(out)
    return str(out)


if __name__ == "__main__":
    print(build(sys.argv[1]))
