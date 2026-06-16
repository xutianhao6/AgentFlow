"""API smoke tests via FastAPI TestClient."""
from fastapi.testclient import TestClient

from agentflow.api.app import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_node_catalog():
    r = client.get("/api/v1/workflows/node-catalog")
    assert r.status_code == 200
    assert len(r.json()["nodes"]) >= 11


def test_workflow_crud_and_run():
    # create
    r = client.post("/api/v1/workflows", json={"name": "t"})
    wf = r.json()
    wid = wf["id"]

    dsl = {
        "workflow_id": wid,
        "name": "t",
        "graph": {
            "nodes": [
                {"id": "start_1", "type": "start", "data": {"outputs": [{"name": "q", "type": "string", "required": True}]}},
                {"id": "end_1", "type": "end", "data": {"inputs": [{"name": "a", "type": "string", "value": "{{start_1.q}}"}]}},
            ],
            "edges": [{"source": "start_1", "target": "end_1"}],
        },
    }
    r = client.put(f"/api/v1/workflows/{wid}", json={"dsl": dsl})
    assert r.status_code == 200

    r = client.post(f"/api/v1/workflows/{wid}/run", json={"inputs": {"q": "hello"}})
    assert r.status_code == 200
    assert r.json()["outputs"]["a"] == "hello"


def test_code_template():
    r = client.get("/api/v1/workflows/code-template", params={"language": "python"})
    assert r.status_code == 200
    assert "def main" in r.json()["template"]


def test_dataset_lifecycle():
    r = client.post("/api/v1/datasets", json={"name": "kb", "index_method": "high_quality"})
    ds = r.json()
    assert ds["index_method"] == "high_quality"
