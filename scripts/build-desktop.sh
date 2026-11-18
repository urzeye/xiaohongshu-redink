#!/usr/bin/env bash
set -euo pipefail

# RedInk Tauri 跨平台桌面客户端打包脚本 (macOS / Linux)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  RedInk Tauri 桌面客户端打包程序 (macOS/Linux)"
echo "=========================================="

if ! command -v pnpm &> /dev/null; then
    echo "[ERROR] 未找到 pnpm，请先安装: npm install -g pnpm"
    exit 1
fi

if ! command -v cargo &> /dev/null; then
    echo "[ERROR] 未找到 cargo/Rust 环境，请先安装: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

echo "[1/3] 安装依赖并构建前端产物..."
pnpm install
pnpm --dir frontend install
pnpm --dir frontend build

echo "[2/3] 执行 Tauri 编译..."
NO_BUNDLE=0
for arg in "$@"; do
    if [ "$arg" == "--no-bundle" ]; then
        NO_BUNDLE=1
    fi
done

if [ "$NO_BUNDLE" -eq 1 ]; then
    pnpm tauri build --no-bundle
    echo "[3/3] 编译完成！可执行文件位于: src-tauri/target/release/redink"
else
    pnpm tauri build
    echo "[3/3] 打包完成！安装包位于: src-tauri/target/release/bundle/"
fi
