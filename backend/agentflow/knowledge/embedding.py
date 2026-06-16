"""Embedding / vectorization.

Uses SiliconFlow's embedding API when a key is configured; otherwise falls back
to a deterministic hashing embedding so semantic search still works offline
(cosine over bag-of-hashed-tokens). Both query and documents go through the same
path, so dimensions always match.
"""
from __future__ import annotations

import hashlib
import re

import httpx

from agentflow.core.config import settings

_DIM = 256
_API_KEY = settings.siliconflow_api_key or settings.anthropic_api_key
_BASE_URL = settings.siliconflow_base_url.rstrip("/")


def _tokenize(text: str) -> list[str]:
    # words + CJK char bigrams for Chinese support
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    cjk = re.findall(r"[一-鿿]", text)
    tokens += ["".join(pair) for pair in zip(cjk, cjk[1:])]
    tokens += cjk
    return tokens


def _hash_embed(text: str) -> list[float]:
    """Deterministic hashing embedding (offline fallback)."""
    vec = [0.0] * _DIM
    for tok in _tokenize(text):
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % _DIM
        vec[idx] += 1.0
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _api_embed(texts: list[str]) -> list[list[float]] | None:
    """Call SiliconFlow embeddings; return None on any failure to allow fallback."""
    if not _API_KEY:
        return None
    try:
        resp = httpx.post(
            f"{_BASE_URL}/embeddings",
            headers={"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"},
            json={"model": settings.embedding_model, "input": texts},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]
    except Exception:
        return None


def embed(text: str) -> list[float]:
    result = _api_embed([text])
    if result is not None:
        return result[0]
    return _hash_embed(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    result = _api_embed(texts)
    if result is not None:
        return result
    return [_hash_embed(t) for t in texts]
