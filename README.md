# AgentFlow ⚡

> 基于 LangGraph 思想构建的**可视化 Agent 工作流编排平台**（对标 Dify）。

用户在画布上拖拽节点、连线、配置 IO，即可编排一条 AI 工作流；后端将这张可视化图（DSL）编译为状态驱动的执行图运行。

## 功能模块

| 模块 | 说明 |
|------|------|
| 可视化工作流编排 | Vue Flow 画布 + DSL + StateGraph 风格编译器 |
| 内置节点库 | start/end/llm/knowledge_retrieval/if_else/iteration/http_request/tool/code/template/aggregator |
| 节点 IO 规范 + 变量系统 | `FieldSchema` 字段契约、`{{node.field}}` 变量引用、连线/类型/DAG 校验 |
| 知识库 RAG | 上传 → 切分(General/Parent-Child/QA) → 索引(高质量/经济) → 检索(语义/全文/混合 + Rerank) |
| 插件市场 | 插件即节点，安装即出现在节点面板；内置天气工具示例 |
| 自定义代码节点 | 选语言(Python/TS) → 生成模板 → 沙箱执行（子进程隔离 + 超时 + 危险模块拦截） |
| 工作流市场 | DSL 导出/导入 + 依赖校验 + ID 重映射 |
| 调试日志 | 仅测试态记录每节点 输入/输出/状态/错误/耗时；单步运行；Run History；Last Run |

## 技术栈

- **前端**：Vue3 `<script setup>` + Vite + TS + Pinia + Vue Router + Vue Flow + Ant Design Vue + Axios
- **后端**：Python + FastAPI + SQLAlchemy + (LangGraph 风格编译器) + Jinja2 + httpx + numpy

## 模型与零依赖运行

- **LLM / Embedding 默认使用 [SiliconFlow](https://siliconflow.cn)**（OpenAI 兼容 API）：
  - 对话模型：`Qwen/Qwen2.5-7B-Instruct`（可在节点配置切换 72B / DeepSeek-V3 / GLM-4）
  - 向量模型：`BAAI/bge-large-zh-v1.5`（1024 维，中文语义检索）
  - 配置见 `backend/.env` 的 `SILICONFLOW_API_KEY` / `LLM_MODEL` / `EMBEDDING_MODEL`
- 其余存储默认 **SQLite**、**进程内向量库（numpy 余弦）**、**内存版 Redis 回退**，无需任何外部基础设施即可启动。
- 若未配置 SiliconFlow Key，LLM/Embedding 自动降级为 **mock / 哈希向量**，平台仍可完整演示。
- 生产部署可切换 MySQL / Redis / Chroma（见 `docker/docker-compose.yml`）。

## 本地启动

### 后端

```bash
cd backend
pip install -r requirements.txt      # 或 uv sync
python main.py                       # http://localhost:8000  (自动建表 + 注入演示数据)
# 测试：PYTHONPATH=. pytest tests/
```

### 前端

```bash
cd frontend
pnpm install        # 或 npm install
pnpm dev            # http://localhost:5173 （代理 /api → :8000）
```

### （可选）生产基础设施

```bash
docker compose -f docker/docker-compose.yml up -d   # mysql + redis + chroma
# 然后修改 backend/.env 的 DATABASE_URL / REDIS_URL 指向容器
```

## 接口总览

| 分类 | 接口 |
|------|------|
| 工作流 | `POST/PUT/GET/DELETE /api/v1/workflows`、`/validate`、`/{id}/run`、`/{id}/debug`(SSE)、`/{id}/nodes/{nid}/run`、`/node-catalog`、`/code-template` |
| 知识库 | `POST /api/v1/datasets`、`/{id}/documents`(上传/列表/删除)、`/{id}/retrieve` |
| 插件市场 | `GET /api/v1/plugins/market`、`/installed`、`POST /install`、`/publish`、`DELETE /{id}` |
| 工作流市场 | `GET /api/v1/workflows/market`、`POST /import`、`/{id}/publish`、`GET /{id}/export` |
| 调试日志 | `GET /api/v1/workflows/{id}/runs`、`/api/v1/runs/{run_id}`、`/api/v1/runs/{run_id}/nodes/{nid}` |

## 前后端契约边界

| 契约 | 前端 | 后端 |
|------|------|------|
| Workflow DSL | `types/dsl.ts` | `engine/dsl.py` |
| 节点 IO Schema | `types/node.ts` | `engine/nodes/base.py` |
| 节点日志 | `types/log.ts` | `schemas/log.py` |
| SSE 流式 | `utils/sse.ts` | `routes/workflow.py` |

DSL 是前后端的「普通话」：画布序列化为 DSL 上传，加载时反序列化渲染回画布（`utils/dsl.ts` 双向互转）。
