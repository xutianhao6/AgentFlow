"""Workflow routes: CRUD / run / debug(SSE) / single-step / validate / catalog."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from agentflow.api.deps import current_user, get_db
from agentflow.engine.dsl import WorkflowDSL
from agentflow.engine.nodes.registry import registry
from agentflow.engine.runtime import runtime
from agentflow.engine.validator import validate_dsl
from agentflow.repositories.workflow_repo import WorkflowRepository
from agentflow.sandbox.templates import get_template
from agentflow.schemas.workflow import (
    RunRequest,
    SingleNodeRunRequest,
    ValidateRequest,
    ValidateResponse,
    WorkflowCreate,
    WorkflowUpdate,
)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflow"])


def _wf_out(wf) -> dict:
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "version": wf.version,
        "dsl": wf.dsl,
        "created_at": wf.created_at.isoformat() if wf.created_at else None,
        "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
    }


# ---- node catalog & code template (must precede /{id} routes) ----
@router.get("/node-catalog")
def node_catalog():
    """All registered node types for the frontend node panel."""
    return {"nodes": registry.catalog()}


@router.get("/code-template")
def code_template(language: str = "python"):
    return {"language": language, "template": get_template(language)}


# ---- CRUD ----
@router.get("")
def list_workflows(db: Session = Depends(get_db), user: str = Depends(current_user)):
    repo = WorkflowRepository(db)
    return {"items": [_wf_out(w) for w in repo.list(user)]}


@router.post("")
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db), user: str = Depends(current_user)):
    repo = WorkflowRepository(db)
    dsl = body.dsl or {"name": body.name, "graph": {"nodes": [], "edges": []}}
    wf = repo.create(name=body.name, dsl=dsl, description=body.description, user_id=user)
    return _wf_out(wf)


@router.get("/{wf_id}")
def get_workflow(wf_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf = repo.get(wf_id)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    return _wf_out(wf)


@router.put("/{wf_id}")
def update_workflow(wf_id: str, body: WorkflowUpdate, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf = repo.update_dsl(wf_id, body.dsl, name=body.name, description=body.description)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    return _wf_out(wf)


@router.delete("/{wf_id}")
def delete_workflow(wf_id: str, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    if not repo.delete(wf_id):
        raise HTTPException(404, "工作流不存在")
    return {"deleted": True}


# ---- validation ----
@router.post("/validate", response_model=ValidateResponse)
def validate(body: ValidateRequest):
    errors = validate_dsl(WorkflowDSL(**body.dsl))
    return ValidateResponse(valid=not errors, errors=errors)


# ---- production run ----
@router.post("/{wf_id}/run")
def run_workflow(wf_id: str, body: RunRequest, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf = repo.get(wf_id)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    result = runtime.run(wf.dsl, body.inputs, mode="production", workflow_id=wf_id)
    repo.save_run(result)
    return result


# ---- debug run (SSE streaming + logs) ----
@router.post("/{wf_id}/debug")
def debug_workflow(wf_id: str, body: RunRequest, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf = repo.get(wf_id)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    dsl = wf.dsl

    def event_stream():
        final = None
        for evt in runtime.debug_stream(dsl, body.inputs, workflow_id=wf_id):
            if evt["event"] == "run_finished":
                final = evt["data"]
            yield f"event: {evt['event']}\ndata: {json.dumps(evt['data'], ensure_ascii=False, default=str)}\n\n"
        # persist the run record after streaming completes. The request-scoped
        # session is already torn down by now, so open a fresh one.
        if final:
            from agentflow.core.db import SessionLocal

            sdb = SessionLocal()
            try:
                WorkflowRepository(sdb).save_run({
                    "run_id": final["run_id"],
                    "workflow_id": wf_id,
                    "mode": "debug",
                    "status": final["status"],
                    "inputs": final.get("inputs", {}),
                    "outputs": final.get("outputs", {}),
                    "error": final.get("error"),
                    "total_ms": final.get("total_ms", 0),
                })
            except Exception:
                pass
            finally:
                sdb.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---- single-step run ----
@router.post("/{wf_id}/nodes/{node_id}/run")
def run_single_node(wf_id: str, node_id: str, body: SingleNodeRunRequest, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf = repo.get(wf_id)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    return runtime.run_single_node(wf.dsl, node_id, body.inputs)
