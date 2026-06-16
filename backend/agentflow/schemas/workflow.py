"""Workflow request/response schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentflow.engine.dsl import WorkflowDSL


class WorkflowCreate(BaseModel):
    name: str = "未命名工作流"
    description: str = ""
    dsl: dict | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    dsl: dict


class WorkflowOut(BaseModel):
    id: str
    name: str
    description: str
    version: int
    dsl: dict
    created_at: str | None = None
    updated_at: str | None = None


class RunRequest(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)


class SingleNodeRunRequest(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)


class ValidateRequest(BaseModel):
    dsl: dict


class ValidateResponse(BaseModel):
    valid: bool
    errors: list[str] = []
