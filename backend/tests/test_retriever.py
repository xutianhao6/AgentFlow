"""Retriever tests over the LlamaIndex + Chroma pipeline."""
import uuid

import pytest

from agentflow.knowledge.indexer import index_chunks, remove_document
from agentflow.knowledge.retriever import retriever
from agentflow.knowledge.splitter import split


@pytest.fixture
def seeded():
    """Index a tiny corpus into a unique dataset; clean up after."""
    ds = f"ds_test_{uuid.uuid4().hex[:8]}"
    doc = f"doc_test_{uuid.uuid4().hex[:8]}"
    text = "RAG 是检索增强生成。\n\nLangGraph 构建状态图。"
    index_chunks(ds, doc, split(text, "general"), "high_quality")
    yield ds, doc
    remove_document(doc)


@pytest.mark.parametrize("mode", ["semantic", "keyword", "hybrid"])
def test_retrieval_modes(seeded, mode):
    ds, _ = seeded
    res = retriever.retrieve(
        "RAG 检索", [ds], top_k=1, score_threshold=0.0, search_mode=mode
    )
    assert len(res) == 1
    assert "score" in res[0]
    assert res[0]["dataset_id"] == ds


def test_delete_document_removes_from_index(seeded):
    ds, doc = seeded
    remove_document(doc)
    res = retriever.retrieve(
        "RAG 检索", [ds], top_k=3, score_threshold=0.0, search_mode="hybrid"
    )
    assert res == []
