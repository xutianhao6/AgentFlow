"""Plugin request/response schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class InstallRequest(BaseModel):
    plugin_id: str


class PublishRequest(BaseModel):
    name: str
    type: Literal["tool", "model", "extension", "agent_strategy"] = "tool"
    description: str = ""
    icon: str = "plugin"
    version: str = "1.0.0"
    author: str = "anonymous"
    manifest: dict = {}
