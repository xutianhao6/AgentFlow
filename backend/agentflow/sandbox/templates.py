"""Code templates (Python / TypeScript-JavaScript) for the code node."""
from __future__ import annotations

PYTHON_TEMPLATE = '''# 输入由上游节点变量映射而来，通过参数传入
# 输出必须是 dict，对应节点 outputs 定义的字段
def main(inputs: dict) -> dict:
    # ====== 在此编写你的核心逻辑 ======
    text = inputs.get("text", "")
    result = text.upper()
    # =================================
    return {
        "output": result,   # 对应 outputs 字段
    }
'''

TYPESCRIPT_TEMPLATE = '''// inputs 来自上游节点；返回对象对应 outputs 字段
function main(inputs) {
  // ====== 在此编写你的核心逻辑 ======
  const text = inputs["text"] || "";
  const result = text.toUpperCase();
  // =================================
  return {
    output: result,
  };
}
'''


def get_template(language: str) -> str:
    if language in ("typescript", "javascript", "ts", "js"):
        return TYPESCRIPT_TEMPLATE
    return PYTHON_TEMPLATE
