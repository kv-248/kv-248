"""Minimal chat-LLM clients used as rewriters / mutation operators."""

from __future__ import annotations

import time


class ChatLLM:
    """OpenAI-compatible chat endpoint (vLLM / SGLang serving Qwen3, or a hosted API).
    Tracks call count and token usage so LLM overhead can be reported next to NFEs."""

    def __init__(self, model: str, base_url: str = "http://localhost:8000/v1", api_key: str = "EMPTY", timeout: int = 300):
        self.model, self.base_url, self.api_key, self.timeout = model, base_url.rstrip("/"), api_key, timeout
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.seconds = 0.0

    def chat(self, messages: list[dict], temperature: float = 0.8, max_tokens: int = 1024, n: int = 1):
        import requests

        t0 = time.time()
        r = requests.post(
            f"{self.base_url}/chat/completions",
            json={"model": self.model, "messages": messages, "temperature": temperature,
                  "max_tokens": max_tokens, "n": n},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        self.seconds += time.time() - t0
        self.calls += 1
        usage = data.get("usage", {})
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        outs = [c["message"]["content"] for c in data["choices"]]
        return outs[0] if n == 1 else outs

    def usage(self) -> dict:
        return {"calls": self.calls, "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens, "seconds": round(self.seconds, 2)}


class ScriptedLLM:
    """Offline stand-in for tests: returns canned responses in order (cycling)."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def chat(self, messages, temperature: float = 0.8, max_tokens: int = 1024, n: int = 1):
        outs = [self.responses[(self.calls + i) % len(self.responses)] for i in range(n)]
        self.calls += 1
        return outs[0] if n == 1 else outs

    def usage(self) -> dict:
        return {"calls": self.calls}
