# 贡献指南

感谢你对 AgentFlow 的关注！欢迎任何形式的贡献——Bug 反馈、功能建议、文档改进、代码 PR。

## 提交 Issue

- **Bug 反馈**：请附上复现步骤、期望行为、实际行为，以及环境信息（操作系统、Python / Node 版本）。
- **功能建议**：说明使用场景和动机，方便讨论优先级。

## 提交 Pull Request

1. Fork 本仓库并克隆到本地
2. 从 `main` 切出特性分支：`git checkout -b feat/your-feature`
3. 完成改动并自测（见下方「本地开发」）
4. 提交：`git commit -m "feat: 简要说明你的改动"`
5. 推送并发起 PR：`git push origin feat/your-feature`

提交信息建议遵循 [Conventional Commits](https://www.conventionalcommits.org/)：
`feat:` 新功能 · `fix:` 修复 · `docs:` 文档 · `refactor:` 重构 · `test:` 测试 · `chore:` 杂项。

## 本地开发

```bash
# 一键启动（前后端依赖自动安装）
./start.sh          # macOS / Linux / Git Bash
./start.ps1         # Windows PowerShell
```

提交前请确保通过检查：

```bash
# 后端测试
cd backend && PYTHONPATH=. pytest tests/

# 前端类型检查 + 构建
cd frontend && npm run build
```

## 代码约定

- **前后端契约对齐**：修改 DSL / 节点 IO / 日志结构时，前端 `frontend/src/types/` 与后端 `backend/agentflow/engine/dsl.py`、`schemas/` 字段必须同步。
- **后端分层**：`routes（接口）→ service（业务）→ repository（数据访问）→ models（ORM）`，不要跨层调用。
- **新增节点**：通过 `@register_node` 注册，前端会自动从 `node-catalog` 拉取渲染。
- 保持与周边代码一致的命名、注释密度和风格。

## 行为准则

请保持友善、尊重与建设性。我们希望 AgentFlow 是一个让人愉快参与的社区。
