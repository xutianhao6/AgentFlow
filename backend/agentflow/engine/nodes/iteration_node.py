"""Iteration node — iterate over an array and apply a transform per item.

For simplicity the per-item operation supports a Jinja2 template or a code
snippet via the sandbox. The common case (collect a field from each item) is
handled inline.
"""
from __future__ import annotations

from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema


@register_node
class IterationNode(BaseNode):
    type = "iteration"
    category = "逻辑"
    label = "迭代"
    icon = "repeat"
    default_io = NodeIOSpec(
        inputs=[FieldSchema(name="items", type="array[object]", required=True)],
        outputs=[FieldSchema(name="results", type="array[object]")],
    )

    def run(self, inputs: dict, state: dict) -> dict:
        items = inputs.get("items") or []
        if not isinstance(items, list):
            items = [items]

        item_field = self.data.get("item_field")  # extract a field from each item
        template = self.data.get("template")       # jinja2 per item

        results = []
        for it in items:
            if template:
                from jinja2 import Template
                results.append(Template(template).render(item=it))
            elif item_field and isinstance(it, dict):
                results.append(it.get(item_field))
            else:
                results.append(it)
        return {"results": results}
