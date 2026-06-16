"""Debug-mode node logger. Persists NodeRunLog rows to MySQL/SQLite.

Also keeps a per-node "Last Run" cache in Redis so the canvas can show the last
successful IO without re-running.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agentflow.core.redis_client import redis_client
from agentflow.utils.logger import get_logger

logger = get_logger("observability")


class NodeRunLog(BaseModel):
    run_id: str
    workflow_id: str
    node_id: str
    node_type: str
    status: str  # running | succeeded | failed
    inputs: dict = {}
    outputs: dict = {}
    debug: dict = {}  # node-specific debug detail (e.g. LLM real prompt + raw response)
    error: str | None = None
    error_node: bool = False
    elapsed_ms: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0


class DebugLogger:
    def save(self, log: NodeRunLog) -> None:
        """Persist a node run log to the database and cache Last Run."""
        # Lazy import to avoid circulars at module import time.
        from agentflow.core.db import SessionLocal
        from agentflow.models.workflow import NodeRunLogORM

        db = SessionLocal()
        try:
            row = NodeRunLogORM(
                run_id=log.run_id,
                node_id=log.node_id,
                node_type=log.node_type,
                status=log.status,
                inputs=log.inputs,
                outputs=log.outputs,
                debug=log.debug,
                error=log.error,
                elapsed_ms=log.elapsed_ms,
            )
            db.add(row)
            db.commit()
        except Exception as e:  # never let logging break a run
            db.rollback()
            logger.warning("debug log save failed: %s", e)
        finally:
            db.close()

        # Last Run cache (only successful runs)
        if log.status == "succeeded":
            key = f"lastrun:{log.workflow_id}:{log.node_id}"
            try:
                redis_client.set_json(key, log.model_dump(), ex=86400)
            except Exception:
                pass

    def get_last_run(self, workflow_id: str, node_id: str) -> dict[str, Any] | None:
        try:
            return redis_client.get_json(f"lastrun:{workflow_id}:{node_id}")
        except Exception:
            return None


debug_logger = DebugLogger()
