"""Python sandbox.

Executes user code in a separate subprocess with a timeout. The harness script
restricts dangerous imports and communicates inputs/outputs over stdin/stdout as
JSON. Runs the user's ``main(inputs) -> dict`` entrypoint.

NOTE: subprocess isolation + import blocking + timeout is a pragmatic sandbox.
A production deployment should add OS-level limits (cgroups / seccomp / gVisor /
containers) as noted in the design doc.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import os

from agentflow.core.exceptions import SandboxError, SandboxTimeout
from agentflow.sandbox.base import Sandbox

_HARNESS = r'''
import json, sys, builtins

BLOCKED = {blocked}

_real_import = builtins.__import__
def _guard(name, *a, **k):
    root = name.split(".")[0]
    if root in BLOCKED:
        raise ImportError("禁止导入模块: " + root)
    return _real_import(name, *a, **k)
builtins.__import__ = _guard

payload = json.loads(sys.stdin.read())
user_code = payload["code"]
inputs = payload["inputs"]
entry = payload["entry"]

ns = {{}}
try:
    exec(user_code, ns)
    fn = ns.get(entry)
    if fn is None:
        raise RuntimeError("未找到入口函数: " + entry)
    result = fn(inputs)
    print("__RESULT__" + json.dumps(result, ensure_ascii=False, default=str))
except Exception as e:
    print("__ERROR__" + str(e))
'''


class PythonSandbox(Sandbox):
    def execute(self, code: str, entry: str, inputs: dict, timeout: int = 10) -> dict:
        # Static check for obviously dangerous imports
        for mod in self.BLOCKED_PYTHON:
            if f"import {mod}" in code or f"from {mod}" in code:
                raise SandboxError(f"禁止使用模块: {mod}")

        harness = _HARNESS.format(blocked=repr(self.BLOCKED_PYTHON))
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(harness)
            harness_path = f.name

        payload = json.dumps({"code": code, "inputs": inputs, "entry": entry})
        try:
            proc = subprocess.run(
                [sys.executable, harness_path],
                input=payload,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={"PATH": os.environ.get("PATH", "")},  # minimal env
            )
        except subprocess.TimeoutExpired:
            raise SandboxTimeout("代码执行超时")
        finally:
            try:
                os.unlink(harness_path)
            except OSError:
                pass

        out = proc.stdout.strip()
        # find result/error marker
        for line in out.splitlines():
            if line.startswith("__RESULT__"):
                return json.loads(line[len("__RESULT__"):])
            if line.startswith("__ERROR__"):
                raise SandboxError(line[len("__ERROR__"):])
        if proc.stderr:
            raise SandboxError(proc.stderr.strip()[:500])
        raise SandboxError("代码没有产生有效输出")
