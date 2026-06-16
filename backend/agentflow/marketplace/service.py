"""Workflow marketplace business logic."""
from __future__ import annotations

from sqlalchemy.orm import Session

from agentflow.core.exceptions import DependencyError, NotFoundError
from agentflow.marketplace.exporter import exporter
from agentflow.marketplace.importer import importer
from agentflow.repositories.log_repo import MarketplaceRepository
from agentflow.repositories.plugin_repo import PluginRepository
from agentflow.repositories.workflow_repo import WorkflowRepository


class MarketplaceService:
    def __init__(self, db: Session, user_id: str = "default") -> None:
        self.db = db
        self.user_id = user_id
        self.repo = MarketplaceRepository(db)
        self.wf_repo = WorkflowRepository(db)
        self.plugin_repo = PluginRepository(db)

    def list_templates(self, category: str | None = None, keyword: str | None = None) -> list[dict]:
        return [_tpl_dict(t) for t in self.repo.list(category, keyword)]

    def publish(self, workflow_id: str, category: str = "通用") -> dict:
        wf = self.wf_repo.get(workflow_id)
        if not wf:
            raise NotFoundError("工作流不存在")
        exported = exporter.export({"name": wf.name, "description": wf.description, "dsl": wf.dsl})
        tpl = self.repo.create(
            name=wf.name,
            description=wf.description,
            dsl=exported["dsl"],
            dependencies=exported["dependencies"],
            author=self.user_id,
            category=category,
        )
        return _tpl_dict(tpl)

    def export_dsl(self, workflow_id: str) -> dict:
        wf = self.wf_repo.get(workflow_id)
        if not wf:
            raise NotFoundError("工作流不存在")
        return exporter.export({"name": wf.name, "description": wf.description, "dsl": wf.dsl})

    def import_template(self, template_id: str) -> dict:
        tpl = self.repo.get(template_id)
        if not tpl:
            raise NotFoundError("模板不存在")

        installed = {p.id for p in self.plugin_repo.list_installed(self.user_id)}
        missing = importer.check_dependencies(tpl.dependencies or {}, installed)
        if missing:
            raise DependencyError(f"缺少依赖插件，请先安装: {missing}")

        new_dsl = importer.remap_ids(tpl.dsl)
        wf = self.wf_repo.create(
            name=f"{tpl.name} (副本)",
            dsl=new_dsl,
            description=tpl.description,
            user_id=self.user_id,
        )
        self.repo.increment_downloads(template_id)
        return {"workflow_id": wf.id, "name": wf.name}


def _tpl_dict(t) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "dependencies": t.dependencies,
        "author": t.author,
        "downloads": t.downloads,
        "category": t.category,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }
