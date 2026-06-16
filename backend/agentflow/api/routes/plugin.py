"""Plugin marketplace routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agentflow.api.deps import current_user, get_db
from agentflow.plugins.service import PluginService
from agentflow.schemas.plugin import InstallRequest, PublishRequest

router = APIRouter(prefix="/api/v1/plugins", tags=["plugin"])


@router.get("/market")
def market(type: str | None = None, keyword: str | None = None, db: Session = Depends(get_db), user: str = Depends(current_user)):
    return {"items": PluginService(db, user).market(type, keyword)}


@router.get("/installed")
def installed(db: Session = Depends(get_db), user: str = Depends(current_user)):
    return {"items": PluginService(db, user).installed()}


@router.post("/install")
def install(body: InstallRequest, db: Session = Depends(get_db), user: str = Depends(current_user)):
    try:
        return PluginService(db, user).install(body.plugin_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/publish")
def publish(body: PublishRequest, db: Session = Depends(get_db), user: str = Depends(current_user)):
    return PluginService(db, user).publish(
        name=body.name, type_=body.type, manifest=body.manifest,
        description=body.description, author=body.author, icon=body.icon, version=body.version,
    )


@router.delete("/{plugin_id}")
def uninstall(plugin_id: str, db: Session = Depends(get_db), user: str = Depends(current_user)):
    if not PluginService(db, user).uninstall(plugin_id):
        raise HTTPException(404, "未安装该插件")
    return {"uninstalled": True}
