"""DSL validation: connection references, type compatibility, required inputs, DAG."""
from __future__ import annotations

from agentflow.engine.dsl import WorkflowDSL
from agentflow.engine.variable import resolver

# type compatibility groups (lhs upstream type -> acceptable downstream types)
_NUMERIC = {"number"}
_STRINGY = {"string"}


def _compatible(src_type: str, dst_type: str) -> bool:
    if dst_type == "object" or src_type == "object":
        return True  # object accepts anything (loose)
    if src_type == dst_type:
        return True
    # allow number<->string coercion is NOT allowed per spec (string != number)
    # allow array[object] to feed object
    if src_type.startswith("array") and dst_type.startswith("array"):
        return True
    return False


def validate_dsl(dsl: WorkflowDSL) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    nodes = dsl.graph.nodes
    node_map = {n.id: n for n in nodes}

    # output field type index: {node_id: {field: type}}
    out_index: dict[str, dict[str, str]] = {}
    for n in nodes:
        out_index[n.id] = {
            f.get("name"): f.get("type", "string")
            for f in n.data.get("outputs", []) or []
        }
    # start node outputs ARE its inputs declaration
    for n in nodes:
        if n.type == "start":
            out_index[n.id] = {
                f.get("name"): f.get("type", "string")
                for f in n.data.get("outputs", []) or []
            }

    # ---- topology: build adjacency + detect cycles ----
    adj: dict[str, list[str]] = {n.id: [] for n in nodes}
    indeg: dict[str, int] = {n.id: 0 for n in nodes}
    for e in dsl.graph.edges:
        if e.source not in node_map or e.target not in node_map:
            errors.append(f"边引用了不存在的节点: {e.source} -> {e.target}")
            continue
        adj[e.source].append(e.target)
        indeg[e.target] += 1

    # Kahn topological order; cycle if not all consumed
    order: list[str] = []
    queue = [nid for nid, d in indeg.items() if d == 0]
    indeg_work = dict(indeg)
    while queue:
        cur = queue.pop(0)
        order.append(cur)
        for nxt in adj.get(cur, []):
            indeg_work[nxt] -= 1
            if indeg_work[nxt] == 0:
                queue.append(nxt)
    if len(order) != len(nodes):
        errors.append("工作流存在环 (cycle)，必须是有向无环图 (DAG)")
    order_index = {nid: i for i, nid in enumerate(order)}

    # ---- per-node input reference checks ----
    for n in nodes:
        node_pos = order_index.get(n.id, 10**9)
        for inp in n.data.get("inputs", []) or []:
            name = inp.get("name")
            dst_type = inp.get("type", "string")
            value = inp.get("value")
            required = inp.get("required", False)
            has_default = inp.get("default") is not None

            refs = resolver.references(value) if value else []

            if required and not refs and not has_default and value in (None, ""):
                errors.append(f"节点 {n.id} 的必填输入 '{name}' 未连线且无默认值")

            for ref_node, ref_field in refs:
                # 1. referenced node exists
                if ref_node not in node_map and ref_node != "__inputs__":
                    errors.append(f"节点 {n.id} 输入 '{name}' 引用了不存在的节点 {ref_node}")
                    continue
                # 2. referenced field exists
                ref_field_root = ref_field.split(".")[0]
                src_outputs = out_index.get(ref_node, {})
                if ref_node != "__inputs__" and src_outputs and ref_field_root not in src_outputs:
                    errors.append(
                        f"节点 {n.id} 输入 '{name}' 引用了 {ref_node} 不存在的输出字段 '{ref_field_root}'"
                    )
                    continue
                # 3. type compatibility
                src_type = src_outputs.get(ref_field_root, "object")
                if not _compatible(src_type, dst_type):
                    errors.append(
                        f"节点 {n.id} 输入 '{name}' 类型不兼容: 上游 {ref_node}.{ref_field_root} "
                        f"是 {src_type}，下游需要 {dst_type}"
                    )
                # 4. no referencing downstream/future nodes
                if ref_node in order_index and order_index[ref_node] >= node_pos:
                    errors.append(
                        f"节点 {n.id} 输入 '{name}' 引用了下游/未执行节点 {ref_node} 的输出"
                    )

    # ---- must have at least one start and one end ----
    types = [n.type for n in nodes]
    if "start" not in types:
        errors.append("工作流缺少 start 开始节点")
    if "end" not in types:
        errors.append("工作流缺少 end 结束节点")

    return errors
