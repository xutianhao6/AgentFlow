"""Knowledge base data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentflow.models.knowledge import DatasetORM, DocumentORM, ChunkORM
from agentflow.utils.ids import dataset_id as gen_ds_id, document_id as gen_doc_id


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- dataset ----
    def create_dataset(
        self,
        name: str,
        index_method: str,
        description: str = "",
        user_id: str = "default",
        embedding_model: str | None = None,
    ) -> DatasetORM:
        kwargs = {} if embedding_model is None else {"embedding_model": embedding_model}
        ds = DatasetORM(
            id=gen_ds_id(),
            name=name,
            index_method=index_method,
            description=description,
            user_id=user_id,
            **kwargs,
        )
        self.db.add(ds)
        self.db.commit()
        self.db.refresh(ds)
        return ds

    def get_dataset(self, ds_id: str) -> DatasetORM | None:
        return self.db.get(DatasetORM, ds_id)

    def list_datasets(self, user_id: str = "default") -> list[DatasetORM]:
        stmt = select(DatasetORM).where(DatasetORM.user_id == user_id).order_by(DatasetORM.created_at.desc())
        return list(self.db.scalars(stmt))

    def delete_dataset(self, ds_id: str) -> bool:
        ds = self.get_dataset(ds_id)
        if not ds:
            return False
        for doc in self.list_documents(ds_id):
            self.db.delete(doc)
        for ch in self.db.scalars(select(ChunkORM).where(ChunkORM.dataset_id == ds_id)):
            self.db.delete(ch)
        self.db.delete(ds)
        self.db.commit()
        return True

    # ---- document ----
    def create_document(self, dataset_id: str, name: str, chunk_strategy: str) -> DocumentORM:
        doc = DocumentORM(id=gen_doc_id(), dataset_id=dataset_id, name=name, chunk_strategy=chunk_strategy, status="pending")
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, doc_id: str) -> DocumentORM | None:
        return self.db.get(DocumentORM, doc_id)

    def list_documents(self, dataset_id: str) -> list[DocumentORM]:
        stmt = select(DocumentORM).where(DocumentORM.dataset_id == dataset_id).order_by(DocumentORM.created_at.desc())
        return list(self.db.scalars(stmt))

    def update_document_status(self, doc_id: str, status: str, chunk_count: int | None = None) -> None:
        doc = self.get_document(doc_id)
        if not doc:
            return
        doc.status = status
        if chunk_count is not None:
            doc.chunk_count = chunk_count
        self.db.commit()

    def delete_document(self, doc_id: str) -> bool:
        doc = self.get_document(doc_id)
        if not doc:
            return False
        for ch in self.db.scalars(select(ChunkORM).where(ChunkORM.document_id == doc_id)):
            self.db.delete(ch)
        self.db.delete(doc)
        self.db.commit()
        return True

    # ---- chunk ----
    def add_chunks(self, dataset_id: str, document_id: str, rows: list[dict]) -> None:
        for r in rows:
            self.db.add(
                ChunkORM(
                    id=r["chunk_id"],
                    document_id=document_id,
                    dataset_id=dataset_id,
                    content=r["content"],
                    vector_id=r["vector_id"],
                    meta=r["metadata"],
                )
            )
        self.db.commit()
