# Changelog

All notable changes to this project will be documented in this file.

## [0.4.2] - 2026-11-20

### 🚀 架构纯粹化与极简 Web 回归
- **移除 Tauri 桌面端外壳**：全面清理 Rust/Tauri 桌面端层与跨平台打包复杂度，回归轻量可靠的 **Vue 3 + Python (Flask/FastAPI)** 架构。
- **杜绝环境与死锁问题**：彻底消除桌面混合架构下的本地多进程拉起超时、探活死锁、SmartScreen 及 macOS Gatekeeper 签名受阻问题。

### ⚡ 开箱即用与家庭宽带防风控
- **一键双击极简启动**：原生提供 Windows `start.bat` 与 macOS/Linux `start.sh`，自动检测环境依赖并在默认浏览器打开应用，保持家庭宽带原生 IP 防风控保护。
- **CI/CD 自动免构建打包**：升级 GitHub Release 自动化工作流，发版时自动编译前端静态资源并打包 `RedInk-*.zip`，普通用户解压后无需安装 Node.js/pnpm 即可开箱即用。

### 🎨 UI 布局与视觉体验优化
- **消除横向溢出滚动条**：重构大纲页面卡片自适应栅格比例与主容器最大宽度，适配各类笔记本屏幕与浏览器窗口尺寸。
- **设置页配置管理升级**：预置主流模型（DeepSeek、通义千问、火山方舟/豆包、智谱等）开箱即用模板，支持外部修改后一键免重启热重载。

### 🐳 Docker 与文档完善
- **容器端口规范**：修正生产 Docker 容器统一访问端口为 `12398`，更新 `docker-compose.yml` 镜像标签与说明文档。


## [0.4.0] - 2026-11-18

### 🖥️ Desktop Application (Tauri v2)
- **Cross-Platform Desktop App**: Implemented native desktop application based on Tauri v2 for Windows (`.exe` / NSIS) and macOS (`.dmg` Universal Apple Silicon & Intel).
- **Zero-Friction Local Execution**: Runs directly in the user's home broadband environment to prevent account IP risk, eliminating manual Docker and Node.js setup requirements.
- **Process Lifecycle Management**: Seamlessly manages the local Python engine and `xiaohongshu-mcp` service without terminal black windows.
- **System Tray & Native Shortcuts**: Added system tray integration (minimize, quick show, restart engine) and native application menu support.

### 🚀 Publish Engine Improvements
- **Creator Center Session Auto-Sync**: Automatically synchronizes and injects `galaxy_creator_session_id` into `cookies.json` using the existing `web_session`, resolving creator center publish compatibility issues.
- **Creator Authorization Detection**: Real-time status detection for creator center authorization and real browser window opening for login authorization.
- **Silent Background Automation**: Upgraded to background silent publishing; eliminates unexpected browser popups and session flicker during routine checks.

### 🎨 Image Generation & Aspect Ratio Fixes
- **Dynamic Dimension Mapping**: Dynamically maps aspect ratio options (3:4, 1:1, 4:3, 9:16, 16:9) to standard pixel dimensions (e.g. 864x1152 for 3:4) across Volcano Ark and OpenAI-compatible APIs, resolving 1:1 square output limitations.

### 🛡️ Desktop & Web Stability
- **History Image Preview 401 Fix**: Injected authentication headers and tokens for image preview URLs, preventing 401 unauthorized errors on desktop.
- **Auto-Recovery for Missing History Images**: Automatically recovers missing history thumbnails or images from task directories without breaking history views.
- **Polling & Navigation Resilience**: Improved frontend long-polling resilience, tag copying, and menu navigation.

## [0.3.5] - 2026-03-05

### ✨ New Features / Visual Updates

- **Brand Identity**: Completely redesigned the core application logo. Replaced old visuals with an elegant, romantic skeuomorphic design featuring an intricate crystal starry night rose without distracting textual elements, improving the app's overall aesthetics.
- Favicon and top banner logo (144x144, 2048x2048 PNGs) have been successfully updated.

### 🎨 UI Improvements

- **Result View Enhancements**: Refined the user interface for displaying operation results.
  - Adjusted result tag colors to a crisp, professional blue tone.
  - Re-themed the progress bar to drift away from standard error red, providing a calmer, non-distracting appropriate color scheme.
