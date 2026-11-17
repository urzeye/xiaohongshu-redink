<div align="center">

<img src="frontend/public/logo.png" alt="RedInk" width="200"/>

# RedInk (红墨) · 小红书 AI 爆款图文创作工具

**让传播不再需要门槛，让创作从未如此简单**

一句话选题 ➔ 智能大纲 ➔ 批量并发生成 3:4 竖图 ➔ 一键发布至小红书

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/Vue-3.4%2B-brightgreen.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](docker-compose.yml)

*本项目基于 [HisMax/RedInk](https://github.com/HisMax/RedInk) 及其衍生生态重构升级，在此衷心感谢原作者的卓越开源贡献！*

</div>

---

## 💡 为什么选择 RedInk？

对于个人博主、自媒体创作者和社媒运营来说，小红书图文制作常常面临几大痛点：**选题没灵感**、**封面排版慢**、**多图批量制作耗时**、**风格前后不统一**。

**RedInk (红墨)** 是一套专为社媒多图叙事定制的端到端开源创作引擎：
- 🎯 **一句话选题生成整套笔记**：输入一个想法，AI 自动拆解爆款大纲、正文与配图提示词。
- 🎨 **社媒原生 3:4 竖版出图**：严格遵循小红书高吸睛排版比例，封面与内页风格高度一致。
- ⚡ **批量并发制图与局部重试**：多页并发渲染，不满意的单张可一键重新生成。
- 🚀 **端到端一键发布闭环**：打通 VibeSurf 与小红书发布生态，生成满意直接发布。
- 🧠 **双核驱动（含概念可视化）**：不仅支持小红书图文，还支持长文学术概念映射与蓝图可视化。

---

## 效果展示

### 输入一句话，生成完整多图笔记

<details open>
<summary><b>Step 1: 智能大纲生成与自由编辑</b></summary>

<br>

![大纲示例](./images/example-2.png)

**功能特性：**
- 自由编辑每页大纲与核心文案
- 自由拖拽调整页面顺序与分块
- 自定义配置每张卡片的视觉描述词

</details>

<details open>
<summary><b>Step 2: 爆款封面页生成</b></summary>

<br>

![封面示例](./images/example-3.png)

**封面亮点：**
- 契合小红书首图吸睛规范
- 标题排版突出，文字准确无误
- 建立整组笔记的基准视觉风格

</details>

<details open>
<summary><b>Step 3: 内页多图批量并发生成</b></summary>

<br>

![内容页示例](./images/example-4.png)

**生成说明：**
- 并发批量生成所有内页卡片
- 支持单独重新生成不满意的页面
- 保证前后页面的色彩与设计统一

</details>

---

## 技术架构

<table>
<tr>
<td width="50%" valign="top">

### 后端技术栈 (Backend)

| 技术 | 说明 |
|------|------|
| **语言** | Python 3.9+ |
| **框架** | Flask + SQLAlchemy + Alembic |
| **包管理** | uv (极速依赖解析) |
| **文案模型** | Gemini / OpenAI / DeepSeek / 通义千问 |
| **图像模型** | Google GenAI (Imagen/Gemini) / DashScope / Replicate |
| **自动化发布** | VibeSurf / xiaohongshu-mcp |

</td>
<td width="50%" valign="top">

### 前端技术栈 (Frontend)

| 技术 | 说明 |
|------|------|
| **框架** | Vue 3 + TypeScript |
| **构建工具** | Vite |
| **UI 组件库** | Naive UI |
| **状态管理** | Pinia |
| **设计系统** | Modern CSS + The Viral Press (深色印鉴工坊) |

</td>
</tr>
</table>

---

## 快速开始

无论您是普通用户还是开发者，都可以从下面选择最适合您的部署方式。

### 方式一：Docker 一键部署（🔥推荐）

如果您只需要使用，不需要修改源码，这是最快且对环境毫无侵入的方式。

1. **前置要求**: 已安装 Docker 和 Docker Compose。
2. **启动命令**: 在包含 `docker-compose.yml` 的项目根目录下直接运行：

```bash
docker-compose up -d
```

启动后在浏览器访问 <http://localhost:5173> 即可使用。

---

### 方式二：本地源码部署（开发者）

如果您需要二次开发或自定义功能：

**前置要求**:
- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 18+
- pnpm 9+

#### 1. 克隆项目与配置

```bash
git clone https://github.com/urzeye/xiaohongshu-redink.git
cd xiaohongshu-redink
```

*提示：您可以将 `*.example` 复制一份并去掉 `.example` 后缀作为您的本地开发配置。*

#### 2. 分别安装与启动

分别开启两个终端运行前后端：

**终端 A：启动后端服务**

```bash
# 安装后端依赖
uv sync
# 启动后端服务 (默认监听 http://localhost:12398)
uv run python backend/app.py
```

**终端 B：启动前端 Web**

```bash
cd frontend
# 安装前端依赖
pnpm install
# 启动本地开发服务 (默认监听 http://localhost:5173)
pnpm dev
```

> ✅ **一键启动脚本（可选）**
> - Windows: 双击 `start.bat` 或运行 `scripts/start-windows.bat`
> - macOS / Linux: 运行 `bash scripts/start-all.sh`

*注：您可以在 Web 界面的**系统设置**中直接配置您的外部模型 API 提供商密钥（支持 BYOK 自带密钥）。*

---

## 注意事项

1. **API 配额与限流**: 请留意大语言模型与图像生成 API 的免费/付费配额方案。
2. **生成耗时**: 批量图片并发渲染取决于外部模型响应，请保持耐心。
3. **安全提示**: 切勿将带有私有 API Key 或 Cookies 信息的配置文件提交至公共代码仓库。

---

## 开源协议

本项目基于原项目协议采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议开源。

**你可以自由地：**
- 个人使用 - 用于学习、研究与个人创作
- 分享 - 在任何媒介以任何形式分发本项目
- 修改 - 转换或以本项目为基础进行二次创作

**但需遵守以下条款：**
- 署名 - 必须给出适当的署名（指向原始项目及本项目链接）
- 非商业性使用 - 不得将本作品用于商业目的
- 相同方式共享 - 二次修改必须以相同的协议开源

---

## 致谢

- [HisMax/RedInk](https://github.com/HisMax/RedInk) - 本项目衍生的原仓库。感谢原作者出色的底层设计与开源奉献。

---

**RedInk (红墨)** - 让 AI 帮创作者释放无限可能
