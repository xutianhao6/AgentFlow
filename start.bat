@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  AgentFlow 一键启动脚本 (Windows)
REM  - 安装后端依赖并启动 FastAPI (http://localhost:8000)
REM  - 安装前端依赖并启动 Vite   (http://localhost:5173)
REM ============================================================

REM 切到脚本所在目录 (去掉末尾反斜杠存入 ROOT)
cd /d "%~dp0"
set "ROOT=%CD%"

echo.
echo ===== [1/4] 检查环境 =====
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 python，请先安装 Python 3.10+ 并加入 PATH
    pause
    exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 npm，请先安装 Node.js 18+ 并加入 PATH
    pause
    exit /b 1
)

echo.
echo ===== [2/4] 安装后端依赖 =====
cd /d "%ROOT%\backend"
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)

echo.
echo ===== [3/4] 安装前端依赖 =====
cd /d "%ROOT%\frontend"
if not exist node_modules (
    call npm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo node_modules 已存在，跳过安装
)

echo.
echo ===== [4/4] 启动服务 =====
echo 释放可能被占用的端口 8000 / 5173 ...
for %%P in (8000 5173) do (
    for /f "tokens=5" %%K in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
        echo   终止占用端口 %%P 的进程 PID=%%K
        taskkill /F /PID %%K >nul 2>nul
    )
)

echo 后端: http://localhost:8000   (API 文档 http://localhost:8000/docs)
echo 前端: http://localhost:5173
echo 关闭弹出的两个子窗口即可停止服务。
echo.

REM 用 start 的 /D 参数指定工作目录，避免命令里嵌套引号
start "AgentFlow-Backend"  /D "%ROOT%\backend"  cmd /k python main.py
start "AgentFlow-Frontend" /D "%ROOT%\frontend" cmd /k npm run dev

timeout /t 5 >nul
start "" http://localhost:5173

echo 已在新窗口启动前后端服务。
endlocal
