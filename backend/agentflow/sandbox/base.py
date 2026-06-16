"""Sandbox interface (execute / timeout / resource limits)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Sandbox(ABC):
    # disallowed Python imports / JS globals checked before execution
    BLOCKED_PYTHON = {"os", "subprocess", "socket", "shutil", "sys", "ctypes", "importlib"}

    @abstractmethod
    def execute(self, code: str, entry: str, inputs: dict, timeout: int = 10) -> dict:
        """Run user code in isolation and return the `entry(inputs)` result dict."""
        raise NotImplementedError
