"""ID generation helpers."""
from __future__ import annotations

import uuid


def gen_id(prefix: str = "") -> str:
    raw = uuid.uuid4().hex[:16]
    return f"{prefix}_{raw}" if prefix else raw


def workflow_id() -> str:
    return gen_id("wf")


def run_id() -> str:
    return gen_id("run")


def dataset_id() -> str:
    return gen_id("ds")


def document_id() -> str:
    return gen_id("doc")


def chunk_id() -> str:
    return gen_id("chunk")


def plugin_id() -> str:
    return gen_id("plg")


def template_id() -> str:
    return gen_id("tpl")
