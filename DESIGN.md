---
name: RedInk
description: 让传播不再需要门槛，让创作从未如此简单
colors:
  primary: "#ff2442"
  primary-hover: "#ff4d63"
  primary-active: "#e61731"
  neutral-bg: "#0a0a0b"
  neutral-sidebar: "#111113"
  neutral-card: "#16161a"
  neutral-elevated: "#1c1c21"
  neutral-input: "#0d0d0e"
  text-main: "#ffffff"
  text-sub: "#a1a1aa"
  text-secondary: "#71717a"
  text-placeholder: "#52525b"
  border: "#27272a"
  border-hover: "#3f3f46"
  success: "#10b981"
  error: "#ef4444"
  warning: "#f59e0b"
  info: "#3b82f6"
  accent-cyan: "#06b6d4"
  accent-purple: "#8b5cf6"
  accent-rose: "#f43f5e"
typography:
  display:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
    fontSize: "38px"
    fontWeight: 800
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  headline:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.015em"
  title:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  body:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif'
    fontSize: "12px"
    fontWeight: 500
    letterSpacing: "0.05em"
rounded:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text-main}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.neutral-elevated}"
    textColor: "{colors.text-main}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-sub}"
    rounded: "{rounded.sm}"
    padding: "14px 28px"
  input-field:
    backgroundColor: "{colors.neutral-input}"
    textColor: "{colors.text-main}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
  card-surface:
    backgroundColor: "{colors.neutral-card}"
    rounded: "{rounded.lg}"
    padding: "32px"
---

# Design System: RedInk

## Overview

**Creative North Star: "The Viral Press" (爆款工坊)**

RedInk 是一套专为自媒体与社媒爆款图文打造的工业级生产力设计系统。其核心理念“The Viral Press”融合了现代高精度工业制版的确定性与数字排版工作室的沉浸质感。整个界面以深黑曜石基底为默认主题构建“静音操作台”，消除所有非必要的多余装饰，将 100% 的视觉重量与注意力完全归还给用户正在构思与生成的图文内容。

系统在视觉表现上奉行严苛的高对比度与克制主义：主强调色采用极具张力的小红书印鉴红（#ff2442），它如同加盖在排版稿件上的权威印章与行动信号，在深邃的暗调背景中以微光晕（Crimson Glow）精准指引高价值交互，果断而克制。自 v0.5.0 起，全部交互过渡统一收敛到一条急速回弹缓动曲线（cubic-bezier(0.16, 1, 0.3, 1)）上，配合悬停微抬升，构成确定性的工业操作手感。

**Key Characteristics:**
- **极黑沉浸静音画布**：以 #0a0a0b 为默认底色，通过微弱色调阶梯（Tonal Layering）自然界定层级，无反光干扰；另备完整浅色变体，跟随系统或手动切换。
- **印鉴级视觉重音**：纯正鲜艳的绯红色（#ff2442）作为唯一核心品牌信号，仅在关键转化与状态点亮。
- **确定性工业手感**：紧密贴合的 1px 细微暗调边框、内嵌式输入框与适度倒角（8px/12px/16px），配合 150/220/350ms 三档急速回弹过渡，带来可靠沉稳的操作反馈。
- **社媒原生叙事比例**：排版布局围绕小红书 3:4 竖版多图流展开，保持原生态的移动端卡片感。

## Colors

以沉寂无瑕的黑曜石暗调为底板，将小红书标志性的深红作为高能量印鉴，点缀高明度语义状态色。系统默认深色主题，通过 `data-theme="light"` 切换完整浅色变体，品牌红在两套主题中保持一致。

### Primary
- **Crimson Seal** (#ff2442): 核心品牌与主交互强调色。用于主行动号召按钮（CTA）、选定标签、聚焦外框与高亮徽章，象征爆款发布的印鉴确认。
- **Crimson Hover** (#ff4d63): 悬停高亮态，增强交互响应敏感度。
- **Crimson Active** (#e61731): 点击按下态，提供扎实下陷的按压反馈。

### Neutral（深色默认）
- **Obsidian Press** (#0a0a0b): 全局页面底层画布，吸收一切杂光，构建专注暗房空间。
- **Charcoal Rail** (#111113): 侧边栏固定底色，提供稳定的导航锚点。
- **Graphite Bed** (#16161a): 主卡片与容器表面色，与画布形成 1 级细腻明度差。
- **Elevated Slate** (#1c1c21): 悬浮层、二级按钮与列表子项底色，提供 2 级抬升阶梯。
- **Abyss Input** (#0d0d0e): 输入框底色，呈现微下凹的容纳感。
- **Subtle Zinc** (#27272a): 默认暗色微边框，以 1px 明确结构边界而不显突兀。
- **Chalk White** (#ffffff): 主标题与主文本高对比文字色（符合 WCAG AA 级高对比度）。
- **Muted Zinc** (#a1a1aa): 副标题、辅助说明与未激活图标文字色。
- **Dark Slate** (#71717a): 三级元数据、不可用项与细分注解。

### Status / Auxiliary
- **Signal Emerald** (#10b981): 成功状态色。用于生成成功、发布就绪与健康运行检测指示点。
- **Signal Ruby** (#ef4444): 异常与失败色。用于接口错误、配额耗尽与阻断告警。
- **Signal Amber** (#f59e0b): 警示与注意色。用于并发限流、重试提醒与安全风险。
- **Signal Azure** (#3b82f6): 信息与链接色。用于外部知识库、帮助文档与学术概念图高亮。

### Chart Accents（数据与图表高亮）
- **Cyan Pulse** (#06b6d4) / **Violet Beam** (#8b5cf6) / **Rose Flare** (#f43f5e): 模板市集、概念可视化与历史统计中的系列区分色，仅在数据可视化语境使用，不参与界面结构着色。

### Light Theme（浅色变体）
浅色主题复用同一套令牌语义，画布翻转为 #fafafb，侧边栏与卡片为 #ffffff，悬浮层为 #f4f4f5；主文本转为 #18181b，副文本 #52525b，边框 #e4e4e7 / 悬停 #d4d4d8。状态色同步加深以保证白底对比度（成功 #059669、错误 #dc2626、警示 #d97706、信息 #2563eb），品牌红 #ff2442 保持不变。

### Named Rules
**The Crimson Seal Rule.** 主强调红（#ff2442）在单一视口中的色彩面积严格控制在 ≤5%。红色的克制与稀缺正是其作为爆款印鉴权威感的来源；严禁将大面积背景或长文本涂抹为红色。

## Typography

**Display Font:** system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", PingFang SC, Hiragino Sans GB, Microsoft YaHei, WenQuanYi Micro Hei, sans-serif
**Body Font:** system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", PingFang SC, Hiragino Sans GB, Microsoft YaHei, WenQuanYi Micro Hei, sans-serif
**Label/Mono Font:** ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace

**Character:** 严谨、清晰、极高数字渲染精度的现代无衬线体。现代系统字体族带来紧凑的字距与几何张力，兼顾苹方与微软雅黑的清晰笔画，在大字号下充满力量感，在小字号下保持长文可读性。

### Hierarchy
- **Display** (800, 38px, line-height 1.3, letter-spacing -0.025em): 着陆页英雄区核心大标题与品牌展示，仅用于 Persuade 场景。
- **Headline** (700, 28px, line-height 1.3, letter-spacing -0.015em): 页面主标题（H1 / Page Title）；移动端（<768px）收敛至 22px。
- **Title** (600, 18px, line-height 1.4, letter-spacing -0.01em): 模块标题与卡片标题（H2 / Section Title）。
- **Body** (400, 15px, line-height 1.65): 主要正文与提示说明，段落保持舒适的行高呼吸感。
- **Small** (400, 13px, line-height 1.5): 表单标签、卡片副标题与状态辅助文案。
- **Label / Caption** (500, 12px, line-height 1.4, letter-spacing 0.05em, uppercase): 药丸徽章、版本标签与元数据。

### Named Rules
**The Content Hierarchy Rule.** 页面各视口内标题、说明与正文字号跳跃比不低于 1.4 倍，副标题与标签必须使用置灰文本色（#a1a1aa / #71717a），确保创作者扫视时瞬间分辨信息层级。

**The Tabular Metric Rule.** 一切数字度量（统计值、页码、配额、进度、计数徽章）必须启用等宽数字（`font-variant-numeric: tabular-nums`），保证工业级的纵向对齐与数值跳变稳定。

## Layout

RedInk 采用固定左侧导航栏 + 自适应主内容区的流式布局：
- **侧边栏 (Sidebar)**: 默认宽度 280px，支持折叠至 72px 紧凑模式；边框右侧以 1px `#27272a` 细线切齐。
- **主容器 (Container)**: 最大宽度限定为 1440px，全局栅格间隙统一 24px (`--grid-gap`)，保持大屏下的视线聚集。
- **12 列栅格系统**: 支持标准 12 列灵活划分，各栅格间距统一为 24px。
- **响应式断点**:
  - `> 1200px`: 完整展开，主内容区内边距 24px / 32px。
  - `992px - 1200px`: 主内容内边距放宽至 36px / 40px。
  - `< 992px`: 侧边栏微调至 240px，主内容内边距收缩至 28px / 24px。
  - `< 768px`: 侧边栏抽屉式隐藏（`translateX(-100%)`），顶部出现 56px 移动顶栏，抽屉呼出时带 65% 黑色遮罩与 4px 背景模糊；主视口全屏填充（内边距 20px / 16px），页面标题收敛至 22px。

## Elevation & Depth

RedInk 严格采用“暗色阶分层（Tonal Layering）+ 微弱内发光 + 响应式轻抬升”的混合深度模型，放弃传统拟物化的大阴影，追求实体卡片在暗黑空间中的漂浮感。

### Shadow Vocabulary
- **Subtle Surface** (`box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35)`): 卡片与容器静止状态下的柔和环境遮蔽。
- **Lifted Surface** (`box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45)`): 卡片悬停（Hover）与聚焦时的立体抬升。
- **Deep Overlay** (`box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55)`): 移动端抽屉侧栏等最高悬浮层。
- **Seal Imprint** (`box-shadow: 0 4px 14px rgba(255, 36, 66, 0.28)`): 主按钮静止态的印鉴投影；悬停扩散为 `0 6px 20px rgba(255, 36, 66, 0.38)`，按下收拢为 `0 2px 8px rgba(255, 36, 66, 0.25)`。
- **Crimson Glow** (`box-shadow: 0 0 24px rgba(255, 36, 66, 0.28)`): 进度条与核心活动项的特征漫射光晕。

### Motion Grammar
全系统过渡统一为急速回弹曲线 `cubic-bezier(0.16, 1, 0.3, 1)`，分三档：微交互 150ms（按钮按压、颜色切换）、标准 220ms（卡片、侧栏折叠、菜单展开）、重过渡 350ms（弹窗浮现与页面级变化）；弹性强调使用 `cubic-bezier(0.34, 1.35, 0.64, 1)`。悬停抬升按元素量级递增：按钮 -1.5px、图片卡片 -4px、场景卡片 -6px。页面切换为约 240ms 的透明度 + 6px 纵向位移动画，并完整响应 `prefers-reduced-motion`。

### Named Rules
**The Quiet Canvas Rule.** 界面的空间感必须首先通过背景明度阶梯（#0a0a0b 底色 -> #16161a 容器 -> #1c1c21 悬浮项）与 1px 微边框表达。阴影仅作为交互状态的微动效反馈，严禁在静止态使用厚重发光或刺眼投影。

## Shapes

- **XS (4px)**: 徽章（Badge）、小提示胶囊、进度条轨道。
- **SM (8px)**: 按钮（Button）、表单输入框（Input）、操作标签（Tag）。
- **MD (12px)**: 导航项（Nav Item）、设置卡片子项（List Item Card）、图片卡片、模式卡图标底座。
- **LG (16px)**: 主功能卡片（Card）、模态弹窗外壳。
- **XL (20px)**: 模式选择大卡片（Mode Card）、特色推荐容器。
- **Full Pill (9999px)**: 计数徽章、滚动条与胶囊开关。

边框风格全系统高度统一为 1px 细线实线（`border: 1px solid var(--border-color)`）。全局焦点可见环为 2px 品牌红外描边、2px 偏移（`:focus-visible`，符合 WCAG 2.2 AA）；输入框聚焦时边框平滑过渡为 `var(--primary)`，并附带 3px 柔和淡红外发光。

## Components

### Buttons
- **Shape:** 饱满矩形倒角 (8px radius, `padding: 14px 28px`)，字号 15px / 600。
- **Primary:** 背景为 Crimson Seal (#ff2442)，文本为纯白，静止态带 Seal Imprint 投影 (`0 4px 14px rgba(255, 36, 66, 0.28)`)。
- **Hover / Focus:** 上浮 1.5px (`transform: translateY(-1.5px)`)，颜色变为 #ff4d63，投影扩散。
- **Active / Disabled:** 按下回落原位、投影收拢；禁用态透明度 0.55，投影与位移全部移除。
- **Secondary:** 背景为 Elevated Slate (#1c1c21)，边框 1px Subtle Zinc (#27272a)，悬停时回落至 Graphite Bed (#16161a) 并轻微上浮。
- **Ghost:** 背景透明，边框透明，悬停时填充 #1c1c21 并显示微边框，保持轻巧无压。
- **Sizes:** 小号 (`padding: 8px 16px`, 13px) 与大号 (`padding: 16px 36px`, 16px, 12px radius) 仅在密度极端处使用。

### Cards / Containers
- **Corner Style:** 16px 圆角 (`--radius-lg`)。
- **Background:** Graphite Bed (#16161a)。
- **Border:** 1px Subtle Zinc (#27272a)，悬停时渐变为 #3f3f46。
- **Shadow Strategy:** 静止 Subtle Surface，悬停升级为 Lifted Surface（见 Elevation & Depth）。
- **Internal Padding:** 24px - 32px。

### Inputs / Fields
- **Style:** 深邃下凹的 Abyss Input (#0d0d0e) 底色，1px 边框，内边距 `16px 20px`，8px 圆角。
- **Focus:** 边框平滑变为 #ff2442，底色抬升为 Graphite Bed (#16161a)，附带 3px 柔和淡红外发光（`box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.06)`）。

### Chips / Tags
- **Style:** Elevated Slate (#1c1c21) 底色，8px 圆角，字号 13px，间距 `10px 20px`。
- **Active State:** 激活时背景变为半透明淡红（`rgba(255, 36, 66, 0.12)`），边框与文本高亮为 Crimson Seal (#ff2442)。

### Tabs
- **Style:** 底部 1px 分栏线的横向标签条，项间距 32px，字号 15px / 500，默认置灰 (#a1a1aa)。
- **Active State:** 文本转为 Crimson Seal 并加粗至 600，底部浮出 2px 红色指示条（顶端 2px 圆角）。

### Navigation
- **Style:** 垂直排布在侧边栏，字号 15px / 500，圆角 12px，内边距 `14px 18px`。
- **Active State:** 背景填充淡红 (`rgba(255, 36, 66, 0.12)`)，左侧带有 3px 宽的小红书红竖条锚点 (`border-radius: 0 2px 2px 0`)。

### Mode Card (Signature Component)
- **Style:** 首页双核模式选择卡片（小红书模式 / 概念图模式），20px 大圆角卡片 (`padding: 36px 32px`)，内嵌 64px 圆角渐变图标底座——小红书模式为绯红渐变 (#ff2442 -> #ff526a)，概念图模式为湛蓝渐变 (#2563eb -> #3b82f6)；标题 22px / 700。
- **Hover:** 边框点亮为对应模式色（60% 透明度），并浮起对应色相的宽发散阴影（`0 16px 40px`，8% 模式色 + 20% 黑色环境影）。

## Do's and Don'ts

### Do:
- **Do** 严格保持暗黑静音底色（#0a0a0b 默认画布），确保所有内容卡片有明确的 1px 微边框（#27272a）包裹。
- **Do** 将主按钮、关键触发操作与核心选中态精准赋予 Crimson Seal（#ff2442）印鉴投影与微光晕。
- **Do** 在所有图文预览中保持 3:4 原生竖图比例 (`.ratio-redbook`)，真实还原小红书移动端阅读体验。
- **Do** 在异步图文批量渲染时展示清晰的分步骤进度条（带 Crimson Glow）与单卡片重试入口。
- **Do** 为统计值、计数与进度数字启用 tabular-nums 等宽数字，保持工业仪表盘式对齐。
- **Do** 新增颜色令牌时同步定义深色与浅色两套取值，保持双主题语义一致。

### Don't:
- **Don't** 在背景或装饰容器上使用大面积高饱和度红色渐变，避免视觉疲劳与抢夺注意力（模式卡图标底座的小面积渐变是唯一例外）。
- **Don't** 使用未经收敛的纯白色边框（禁止使用 `#ffffff` 作为边框色），必须使用 `#27272a` 或带有半透明度的暗色描边。
- **Don't** 在同一屏幕中并列放置两个以上的顶级红色实体主按钮，破坏单一行动焦点。
- **Don't** 混合使用随意圆角；严格遵循 4px/8px/12px/16px/20px 的阶梯规范。
