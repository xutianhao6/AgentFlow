"""Installed-plugin registry — maps plugin_id -> a callable invoke()."""
from __future__ import annotations

from typing import Callable

from agentflow.plugins.schema import PluginManifest


class PluginRegistry:
    def __init__(self) -> None:
        # plugin_id -> {"manifest": PluginManifest, "invoke": callable}
        self._plugins: dict[str, dict] = {}

    def register(self, plugin_id: str, manifest: PluginManifest, invoke: Callable[[dict], dict]) -> None:
        self._plugins[plugin_id] = {"manifest": manifest, "invoke": invoke}

    def get(self, plugin_id: str) -> dict | None:
        return self._plugins.get(plugin_id)

    def has(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins

    def all(self) -> dict[str, dict]:
        return self._plugins


plugin_registry = PluginRegistry()
