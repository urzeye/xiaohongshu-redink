@echo off
chcp 65001 >nul
title RedInk · 小红书 AI 爆款创作与本地安全发布引擎

echo ========================================================
echo   RedInk · 小红书 AI 爆款创作与本地安全发布引擎
echo   运行于本地家庭宽带网络环境，提供专属防风控保障
echo ========================================================
echo.

cd /d "%~dp0"

:: 检查 Python 运行环境
set PYTHON_CMD=
where uv >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=uv run python"
    echo [OK] 检测到 uv 包管理环境
    goto :check_frontend
)

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
    echo [OK] 检测到本地虚拟环境 .venv
    goto :check_frontend
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    echo [OK] 检测到系统 Python 环境
    goto :check_frontend
)

echo [错误] 未在当前系统中找到 Python 或 uv 环境！
echo 请先安装 Python 3.9+ (或运行: powershell -c "irm https://astral.sh/uv/install.ps1 | iex")
pause
exit /b 1

:check_frontend
:: 检查前端静态产物是否已构建
if not exist "frontend\dist\index.html" (
    echo [提示] 首次运行或未检测到前端构建产物，正在尝试自动编译前端...
    where pnpm >nul 2>nul
    if %errorlevel% equ 0 (
        call pnpm --dir frontend install
        call pnpm --dir frontend build
    ) else (
        echo [警告] 未检测到 pnpm，跳过前端编译。请在 frontend 目录执行 pnpm install && pnpm build。
    )
)

echo.
echo [启动] 正在唤醒本地核心服务 (默认端口: 12398)...
echo [提示] 服务就绪后将自动在浏览器中打开: http://127.0.0.1:12398
echo.

:: 延迟 2 秒自动打开浏览器
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:12398"

:: 启动后端服务（托管前端 SPA 与 API）
%PYTHON_CMD% backend/app.py

if %errorlevel% neq 0 (
    echo.
    echo [异常退出] 服务已终止，代码: %errorlevel%
    pause
)
