"""Object storage for uploaded documents and plugin packages (local filesystem)."""
from __future__ import annotations

import os
import shutil

from agentflow.core.config import settings


class ObjectStorage:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, rel_path: str, data: bytes) -> str:
        path = os.path.join(self.base_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def read(self, rel_path: str) -> bytes:
        with open(os.path.join(self.base_dir, rel_path), "rb") as f:
            return f.read()

    def delete(self, rel_path: str) -> None:
        path = os.path.join(self.base_dir, rel_path)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.exists(path):
            os.remove(path)


object_storage = ObjectStorage(settings.storage_dir)
