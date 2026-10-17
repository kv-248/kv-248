"""Distillation-aware prompting: analysis and prompt evolution for few-step diffusion models."""

from __future__ import annotations


def make_judge(spec: str, device: str = "cuda"):
    """'mock' | 'hf:<model_id>' | 'openai:<model>@<base_url>'"""
    from .judges import HFVLMJudge, MockJudge, OpenAIVLMJudge

    if spec == "mock":
        return MockJudge()
    kind, _, rest = spec.partition(":")
    if kind == "hf":
        return HFVLMJudge(rest, device=device)
    if kind == "openai":
        model, _, url = rest.partition("@")
        return OpenAIVLMJudge(model, base_url=url or "http://localhost:8000/v1")
    raise ValueError(f"unknown judge spec {spec!r}")


def make_llm(spec: str | None):
    """None | 'echo' (offline smoke tests) | 'openai:<model>@<base_url>'"""
    from .llm import ChatLLM, EchoLLM

    if not spec:
        return None
    if spec == "echo":
        return EchoLLM()
    kind, _, rest = spec.partition(":")
    if kind != "openai":
        raise ValueError(f"unknown llm spec {spec!r}")
    model, _, url = rest.partition("@")
    return ChatLLM(model, base_url=url or "http://localhost:8000/v1")
