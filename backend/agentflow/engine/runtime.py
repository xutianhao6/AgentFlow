"""Workflow runtime — run / debug entry points + SSE streaming + single-step."""
from __future__ import annotations

import time
from typing import Any, Iterator

from agentflow.core.exceptions import NodeError
from agentflow.engine.compiler import WorkflowCompiler
from agentflow.engine.nodes import registry  # noqa: F401 ensures nodes registered
from agentflow.engine.nodes.registry import registry as node_registry
from agentflow.engine.state import new_state
from agentflow.engine.validator import validate_dsl
from agentflow.engine.dsl import WorkflowDSL
from agentflow.engine.variable import resolve_inputs
from agentflow.utils.ids import run_id as gen_run_id


class WorkflowRuntime:
    def __init__(self) -> None:
        self.compiler = WorkflowCompiler(node_registry)

    # ---------- full run ----------
    def run(
        self,
        dsl: dict,
        inputs: dict[str, Any],
        mode: str = "production",
        workflow_id: str | None = None,
    ) -> dict:
        wf_id = workflow_id or dsl.get("workflow_id") or "wf_adhoc"
        rid = gen_run_id()
        compiled = self.compiler.compile(dsl)
        state = new_state(wf_id, rid, mode, inputs)
        start = time.perf_counter()
        error = None
        try:
            state = compiled.invoke(state)
            status = "succeeded"
        except NodeError as e:
            error, status = str(e), "failed"
        total_ms = int((time.perf_counter() - start) * 1000)

        outputs = self._extract_outputs(dsl, state)
        return {
            "run_id": rid,
            "workflow_id": wf_id,
            "mode": mode,
            "status": status,
            "inputs": inputs,
            "outputs": outputs,
            "error": error,
            "total_ms": total_ms,
            "node_logs": state.get("node_logs", []),
            "variables": state.get("variables", {}),
        }

    # ---------- streaming debug run (SSE) ----------
    def debug_stream(self, dsl: dict, inputs: dict[str, Any], workflow_id: str | None = None) -> Iterator[dict]:
        """Yield events as the graph executes: validation, node start/finish, done."""
        wf_id = workflow_id or dsl.get("workflow_id") or "wf_adhoc"
        rid = gen_run_id()

        # validate first
        errors = validate_dsl(WorkflowDSL(**dsl))
        if errors:
            yield {"event": "error", "data": {"run_id": rid, "errors": errors}}
            return

        yield {"event": "run_started", "data": {"run_id": rid, "workflow_id": wf_id}}

        compiled = self.compiler.compile(dsl)
        state = new_state(wf_id, rid, "debug", inputs)
        start = time.perf_counter()

        # Execute step-by-step so we can emit per-node events.
        node_map = {n["id"]: n for n in dsl["graph"]["nodes"]}
        frontier = list(compiled.edges.get("__start__", []))
        error = None
        steps = 0
        seen_logs = 0
        while frontier and steps < 200:
            node_id = frontier.pop(0)
            steps += 1
            if node_id == "__end__":
                break
            fn = compiled.nodes.get(node_id)
            if fn is None:
                continue
            node_type = node_map.get(node_id, {}).get("type", "")
            yield {"event": "node_started", "data": {"node_id": node_id, "node_type": node_type}}
            state["current_node"] = node_id
            try:
                update = fn(state)
                state = compiled._apply(state, update)
            except NodeError as e:
                error = str(e)
                # emit the failure log if present
                new_logs = state.get("node_logs", [])[seen_logs:]
                for lg in new_logs:
                    yield {"event": "node_finished", "data": lg}
                yield {"event": "node_failed", "data": {"node_id": node_id, "error": error}}
                break

            # emit any newly produced node logs
            logs = state.get("node_logs", [])
            for lg in logs[seen_logs:]:
                yield {"event": "node_finished", "data": lg}
            seen_logs = len(logs)

            if node_id in compiled.cond_edges:
                nxt = compiled.cond_edges[node_id](state)
                if nxt and nxt != "__end__":
                    frontier.append(nxt)
            else:
                for dst in compiled.edges.get(node_id, []):
                    if dst != "__end__":
                        frontier.append(dst)

        total_ms = int((time.perf_counter() - start) * 1000)
        outputs = self._extract_outputs(dsl, state)
        status = "failed" if error else "succeeded"
        yield {
            "event": "run_finished",
            "data": {
                "run_id": rid,
                "workflow_id": wf_id,
                "status": status,
                "outputs": outputs,
                "error": error,
                "total_ms": total_ms,
                "inputs": inputs,
                "node_logs": state.get("node_logs", []),
            },
        }

    # ---------- single-step run ----------
    def run_single_node(self, dsl: dict, node_id: str, inputs: dict[str, Any]) -> dict:
        """Run exactly one node, with manually-provided inputs."""
        node_map = {n["id"]: n for n in dsl["graph"]["nodes"]}
        if node_id not in node_map:
            raise NodeError(f"节点 {node_id} 不存在")
        node = node_map[node_id]
        impl = node_registry.create(node["type"], node.get("data", {}))

        # Build a minimal state with provided inputs placed in the node's namespace
        # and also as __inputs__ for start-like nodes.
        state = new_state(dsl.get("workflow_id", "wf_adhoc"), gen_run_id(), "debug", inputs)
        # Make provided inputs directly resolvable: store under each referenced node too.
        start = time.perf_counter()
        error = None
        outputs: dict = {}
        try:
            # Resolve declared inputs but override with provided inputs by name.
            resolved = resolve_inputs(node.get("data", {}).get("inputs", []), state["variables"])
            resolved.update(inputs or {})
            outputs = impl.run(resolved, state)
            status = "succeeded"
        except NodeError as e:
            error, status = str(e), "failed"
        except Exception as e:
            error, status = str(e), "failed"
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "node_id": node_id,
            "node_type": node["type"],
            "status": status,
            "inputs": inputs,
            "outputs": outputs,
            "error": error,
            "elapsed_ms": elapsed,
        }

    # ---------- helpers ----------
    @staticmethod
    def _extract_outputs(dsl: dict, state: dict) -> dict:
        """Collect outputs of the end node(s) as the workflow result."""
        variables = state.get("variables", {})
        result: dict = {}
        for n in dsl["graph"]["nodes"]:
            if n["type"] == "end":
                result.update(variables.get(n["id"], {}))
        return result


runtime = WorkflowRuntime()
