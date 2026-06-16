"""Workflow data access."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentflow.models.workflow import WorkflowORM, WorkflowRunORM, NodeRunLogORM
from agentflow.utils.ids import workflow_id as gen_wf_id


class WorkflowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- workflow ----
    def create(self, name: str, dsl: dict, description: str = "", user_id: str = "default") -> WorkflowORM:
        wf = WorkflowORM(
            id=gen_wf_id(), name=name, description=description, dsl=dsl, user_id=user_id, version=1
        )
        dsl.setdefault("workflow_id", wf.id)
        wf.dsl = dsl
        self.db.add(wf)
        self.db.commit()
        self.db.refresh(wf)
        return wf

    def get(self, wf_id: str) -> WorkflowORM | None:
        return self.db.get(WorkflowORM, wf_id)

    def list(self, user_id: str = "default") -> list[WorkflowORM]:
        stmt = select(WorkflowORM).where(WorkflowORM.user_id == user_id).order_by(WorkflowORM.updated_at.desc())
        return list(self.db.scalars(stmt))

    def update_dsl(self, wf_id: str, dsl: dict, name: str | None = None, description: str | None = None) -> WorkflowORM | None:
        wf = self.get(wf_id)
        if not wf:
            return None
        dsl["workflow_id"] = wf_id
        wf.dsl = dsl
        wf.version = (wf.version or 1) + 1
        if name is not None:
            wf.name = name
        if description is not None:
            wf.description = description
        self.db.commit()
        self.db.refresh(wf)
        return wf

    def delete(self, wf_id: str) -> bool:
        wf = self.get(wf_id)
        if not wf:
            return False
        self.db.delete(wf)
        self.db.commit()
        return True

    # ---- runs ----
    def save_run(self, run: dict) -> WorkflowRunORM:
        row = WorkflowRunORM(
            run_id=run["run_id"],
            workflow_id=run["workflow_id"],
            mode=run.get("mode", "debug"),
            status=run.get("status", "succeeded"),
            inputs=run.get("inputs", {}),
            outputs=run.get("outputs", {}),
            error=run.get("error"),
            total_ms=run.get("total_ms", 0),
        )
        self.db.add(row)
        self.db.commit()
        return row

    def list_runs(self, wf_id: str, limit: int = 50) -> list[WorkflowRunORM]:
        stmt = (
            select(WorkflowRunORM)
            .where(WorkflowRunORM.workflow_id == wf_id)
            .order_by(WorkflowRunORM.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def get_run(self, run_id: str) -> WorkflowRunORM | None:
        return self.db.get(WorkflowRunORM, run_id)

    def list_node_logs(self, run_id: str) -> list[NodeRunLogORM]:
        stmt = select(NodeRunLogORM).where(NodeRunLogORM.run_id == run_id).order_by(NodeRunLogORM.id.asc())
        return list(self.db.scalars(stmt))
