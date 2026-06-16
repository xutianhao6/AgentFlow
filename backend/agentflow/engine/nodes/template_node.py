"""Template transform node — Jinja2 text processing."""
from __future__ import annotations

from agentflow.core.exceptions import NodeError
from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema


@register_node
class TemplateNode(BaseNode):
    type = "template"
    category = "数据"
    label = "模板转换"
    icon = "template"
    default_io = NodeIOSpec(
        outputs=[FieldSchema(name="output", type="string")]
    )

    def run(self, inputs: dict, state: dict) -> dict:
        from jinja2 import Template, TemplateError

        template_str = self.data.get("template", "")
        try:
            rendered = Template(template_str).render(**inputs)
        except TemplateError as e:
            raise NodeError(f"模板渲染失败: {e}")
        return {"output": rendered}
