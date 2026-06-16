# AgentFlow ⚡

> 基于 **LangGraph 思想**构建的可视化 **Agent 工作流编排平台**（对标 Dify）。
>
> 在画布上拖拽节点、连线、配置输入输出，即可编排一条 AI 工作流；后端把这张可视化图（DSL）编译成状态驱动的执行图运行。

<p>
  <img alt="frontend" src="https://img.shields.io/badge/frontend-Vue3%20%2B%20Vue%20Flow-42b883">
  <img alt="backend" src="https://img.shields.io/badge/backend-FastAPI%20%2B%20LlamaIndex-009688">
  <img alt="zero-infra" src="https://img.shields.io/badge/run-zero%20infra%20(SQLite)-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## 目录

- [核心特性](#核心特性)
- [整体架构](#整体架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [内置节点库](#内置节点库)
- [知识库 / RAG](#知识库--rag)
- [画布快捷键](#画布快捷键)
- [接口总览](#接口总览)
- [前后端契约](#前后端契约)
- [项目结构](#项目结构)
- [配置项](#配置项)
- [测试](#测试)
- [生产部署](#生产部署)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 核心特性

| 模块 | 说明 |
|------|------|
| 🎨 **可视化编排** | Vue Flow 画布 + DSL + LangGraph 风格 StateGraph 编译器；拖拽、连线、缩放、小地图 |
| 🧩 **内置节点库** | start / end / llm / knowledge_retrieval / if_else / iteration / http_request / tool / code / template / aggregator |
| 🔗 **节点 IO + 变量系统** | `FieldSchema` 字段契约、`{{node.field}}` 变量引用、连线/类型/DAG 校验 |
| 📚 **知识库 RAG** | 基于 **LlamaIndex + Chroma**：上传 → 切分(General/Parent-Child/QA) → 索引 → 检索(语义/关键词/混合 + Rerank) |
| 🛒 **插件市场** | 插件即节点，安装即出现在节点面板；内置「天气查询」示例工具 |
| 💻 **自定义代码节点** | 选语言(Python / TS) → 生成模板 → 沙箱执行（子进程隔离 + 超时 + 危险模块拦截） |
| 🔁 **工作流市场** | DSL 导出 / 导入 + 依赖校验 + 节点 ID 重映射 |
| 🐛 **调试日志** | 仅测试态记录每节点 输入/输出/状态/错误/耗时；单步运行；运行历史；Last Run 角标 |
| ⌨️ **键盘快捷键** | 删除 / 复制粘贴 / 复制副本 / 全选 / 撤销重做（见下） |

> **零依赖即可运行**：默认 SQLite + 进程内向量库(Chroma 本地持久化) + 内存版 Redis 回退，无需任何外部基础设施即可启动并完整演示。

---

## 整体架构

前后端分离的 monorepo：画布序列化为 **DSL** 上传，后端编译为可执行状态图运行，逐节点把状态通过 **SSE** 推回前端调试面板。

```
┌─────────────────────────── 前端 (Vue3 + Vue Flow) ───────────────────────────┐
│  画布编排  ·  节点配置面板  ·  变量引用  ·  代码编辑器(Monaco)  ·  调试面板     │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                     │  Workflow DSL (utils/dsl.ts ↔ engine/dsl.py)
                                     │  REST + SSE   /api/v1/*
┌───────────────────────────────────▼──────────────────────────────────────────┐
│                          后端 (FastAPI)                                        │
│  routes → service → repository → models(ORM)                                   │
│                 │                                                              │
│                 ├─ engine     DSL → CompiledGraph(StateGraph 风格) → 运行/调试 │
│                 ├─ knowledge  LlamaIndex 管线（切分/索引/检索）→ Chroma        │
│                 ├─ plugins    插件即节点（manifest + 运行时加载）              │
│                 └─ sandbox    Python / Node 子进程沙箱                         │
└────────────────────────────────────────────────────────────────────────────┘
        存储：SQLite(默认) / MySQL  ·  Chroma 本地持久化  ·  Redis(可选，内存回退)
```

> **编译器说明**：后端自带一个复刻 LangGraph `StateGraph` 语义的原生执行器（`CompiledGraph`）——节点函数返回部分状态、经 reducer 合并、支持条件边分支。因此**装不装 `langgraph` 都能跑**。

---

## 技术栈

**前端**：Vue3 `<script setup>` · Vite · TypeScript · Pinia · Vue Router · **Vue Flow**(画布) · **Ant Design Vue** · Axios · **Monaco Editor**(代码节点)

**后端**：Python 3.10+ · **FastAPI** · SQLAlchemy 2.0 · **LlamaIndex**(RAG) · **ChromaDB**(向量库) · Jinja2(模板节点) · httpx · numpy

**模型**：默认 **[SiliconFlow](https://siliconflow.cn)**（OpenAI 兼容 API）
- 对话模型：`Qwen/Qwen2.5-7B-Instruct`（节点内可切换 72B / DeepSeek-V3 / GLM-4）
- 向量模型：`BAAI/bge-large-zh-v1.5`（1024 维，中文语义检索）
- **未配置 Key 时自动降级**为 mock LLM / 哈希向量，平台仍可完整演示。

---

## 快速开始

### 方式一：一键脚本（推荐）

```bash
# Git Bash / Linux / macOS
./start.sh

# Windows PowerShell
./start.ps1

# Windows CMD
start.bat
```

脚本会自动安装前后端依赖、释放占用端口，并同时启动：
- 后端 → http://localhost:8000 （API 文档 `/docs`）
- 前端 → http://localhost:5173 （开发代理 `/api` → `:8000`）

### 方式二：手动启动

**后端**

```bash
cd backend
pip install -r requirements.txt        # 或 uv sync
python main.py                         # http://localhost:8000（自动建表 + 注入演示数据）
```

**前端**

```bash
cd frontend
pnpm install                           # 或 npm install
pnpm dev                               # http://localhost:5173
```

启动后打开前端，即可看到内置的「**知识库问答工作流**」演示模板（start → 知识检索 → LLM → end 的 RAG 链路）。

> 想接入真实模型？在 `backend/.env` 填入 `SILICONFLOW_API_KEY` 即可，其余开箱即用。

---

## 内置节点库

| 节点 | type | 说明 |
|------|------|------|
| 开始 | `start` | 工作流入口，定义入参 |
| 结束 | `end` | 工作流出口，收集结果 |
| LLM | `llm` | 调用对话模型，支持 system / prompt / 变量注入 |
| 知识检索 | `knowledge_retrieval` | RAG 检索，输出文档块数组 |
| 条件分支 | `if_else` | 按条件路由到不同分支 |
| 循环迭代 | `iteration` | 对数组逐项执行子流程 |
| HTTP 请求 | `http_request` | 调用外部 HTTP 接口 |
| 工具 | `tool` | 插件工具节点（安装的插件） |
| 代码 | `code` | 自定义 Python / TS 代码（沙箱执行） |
| 模板 | `template` | Jinja2 文本模板拼装 |
| 聚合 | `aggregator` | 合并多路输入 |

节点通过 `@register_node` 自动注册，前端 `GET /api/v1/workflows/node-catalog` 拉取节点目录渲染到左侧面板。

---

## 知识库 / RAG

知识库基于 **LlamaIndex** 管线 + **Chroma** 持久化向量库实现，对前端保持稳定的 REST 契约。

```
上传文档 → 解析(pdf/md/docx/txt) → 切分 → 索引(Chroma) → 检索 → (Rerank)
```

- **切分策略**：`general`（句子切分）/ `parent_child`（父子块，子块入索引、父块上下文随元数据）/ `qa`（问答对）
- **索引方式**：`high_quality`（向量，真实 embedding）/ `economy`（关键词 BM25 为主）
- **检索模式**：`semantic`（向量）/ `keyword`（BM25）/ `hybrid`（`QueryFusionRetriever` 融合，可调语义/关键词权重）
- **Rerank**：可选，基于查询词重叠的轻量重排
- **持久化**：向量落盘到 `backend/storage/chroma`，重启后自动恢复
- **离线降级**：未配置 SiliconFlow Key 时用确定性哈希向量，全流程仍可跑通

> ⚠️ `bge-large-zh-v1.5` 单段输入上限为 **512 token**，切分层已强制每块 ≤480 字符并对超限块容错跳过，避免上传报错。

---

## 画布快捷键

在工作流编辑器画布中（顶部工具栏「⌨ 快捷键」也可查看）：

| 快捷键 | 行为 |
|--------|------|
| `Delete` / `Backspace` | 删除选中节点与连线（自动联动删除相连边） |
| `Ctrl/⌘ + C` / `V` | 复制 / 粘贴节点（新 ID、位置偏移） |
| `Ctrl/⌘ + D` | 复制为副本 |
| `Ctrl/⌘ + A` | 全选节点 |
| `Esc` | 取消选中 / 关闭配置面板 |
| `Ctrl/⌘ + Z` | 撤销 |
| `Ctrl/⌘ + Shift + Z`（或 `Ctrl + Y`） | 重做 |

> **开始 / 结束节点受保护，不可删除**；在配置面板输入框内打字时快捷键自动失效，不会误删节点。

---

## 接口总览

| 分类 | 接口 |
|------|------|
| 健康检查 | `GET /api/v1/health` |
| 工作流 | `POST/PUT/GET/DELETE /api/v1/workflows`、`/validate`、`/{id}/run`、`/{id}/debug`(SSE)、`/{id}/nodes/{nid}/run`、`/node-catalog`、`/code-template` |
| 知识库 | `GET/POST /api/v1/datasets`、`GET/DELETE /{id}`、`POST/GET/DELETE /{id}/documents`、`POST /{id}/retrieve` |
| 插件市场 | `GET /api/v1/plugins/market`、`/installed`、`POST /install`、`/publish`、`DELETE /{id}` |
| 工作流市场 | `GET /api/v1/workflows/market`、`POST /import`、`/{id}/publish`、`GET /{id}/export` |
| 调试日志 | `GET /api/v1/workflows/{id}/runs`、`/api/v1/runs/{run_id}`、`/api/v1/runs/{run_id}/nodes/{nid}` |

> 完整交互式文档见后端启动后的 **http://localhost:8000/docs** （Swagger UI）。

---

## 前后端契约

DSL 是前后端的「普通话」：画布序列化为 DSL 上传，加载时反序列化渲染回画布（`utils/dsl.ts` 双向互转）。

| 契约 | 前端 | 后端 |
|------|------|------|
| Workflow DSL | `types/dsl.ts` | `engine/dsl.py` |
| 节点 IO Schema | `types/node.ts` | `engine/nodes/base.py` |
| 节点日志 | `types/log.ts` | `schemas/log.py` |
| SSE 流式 | `utils/sse.ts` | `routes/workflow.py` |

> **关键约定**：前端 `types/` 与后端 `engine/dsl.py`、`schemas/` 字段必须对齐。

---

## 项目结构

```
AgentFlow/
├── frontend/                      # Vue3 前端
│   └── src/
│       ├── views/                 # 页面（workflow / knowledge / plugin / marketplace）
│       ├── components/canvas/     # 画布核心（FlowCanvas / 节点 / 连线 / 配置面板）
│       ├── components/code-editor # Monaco 代码编辑器
│       ├── components/debug/      # 调试日志面板
│       ├── composables/           # useFlowGraph / useCanvasShortcuts / useDebugRun ...
│       ├── stores/                # Pinia 状态
│       ├── api/ · types/ · utils/ # 接口层 / 类型 / DSL 互转
│
├── backend/                       # FastAPI 后端
│   ├── main.py                    # 启动入口
│   └── agentflow/
│       ├── api/routes/            # workflow / knowledge / plugin / marketplace / logs
│       ├── core/                  # config / llm / db / redis_client / object_storage
│       ├── engine/                # dsl / compiler / runtime / validator + nodes/
│       ├── knowledge/             # llama_setup / loader / splitter / indexer / retriever
│       ├── plugins/               # 插件系统 + builtin/weather_tool
│       ├── sandbox/               # python / node 子进程沙箱
│       ├── marketplace/           # 工作流市场导入导出
│       ├── observability/         # 调试日志 / tracer
│       ├── models/ · schemas/ · repositories/   # ORM / Pydantic / 数据访问
│       └── state/                 # session_store / checkpointer
│
├── docker/docker-compose.yml      # mysql + redis + chroma（生产可选）
├── docs/                          # 功能开发文档 / 项目目录结构
└── start.sh · start.ps1 · start.bat
```

> 后端分层：`routes（接口）→ service（业务）→ repository（数据访问）→ models（ORM）`，能力域（engine / knowledge / plugins / sandbox）横向挂在 service 下。

---

## 配置项

后端配置见 `backend/.env`（pydantic-settings 自动读取）：

| 变量 | 默认 | 说明 |
|------|------|------|
| `DATABASE_URL` | `sqlite:///./agentflow.db` | 数据库；生产可换 `mysql+pymysql://...` |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis；不可达时回退内存版 |
| `STORAGE_DIR` | `./storage` | 文档 / 插件包 / Chroma 落盘目录 |
| `SILICONFLOW_API_KEY` | 空 | 模型 Key；为空则降级 mock / 哈希向量 |
| `SILICONFLOW_BASE_URL` | `https://api.siliconflow.cn/v1` | OpenAI 兼容 base url |
| `LLM_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | 默认对话模型 |
| `EMBEDDING_MODEL` | `BAAI/bge-large-zh-v1.5` | 默认向量模型 |
| `CORS_ORIGINS` | `http://localhost:5173` | 允许的前端来源，逗号分隔 |

---

## 测试

```bash
cd backend
PYTHONPATH=. pytest tests/             # 全部
PYTHONPATH=. pytest tests/test_retriever.py -v   # RAG 检索（三种模式 + 删除失效）
```

覆盖：DSL→StateGraph 编译、节点执行、检索、沙箱隔离、API 集成。

```bash
cd frontend
npm run build                          # vue-tsc 类型检查 + Vite 构建
```

---

## 生产部署

```bash
# 起 mysql + redis + chroma 容器
docker compose -f docker/docker-compose.yml up -d

# 修改 backend/.env：
#   DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/agentflow
#   REDIS_URL=redis://localhost:6379/0
# 然后正常启动后端即可
```

> 代码沙箱当前为「子进程隔离 + 危险模块拦截 + 超时」的务实方案；生产环境建议叠加 OS 级限制（cgroups / seccomp / gVisor / 容器）。

---

## 常见问题

**Q：没有模型 Key 能用吗？**
A：能。LLM 自动降级为 mock 回显，Embedding 降级为确定性哈希向量，所有功能（编排/运行/RAG/检索）均可完整演示。

**Q：上传 PDF 报 `parameter is invalid (20015)`？**
A：已修复。根因是 `bge-large-zh` 的 512 token 上限；切分层现强制每块 ≤480 字符并对超限块容错跳过。若仍报「未提取到文本」，多为扫描件/图片型 PDF，需要 OCR（暂不支持）。

**Q：知识库数据存在哪？重启会丢吗？**
A：向量落盘到 `backend/storage/chroma`，元数据存数据库，重启自动恢复，不会丢。

**Q：画布删不掉开始/结束节点？**
A：这是有意保护——工作流必须有 start/end。其余节点可用 `Delete` 删除。

---

## 贡献

欢迎任何形式的贡献——Bug 反馈、功能建议、文档改进、代码 PR。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

简要流程：Fork → 切特性分支 → 自测（`pytest` + `npm run build`）→ 发起 PR。提交信息建议遵循 [Conventional Commits](https://www.conventionalcommits.org/)。

如果这个项目对你有帮助，欢迎点个 ⭐ Star 支持一下！

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源——可自由使用、修改、商用，只需保留版权声明。

---

<p align="center"><sub>AgentFlow · 让 AI 工作流像搭积木一样简单</sub></p>
