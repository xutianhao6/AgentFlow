"""Workflow marketplace ORM model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agentflow.core.db import Base


class WorkflowTemplateORM(Base):
    __tablename__ = "workflow_template"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    dsl: Mapped[dict] = mapped_column(JSON, default=dict)
    dependencies: Mapped[dict] = mapped_column(JSON, default=dict)  # plugins / datasets declaration
    author: Mapped[str] = mapped_column(String(64), default="anonymous")
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String(32), default="通用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
