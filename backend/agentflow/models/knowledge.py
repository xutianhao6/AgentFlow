"""Knowledge base ORM models: dataset / document / chunk."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agentflow.core.db import Base


class DatasetORM(Base):
    __tablename__ = "dataset"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    index_method: Mapped[str] = mapped_column(String(16), default="high_quality")  # high_quality / economy
    embedding_model: Mapped[str] = mapped_column(String(64), default="hash-embedding")
    user_id: Mapped[str] = mapped_column(String(64), default="default")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentORM(Base):
    __tablename__ = "document"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    chunk_strategy: Mapped[str] = mapped_column(String(16), default="general")  # general/parent_child/qa
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/indexing/done/failed
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChunkORM(Base):
    __tablename__ = "chunk"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), index=True)
    dataset_id: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text)
    vector_id: Mapped[str] = mapped_column(String(64))
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
