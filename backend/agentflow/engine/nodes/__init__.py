"""Built-in node library. Importing this package registers all built-in nodes."""
from agentflow.engine.nodes.registry import registry  # noqa: F401

# Import side-effects register each node class into the global registry.
from agentflow.engine.nodes import (  # noqa: F401,E402
    start_end,
    llm_node,
    knowledge_node,
    condition_node,
    iteration_node,
    http_node,
    tool_node,
    code_node,
    template_node,
    aggregator_node,
)
