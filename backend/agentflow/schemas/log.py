"""Log / marketplace request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel


class NodeRunLogOut(BaseModel):
    id: int
    run_id: str
    node_id: str
    node_type: str
    status: str
    inputs: dict = {}
    outputs: dict = {}
    error: str | None = None
    elapsed_ms: int = 0
    created_at: str | None = None


class WorkflowRunOut(BaseModel):
    run_id: str
    workflow_id: str
    mode: str
    status: str
    inputs: dict = {}
    outputs: dict = {}
    error: str | None = None
    total_ms: int = 0
    created_at: str | None = None


class PublishTemplateRequest(BaseModel):
    category: str = "通用"


class ImportTemplateRequest(BaseModel):
    template_id: str
