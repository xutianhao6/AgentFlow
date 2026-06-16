"""Dependency injection: DB session + current user."""
from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from agentflow.core.db import get_session


def get_db() -> Session:  # pragma: no cover - thin wrapper
    yield from get_session()


def current_user(x_user_id: str | None = Header(default=None)) -> str:
    """Minimal auth stub: read user id from header, default to 'default'."""
    return x_user_id or "default"
