"""trace_node decorator — debug-mode instrumentation around node execution."""
from __future__ import annotations

import copy
import functools
import time

from agentflow.core.exceptions import NodeError
from agentflow.observability.debug_logger import NodeRunLog, debug_logger


def trace_node(node_id: str, node_type: str):
    """Wrap a node runner to capture inputs/outputs/status/error in debug mode."""

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(state: dict) -> dict:
            # Production mode: skip detailed recording.
            if state.get("mode") != "debug":
                return fn(state)

            start = time.perf_counter()
            # clear any stale per-node debug slots before running
            dbg_slot = state.setdefault("_node_debug", {})
            dbg_slot.pop("_resolved_inputs", None)
            dbg_slot.pop("_current", None)
            error = None
            out: dict = {}
            try:
                out = fn(state)
                status = "succeeded"
            except NodeError as e:
                error, status = str(e), "failed"
                out = {"variables": {node_id: {"error": str(e)}}}
            except Exception as e:  # unexpected -> still log as failure
                error, status = str(e), "failed"
                out = {"variables": {node_id: {"error": str(e)}}}

            elapsed = int((time.perf_counter() - start) * 1000)
            finished = time.perf_counter()

            # node-specific resolved inputs + extra debug detail (e.g. LLM prompt)
            resolved_inputs = dbg_slot.get("_resolved_inputs", {})
            node_debug = dbg_slot.get("_current", {})
            node_outputs = out.get("variables", {}).get(node_id, {})

            log = NodeRunLog(
                run_id=state.get("run_id", ""),
                workflow_id=state.get("workflow_id", ""),
                node_id=node_id,
                node_type=node_type,
                status=status,
                inputs=copy.deepcopy(resolved_inputs),
                outputs=node_outputs,
                error=error,
                error_node=bool(error),
                elapsed_ms=elapsed,
                started_at=start,
                finished_at=finished,
                debug=copy.deepcopy(node_debug),
            )
            debug_logger.save(log)

            out.setdefault("node_logs", [])
            out["node_logs"] = out["node_logs"] + [log.model_dump()]

            if error:
                raise NodeError(error)
            return out

        return wrapper

    return deco
