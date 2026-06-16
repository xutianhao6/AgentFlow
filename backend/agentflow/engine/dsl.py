"""Workflow DSL data structures (the contract between canvas and engine)."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

VarType = Literal[
    "string", "number", "boolean", "object",
    "array[string]", "array[object]", "file",
]


class FieldSchema(BaseModel):
    name: str
    type: VarType = "string"
    required: bool = False
    description: str = ""
    default: Any = None
    value: str | None = None  # expression like {{node_id.field}}


class GraphNode(BaseModel):
    id: str
    type: str
    data: dict[str, Any] = Field(default_factory=dict)
    # Optional canvas position (preserved for round-tripping with Vue Flow)
    position: dict[str, float] | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    # For conditional branching: which source handle / branch key this edge represents
    sourceHandle: str | None = None
    condition: dict[str, Any] | None = None


class WorkflowGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class WorkflowDSL(BaseModel):
    workflow_id: str | None = None
    name: str = "未命名工作流"
    description: str = ""
    version: int = 1
    graph: WorkflowGraph = Field(default_factory=WorkflowGraph)

    def node_map(self) -> dict[str, GraphNode]:
        return {n.id: n for n in self.graph.nodes}
