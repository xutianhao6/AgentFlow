"""Redis connection pool with graceful in-memory fallback.

If the `redis` package is missing or the server is unreachable, we fall back to
a process-local dict so the platform still runs for demos/tests.
"""
from __future__ import annotations

import json
import time
from typing import Any

from agentflow.core.config import settings


class _InMemoryRedis:
    """Minimal subset of the redis API used by AgentFlow."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}

    def _expired(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is not None and exp < time.time():
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._data[key] = value
        if ex:
            self._expiry[key] = time.time() + ex

    def get(self, key: str):
        if self._expired(key):
            return None
        return self._data.get(key)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._expiry.pop(key, None)

    def set_json(self, key: str, value: Any, ex: int | None = None) -> None:
        self.set(key, json.dumps(value), ex=ex)

    def get_json(self, key: str):
        raw = self.get(key)
        return json.loads(raw) if raw else None


def _build_client():
    try:
        import redis  # type: ignore

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()

        # add json helpers on the real client too
        def set_json(key, value, ex=None):
            client.set(key, json.dumps(value), ex=ex)

        def get_json(key):
            raw = client.get(key)
            return json.loads(raw) if raw else None

        client.set_json = set_json  # type: ignore[attr-defined]
        client.get_json = get_json  # type: ignore[attr-defined]
        return client
    except Exception:
        return _InMemoryRedis()


redis_client = _build_client()
