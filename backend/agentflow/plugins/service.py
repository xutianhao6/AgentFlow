"""Plugin install / uninstall / publish business logic."""
from __future__ import annotations

from sqlalchemy.orm import Session

from agentflow.plugins.registry import plugin_registry
from agentflow.plugins.schema import PluginManifest
from agentflow.repositories.plugin_repo import PluginRepository


class PluginService:
    def __init__(self, db: Session, user_id: str = "default") -> None:
        self.db = db
        self.user_id = user_id
        self.repo = PluginRepository(db)

    def market(self, type_: str | None = None, keyword: str | None = None) -> list[dict]:
        rows = self.repo.list_market(type_, keyword)
        return [_plugin_dict(p, self.repo.is_installed(self.user_id, p.id)) for p in rows]

    def installed(self) -> list[dict]:
        rows = self.repo.list_installed(self.user_id)
        return [_plugin_dict(p, True) for p in rows]

    def install(self, plugin_id: str) -> dict:
        plugin = self.repo.get(plugin_id)
        if not plugin:
            raise ValueError("插件不存在")
        self.repo.install(self.user_id, plugin_id)
        self.repo.increment_downloads(plugin_id)
        # ensure runtime registration so the node becomes usable immediately
        self._ensure_registered(plugin)
        return _plugin_dict(plugin, True)

    def uninstall(self, plugin_id: str) -> bool:
        return self.repo.uninstall(self.user_id, plugin_id)

    def publish(self, name: str, type_: str, manifest: dict, description: str = "", author: str = "anonymous", icon: str = "plugin", version: str = "1.0.0") -> dict:
        plugin = self.repo.create(
            name=name, type=type_, version=version, description=description,
            icon=icon, author=author, manifest=manifest, status="published",
        )
        return _plugin_dict(plugin, False)

    def _ensure_registered(self, plugin) -> None:
        if plugin_registry.has(plugin.id):
            return
        # Register a generic echo invoke for user-published plugins lacking code.
        manifest = PluginManifest(**(plugin.manifest or {"name": plugin.name, "type": plugin.type}))

        def _invoke(inputs: dict) -> dict:
            # default behaviour: echo declared outputs (demo). Real plugins would
            # run their packaged code in the sandbox.
            outs = {}
            for f in manifest.io_spec.outputs:
                outs[f.name] = inputs.get(f.name, f.default)
            return outs or {"result": inputs}

        plugin_registry.register(plugin.id, manifest, _invoke)


def _plugin_dict(p, installed: bool) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "type": p.type,
        "version": p.version,
        "description": p.description,
        "icon": p.icon,
        "author": p.author,
        "manifest": p.manifest,
        "downloads": p.downloads,
        "status": p.status,
        "installed": installed,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
