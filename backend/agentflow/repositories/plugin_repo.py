"""Plugin data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentflow.models.plugin import PluginORM, PluginInstallationORM
from agentflow.utils.ids import plugin_id as gen_plugin_id


class PluginRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_market(self, type_: str | None = None, keyword: str | None = None) -> list[PluginORM]:
        stmt = select(PluginORM).where(PluginORM.status == "published")
        if type_:
            stmt = stmt.where(PluginORM.type == type_)
        rows = list(self.db.scalars(stmt.order_by(PluginORM.downloads.desc())))
        if keyword:
            kw = keyword.lower()
            rows = [r for r in rows if kw in r.name.lower() or kw in (r.description or "").lower()]
        return rows

    def get(self, plugin_id: str) -> PluginORM | None:
        return self.db.get(PluginORM, plugin_id)

    def create(self, **kwargs) -> PluginORM:
        plugin = PluginORM(id=kwargs.pop("id", None) or gen_plugin_id(), **kwargs)
        self.db.add(plugin)
        self.db.commit()
        self.db.refresh(plugin)
        return plugin

    def increment_downloads(self, plugin_id: str) -> None:
        p = self.get(plugin_id)
        if p:
            p.downloads = (p.downloads or 0) + 1
            self.db.commit()

    def delete(self, plugin_id: str) -> bool:
        p = self.get(plugin_id)
        if not p:
            return False
        self.db.delete(p)
        self.db.commit()
        return True

    # ---- installation ----
    def install(self, user_id: str, plugin_id: str) -> PluginInstallationORM:
        existing = self.db.scalar(
            select(PluginInstallationORM).where(
                PluginInstallationORM.user_id == user_id,
                PluginInstallationORM.plugin_id == plugin_id,
            )
        )
        if existing:
            return existing
        inst = PluginInstallationORM(user_id=user_id, plugin_id=plugin_id)
        self.db.add(inst)
        self.db.commit()
        self.db.refresh(inst)
        return inst

    def uninstall(self, user_id: str, plugin_id: str) -> bool:
        inst = self.db.scalar(
            select(PluginInstallationORM).where(
                PluginInstallationORM.user_id == user_id,
                PluginInstallationORM.plugin_id == plugin_id,
            )
        )
        if not inst:
            return False
        self.db.delete(inst)
        self.db.commit()
        return True

    def list_installed(self, user_id: str = "default") -> list[PluginORM]:
        stmt = (
            select(PluginORM)
            .join(PluginInstallationORM, PluginInstallationORM.plugin_id == PluginORM.id)
            .where(PluginInstallationORM.user_id == user_id)
        )
        return list(self.db.scalars(stmt))

    def is_installed(self, user_id: str, plugin_id: str) -> bool:
        return self.db.scalar(
            select(PluginInstallationORM).where(
                PluginInstallationORM.user_id == user_id,
                PluginInstallationORM.plugin_id == plugin_id,
            )
        ) is not None
