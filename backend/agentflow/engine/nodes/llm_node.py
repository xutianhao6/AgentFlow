"""LLM node — calls the large language model."""
from __future__ import annotations

import re

from agentflow.core.exceptions import NodeError
from agentflow.core.llm import llm_client
from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema
from agentflow.engine.variable import resolver

_UNRESOLVED = re.compile(r"\{\{\s*\w+\.[\w\.]+\s*\}\}")


def _to_text(val) -> str:
    if isinstance(val, str):
        return val
    if isinstance(val, (dict, list)):
        import json
        return json.dumps(val, ensure_ascii=False)
    return str(val)


@register_node
class LLMNode(BaseNode):
    type = "llm"
    category = "AI"
    label = "LLM"
    icon = "robot"
    default_io = NodeIOSpec(
        inputs=[
            FieldSchema(name="query", type="string", required=True, description="用户问题/输入（绑定上游输出）"),
            FieldSchema(name="context", type="string", required=False, description="参考资料/上下文（可选）"),
        ],
        outputs=[FieldSchema(name="text", type="string", description="模型生成文本")],
    )

    def run(self, inputs: dict, state: dict) -> dict:
        variables = state.get("variables", {})
        prompt_tpl = self.data.get("prompt", "")
        system_tpl = self.data.get("system")

        # prompt/system 既支持全局 {{node.field}}，也支持引用本节点输入 {{query}}。
        prompt = self._render(prompt_tpl, inputs, variables)
        system = self._render(system_tpl, inputs, variables) if system_tpl else None

        # prompt 为空时，用绑定好的输入字段自动拼一个合理的 prompt，
        # 这样即使用户不写 prompt，只要把 query 绑定到上游也能正常工作。
        if not prompt or not prompt.strip():
            prompt = self._prompt_from_inputs(inputs)
        # 兜底：prompt 与 inputs 都没配置时，自动取上游节点最近的文本输出，
        # 让 start→llm 这种直连也能开箱即用，避免老工作流直接失败。
        if not prompt or not prompt.strip():
            prompt = self._auto_pick_upstream(state)
        if not prompt or not prompt.strip():
            raise NodeError(
                "LLM 节点缺少输入：请在节点配置里把「query」输入绑定到上游节点的输出，"
                "或在 Prompt 里填写内容（可用 {{query}} 或 {{节点ID.字段}} 引用上游）"
            )

        unresolved = _UNRESOLVED.findall(prompt)
        if unresolved:
            raise NodeError(
                f"LLM prompt 含未绑定变量 {unresolved}：请检查这些 {{node.field}} 是否连线/字段名是否正确"
            )

        model = self.data.get("model")
        text = llm_client.complete(
            prompt=prompt,
            model=model,
            system=system,
            max_tokens=int(self.data.get("max_tokens", 1024)),
            temperature=float(self.data.get("temperature", 0.7)),
        )

        # 记录真实调试信息：实际发送的 prompt/system/model + 模型原始返回。
        # tracer 会在 debug 模式下把它写进 NodeRunLog.debug。
        state.setdefault("_node_debug", {})["_current"] = {
            "model": model or "",
            "system": system or "",
            "prompt": prompt,
            "raw_response": text,
            "resolved_inputs": inputs,
            "llm_available": llm_client.available,
        }
        return {"text": text}

    @staticmethod
    def _render(template: str, inputs: dict, variables: dict) -> str:
        """替换本节点输入引用，再做全局 {{node.field}} 解析。

        本节点输入支持三种写法（容错用户少写括号）：{{query}}、{query}、{{ query }}。
        全局引用 {{node.field}} 含点号，不会被单字段名误伤。
        """
        if not template:
            return ""
        out = template
        for name, val in (inputs or {}).items():
            if val is None:
                continue
            rendered = val if isinstance(val, str) else _to_text(val)
            esc = re.escape(name)
            # 双括号 {{name}}
            out = re.sub(r"\{\{\s*" + esc + r"\s*\}\}", lambda _m: rendered, out)
            # 单括号 {name}（仅整词匹配，避免误伤 JSON 等）
            out = re.sub(r"\{\s*" + esc + r"\s*\}", lambda _m: rendered, out)
        return resolver.resolve(out, variables)

    @staticmethod
    def _auto_pick_upstream(state: dict) -> str:
        """没有任何配置时，从变量池里挑一个最可能的上游文本输出作为 query。"""
        variables = state.get("variables", {})
        preferred = ("query", "text", "output", "result", "answer", "content")
        # 优先用工作流入参
        run_inputs = variables.get("__inputs__", {})
        for key in preferred:
            if run_inputs.get(key):
                return _to_text(run_inputs[key])
        # 再从各节点输出里找
        for node_id, bucket in variables.items():
            if node_id == "__inputs__" or not isinstance(bucket, dict):
                continue
            for key in preferred:
                if bucket.get(key):
                    return _to_text(bucket[key])
        # 实在没有，取任意第一个非空标量值
        for bucket in variables.values():
            if isinstance(bucket, dict):
                for v in bucket.values():
                    if isinstance(v, (str, int, float)) and str(v).strip():
                        return _to_text(v)
        return ""

    @staticmethod
    def _prompt_from_inputs(inputs: dict) -> str:
        query = inputs.get("query")
        context = inputs.get("context")
        if not query:
            return ""
        if context:
            return f"【参考资料】{_to_text(context)}\n\n【用户问题】{_to_text(query)}"
        return _to_text(query)
