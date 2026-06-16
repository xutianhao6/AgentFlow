"""Custom code node — runs user Python/JS code in a sandbox."""
from __future__ import annotations

from agentflow.core.exceptions import NodeError, SandboxError, SandboxTimeout
from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node


@register_node
class CodeNode(BaseNode):
    type = "code"
    category = "数据"
    label = "代码执行"
    icon = "code"
    default_io = NodeIOSpec()

    def run(self, inputs: dict, state: dict) -> dict:
        from agentflow.sandbox.python_sandbox import PythonSandbox
        from agentflow.sandbox.node_sandbox import NodeSandbox

        lang = self.data.get("language", "python")
        code = self.data.get("code", "")
        sandbox = PythonSandbox() if lang == "python" else NodeSandbox()
        try:
            outputs = sandbox.execute(
                code=code,
                entry="main",
                inputs=inputs,
                timeout=int(self.data.get("timeout", 10)),
            )
        except SandboxTimeout:
            raise NodeError("代码执行超时")
        except SandboxError as e:
            raise NodeError(f"代码执行失败: {e}")

        if not isinstance(outputs, dict):
            raise NodeError("代码必须返回 dict 类型")

        # Validate against declared outputs
        declared = {f["name"] for f in self.data.get("outputs", []) or []}
        if declared and not declared.issubset(set(outputs.keys())):
            missing = declared - set(outputs.keys())
            raise NodeError(f"返回字段与 outputs 声明不符，缺少: {sorted(missing)}")
        return outputs
