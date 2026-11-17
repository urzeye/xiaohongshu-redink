# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **核心用户**：个人内容创作者、小红书自媒体博主、品牌与社媒运营人员。
- **用户场景与任务**：在日常内容创作中面临选题构思慢、封面设计门槛高、多图批量排版繁琐等瓶颈，需要快速将一个选题或灵感转化为符合小红书爆款排版与视觉习惯的高质量图文笔记并完成发布。
- **次要/辅助用户**：知识创作者、学者与研究人员，需借助“概念可视化”能力将复杂逻辑、理论框架或学术文章转化为清晰的结构化知识蓝图。

## Product Purpose

- **使命与存在价值**：“让传播不再需要门槛，让创作从未如此简单”。
- **解决的核心问题**：抹平视觉设计、社媒文案编排与多图批量制作的技术门槛，让创作者仅需输入一句话或一个主题，即可获得工业化水准的整套图文卡片。
- **成功的标准**：极低的人工干预耗时、高可读性与视觉吸睛度、端到端完整闭环（从主题输入到一键发布至平台）。

## Positioning

- **专为社媒多图叙事定制的端到端创作引擎**：不同于通用单图生成工具或纯文本写作助手，RedInk 围绕“多页图文卡片叙事流”进行全栈设计，无缝融合“智能大纲构思 -> 爆款封面设计 -> 批量内页并发生成 -> 平台一键发布”，具备强烈的社媒原生感与系列感。

## Operating Context

- **前端架构**：Vue 3 + TypeScript + Vite + Pinia + Naive UI，单页 Web 应用（默认监听 `http://localhost:5173`）。
- **后端架构**：Python 3.9+ / Flask / SQLAlchemy / Alembic 统一服务层（默认监听 `http://localhost:12398`）。
- **部署形态**：支持本地开发直接运行（uv + pnpm）及 Docker Compose 容器化一键部署。
- **外部生态集成**：
  - 多模型 API 提供商体系（Gemini/Google GenAI, OpenAI, DashScope/Qwen, Replicate 等，支持 BYOK 自定义配置与环境变量注入）。
  - 小红书发布生态（集成 VibeSurf 浏览器自动化与 xiaohongshu-mcp 协议通道）。
  - 数据存储（支持本地 SQLite / YAML 与 Supabase 云端同步）。

## Capabilities and Constraints

- **核心能力**：
  - **小红书图文模式**：主题输入与搜索扩展、智能大纲生成与分页可视化编辑、封面图生成、内页多图批量并发生成与单页重新生成、生成历史与发布中心。
  - **概念可视化模式**：长文输入、理论框架映射（Framework Mapping）、图表与视觉风格匹配（如蓝图风格）。
  - **通用模块**：模板市集（模版分类检索与一键载入）、知识库管理（理论框架、图表类型与视觉风格 YAML 管理）、系统设置（模型厂商管理、访问令牌与速率限制）。
- **技术与业务约束**：
  - 外部模型存在调用配额、并发限制与生成耗时，系统需提供透明的并发控制、任务进度反馈与单图失败重试机制。
  - 小红书发布依赖登录态管理（Cookie / 本地浏览器会话）与合规性处理。

## Brand Commitments

- **核心品牌名称**：RedInk（代码库及文档历史演进中曾出现 MotifLab 与 渲染AI，官方确立核心品牌延续为 RedInk）。
- **品牌口号**：让传播不再需要门槛，让创作从未如此简单。
- **品牌气质**：高效、敏捷、懂社媒流量密码、专业可信赖的创作者伙伴。

## Evidence on Hand

- **产品代码与前端视图**：`frontend/src/views/`（包含 LandingView、HomeView、OutlineView、GenerateView、ResultView、PublishView、ConceptView、TemplateMarketView 等成熟功能界面）。
- **后端核心架构**：`backend/routes/`、`backend/application/`、`backend/infrastructure/`、`backend/knowledge/`。
- **视觉与设计资产**：`frontend/public/logo.png`、功能演示图 `images/example-2.png`、`images/example-3.png`、`images/example-4.png`。
- **内置知识资产**：`backend/knowledge/frameworks/`（27+ 项理论分析框架）、`backend/knowledge/visual_styles/blueprint_style.yaml` 等。

## Product Principles

1. **端到端闭环，不跳出创作流**：从一个模糊想法到大纲、视觉卡片乃至发布到社媒，保持无缝的一站式流水线体验。
2. **AI 提供初稿，创作者保有最终掌控权**：AI 承担繁琐构思与批量排版工作，但在大纲分块、每页提示词、封面风格与重新生成上赋予创作者完全的微调自由。
3. **社媒原生与视觉一致性**：整组图片必须遵循一致的色彩、排版节奏与叙事逻辑，拒绝风格撕裂与拼接感。
4. **模型中立与开放可扩展**：架构上与特定模型厂商解耦，允许创作者自由切换文案与图片模型，支持本地部署与私有配置。

## Accessibility & Inclusion

- 遵循现代 Web 语义化规范，确保表单与操作按钮具备高可辨识度、清晰的聚焦态与交互反馈。
- 异步批量图片渲染与耗时任务提供直观的进度状态与错误重试提示。
