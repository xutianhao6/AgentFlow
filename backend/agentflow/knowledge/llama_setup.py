"""LlamaIndex wiring: embedding model + persistent Chroma vector store.

This module centralizes all LlamaIndex global configuration so the rest of the
knowledge package stays free of framework-bootstrap noise.

Embedding:
  - With a SiliconFlow key  -> OpenAI-compatible embedding (bge-large-zh, 1024d).
  - Without a key           -> deterministic HashEmbedding (256d, offline).
Both query and documents go through the same embed_model, so dimensions match.

Vector store:
  - chromadb.PersistentClient under <storage_dir>/chroma, single collection.
  - Per-node metadata carries dataset_id/document_id so we can filter & delete
    by dataset / document, mirroring the previous in-process store semantics.
"""
from __future__ import annotations

import os
from threading import Lock

from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding

from agentflow.core.config import settings
from agentflow.knowledge.embedding import _DIM, _hash_embed

COLLECTION_NAME = "agentflow"

_API_KEY = settings.siliconflow_api_key or settings.anthropic_api_key
_BASE_URL = settings.siliconflow_base_url.rstrip("/")


class HashEmbedding(BaseEmbedding):
    """Offline deterministic embedding reusing the hashing logic in embedding.py.

    Lets the whole LlamaIndex pipeline run without network / credentials so the
    platform stays demonstrable. 256-dim, L2-normalized (cosine-friendly).
    """

    def _get_query_embedding(self, query: str) -> list[float]:
        return _hash_embed(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return _hash_embed(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return _hash_embed(text)

    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [_hash_embed(t) for t in texts]


def _build_embed_model() -> BaseEmbedding:
    """SiliconFlow (OpenAI-compatible) when a key exists; else hash fallback."""
    if _API_KEY:
        try:
            from llama_index.embeddings.openai import OpenAIEmbedding

            return OpenAIEmbedding(
                model_name=settings.embedding_model,
                api_base=_BASE_URL,
                api_key=_API_KEY,
                # SiliconFlow accepts a single string per request; keep batches small.
                embed_batch_size=10,
            )
        except Exception:  # noqa: BLE001 — missing extra / init failure -> degrade
            pass
    return HashEmbedding(embed_dim=_DIM)


def embedding_model_name() -> str:
    """Human-readable model name persisted on the dataset row."""
    return settings.embedding_model if _API_KEY else "hash-embedding"


# --- LlamaIndex global config (embedding only; no LLM needed for retrieval) ---
Settings.embed_model = _build_embed_model()
Settings.llm = None


class _ChromaHandle:
    """Lazily-initialized singleton around the persistent Chroma collection."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._collection = None
        self._vector_store = None
        self._index = None

    def _ensure(self) -> None:
        if self._index is not None:
            return
        with self._lock:
            if self._index is not None:
                return
            import chromadb
            from llama_index.vector_stores.chroma import ChromaVectorStore

            persist_dir = os.path.join(settings.storage_dir, "chroma")
            os.makedirs(persist_dir, exist_ok=True)
            client = chromadb.PersistentClient(path=persist_dir)
            self._collection = client.get_or_create_collection(COLLECTION_NAME)
            self._vector_store = ChromaVectorStore(chroma_collection=self._collection)
            storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
            # Bind the index to the existing collection; nodes added later persist.
            self._index = VectorStoreIndex.from_vector_store(
                self._vector_store, storage_context=storage_context
            )

    @property
    def collection(self):
        self._ensure()
        return self._collection

    @property
    def vector_store(self):
        self._ensure()
        return self._vector_store

    @property
    def index(self) -> VectorStoreIndex:
        self._ensure()
        return self._index


chroma = _ChromaHandle()
