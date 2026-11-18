# RedInk Tauri 跨平台桌面客户端打包脚本 (Windows)
[CmdletBinding()]
param(
    [switch]$NoBundle
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RedInk Tauri 桌面客户端打包程序 (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 检查 Node.js / pnpm / Rust 环境
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 pnpm，请先安装 pnpm (npm i -g pnpm)"
}
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 cargo/Rust 环境，请先安装 Rust (https://rustup.rs)"
}

# 2. 安装前端依赖与构建
Write-Host "[1/3] 检查并构建前端资源..." -ForegroundColor Blue
pnpm install
pnpm --dir frontend install
pnpm --dir frontend build

# 3. 执行 Tauri 打包
Write-Host "[2/3] 执行 Tauri 编译..." -ForegroundColor Blue
if ($NoBundle) {
    pnpm tauri build --no-bundle
    Write-Host "[3/3] 编译完成！可执行文件路径: src-tauri\target\release\redink.exe" -ForegroundColor Green
} else {
    pnpm tauri build
    Write-Host "[3/3] 打包完成！安装包位于: src-tauri\target\release\bundle\" -ForegroundColor Green
}
