# Changelog

All notable changes to this project will be documented in this file.

## [0.5.1] - 2026-11-23

### 🐛 布局与视觉修复
- **修复主内容区横向溢出**：移除 Naive UI Provider 上的 `display: contents` 内联样式，改为对 `#app > .n-config-provider` 显式声明 `width: 100%` 与 `min-width: 0`，根治 1200px 视口下主内容区被顶出视口右缘的问题。
- **修正滚动条配色反转**：滚动条滑块默认色改为深色主题适用的浅色，`data-theme="light"` 下使用深色滑块，与主题切换属性逻辑（深色移除属性）对齐。

### ✨ 交互与导航优化
- **路由级代码分割**：全部视图改为按需懒加载，首屏仅加载落地页，加快首次进入与页面切换；新增 `scrollBehavior`，前进/后退恢复滚动位置，主动导航回到顶部。
- **步骤条真实进度**：创作步骤条完成态改为由实际数据驱动（大纲页数、图片数量、主题内容），避免空流程下展示虚假进度。
- **空状态引导**：图文历史与概念图历史空状态新增「开启新创作 / 新建概念图」直达按钮。
- **细节打磨**：模式选择卡片错拍入场动效（遵循减弱动效偏好）、移动端隐藏侧栏折叠按钮、模板分类栏右侧渐隐滚动提示、大纲页无内容时隐藏修订浮窗、结果页空大纲回退至 `/redbook` 创作首页。

### 🧹 设计系统清理
- 清理 19 个零引用设计令牌（未使用的字号、阴影、边框变量等）与休眠的 `[data-theme="dark"]` 选择器，移除 `base.css` 中与 `components.css` 重复的 `.card` 定义，刷新 DESIGN.md 与 design.json 对齐实际实现。

## [0.5.0] - 2026-11-20

### 🎨 全面体验重构 (Impeccable Design System)
- **微动效与排版进化**：引入高精度微物理弹簧曲线 (`--ease-spring`) 与平滑减速曲线 (`--ease-out`)，全面遵循减弱动效偏好；关键指标、百分比进度条与时间计数全量接入等宽数字 (`tabular-nums`)，消除排版跳动。
- **深色工坊质感**：以 Crimson Seal 红印为核心建立深色工坊视觉体系，规范 `--shadow-glow-crimson` 等语义光晕 Token，显著提升卡片与重点操作的层级深度。
- **知识库升级**：重构知识库管理视图，支持按领域、场景模糊搜索与标签分流，增加骨架屏微光与视觉风格色块一键点击复制反馈。
- **沉浸式画廊 Lightbox**：大图预览支持键盘快捷操作（`←`/`→` 切换翻页、`ESC` 关闭），新增页码动态指示与原图直链下载。

### 🛡️ 生产级防御与状态防并发 (Harden & Reliability)
- **告别原生阻塞弹窗**：全局彻底淘汰 `window.confirm()`，全量重构为 Naive UI 气泡确认框 (`NPopconfirm`)，保持现代 UI 一致性且不阻塞浏览器主线程。
- **并发与防重入机制**：大纲规划、启动出图、重试失败页、模板应用等关键动作增加并发锁定；出图期间对“一键下载”、“重绘单页”、“发布到小红书”实施互斥保护并明确展示原因提示。
- **任务安全回退**：渲染未完成时点击“再来一篇”触发确认阻断，防止后台并发任务被意外中止。

### 🔄 全链路跨页面协同与后台感知 (Workflow & Reactivity)
- **全局动态任务胶囊**：用户切换离开生成页时，顶部常驻悬浮渲染进度胶囊，支持实时进度反馈（如 `P3/8`）与一键切回结果页。
- **步骤条解冻**：出图过程中步骤条保持对结果页的导航可达性，支持随时查看大纲与追踪出图。
- **侧边栏状态脉冲**：图文菜单集成红点呼吸动效，直观展示后台活跃任务。

### 📢 小红书多账号管理与发布链路强化 (Publish & Accounts)
- **多账号无缝切换**：支持绑定多个小红书创作者账号，独立持久化凭证与会话状态。
- **历史记录直达发布**：创作历史卡片支持展示已发布账号标识、一键直发、多维度时间排序与分类筛选。

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
