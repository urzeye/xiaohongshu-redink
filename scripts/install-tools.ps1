# RedInk xiaohongshu-mcp Windows Installer / Upgrader
[CmdletBinding()]
param(
    [switch]$Force,
    [string]$Repo = "xpzouying/xiaohongshu-mcp"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolDir = Join-Path $ProjectDir "tools\xiaohongshu-mcp"
$DataDir = Join-Path $ProjectDir "data\xiaohongshu"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RedInk xiaohongshu-mcp Windows 安装/升级" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (-not (Test-Path $ToolDir)) {
    New-Item -ItemType Directory -Path $ToolDir -Force | Out-Null
}
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}

$McpTarget = Join-Path $ToolDir "xiaohongshu-mcp.exe"
$LoginTarget = Join-Path $ToolDir "xiaohongshu-login.exe"
$ConfigTarget = Join-Path $ToolDir "config.json"

if (Test-Path $McpTarget) {
    if (-not $Force) {
        $confirm = Read-Host "已检测到现有 xiaohongshu-mcp.exe，是否确认覆盖升级？(y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-Host "[INFO] 取消升级。" -ForegroundColor Yellow
            return
        }
    }
}

# 确保停止旧进程
Get-Process -Name "*xiaohongshu*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "[INFO] 停止正在运行的进程: $($_.Name) (PID: $($_.Id))" -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

$McpUrl = "https://github.com/$Repo/releases/latest/download/xiaohongshu-mcp-windows-amd64.exe"
$LoginUrl = "https://github.com/$Repo/releases/latest/download/xiaohongshu-login-windows-amd64.exe"

$TempMcp = Join-Path $env:TEMP "xiaohongshu-mcp-download-$PID.exe"
$TempLogin = Join-Path $env:TEMP "xiaohongshu-login-download-$PID.exe"

try {
    Write-Host "[INFO] 正在下载最新 xiaohongshu-mcp.exe..." -ForegroundColor Blue
    Invoke-WebRequest -Uri $McpUrl -OutFile $TempMcp -UseBasicParsing
    Move-Item -Path $TempMcp -Destination $McpTarget -Force
    Write-Host "[OK] xiaohongshu-mcp.exe 安装成功！" -ForegroundColor Green

    Write-Host "[INFO] 正在下载辅助工具 xiaohongshu-login.exe..." -ForegroundColor Blue
    try {
        Invoke-WebRequest -Uri $LoginUrl -OutFile $TempLogin -UseBasicParsing
        Move-Item -Path $TempLogin -Destination $LoginTarget -Force
        Write-Host "[OK] xiaohongshu-login.exe 安装成功！" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] xiaohongshu-login.exe 下载失败（可选组件，不影响核心功能）: $_" -ForegroundColor Yellow
    }

    if (-not (Test-Path $ConfigTarget)) {
        $normalizedDataDir = $DataDir -replace '\\', '/'
        $configContent = @"
{
  "port": 18060,
  "data_dir": "$normalizedDataDir",
  "headless": false,
  "timeout": 30000
}
"@
        Set-Content -Path $ConfigTarget -Value $configContent -Encoding UTF8
        Write-Host "[OK] 已生成默认配置文件: $ConfigTarget" -ForegroundColor Green
    }

    Write-Host "[INFO] 验证二进制可执行性..." -ForegroundColor Blue
    & $McpTarget -h 2>$null | Out-Null
    Write-Host "[OK] 安装及验证全部完成！" -ForegroundColor Green
} finally {
    if (Test-Path $TempMcp) { Remove-Item $TempMcp -Force -ErrorAction SilentlyContinue }
    if (Test-Path $TempLogin) { Remove-Item $TempLogin -Force -ErrorAction SilentlyContinue }
}
