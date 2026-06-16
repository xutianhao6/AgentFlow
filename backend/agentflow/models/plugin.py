"""Plugin marketplace ORM models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from agentflow.core.db import Base


class PluginORM(Base):
    __tablename__ = "plugin"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(32))  # tool/model/extension/agent_strategy
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    description: Mapped[str] = mapped_column(String(512), default="")
    icon: Mapped[str] = mapped_column(String(128), default="plugin")
    author: Mapped[str] = mapped_column(String(64), default="anonymous")
    manifest: Mapped[dict] = mapped_column(JSON, default=dict)  # io_spec etc
    package_url: Mapped[str] = mapped_column(String(255), default="")
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="published")  # published / pending_review
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PluginInstallationORM(Base):
    __tablename__ = "plugin_installation"
    __table_args__ = (UniqueConstraint("user_id", "plugin_id", name="uk_user_plugin"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), default="default")
    plugin_id: Mapped[str] = mapped_column(String(64))
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
