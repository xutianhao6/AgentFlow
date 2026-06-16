"""Variable reference resolution: {{node_id.field}} -> value from the pool."""
from __future__ import annotations

import re
from typing import Any

# matches {{ node_id.field }} or {{ node_id.field.sub }}
PATTERN = re.compile(r"\{\{\s*(\w+)\.([\w\.]+)\s*\}\}")


def _lookup(variables: dict, node_id: str, field_path: str) -> Any:
    bucket = variables.get(node_id, {})
    cur: Any = bucket
    for part in field_path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


class VariableResolver:
    """Resolve {{node.field}} templates against the WorkflowState variable pool."""

    def resolve_value(self, expr: Any, variables: dict) -> Any:
        """Resolve a single field value.

        If the whole string is exactly one reference, return the *typed* value
        (list/dict/number preserved). Otherwise do string interpolation.
        """
        if not isinstance(expr, str):
            return expr

        full = PATTERN.fullmatch(expr.strip())
        if full:
            return _lookup(variables, full.group(1), full.group(2))

        def _sub(m: re.Match) -> str:
            node_id, field = m.group(1), m.group(2)
            # distinguish "referenced node/field truly absent" from "value is None"
            bucket = variables.get(node_id)
            if bucket is None or (isinstance(bucket, dict) and field.split(".")[0] not in bucket):
                # 未绑定/解析失败：保留占位，避免发出空 prompt 让模型瞎答
                return m.group(0)
            val = _lookup(variables, node_id, field)
            if val is None:
                return ""
            if isinstance(val, (dict, list)):
                import json
                return json.dumps(val, ensure_ascii=False)
            return str(val)

        return PATTERN.sub(_sub, expr)

    def resolve(self, template: str, variables: dict) -> str:
        """Backwards-compatible string interpolation (always returns str)."""
        result = self.resolve_value(template, variables)
        return result if isinstance(result, str) else str(result)

    def references(self, expr: str) -> list[tuple[str, str]]:
        """Return list of (node_id, field) referenced in an expression."""
        if not isinstance(expr, str):
            return []
        return [(m.group(1), m.group(2)) for m in PATTERN.finditer(expr)]


resolver = VariableResolver()


def resolve_inputs(input_specs: list[dict], variables: dict) -> dict[str, Any]:
    """Resolve a node's declared inputs into a concrete {name: value} dict."""
    out: dict[str, Any] = {}
    for spec in input_specs or []:
        name = spec["name"]
        if spec.get("value") is not None:
            out[name] = resolver.resolve_value(spec["value"], variables)
        elif spec.get("default") is not None:
            out[name] = spec["default"]
        else:
            out[name] = None
    return out
