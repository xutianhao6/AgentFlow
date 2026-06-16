"""Unified exception definitions."""
from __future__ import annotations


class AgentFlowError(Exception):
    """Base class for all platform errors."""


class NodeError(AgentFlowError):
    """Raised by a node when it fails during execution."""


class ValidationError(AgentFlowError):
    """DSL validation error (connections / types / DAG)."""


class SandboxError(AgentFlowError):
    """Code sandbox execution error."""


class SandboxTimeout(SandboxError):
    """Code execution exceeded the time limit."""


class NotFoundError(AgentFlowError):
    """Requested resource does not exist."""


class DependencyError(AgentFlowError):
    """Workflow import dependency (plugin/dataset) is missing."""
