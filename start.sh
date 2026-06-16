#!/usr/bin/env bash
# ============================================================
#  AgentFlow 一键启动脚本 (Git Bash / Linux / macOS)
#  - 安装后端依赖并启动 FastAPI (http://localhost:8000)
#  - 安装前端依赖并启动 Vite   (http://localhost:5173)
#  按 Ctrl+C 同时停止前后端。
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# --- pick python / npm ---
PY="$(command -v python || command -v python3 || true)"
[ -z "$PY" ] && { echo "[错误] 未找到 python，请安装 Python 3.10+"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "[错误] 未找到 npm，请安装 Node.js 18+"; exit 1; }

echo "===== [1/3] 安装后端依赖 ====="
"$PY" -m pip install -q -r backend/requirements.txt

echo "===== [2/3] 安装前端依赖 ====="
if [ ! -d frontend/node_modules ]; then
  ( cd frontend && npm install )
else
  echo "node_modules 已存在，跳过安装"
fi

# 释放可能被占用的端口 (Git Bash on Windows 用 netstat+taskkill；Linux/mac 用 lsof)
free_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids; pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    [ -n "$pids" ] && kill -9 $pids 2>/dev/null || true
  elif command -v netstat >/dev/null 2>&1 && command -v taskkill >/dev/null 2>&1; then
    netstat -ano 2>/dev/null | grep -E ":$port .*LISTENING" | awk '{print $5}' | sort -u | while read -r pid; do
      [ -n "$pid" ] && taskkill //F //PID "$pid" >/dev/null 2>&1 || true
    done
  fi
}
free_port 8000
free_port 5173

echo "===== [3/3] 启动服务 ====="
echo "后端: http://localhost:8000  (API 文档 /docs)"
echo "前端: http://localhost:5173"
echo "按 Ctrl+C 停止全部服务。"
echo

# stop both children on exit
pids=()
cleanup() {
  echo
  echo "正在停止服务..."
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  exit 0
}
trap cleanup INT TERM

( cd backend  && exec "$PY" main.py ) &
pids+=($!)

( cd frontend && exec npm run dev ) &
pids+=($!)

wait
