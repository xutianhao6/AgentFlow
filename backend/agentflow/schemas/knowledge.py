"""Knowledge base request/response schemas."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    name: str
    description: str = ""
    index_method: Literal["high_quality", "economy"] = "high_quality"


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3
    score_threshold: float = 0.5
    search_mode: Literal["semantic", "keyword", "hybrid"] = "hybrid"
    rerank_enabled: bool = False
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3


class RetrieveResult(BaseModel):
    content: str
    score: float
    metadata: dict[str, Any] = {}
