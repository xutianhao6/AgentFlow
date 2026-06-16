"""LLM client wrapper.

Uses SiliconFlow's OpenAI-compatible chat-completions API when a key is
configured; otherwise falls back to a deterministic mock/echo mode so the
platform remains demonstrable without network access or credentials.
"""
from __future__ import annotations

import httpx

from agentflow.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        self._api_key = settings.siliconflow_api_key or settings.anthropic_api_key
        self._base_url = settings.siliconflow_base_url.rstrip("/")
        self._available = bool(self._api_key)

    @property
    def available(self) -> bool:
        return self._available

    def complete(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        model = model or settings.llm_model
        if not self._available:
            return self._mock(prompt)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = httpx.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:  # network / quota / model errors -> degrade gracefully
            return f"[LLM error: {e}] {self._mock(prompt)}"

    @staticmethod
    def _mock(prompt: str) -> str:
        preview = prompt.strip().replace("\n", " ")
        if len(preview) > 200:
            preview = preview[:200] + "…"
        return f"[mock-llm] Based on your prompt, here is a generated answer. (prompt={preview})"


llm_client = LLMClient()
