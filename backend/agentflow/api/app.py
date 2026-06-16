"""FastAPI application factory + middleware + CORS + startup seeding."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentflow.core.config import settings
from agentflow.core.db import init_db
from agentflow.utils.logger import get_logger

logger = get_logger("api")


def create_app() -> FastAPI:
    app = FastAPI(title="AgentFlow", version="0.1.0", description="可视化 Agent 工作流编排平台")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # routes — register marketplace BEFORE workflow so /market and /import
    # static segments win over the dynamic /{wf_id} routes.
    from agentflow.api.routes import knowledge, logs, marketplace, plugin, workflow

    app.include_router(marketplace.router)
    app.include_router(workflow.router)
    app.include_router(knowledge.router)
    app.include_router(plugin.router)
    app.include_router(logs.router)

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok", "service": "agentflow"}

    @app.on_event("startup")
    def _startup():
        init_db()
        from agentflow.plugins.runtime import load_builtin_plugins
        load_builtin_plugins()
        _seed_demo_data()
        logger.info("AgentFlow API ready")

    return app


def _seed_demo_data() -> None:
    """Seed a demo plugin + workflow template on first run (idempotent)."""
    from agentflow.core.db import SessionLocal
    from agentflow.repositories.plugin_repo import PluginRepository
    from agentflow.repositories.log_repo import MarketplaceRepository

    db = SessionLocal()
    try:
        prepo = PluginRepository(db)
        if not prepo.get("builtin_weather"):
            prepo.create(
                id="builtin_weather",
                name="天气查询",
                type="tool",
                version="1.0.0",
                description="查询城市天气（内置示例插件）",
                icon="weather",
                author="agentflow",
                manifest={
                    "name": "weather_tool",
                    "type": "tool",
                    "io_spec": {
                        "inputs": [{"name": "city", "type": "string", "required": True, "description": "城市名"}],
                        "outputs": [
                            {"name": "temperature", "type": "number"},
                            {"name": "description", "type": "string"},
                        ],
                    },
                },
                status="published",
            )

        mrepo = MarketplaceRepository(db)
        if not mrepo.list():
            mrepo.create(
                name="知识库问答工作流",
                description="开始 → 知识检索 → LLM → 结束 的 RAG 问答模板",
                dsl=_demo_rag_dsl(),
                dependencies={"plugins": [], "datasets": []},
                author="agentflow",
                category="问答",
            )
    finally:
        db.close()


def _demo_rag_dsl() -> dict:
    return {
        "name": "知识库问答工作流",
        "graph": {
            "nodes": [
                {"id": "start_1", "type": "start", "position": {"x": 60, "y": 160},
                 "data": {"outputs": [{"name": "query", "type": "string", "required": True}]}},
                {"id": "kr_1", "type": "knowledge_retrieval", "position": {"x": 320, "y": 160},
                 "data": {"dataset_ids": [], "top_k": 3, "score_threshold": 0.3, "search_mode": "hybrid",
                          "inputs": [{"name": "query", "type": "string", "value": "{{start_1.query}}"}],
                          "outputs": [{"name": "result", "type": "array[object]"}]}},
                {"id": "llm_1", "type": "llm", "position": {"x": 600, "y": 160},
                 "data": {"model": "Qwen/Qwen2.5-7B-Instruct",
                          "system": "你是一个有用的助手。如果提供了参考资料，优先依据资料回答；若资料为空或无关，则用你自己的知识直接回答用户问题，不要答非所问。",
                          "inputs": [
                              {"name": "query", "type": "string", "required": True, "value": "{{start_1.query}}"},
                              {"name": "context", "type": "string", "value": "{{kr_1.result}}"},
                          ],
                          "prompt": "",
                          "outputs": [{"name": "text", "type": "string"}]}},
                {"id": "end_1", "type": "end", "position": {"x": 880, "y": 160},
                 "data": {"inputs": [{"name": "answer", "type": "string", "value": "{{llm_1.text}}"}]}},
            ],
            "edges": [
                {"source": "start_1", "target": "kr_1"},
                {"source": "kr_1", "target": "llm_1"},
                {"source": "llm_1", "target": "end_1"},
            ],
        },
    }


app = create_app()
