"""Knowledge base routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from agentflow.api.deps import get_db
from agentflow.knowledge.service import KnowledgeService
from agentflow.schemas.knowledge import DatasetCreate, RetrieveRequest

router = APIRouter(prefix="/api/v1/datasets", tags=["knowledge"])


@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    return {"items": KnowledgeService(db).list_datasets()}


@router.post("")
def create_dataset(body: DatasetCreate, db: Session = Depends(get_db)):
    return KnowledgeService(db).create_dataset(body.name, body.index_method, body.description)


@router.get("/{ds_id}")
def get_dataset(ds_id: str, db: Session = Depends(get_db)):
    ds = KnowledgeService(db).get_dataset(ds_id)
    if not ds:
        raise HTTPException(404, "知识库不存在")
    return ds


@router.delete("/{ds_id}")
def delete_dataset(ds_id: str, db: Session = Depends(get_db)):
    if not KnowledgeService(db).delete_dataset(ds_id):
        raise HTTPException(404, "知识库不存在")
    return {"deleted": True}


@router.post("/{ds_id}/documents")
async def upload_document(
    ds_id: str,
    file: UploadFile = File(...),
    chunk_strategy: str = Form("general"),
    db: Session = Depends(get_db),
):
    content = await file.read()
    try:
        doc = KnowledgeService(db).upload_document(ds_id, file.filename, content, chunk_strategy)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"文档处理失败: {e}")
    return doc


@router.get("/{ds_id}/documents")
def list_documents(ds_id: str, db: Session = Depends(get_db)):
    return {"items": KnowledgeService(db).list_documents(ds_id)}


@router.delete("/{ds_id}/documents/{doc_id}")
def delete_document(ds_id: str, doc_id: str, db: Session = Depends(get_db)):
    if not KnowledgeService(db).delete_document(doc_id):
        raise HTTPException(404, "文档不存在")
    return {"deleted": True}


@router.post("/{ds_id}/retrieve")
def retrieve(ds_id: str, body: RetrieveRequest, db: Session = Depends(get_db)):
    results = KnowledgeService(db).retrieve(ds_id, body.query, body.model_dump())
    return {"results": results}
