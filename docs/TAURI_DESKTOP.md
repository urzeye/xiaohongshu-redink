# RedInk 跨平台桌面客户端开发与分发指南 (Tauri 方案)

## 📌 背景与核心价值

发布小红书图文最关键的痛点是**账号与 IP 风控**。数据中心 IP（阿里云、腾讯云等）在发帖时极易被风控系统识别为自动化脚本，导致滑块死锁、限流甚至封禁。
因此，优先在个人电脑本地运行，便于用户管理登录态与浏览器会话；本地运行不能保证账号免受平台风控。

然而，传统的开发模式（Dev 模式）需要开启多个黑框控制台、安装 Node.js/Python 依赖环境，对非技术创作者极不友好。**基于 Tauri 的跨平台桌面客户端方案**彻底解决了这一痛点：
- 🪟 **全平台原生支持**：同时支持 Windows (x64) 与 macOS (Apple Silicon M系列及 Intel 架构)
- 🚀 **零黑框极简体验**：无命令行窗口弹出，双击即可作为原生客户端启动
- 📦 **轻量原生内核**：采用 Tauri v2，内存开销极低，打包体积仅 15MB 左右（对比 Electron 150MB+）
- 🛡️ **本地进程生命周期托管**：自动管控后台 Python 引擎与 `xiaohongshu-mcp` 进程，退出应用时自动优雅清理，杜绝端口残留
- 🔔 **系统托盘与原生控制**：支持最小化到任务栏/状态栏托盘，随时打开数据目录、查看日志或重启服务

---

## 🏗️ 架构设计

```
┌────────────────────────────────────────────────────────┐
│                   RedInk Desktop App                   │
├──────────────────────────┬─────────────────────────────┤
│  Frontend (WebView)      │  Tauri Core (Rust)          │
│  - Vue 3 + Naive UI      │  - Process Manager (子进程) │
│  - SPA 路由与图文编辑器  │  - System Tray (系统托盘)   │
│  - 桌面端环境感知状态栏  │  - Cross-platform IPC 通信  │
└────────────┬─────────────┴──────────────┬──────────────┘
             │ HTTP / REST                │ Spawns & Supervises
             ▼                            ▼
┌──────────────────────────┐    ┌────────────────────────┐
│  Python Backend (Flask)  │───▶│  xiaohongshu-mcp       │
│  - 监听 127.0.0.1:12398  │    │  - 监听 18060 端口     │
│  - 数据库/AI出图与文案   │    │  - 本地家庭宽带安全发布│
└──────────────────────────┘    └────────────────────────┘
```

1. **前端层**：直接由 Tauri 内置 Webview 渲染，使用相对路径 `/api` 与 `http://127.0.0.1:12398` 通信；
2. **Rust 控制层**：
   - 自动检测并启动 Python 环境（支持嵌入式 `runtime/`、`.venv`、`uv` 或系统环境）；
   - 探活 `http://127.0.0.1:12398/api/health`，就绪后无缝交付用户；
   - 监听窗口退出与系统信号，保证所有子进程安全终止；
3. **发布网关层**：由 Python 后端的 `mcp_manager` 直接按需拉起 `tools/xiaohongshu-mcp` 可执行文件。

---

## 🛠️ 本地开发与调试

### 前置要求
- **Rust**: 1.77+ (`rustc --version`, `cargo --version`)
- **Node.js**: 18+ (`pnpm` 9+)
- **Python**: 3.9+ (或已配置 uv)

### 常用命令

在项目根目录下：

```bash
# 1. 启动桌面端开发调试模式（同时启动前端热重载与本地桌面窗口）
pnpm desktop:dev

# 2. 仅本地独立编译桌面可执行文件（快速验证，无需 NSIS 打包工具）
pnpm tauri build --no-bundle

# 3. 构建发布级完整安装包（生成 Windows .exe / .msi 或 macOS .dmg）
pnpm desktop:build
```

---

## 📦 跨平台打包与发布 (CI/CD)

项目的唯一自动发布入口是 `.github/workflows/release.yml`，仅在推送版本 Tag 时运行。它调用 `.github/workflows/desktop-release.yml` 构建安装包；后者只有 `workflow_call` 入口，不会独立触发。

### 触发发布
每次推送版本 Tag（例如 `v0.4.0`），只启动一次发布运行，包含以下构建：
1. **Windows Runner**: 生成 NSIS（`.exe`）与 MSI（`.msi`）安装包。
2. **macOS Runner**: 安装 `aarch64-apple-darwin` 和 `x86_64-apple-darwin` 两个 Rust 目标，再由 Tauri 使用 `--target universal-apple-darwin` 生成通用 `.dmg`。

只有两端构建全部成功且三种安装包均存在，才会创建 GitHub Release 并上传产物。构建设置超时并在任一平台失败时取消其他矩阵构建，避免继续消耗运行时间。不要把线上 Actions 用作试错环境；发布前先在本地检查工作流并构建。

Dockerfile、Compose 和 Docker 发布工作流继续保留。Docker 镜像发布只有手动 `workflow_dispatch` 入口，不随 Tag 自动执行。

### 当前安装包的运行依赖

当前安装包包含桌面程序与前端，尚未内置 Python 后端、Python 运行时及 `xiaohongshu-mcp` 等发布工具。用户仍需按 README 准备项目源码、Python 依赖和发布工具，并通过 `REDINK_ROOT` 指向项目目录。开发机成功启动不能替代在全新环境中验证安装包。
