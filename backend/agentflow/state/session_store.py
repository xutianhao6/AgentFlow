"""Redis session / task-state store (uses redis_client with in-memory fallback)."""
from __future__ import annotations

from typing import Any

from agentflow.core.redis_client import redis_client


class SessionStore:
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        redis_client.set_json(f"session:{key}", value, ex=ttl)

    def get(self, key: str) -> Any:
        return redis_client.get_json(f"session:{key}")

    def delete(self, key: str) -> None:
        redis_client.delete(f"session:{key}")


session_store = SessionStore()
