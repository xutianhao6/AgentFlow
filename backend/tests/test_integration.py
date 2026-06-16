"""Full-flow integration test covering every API module + SSE debug."""
import io

from fastapi.testclient import TestClient

from agentflow.api.app import app

client = TestClient(app)


def test_full_platform_flow():
    # ---- 1. create + save workflow ----
    wf = client.post("/api/v1/workflows", json={"name": "集成测试工作流"}).json()
    wid = wf["id"]

    dsl = {
        "workflow_id": wid,
        "name": "集成测试工作流",
        "graph": {
            "nodes": [
                {"id": "start_1", "type": "start", "data": {"outputs": [{"name": "query", "type": "string", "required": True}]}},
                {"id": "tpl_1", "type": "template", "data": {
                    "inputs": [{"name": "q", "type": "string", "value": "{{start_1.query}}"}],
                    "template": "问题是：{{ q }}",
                    "outputs": [{"name": "output", "type": "string"}],
                }},
                {"id": "llm_1", "type": "llm", "data": {"prompt": "{{tpl_1.output}}", "outputs": [{"name": "text", "type": "string"}]}},
                {"id": "end_1", "type": "end", "data": {"inputs": [{"name": "answer", "type": "string", "value": "{{llm_1.text}}"}]}},
            ],
            "edges": [
                {"source": "start_1", "target": "tpl_1"},
                {"source": "tpl_1", "target": "llm_1"},
                {"source": "llm_1", "target": "end_1"},
            ],
        },
    }
    assert client.put(f"/api/v1/workflows/{wid}", json={"dsl": dsl}).status_code == 200

    # ---- 2. validate ----
    v = client.post("/api/v1/workflows/validate", json={"dsl": dsl}).json()
    assert v["valid"] is True

    # ---- 3. debug run via SSE ----
    with client.stream("POST", f"/api/v1/workflows/{wid}/debug", json={"inputs": {"query": "什么是RAG"}}) as resp:
        assert resp.status_code == 200
        events = [line for line in resp.iter_lines() if line and line.startswith("event:")]
    assert any("run_finished" in e for e in events)
    assert any("node_finished" in e for e in events)

    # ---- 4. run history ----
    runs = client.get(f"/api/v1/workflows/{wid}/runs").json()["items"]
    assert len(runs) >= 1
    run_id = runs[0]["run_id"]
    detail = client.get(f"/api/v1/runs/{run_id}").json()
    assert len(detail["node_logs"]) == 4

    # ---- 5. single-step run ----
    single = client.post(f"/api/v1/workflows/{wid}/nodes/tpl_1/run", json={"inputs": {"q": "hi"}}).json()
    assert single["status"] == "succeeded"
    assert single["outputs"]["output"] == "问题是：hi"

    # ---- 6. knowledge: create + upload + retrieve ----
    ds = client.post("/api/v1/datasets", json={"name": "kb", "index_method": "high_quality"}).json()
    dsid = ds["id"]
    files = {"file": ("doc.txt", io.BytesIO("RAG 是检索增强生成技术。".encode("utf-8")), "text/plain")}
    up = client.post(f"/api/v1/datasets/{dsid}/documents", files=files, data={"chunk_strategy": "general"})
    assert up.status_code == 200 and up.json()["status"] == "done"
    rr = client.post(f"/api/v1/datasets/{dsid}/retrieve", json={"query": "RAG", "top_k": 1, "score_threshold": 0.0}).json()
    assert len(rr["results"]) >= 1

    # ---- 7. plugin market + install ----
    market = client.get("/api/v1/plugins/market").json()["items"]
    assert len(market) >= 1
    pid = market[0]["id"]
    client.post("/api/v1/plugins/install", json={"plugin_id": pid})
    installed = client.get("/api/v1/plugins/installed").json()["items"]
    assert any(p["id"] == pid for p in installed)

    # ---- 8. workflow marketplace: publish + browse + import ----
    client.post(f"/api/v1/workflows/{wid}/publish", json={"category": "测试"})
    templates = client.get("/api/v1/workflows/market").json()["items"]
    assert len(templates) >= 1
    tpl_id = templates[0]["id"]
    imported = client.post("/api/v1/workflows/import", json={"template_id": tpl_id}).json()
    assert "workflow_id" in imported

    # ---- 9. export ----
    exported = client.get(f"/api/v1/workflows/{wid}/export").json()
    assert "dsl" in exported and "dependencies" in exported
