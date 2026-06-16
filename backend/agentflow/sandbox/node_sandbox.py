"""Node.js / JavaScript sandbox.

Runs user JS in a `node` subprocess with a timeout. Falls back to a clear error
if Node is not installed on the host.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

from agentflow.core.exceptions import SandboxError, SandboxTimeout
from agentflow.sandbox.base import Sandbox

_HARNESS = r"""
const fs = require('fs');
let payload = JSON.parse(fs.readFileSync(0, 'utf-8'));
{user_code}
try {{
  const result = main(payload.inputs);
  process.stdout.write("__RESULT__" + JSON.stringify(result));
}} catch (e) {{
  process.stdout.write("__ERROR__" + (e && e.message ? e.message : String(e)));
}}
"""


class NodeSandbox(Sandbox):
    def execute(self, code: str, entry: str, inputs: dict, timeout: int = 10) -> dict:
        node_bin = shutil.which("node")
        if not node_bin:
            raise SandboxError("未检测到 Node.js 运行时，无法执行 JS 代码节点")

        # block obvious dangerous calls
        for bad in ("require('child_process')", 'require("child_process")', "require('fs')", "process.exit"):
            if bad in code:
                raise SandboxError(f"禁止使用: {bad}")

        harness = _HARNESS.format(user_code=code)
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(harness)
            path = f.name

        try:
            proc = subprocess.run(
                [node_bin, path],
                input=json.dumps({"inputs": inputs}),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise SandboxTimeout("代码执行超时")
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

        out = proc.stdout.strip()
        if out.startswith("__RESULT__"):
            return json.loads(out[len("__RESULT__"):])
        if out.startswith("__ERROR__"):
            raise SandboxError(out[len("__ERROR__"):])
        if proc.stderr:
            raise SandboxError(proc.stderr.strip()[:500])
        raise SandboxError("代码没有产生有效输出")
