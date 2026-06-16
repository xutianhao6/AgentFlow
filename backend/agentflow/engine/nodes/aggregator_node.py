"""Variable aggregator node — normalize variables from multiple branches.

Returns the first non-empty resolved input value (Dify-style branch aggregation).
"""
from __future__ import annotations

from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema


@register_node
class AggregatorNode(BaseNode):
    type = "aggregator"
    category = "数据"
    label = "变量聚合"
    icon = "merge"
    default_io = NodeIOSpec(
        outputs=[FieldSchema(name="output", type="object")]
    )

    def run(self, inputs: dict, state: dict) -> dict:
        # inputs is {name: value}; pick first non-empty in declared order
        for spec in self.data.get("inputs", []) or []:
            val = inputs.get(spec["name"])
            if val not in (None, "", [], {}):
                return {"output": val}
        return {"output": None}
