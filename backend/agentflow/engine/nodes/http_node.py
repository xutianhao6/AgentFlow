"""HTTP request node — call external APIs."""
from __future__ import annotations

import json

from agentflow.core.exceptions import NodeError
from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema
from agentflow.engine.variable import resolver


@register_node
class HttpNode(BaseNode):
    type = "http_request"
    category = "集成"
    label = "HTTP 请求"
    icon = "globe"
    default_io = NodeIOSpec(
        outputs=[
            FieldSchema(name="status_code", type="number"),
            FieldSchema(name="body", type="string"),
            FieldSchema(name="json", type="object"),
        ]
    )

    def run(self, inputs: dict, state: dict) -> dict:
        import httpx

        variables = state.get("variables", {})
        method = self.data.get("method", "GET").upper()
        url = resolver.resolve(self.data.get("url", ""), variables)
        headers = {
            k: resolver.resolve(str(v), variables)
            for k, v in (self.data.get("headers", {}) or {}).items()
        }
        body_tpl = self.data.get("body")
        timeout = float(self.data.get("timeout", 30))

        kwargs = {"headers": headers, "timeout": timeout}
        if body_tpl:
            resolved_body = resolver.resolve(body_tpl, variables) if isinstance(body_tpl, str) else body_tpl
            kwargs["content"] = resolved_body if isinstance(resolved_body, (str, bytes)) else json.dumps(resolved_body)

        try:
            resp = httpx.request(method, url, **kwargs)
        except Exception as e:
            raise NodeError(f"HTTP 请求失败: {e}")

        parsed = None
        try:
            parsed = resp.json()
        except Exception:
            parsed = None

        return {
            "status_code": resp.status_code,
            "body": resp.text,
            "json": parsed,
        }
