"""Sandbox isolation tests."""
import pytest

from agentflow.core.exceptions import SandboxError
from agentflow.sandbox.python_sandbox import PythonSandbox


def test_python_run():
    out = PythonSandbox().execute(
        'def main(inputs):\n    return {"output": inputs["x"] * 2}',
        "main", {"x": 21}, timeout=10,
    )
    assert out["output"] == 42


def test_python_blocks_os_import():
    with pytest.raises(SandboxError):
        PythonSandbox().execute(
            "import os\ndef main(inputs):\n    return {}",
            "main", {}, timeout=10,
        )
