"""Node base class + IO schema."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agentflow.engine.dsl import FieldSchema


class NodeIOSpec(BaseModel):
    inputs: list[FieldSchema] = []
    outputs: list[FieldSchema] = []


class BaseNode:
    """All built-in nodes inherit from this and declare ``type`` + ``io_spec``."""

    type: str = "base"
    # default IO declaration (a node may also read inputs/outputs from its data)
    default_io: NodeIOSpec = NodeIOSpec()

    # node category for the frontend node panel
    category: str = "其他"
    label: str = "节点"
    icon: str = "node"

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.data = data or {}

    def run(self, inputs: dict, state: dict) -> dict:
        """Execute node logic; return an outputs dict {field: value}."""
        raise NotImplementedError

    # ---- helpers for the frontend node catalog ----
    @classmethod
    def describe(cls) -> dict:
        return {
            "type": cls.type,
            "label": cls.label,
            "category": cls.category,
            "icon": cls.icon,
            "default_io": cls.default_io.model_dump(),
        }
