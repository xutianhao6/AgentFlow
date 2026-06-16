"""DSL → executable StateGraph compiler.

Compiles the visual DSL into an executable graph. We provide a native executor
(``CompiledGraph``) that reproduces LangGraph's StateGraph semantics — node
functions returning partial-state updates merged via reducers, plus conditional
edges for branching — so the platform runs with or without ``langgraph``
installed. The structure mirrors the design doc's ``WorkflowCompiler``.
"""
from __future__ import annotations

from typing import Any, Callable

from agentflow.engine.nodes.registry import NodeRegistry, registry as default_registry
from agentflow.engine.state import _deep_merge, _merge_logs
from agentflow.engine.variable import resolve_inputs
from agentflow.observability.tracer import trace_node

START = "__start__"
END = "__end__"


class CompiledGraph:
    """A minimal state-graph executor with reducers + conditional edges."""

    def __init__(self) -> None:
        self.nodes: dict[str, Callable[[dict], dict]] = {}
        self.edges: dict[str, list[str]] = {}
        self.cond_edges: dict[str, Callable[[dict], str]] = {}

    def add_node(self, node_id: str, fn: Callable[[dict], dict]) -> None:
        self.nodes[node_id] = fn
        self.edges.setdefault(node_id, [])

    def add_edge(self, src: str, dst: str) -> None:
        self.edges.setdefault(src, []).append(dst)

    def add_conditional_edges(self, src: str, router: Callable[[dict], str]) -> None:
        self.cond_edges[src] = router

    def _apply(self, state: dict, update: dict) -> dict:
        """Merge a node's partial update into state using the reducers."""
        if not update:
            return state
        if "variables" in update:
            state["variables"] = _deep_merge(state.get("variables", {}), update["variables"])
        if "node_logs" in update:
            state["node_logs"] = _merge_logs(state.get("node_logs", []), update["node_logs"])
        for k, v in update.items():
            if k not in ("variables", "node_logs"):
                state[k] = v
        return state

    def invoke(self, state: dict, max_steps: int = 200) -> dict:
        """Execute the graph from START to END, returning the final state."""
        # find entry
        current = self.edges.get(START, [])
        frontier = list(current)
        visited_steps = 0

        while frontier and visited_steps < max_steps:
            node_id = frontier.pop(0)
            visited_steps += 1
            if node_id == END:
                break
            fn = self.nodes.get(node_id)
            if fn is None:
                continue
            state["current_node"] = node_id
            update = fn(state)
            state = self._apply(state, update)

            # routing
            if node_id in self.cond_edges:
                nxt = self.cond_edges[node_id](state)
                if nxt and nxt != END:
                    frontier.append(nxt)
            else:
                for dst in self.edges.get(node_id, []):
                    if dst == END:
                        continue
                    frontier.append(dst)
        return state


class WorkflowCompiler:
    def __init__(self, node_registry: NodeRegistry | None = None) -> None:
        self.registry = node_registry or default_registry

    def compile(self, dsl: dict) -> CompiledGraph:
        g = CompiledGraph()
        graph = dsl["graph"]
        node_map = {n["id"]: n for n in graph["nodes"]}

        # 1. register nodes
        for node in graph["nodes"]:
            node_impl = self.registry.create(node["type"], node.get("data", {}))
            g.add_node(node["id"], self._wrap(node_impl, node))

        # 2. start/end edges
        for node in graph["nodes"]:
            if node["type"] == "start":
                g.add_edge(START, node["id"])
            if node["type"] == "end":
                g.add_edge(node["id"], END)

        # 3. regular + conditional edges
        # group edges by source to detect branching
        by_source: dict[str, list[dict]] = {}
        for edge in graph["edges"]:
            by_source.setdefault(edge["source"], []).append(edge)

        for src, edges in by_source.items():
            src_node = node_map.get(src, {})
            is_branching = src_node.get("type") == "if_else" or any(
                e.get("sourceHandle") or e.get("condition") for e in edges
            )
            if is_branching and src_node.get("type") == "if_else":
                g.add_conditional_edges(src, self._make_router(src, edges))
            else:
                for e in edges:
                    g.add_edge(e["source"], e["target"])

        return g

    def _make_router(self, src: str, edges: list[dict]) -> Callable[[dict], str]:
        """Route based on the if_else node's selected branch key."""
        # map branch key -> target node
        mapping = {}
        for e in edges:
            key = e.get("sourceHandle") or (e.get("condition") or {}).get("key")
            if key:
                mapping[key] = e["target"]
        default_target = edges[0]["target"] if edges else END

        def router(state: dict) -> str:
            branch = state.get("variables", {}).get(src, {}).get("branch")
            return mapping.get(branch, mapping.get("else", default_target))

        return router

    def _wrap(self, node_impl, node: dict):
        """Wrap node: resolve inputs + run + debug trace, return state update."""
        node_id = node["id"]
        node_type = node["type"]

        @trace_node(node_id, node_type)
        def runner(state: dict) -> dict:
            variables = state.get("variables", {})
            inputs = resolve_inputs(node.get("data", {}).get("inputs", []), variables)
            # stash this node's resolved inputs so the tracer logs node-specific
            # inputs (not the whole variable pool).
            state.setdefault("_node_debug", {})["_resolved_inputs"] = inputs
            outputs = node_impl.run(inputs, state)
            return {"variables": {node_id: outputs or {}}}

        return runner
