"""Retrieval: semantic / keyword / hybrid + optional Rerank, via LlamaIndex.

  - semantic -> Chroma vector retriever (embedding similarity).
  - keyword  -> BM25Retriever over the dataset's persisted nodes.
  - hybrid   -> QueryFusionRetriever fusing the two with configurable weights.

Public surface (``retriever`` singleton + ``retrieve(...)`` signature + result
dict shape) is unchanged so routes and the workflow node need no edits.
"""
from __future__ import annotations

from typing import Literal

from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from pydantic import BaseModel

from agentflow.knowledge.llama_setup import chroma


class RetrievalConfig(BaseModel):
    search_mode: Literal["semantic", "keyword", "hybrid"] = "hybrid"
    top_k: int = 3
    score_threshold: float = 0.5
    rerank_enabled: bool = False
    rerank_model: str | None = None
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3


def _dataset_filters(dataset_ids: list[str]) -> MetadataFilters | None:
    if not dataset_ids:
        return None
    return MetadataFilters(
        filters=[
            MetadataFilter(key="dataset_id", value=dataset_ids, operator=FilterOperator.IN)
        ]
    )


def _load_nodes(dataset_ids: list[str]) -> list[TextNode]:
    """Read the dataset's persisted nodes from Chroma (for BM25)."""
    where = {"dataset_id": {"$in": dataset_ids}} if dataset_ids else None
    try:
        got = chroma.collection.get(where=where, include=["documents", "metadatas"])
    except Exception:  # noqa: BLE001
        return []
    nodes: list[TextNode] = []
    ids = got.get("ids") or []
    docs = got.get("documents") or []
    metas = got.get("metadatas") or []
    for nid, text, meta in zip(ids, docs, metas):
        if not text:
            continue
        nodes.append(TextNode(id_=nid, text=text, metadata=dict(meta or {})))
    return nodes


class Retriever:
    def retrieve(
        self,
        query: str,
        dataset_ids: list[str],
        top_k: int = 3,
        score_threshold: float = 0.5,
        search_mode: str = "hybrid",
        rerank: bool = False,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[dict]:
        dataset_ids = dataset_ids or []
        pool = max(top_k * 3, top_k)

        try:
            hits = self._run(
                query, dataset_ids, pool, search_mode, semantic_weight, keyword_weight
            )
        except Exception:  # noqa: BLE001 — any branch failure -> degrade to vector-only
            hits = self._vector(query, dataset_ids, pool)

        # threshold filter; if nothing passes, still return the best few (avoid empty RAG)
        filtered = [h for h in hits if h.get("score", 0) >= score_threshold]
        result = filtered if filtered else hits

        if rerank:
            result = self._rerank(query, result)

        result.sort(key=lambda r: r.get("score", 0), reverse=True)
        return [self._to_dict(h) for h in result[:top_k]]

    # ---- branches ----
    def _run(self, query, dataset_ids, pool, mode, sw, kw_w) -> list[dict]:
        if mode == "semantic":
            return self._vector(query, dataset_ids, pool)
        if mode == "keyword":
            return self._bm25(query, dataset_ids, pool)
        return self._hybrid(query, dataset_ids, pool, sw, kw_w)

    def _vector(self, query, dataset_ids, pool) -> list[dict]:
        retr = chroma.index.as_retriever(
            similarity_top_k=pool, filters=_dataset_filters(dataset_ids)
        )
        return [self._from_node(ns) for ns in retr.retrieve(query)]

    def _bm25(self, query, dataset_ids, pool) -> list[dict]:
        nodes = _load_nodes(dataset_ids)
        if not nodes:
            return []
        from llama_index.retrievers.bm25 import BM25Retriever

        retr = BM25Retriever.from_defaults(
            nodes=nodes, similarity_top_k=min(pool, len(nodes))
        )
        return [self._from_node(ns) for ns in retr.retrieve(query)]

    def _hybrid(self, query, dataset_ids, pool, sw, kw_w) -> list[dict]:
        from llama_index.core.retrievers import QueryFusionRetriever

        vector_retr = chroma.index.as_retriever(
            similarity_top_k=pool, filters=_dataset_filters(dataset_ids)
        )
        nodes = _load_nodes(dataset_ids)
        if not nodes:
            return self._vector(query, dataset_ids, pool)

        from llama_index.retrievers.bm25 import BM25Retriever

        bm25_retr = BM25Retriever.from_defaults(
            nodes=nodes, similarity_top_k=min(pool, len(nodes))
        )
        fusion = QueryFusionRetriever(
            [vector_retr, bm25_retr],
            retriever_weights=[sw, kw_w],
            similarity_top_k=pool,
            num_queries=1,  # no LLM query rewriting
            mode="relative_score",
            use_async=False,
        )
        return [self._from_node(ns) for ns in fusion.retrieve(query)]

    # ---- helpers ----
    @staticmethod
    def _from_node(node_with_score) -> dict:
        node = node_with_score.node
        meta = dict(node.metadata or {})
        # Expose the namespaced doc id under the public ``document_id`` key.
        if "af_document_id" in meta and "document_id" not in meta:
            meta["document_id"] = meta["af_document_id"]
        return {
            "content": node.get_content(),
            "metadata": meta,
            "dataset_id": meta.get("dataset_id"),
            "score": float(node_with_score.score or 0.0),
        }

    @staticmethod
    def _rerank(query: str, hits: list[dict]) -> list[dict]:
        """Lightweight rerank: boost score by token overlap with the query."""
        q_tokens = set(query.lower().split())
        for h in hits:
            overlap = len(q_tokens & set(h["content"].lower().split()))
            h["score"] = h.get("score", 0) + 0.05 * overlap
        return hits

    @staticmethod
    def _to_dict(hit: dict) -> dict:
        return {
            "content": hit["content"],
            "score": round(float(hit.get("score", 0)), 4),
            "metadata": hit.get("metadata", {}),
            "dataset_id": hit.get("dataset_id"),
        }


retriever = Retriever()
