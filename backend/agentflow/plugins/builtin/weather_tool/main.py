"""Builtin example plugin — weather tool."""
from __future__ import annotations

from agentflow.plugins.schema import PluginManifest, PluginResult, ToolPlugin
from agentflow.engine.dsl import FieldSchema
from agentflow.plugins.schema import PluginIOSpec

MANIFEST = PluginManifest(
    name="weather_tool",
    version="1.0.0",
    type="tool",
    author="agentflow",
    description="查询城市天气",
    icon="weather",
    entrypoint="main.py",
    io_spec=PluginIOSpec(
        inputs=[FieldSchema(name="city", type="string", required=True, description="城市名")],
        outputs=[
            FieldSchema(name="temperature", type="number"),
            FieldSchema(name="description", type="string"),
        ],
    ),
)


class WeatherTool(ToolPlugin):
    def invoke(self, inputs: dict) -> PluginResult:
        city = inputs.get("city", "未知")
        # Deterministic mock weather (no external network dependency required).
        temp = (sum(ord(c) for c in city) % 30) + 5
        descs = ["晴", "多云", "小雨", "阴", "雷阵雨"]
        desc = descs[sum(ord(c) for c in city) % len(descs)]
        return PluginResult(outputs={
            "temperature": temp,
            "description": f"{city} 今天{desc}",
        })
