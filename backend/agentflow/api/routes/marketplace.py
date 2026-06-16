"""Workflow marketplace routes (mounted on /api/v1/workflows, registered BEFORE
the dynamic /{wf_id} routes so static segments resolve correctly)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agentflow.api.deps import current_user, get_db
from agentflow.core.exceptions import DependencyError, NotFoundError
from agentflow.marketplace.service import MarketplaceService
from agentflow.schemas.log import ImportTemplateRequest, PublishTemplateRequest

router = APIRouter(prefix="/api/v1/workflows", tags=["marketplace"])


@router.get("/market")
def market(category: str | None = None, keyword: str | None = None, db: Session = Depends(get_db), user: str = Depends(current_user)):
    return {"items": MarketplaceService(db, user).list_templates(category, keyword)}


@router.post("/import")
def import_template(body: ImportTemplateRequest, db: Session = Depends(get_db), user: str = Depends(current_user)):
    try:
        return MarketplaceService(db, user).import_template(body.template_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except DependencyError as e:
        raise HTTPException(409, str(e))


@router.post("/{wf_id}/publish")
def publish_template(wf_id: str, body: PublishTemplateRequest, db: Session = Depends(get_db), user: str = Depends(current_user)):
    try:
        return MarketplaceService(db, user).publish(wf_id, body.category)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/{wf_id}/export")
def export_dsl(wf_id: str, db: Session = Depends(get_db), user: str = Depends(current_user)):
    try:
        return MarketplaceService(db, user).export_dsl(wf_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
