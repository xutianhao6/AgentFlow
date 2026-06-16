# ============================================================
#  AgentFlow 一键启动脚本 (PowerShell)
#  用法: 右键“使用 PowerShell 运行”，或在 PowerShell 中执行:
#        powershell -ExecutionPolicy Bypass -File .\start.ps1
# ============================================================
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

function Need($cmd, $hint) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "[错误] 未找到 $cmd，$hint" -ForegroundColor Red
        exit 1
    }
}
Need python "请安装 Python 3.10+ 并加入 PATH"
Need npm    "请安装 Node.js 18+ 并加入 PATH"

Write-Host "===== [1/3] 安装后端依赖 =====" -ForegroundColor Cyan
python -m pip install -q -r backend/requirements.txt

Write-Host "===== [2/3] 安装前端依赖 =====" -ForegroundColor Cyan
if (-not (Test-Path "frontend/node_modules")) {
    Push-Location frontend; npm install; Pop-Location
} else {
    Write-Host "node_modules 已存在，跳过安装"
}

Write-Host "===== [3/3] 启动服务 =====" -ForegroundColor Cyan
# 释放可能被占用的端口，避免 WinError 10013 (端口已被占用)
foreach ($port in 8000, 5173) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "  终止占用端口 $port 的进程 PID=$($_.OwningProcess)"
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
}
Start-Sleep -Milliseconds 500

Write-Host "后端: http://localhost:8000  (API 文档 /docs)"
Write-Host "前端: http://localhost:5173"
Write-Host "已在新窗口启动前后端，关闭对应窗口即可停止。`n"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; python main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm run dev"

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"
