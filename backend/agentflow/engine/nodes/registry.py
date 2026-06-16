"""Node registration center."""
from __future__ import annotations

from typing import Any

from agentflow.engine.nodes.base import BaseNode


class NodeRegistry:
    def __init__(self) -> None:
        self._types: dict[str, type[BaseNode]] = {}

    def register(self, node_cls: type[BaseNode]) -> type[BaseNode]:
        self._types[node_cls.type] = node_cls
        return node_cls

    def create(self, type_: str, data: dict) -> BaseNode:
        if type_ not in self._types:
            raise KeyError(f"未知节点类型: {type_}")
        return self._types[type_](data)

    def has(self, type_: str) -> bool:
        return type_ in self._types

    def catalog(self) -> list[dict]:
        """Describe all registered node types for the frontend node panel."""
        return [cls.describe() for cls in self._types.values()]


registry = NodeRegistry()


def register_node(cls: type[BaseNode]) -> type[BaseNode]:
    """Decorator to register a node class."""
    return registry.register(cls)
