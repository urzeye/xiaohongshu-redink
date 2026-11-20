#!/usr/bin/env bash
set -e

# RedInk · 小红书 AI 爆款创作与本地安全发布引擎 (macOS / Linux 启动脚本)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo "  RedInk · 小红书 AI 爆款创作与本地安全发布引擎"
echo "  运行于本地家庭宽带网络环境，提供专属防风控保障"
echo "========================================================"
echo ""

# 检测 Python / uv
PYTHON_CMD=""
if command -v uv &>/dev/null; then
    PYTHON_CMD="uv run python"
    echo "[OK] 检测到 uv 包管理环境"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "[OK] 检测到本地虚拟环境 .venv"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo "[OK] 检测到系统 Python3 环境"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo "[OK] 检测到系统 Python 环境"
else
    echo "[错误] 未在当前系统中找到 Python 或 uv 环境！"
    echo "请先安装 Python 3.9+ (或运行: curl -LsSf https://astral.sh/uv/install.sh | sh)"
    exit 1
fi

# 检查前端静态产物
if [ ! -f "frontend/dist/index.html" ]; then
    echo "[提示] 首次运行或未检测到前端构建产物，正在尝试自动编译前端..."
    if command -v pnpm &>/dev/null; then
        pnpm --dir frontend install
        pnpm --dir frontend build
    else
        echo "[警告] 未检测到 pnpm，跳过前端编译。请在 frontend 目录执行 pnpm install && pnpm build。"
    fi
fi

echo ""
echo "[启动] 正在唤醒本地核心服务 (默认端口: 12398)..."
echo "[提示] 服务就绪后请在浏览器中访问: http://127.0.0.1:12398"
echo ""

# 尝试自动打开浏览器
(
    sleep 2
    if command -v xdg-open &>/dev/null; then
        xdg-open "http://127.0.0.1:12398"
    elif command -v open &>/dev/null; then
        open "http://127.0.0.1:12398"
    fi
) &

exec $PYTHON_CMD backend/app.py
