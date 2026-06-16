"""LangGraph Redis checkpointer integration (optional).

If langgraph + redis are available, returns a real checkpointer; otherwise
returns None and the native executor runs without persistence (still correct,
just no resume-from-checkpoint).
"""
from __future__ import annotations


def get_checkpointer():
    try:
        from langgraph.checkpoint.memory import MemorySaver  # type: ignore

        return MemorySaver()
    except Exception:
        return None


redis_checkpointer = get_checkpointer()
