"""Knowledge base business orchestration."""
from __future__ import annotations

from sqlalchemy.orm import Session

from agentflow.knowledge.indexer import index_chunks, remove_document, remove_dataset
from agentflow.knowledge.llama_setup import embedding_model_name
from agentflow.knowledge.loader import load_text
from agentflow.knowledge.retriever import retriever
from agentflow.knowledge.splitter import split
from agentflow.repositories.knowledge_repo import KnowledgeRepository


class KnowledgeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)

    def create_dataset(self, name: str, index_method: str, description: str = "") -> dict:
        ds = self.repo.create_dataset(
            name=name,
            index_method=index_method,
            description=description,
            embedding_model=embedding_model_name(),
        )
        return _dataset_dict(ds)

    def list_datasets(self) -> list[dict]:
        return [_dataset_dict(d) for d in self.repo.list_datasets()]

    def get_dataset(self, ds_id: str) -> dict | None:
        ds = self.repo.get_dataset(ds_id)
        return _dataset_dict(ds) if ds else None

    def delete_dataset(self, ds_id: str) -> bool:
        remove_dataset(ds_id)
        return self.repo.delete_dataset(ds_id)

    def upload_document(self, dataset_id: str, filename: str, content: bytes, chunk_strategy: str = "general") -> dict:
        ds = self.repo.get_dataset(dataset_id)
        if not ds:
            raise ValueError("知识库不存在")

        doc = self.repo.create_document(dataset_id, filename, chunk_strategy)
        self.repo.update_document_status(doc.id, "indexing")
        try:
            text = load_text(filename, content)
            chunks = split(text, strategy=chunk_strategy)
            rows = index_chunks(dataset_id, doc.id, chunks, index_method=ds.index_method)
            self.repo.add_chunks(dataset_id, doc.id, rows)
            self.repo.update_document_status(doc.id, "done", chunk_count=len(rows))
        except Exception as e:  # noqa: BLE001
            self.repo.update_document_status(doc.id, "failed")
            raise e
        return _document_dict(self.repo.get_document(doc.id))

    def list_documents(self, dataset_id: str) -> list[dict]:
        return [_document_dict(d) for d in self.repo.list_documents(dataset_id)]

    def delete_document(self, doc_id: str) -> bool:
        remove_document(doc_id)
        return self.repo.delete_document(doc_id)

    def retrieve(self, dataset_id: str, query: str, config: dict) -> list[dict]:
        return retriever.retrieve(
            query=query,
            dataset_ids=[dataset_id],
            top_k=int(config.get("top_k", 3)),
            score_threshold=float(config.get("score_threshold", 0.5)),
            search_mode=config.get("search_mode", "hybrid"),
            rerank=bool(config.get("rerank_enabled", False)),
            semantic_weight=float(config.get("semantic_weight", 0.7)),
            keyword_weight=float(config.get("keyword_weight", 0.3)),
        )


def _dataset_dict(ds) -> dict:
    return {
        "id": ds.id,
        "name": ds.name,
        "description": ds.description,
        "index_method": ds.index_method,
        "embedding_model": ds.embedding_model,
        "created_at": ds.created_at.isoformat() if ds.created_at else None,
    }


def _document_dict(doc) -> dict:
    return {
        "id": doc.id,
        "dataset_id": doc.dataset_id,
        "name": doc.name,
        "chunk_strategy": doc.chunk_strategy,
        "status": doc.status,
        "chunk_count": doc.chunk_count,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }
