// Code templates mirror backend agentflow/sandbox/templates.py
export const PYTHON_TEMPLATE = `# 输入由上游节点变量映射而来，通过参数传入
# 输出必须是 dict，对应节点 outputs 定义的字段
def main(inputs: dict) -> dict:
    # ====== 在此编写你的核心逻辑 ======
    text = inputs.get("text", "")
    result = text.upper()
    # =================================
    return {
        "output": result,   # 对应 outputs 字段
    }
`

export const TYPESCRIPT_TEMPLATE = `// inputs 来自上游节点；返回对象对应 outputs 字段
function main(inputs) {
  // ====== 在此编写你的核心逻辑 ======
  const text = inputs["text"] || "";
  const result = text.toUpperCase();
  // =================================
  return {
    output: result,
  };
}
`

export function getTemplate(language: string): string {
  return language === 'python' ? PYTHON_TEMPLATE : TYPESCRIPT_TEMPLATE
}
