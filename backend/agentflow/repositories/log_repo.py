"""Marketplace template + log convenience data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentflow.models.marketplace import WorkflowTemplateORM
from agentflow.utils.ids import template_id as gen_tpl_id


class MarketplaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, category: str | None = None, keyword: str | None = None) -> list[WorkflowTemplateORM]:
        stmt = select(WorkflowTemplateORM).order_by(WorkflowTemplateORM.downloads.desc())
        if category:
            stmt = stmt.where(WorkflowTemplateORM.category == category)
        rows = list(self.db.scalars(stmt))
        if keyword:
            kw = keyword.lower()
            rows = [r for r in rows if kw in r.name.lower() or kw in (r.description or "").lower()]
        return rows

    def get(self, tpl_id: str) -> WorkflowTemplateORM | None:
        return self.db.get(WorkflowTemplateORM, tpl_id)

    def create(self, name: str, description: str, dsl: dict, dependencies: dict, author: str = "anonymous", category: str = "通用") -> WorkflowTemplateORM:
        tpl = WorkflowTemplateORM(
            id=gen_tpl_id(), name=name, description=description, dsl=dsl,
            dependencies=dependencies, author=author, category=category,
        )
        self.db.add(tpl)
        self.db.commit()
        self.db.refresh(tpl)
        return tpl

    def increment_downloads(self, tpl_id: str) -> None:
        tpl = self.get(tpl_id)
        if tpl:
            tpl.downloads = (tpl.downloads or 0) + 1
            self.db.commit()
