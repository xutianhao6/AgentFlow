"""Start / End nodes."""
from __future__ import annotations

from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.variable import resolve_inputs


@register_node
class StartNode(BaseNode):
    type = "start"
    category = "起止"
    label = "开始"
    icon = "play"
    default_io = NodeIOSpec(outputs=[])

    def run(self, inputs: dict, state: dict) -> dict:
        # Start node exposes the workflow inputs as its outputs.
        run_inputs = state.get("variables", {}).get("__inputs__", {})
        outputs = {}
        for field in self.data.get("outputs", []) or []:
            name = field["name"]
            outputs[name] = run_inputs.get(name, field.get("default"))
        return outputs


@register_node
class EndNode(BaseNode):
    type = "end"
    category = "起止"
    label = "结束"
    icon = "stop"
    default_io = NodeIOSpec(inputs=[])

    def run(self, inputs: dict, state: dict) -> dict:
        # End node simply surfaces its resolved inputs as the workflow output.
        resolved = resolve_inputs(self.data.get("inputs", []), state.get("variables", {}))
        return resolved
