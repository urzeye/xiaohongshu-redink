# RedInk 绿色便携免安装包构建脚本 (Windows)
[CmdletBinding()]
param(
    [string]$OutputDir = "release\RedInk-Windows-Portable",
    [switch]$Zip
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RedInk 绿色便携包一键打包程序 (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 检查 redink.exe 是否已编译
$ReleaseExe = Join-Path $ProjectRoot "src-tauri\target\release\redink.exe"
if (-not (Test-Path $ReleaseExe)) {
    Write-Host "[1/4] 未发现 release 编译产物，正在先编译前端与 Tauri..." -ForegroundColor Yellow
    pnpm run desktop:build -- --no-bundle
} else {
    Write-Host "[1/4] 已找到 release 编译产物: $ReleaseExe" -ForegroundColor Green
}

# 2. 创建便携目标目录
$TargetDir = Join-Path $ProjectRoot $OutputDir
if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Write-Host "[2/4] 初始化便携目录: $TargetDir" -ForegroundColor Blue

# 3. 复制必需的应用文件
Write-Host "[3/4] 正在复制应用与 Python 后端文件..." -ForegroundColor Blue

# 3.1 复制 redink.exe
Copy-Item $ReleaseExe -Destination (Join-Path $TargetDir "redink.exe")

# 3.2 复制 backend 源码 (排除 __pycache__ 等)
$TargetBackend = Join-Path $TargetDir "backend"
New-Item -ItemType Directory -Force -Path $TargetBackend | Out-Null
Get-ChildItem -Path (Join-Path $ProjectRoot "backend") | Where-Object {
    $_.Name -notin @("__pycache__", ".pytest_cache", ".mypy_cache")
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $TargetBackend -Recurse -Force
}

# 递归清理目标 backend 下可能拷贝进去的 __pycache__
Get-ChildItem -Path $TargetBackend -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 3.3 复制 tools 目录 (包含 xiaohongshu-mcp.exe 等)
$ToolsDir = Join-Path $ProjectRoot "tools"
if (Test-Path $ToolsDir) {
    Copy-Item -Path $ToolsDir -Destination $TargetDir -Recurse -Force
}

# 3.4 复制必要配置文件与示例
$FilesToCopy = @(
    "pyproject.toml",
    "alembic.ini",
    "README.md",
    ".env.example",
    "text_providers.yaml.example",
    "image_providers.yaml.example",
    "search_providers.yaml.example"
)
foreach ($file in $FilesToCopy) {
    $src = Join-Path $ProjectRoot $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $TargetDir -Force
    }
}

# 3.5 复制内置模板数据
$TargetData = Join-Path $TargetDir "data"
New-Item -ItemType Directory -Force -Path $TargetData | Out-Null
$TemplateJson = Join-Path $ProjectRoot "data\template.json"
if (Test-Path $TemplateJson) {
    Copy-Item -Path $TemplateJson -Destination $TargetData -Force
}

# 4. 生成便携启动说明使用说明.txt
$ReadmePath = Join-Path $TargetDir "使用说明.txt"
$ReadmeContent = @"
RedInk · 小红书 AI 爆款创作与本地安全发布引擎 (绿色便携版)
============================================================

【启动方法】：
双击运行当前目录下的 redink.exe 即可直接启动！

【目录结构说明】：
- redink.exe: 原生桌面客户端主程序（GUI 界面）
- backend/: Python 核心创作与发布引擎代码包
- tools/: 小红书自动化发布网关 (xiaohongshu-mcp)
- data/: 您的用户数据与生成历史（首次启动后自动创建并持久化）
- .env.example: 环境变量配置模版

【重要说明】：
请保持当前文件夹内的完整结构，不要仅将 redink.exe 单独挪出。
本机需安装有 Python 3.9+ 或 uv（安装时请勾选 Add Python to PATH）。
进入客户端后在「系统设置」中填写您的 AI 大模型 API Key 即可开始创作！
"@
Set-Content -Path $ReadmePath -Value $ReadmeContent -Encoding UTF8

Write-Host "[4/4] 绿色便携包制作完成: $TargetDir" -ForegroundColor Green

# 5. 可选压缩为 zip
if ($Zip) {
    $ZipPath = "$TargetDir.zip"
    Write-Host "正在生成压缩包: $ZipPath ..." -ForegroundColor Blue
    if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
    Compress-Archive -Path "$TargetDir\*" -DestinationPath $ZipPath -Force
    Write-Host "压缩包已生成: $ZipPath" -ForegroundColor Green
}
