"""Chunking strategies: General / Parent-Child / Q&A (Dify-style).

Built on LlamaIndex node parsers but keeping the three product-facing strategies
and their metadata contract (e.g. ``parent_content`` for parent-child). Output is
a list of LlamaIndex ``TextNode`` so downstream indexing/retrieval can use the
framework directly.
"""
from __future__ import annotations

import re

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode

# bge-large-zh-v1.5 (and most bge-large models) cap input at 512 tokens. For
# Chinese text one character can be >1 token under the model tokenizer, while
# SentenceSplitter counts tiktoken tokens — so a "500-token" chunk can still
# overflow 512 model tokens and trigger SiliconFlow error 20015. We therefore
# enforce a conservative hard CHARACTER cap on every emitted chunk.
MAX_CHARS = 480


def _hard_wrap(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Split a string into <=limit-char pieces (last-resort guard)."""
    return [text[i : i + limit] for i in range(0, len(text), limit)]


def _nodes_from_text(text: str, chunk_size: int, chunk_overlap: int = 50) -> list[TextNode]:
    """Sentence-aware splitting via LlamaIndex, returned as TextNodes.

    Every node is additionally capped at MAX_CHARS so no chunk can exceed the
    embedding model's token limit.
    """
    parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = parser.get_nodes_from_documents([Document(text=text)])
    out: list[TextNode] = []
    for n in nodes:
        content = n.get_content().strip()
        if not content:
            continue
        for piece in _hard_wrap(content):
            piece = piece.strip()
            if piece:
                out.append(TextNode(text=piece))
    return out


def split_general(text: str, max_len: int = 400, overlap: int = 40) -> list[TextNode]:
    return _nodes_from_text(text, chunk_size=max_len, chunk_overlap=overlap)


def split_parent_child(text: str, parent_len: int = 1000, child_len: int = 250) -> list[TextNode]:
    """Child chunks are retrieved; parent context is attached to metadata.

    Mirrors the previous behavior: index the small child chunks but carry the
    enclosing parent's full text so callers can expand context at answer time.
    """
    parents = _nodes_from_text(text, chunk_size=parent_len, chunk_overlap=0)
    nodes: list[TextNode] = []
    for pi, parent in enumerate(parents):
        parent_text = parent.get_content()
        children = _nodes_from_text(parent_text, chunk_size=child_len, chunk_overlap=0)
        for child in children:
            child.metadata.update({"parent_index": pi, "parent_content": parent_text})
            nodes.append(child)
    return nodes


def split_qa(text: str) -> list[TextNode]:
    """Split into Q&A pairs.

    Recognizes "Q: ... A: ..." patterns (English or 中文). Falls back to general
    splitting when no pairs are found.
    """
    pairs = re.findall(
        r"(?:Q|问)[:：]\s*(.+?)\s*(?:A|答)[:：]\s*(.+?)(?=(?:Q|问)[:：]|$)", text, re.S
    )
    if pairs:
        nodes: list[TextNode] = []
        for q, a in pairs:
            q, a = q.strip(), a.strip()
            full = f"问：{q}\n答：{a}"
            # Cap the embedded text; keep the full Q/A in metadata for the answer.
            nodes.append(
                TextNode(text=full[:MAX_CHARS], metadata={"question": q, "answer": a})
            )
        return nodes
    return split_general(text, max_len=400)


def split(text: str, strategy: str = "general", **kwargs) -> list[TextNode]:
    if strategy == "parent_child":
        return split_parent_child(text, **kwargs)
    if strategy == "qa":
        return split_qa(text)
    return split_general(text, **kwargs)
