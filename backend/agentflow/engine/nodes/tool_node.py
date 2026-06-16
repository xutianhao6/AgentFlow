"""Tool node — invokes an installed plugin from the plugin marketplace."""
from __future__ import annotations

from agentflow.core.exceptions import NodeError
from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node


@register_node
class ToolNode(BaseNode):
    type = "tool"
    category = "集成"
    label = "工具"
    icon = "tool"
    default_io = NodeIOSpec()

    def run(self, inputs: dict, state: dict) -> dict:
        from agentflow.plugins.runtime import plugin_runtime

        plugin_id = self.data.get("plugin_id")
        if not plugin_id:
            raise NodeError("工具节点未指定 plugin_id")
        try:
            result = plugin_runtime.invoke(plugin_id, inputs)
        except Exception as e:
            raise NodeError(f"插件执行失败: {e}")
        return result
