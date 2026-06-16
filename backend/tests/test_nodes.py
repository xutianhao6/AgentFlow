"""Node execution tests."""
from agentflow.engine.nodes.registry import registry


def test_template_node():
    node = registry.create("template", {"template": "Hi {{ name }}"})
    out = node.run({"name": "Bob"}, {"variables": {}})
    assert out["output"] == "Hi Bob"


def test_aggregator_first_non_empty():
    node = registry.create("aggregator", {"inputs": [{"name": "a"}, {"name": "b"}]})
    out = node.run({"a": None, "b": "x"}, {"variables": {}})
    assert out["output"] == "x"


def test_catalog_has_all_node_types():
    types = {n["type"] for n in registry.catalog()}
    for t in ["start", "end", "llm", "knowledge_retrieval", "if_else", "iteration",
              "http_request", "tool", "code", "template", "aggregator"]:
        assert t in types
