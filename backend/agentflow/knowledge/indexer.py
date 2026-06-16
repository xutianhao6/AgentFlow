"""Indexing via LlamaIndex + Chroma.

Both index methods (high_quality / economy) persist nodes to the same Chroma
collection. The difference surfaces at retrieval time:
  - high_quality -> vector (semantic) search is meaningful (real embeddings).
  - economy      -> keyword (BM25) search over the same persisted nodes.
Storing both uniformly keeps the pipeline simple and lets hybrid search work for
either dataset; BM25 needs the node text in the store regardless.
"""
from __future__ import annotations

from llama_index.core.schema import TextNode

from agentflow.knowledge.llama_setup import chroma
from agentflow.utils.ids import chunk_id


def index_chunks(
    dataset_id: str,
    document_id: str,
    nodes: list[TextNode],
    index_method: str = "high_quality",
) -> list[dict]:
    """Index nodes into Chroma; return metadata rows for the SQLite mirror.

    Each row: {chunk_id, vector_id, content, metadata}. The vector_id equals the
    node id so deletes by document/dataset can target the store precisely.
    """
    rows: list[dict] = []
    for node in nodes:
        cid = chunk_id()
        node.id_ = cid
        # NOTE: ``document_id`` is a reserved key in LlamaIndex's Chroma metadata
        # (it overwrites it with the ref doc, ending up as the string "None"), so we
        # namespace ours as ``af_document_id`` to keep delete-by-document working.
        node.metadata.update(
            {
                "dataset_id": dataset_id,
                "af_document_id": document_id,
                "chunk_id": cid,
                "index_method": index_method,
            }
        )
        rows.append(
            {
                "chunk_id": cid,
                "vector_id": cid,
                "content": node.get_content(),
                "metadata": dict(node.metadata),
            }
        )

    if nodes:
        _insert_resilient(nodes, rows)
    return rows


def _insert_resilient(nodes, rows) -> None:
    """Persist nodes, tolerating individual embedding failures.

    A batch insert is fastest, but one bad chunk (e.g. an over-limit input the
    embedding API rejects with HTTP 400) would otherwise fail the whole upload.
    On batch failure we retry node-by-node and drop only the offenders, keeping
    ``rows`` in sync so the SQLite mirror reflects what actually got indexed.
    """
    try:
        chroma.index.insert_nodes(nodes)
        return
    except Exception:  # noqa: BLE001 — fall back to per-node so one bad chunk ≠ total failure
        pass

    kept_ids: set[str] = set()
    for node in nodes:
        try:
            chroma.index.insert_nodes([node])
            kept_ids.add(node.id_)
        except Exception:  # noqa: BLE001 — skip this chunk, keep going
            continue
    rows[:] = [r for r in rows if r["chunk_id"] in kept_ids]


def remove_document(document_id: str) -> None:
    try:
        chroma.collection.delete(where={"af_document_id": document_id})
    except Exception:  # noqa: BLE001 — collection may be empty / not yet created
        pass


def remove_dataset(dataset_id: str) -> None:
    try:
        chroma.collection.delete(where={"dataset_id": dataset_id})
    except Exception:  # noqa: BLE001
        pass
