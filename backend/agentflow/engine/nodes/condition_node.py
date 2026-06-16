"""Condition (IF/ELSE) branching node.

The node evaluates a list of conditions; ``run`` records which branch was
selected into outputs (``branch``). The compiler reads this to route edges via
conditional_edges.
"""
from __future__ import annotations

from typing import Any

from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema


def _cmp(left: Any, op: str, right: Any) -> bool:
    try:
        if op in ("contains",):
            return str(right) in str(left)
        if op in ("not_contains",):
            return str(right) not in str(left)
        if op in ("is_empty",):
            return left in (None, "", [], {})
        if op in ("is_not_empty",):
            return left not in (None, "", [], {})
        if op in ("==", "eq"):
            return str(left) == str(right)
        if op in ("!=", "ne"):
            return str(left) != str(right)
        # numeric comparisons
        lf, rf = float(left), float(right)
        if op in (">", "gt"):
            return lf > rf
        if op in (">=", "gte"):
            return lf >= rf
        if op in ("<", "lt"):
            return lf < rf
        if op in ("<=", "lte"):
            return lf <= rf
    except (ValueError, TypeError):
        return False
    return False


@register_node
class IfElseNode(BaseNode):
    type = "if_else"
    category = "逻辑"
    label = "条件分支"
    icon = "branch"
    default_io = NodeIOSpec(
        outputs=[FieldSchema(name="branch", type="string", description="命中的分支 key")]
    )

    def run(self, inputs: dict, state: dict) -> dict:
        """Evaluate cases; each case = {key, conditions:[{value, op, target}], logic}."""
        variables = state.get("variables", {})
        from agentflow.engine.variable import resolver

        for case in self.data.get("cases", []) or []:
            logic = case.get("logic", "and")
            results = []
            for cond in case.get("conditions", []) or []:
                left = resolver.resolve_value(cond.get("value", ""), variables)
                results.append(_cmp(left, cond.get("op", "=="), cond.get("target")))
            hit = all(results) if logic == "and" else any(results)
            if results and hit:
                return {"branch": case.get("key", "true")}
        return {"branch": self.data.get("else_key", "else")}
