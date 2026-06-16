"""Plugin loading & execution. Builtin plugins run natively; uploaded plugin
code runs in the sandbox for isolation."""
from __future__ import annotations

from agentflow.core.exceptions import NodeError
from agentflow.plugins.registry import plugin_registry
from agentflow.plugins.schema import PluginResult


class PluginRuntime:
    def invoke(self, plugin_id: str, inputs: dict) -> dict:
        entry = plugin_registry.get(plugin_id)
        if not entry:
            raise NodeError(f"插件未安装或不存在: {plugin_id}")
        invoke = entry["invoke"]
        result = invoke(inputs)
        if isinstance(result, PluginResult):
            return result.outputs
        if isinstance(result, dict):
            return result
        raise NodeError("插件返回值必须为 dict 或 PluginResult")


plugin_runtime = PluginRuntime()


def load_builtin_plugins() -> None:
    """Register builtin example plugins into the registry."""
    from agentflow.plugins.builtin.weather_tool.main import WeatherTool, MANIFEST

    plugin_registry.register(
        plugin_id="builtin_weather",
        manifest=MANIFEST,
        invoke=lambda inputs: WeatherTool().invoke(inputs),
    )
