"""DSL -> StateGraph compile + run tests."""
from agentflow.engine.runtime import runtime
from agentflow.engine.validator import validate_dsl
from agentflow.engine.dsl import WorkflowDSL


def _linear_dsl():
    return {
        "workflow_id": "wf_t",
        "graph": {
            "nodes": [
                {"id": "start_1", "type": "start", "data": {"outputs": [{"name": "query", "type": "string", "required": True}]}},
                {"id": "llm_1", "type": "llm", "data": {"prompt": "Q: {{start_1.query}}", "outputs": [{"name": "text", "type": "string"}]}},
                {"id": "end_1", "type": "end", "data": {"inputs": [{"name": "answer", "type": "string", "value": "{{llm_1.text}}"}]}},
            ],
            "edges": [
                {"source": "start_1", "target": "llm_1"},
                {"source": "llm_1", "target": "end_1"},
            ],
        },
    }


def test_validate_ok():
    assert validate_dsl(WorkflowDSL(**_linear_dsl())) == []


def test_run_linear():
    r = runtime.run(_linear_dsl(), {"query": "hi"}, mode="debug", workflow_id="wf_t")
    assert r["status"] == "succeeded"
    assert "answer" in r["outputs"]
    assert len(r["node_logs"]) == 3


def test_validate_detects_bad_reference():
    dsl = _linear_dsl()
    dsl["graph"]["nodes"][1]["data"]["prompt"] = "{{missing.text}}"
    dsl["graph"]["nodes"][1]["data"]["inputs"] = [{"name": "x", "type": "string", "value": "{{missing.text}}", "required": True}]
    errors = validate_dsl(WorkflowDSL(**dsl))
    assert any("不存在" in e for e in errors)
