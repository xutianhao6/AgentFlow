"""Plugin manifest specification + base plugin classes."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentflow.engine.dsl import FieldSchema

PluginType = Literal["tool", "model", "extension", "agent_strategy"]


class PluginIOSpec(BaseModel):
    inputs: list[FieldSchema] = Field(default_factory=list)
    outputs: list[FieldSchema] = Field(default_factory=list)


class PluginManifest(BaseModel):
    name: str
    version: str = "1.0.0"
    type: PluginType = "tool"
    author: str = "anonymous"
    description: str = ""
    icon: str = "plugin"
    entrypoint: str = "main.py"
    io_spec: PluginIOSpec = Field(default_factory=PluginIOSpec)


class PluginResult(BaseModel):
    outputs: dict[str, Any] = Field(default_factory=dict)


class ToolPlugin:
    """Base class for tool plugins. Authors implement ``invoke``."""

    def invoke(self, inputs: dict) -> PluginResult:  # pragma: no cover - overridden
        raise NotImplementedError
