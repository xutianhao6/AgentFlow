"""Debug log / run-history routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agentflow.api.deps import get_db
from agentflow.observability.debug_logger import debug_logger
from agentflow.repositories.workflow_repo import WorkflowRepository

router = APIRouter(prefix="/api/v1", tags=["logs"])


def _run_out(r) -> dict:
    return {
        "run_id": r.run_id,
        "workflow_id": r.workflow_id,
        "mode": r.mode,
        "status": r.status,
        "inputs": r.inputs,
        "outputs": r.outputs,
        "error": r.error,
        "total_ms": r.total_ms,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def _log_out(l) -> dict:
    return {
        "id": l.id,
        "run_id": l.run_id,
        "node_id": l.node_id,
        "node_type": l.node_type,
        "status": l.status,
        "inputs": l.inputs,
        "outputs": l.outputs,
        "debug": getattr(l, "debug", {}) or {},
        "error": l.error,
        "elapsed_ms": l.elapsed_ms,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


@router.get("/workflows/{wf_id}/runs")
def list_runs(wf_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    return {"items": [_run_out(r) for r in repo.list_runs(wf_id)]}


@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(404, "运行记录不存在")
    logs = repo.list_node_logs(run_id)
    return {"run": _run_out(run), "node_logs": [_log_out(l) for l in logs]}


@router.get("/runs/{run_id}/nodes/{node_id}")
def node_last_run(run_id: str, node_id: str, db: Session = Depends(get_db)):
    """Last Run for a node within a run; falls back to the cached last-run."""
    repo = WorkflowRepository(db)
    logs = [l for l in repo.list_node_logs(run_id) if l.node_id == node_id]
    if logs:
        return _log_out(logs[-1])
    run = repo.get_run(run_id)
    if run:
        cached = debug_logger.get_last_run(run.workflow_id, node_id)
        if cached:
            return cached
    raise HTTPException(404, "无该节点日志")
