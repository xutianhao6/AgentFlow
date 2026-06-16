"""WorkflowState — the runtime variable pool shared across nodes.

When LangGraph is installed we use a TypedDict with reducers exactly as in the
design doc. The reducers ensure each node writes only into its own ``node_id``
namespace, so nodes can never clobber each other.
"""
from __future__ import annotations

from operator import or_
from typing import Annotated, Any, TypedDict


def _merge_logs(a: list, b: list) -> list:
    return (a or []) + (b or [])


def _deep_merge(a: dict, b: dict) -> dict:
    """Reducer for the variables pool: merge per-node namespaces."""
    out = dict(a or {})
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            merged = dict(out[k])
            merged.update(v)
            out[k] = merged
        else:
            out[k] = v
    return out


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    run_id: str
    mode: str  # "debug" | "production"
    # variable pool: {node_id: {field: value}}
    variables: Annotated[dict, _deep_merge]
    current_node: str
    error: str | None
    # debug logs (accumulated only in debug mode)
    node_logs: Annotated[list, _merge_logs]


def new_state(workflow_id: str, run_id: str, mode: str, inputs: dict[str, Any] | None = None) -> dict:
    """Create an initial state dict. Start-node inputs land under the start node id later."""
    return {
        "workflow_id": workflow_id,
        "run_id": run_id,
        "mode": mode,
        "variables": {"__inputs__": inputs or {}},
        "current_node": "",
        "error": None,
        "node_logs": [],
    }
