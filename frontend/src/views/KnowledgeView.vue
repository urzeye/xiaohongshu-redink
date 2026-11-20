<template>
  <div class="container knowledge-container">
    <div class="page-header knowledge-header">
      <div>
        <h1 class="page-title">知识库管理</h1>
        <p class="page-subtitle">管理理论框架、图表类型与视觉设计预设规范</p>
      </div>
      <div class="header-search-wrap">
        <div class="search-input-box">
          <svg
            class="search-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            :placeholder="getSearchPlaceholder"
          />
          <button
            v-if="searchQuery"
            class="clear-btn"
            @click="searchQuery = ''"
            title="清除搜索"
          >
            &times;
          </button>
        </div>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="tabs-bar">
      <div class="tabs-group">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <svg
            v-if="tab.id === 'frameworks'"
            class="tab-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          <svg
            v-else-if="tab.id === 'charts'"
            class="tab-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
          <svg
            v-else-if="tab.id === 'styles'"
            class="tab-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"></circle>
            <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"></circle>
            <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"></circle>
            <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"></circle>
            <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path>
          </svg>
          <span>{{ tab.label }}</span>
          <span class="tab-count">{{ getTabCount(tab.id) }}</span>
        </button>
      </div>

      <div class="result-count-label">
        <span class="count-num">{{ currentFilteredCount }}</span> 项已收录
      </div>
    </div>

    <!-- 内容区 -->
    <div class="tab-content">
      <!-- 理论框架 -->
      <div
        v-if="activeTab === 'frameworks'"
        class="content-section"
      >
        <div class="section-intro">
          <p class="section-desc">用于概念剖析、深度认知与知识映射的理论分析模型</p>
        </div>

        <!-- Skeleton Loading -->
        <div
          v-if="loading"
          class="card-grid"
        >
          <div
            v-for="i in 6"
            :key="i"
            class="knowledge-card skeleton-card"
          >
            <div class="skeleton-line title"></div>
            <div class="skeleton-line desc"></div>
            <div class="skeleton-line desc short"></div>
            <div class="skeleton-tags">
              <div class="skeleton-tag"></div>
              <div class="skeleton-tag"></div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="filteredFrameworks.length === 0"
          class="empty-panel"
        >
          <div class="empty-icon">🔍</div>
          <div class="empty-text">未找到与「{{ searchQuery }}」匹配的理论框架</div>
          <button class="btn btn-secondary btn-sm" @click="searchQuery = ''">清除筛选</button>
        </div>

        <!-- Cards -->
        <div
          v-else
          class="card-grid"
        >
          <div
            v-for="framework in filteredFrameworks"
            :key="framework.id"
            class="knowledge-card"
          >
            <div class="card-header-line">
              <h3 class="card-title">{{ framework.name }}</h3>
              <span v-if="framework.components?.length" class="component-pill">
                {{ framework.components.length }} 模块
              </span>
            </div>
            <p class="card-desc">{{ framework.description }}</p>
            <div class="card-tags">
              <span
                v-for="domain in framework.domains"
                :key="domain"
                class="tag"
                @click="searchQuery = domain"
                title="按此领域筛选"
              >
                {{ domain }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表类型 -->
      <div
        v-if="activeTab === 'charts'"
        class="content-section"
      >
        <div class="section-intro">
          <p class="section-desc">结构化图示表达规范，适配不同信息密度与认知层级</p>
        </div>

        <!-- Skeleton Loading -->
        <div
          v-if="loading"
          class="card-grid"
        >
          <div
            v-for="i in 6"
            :key="i"
            class="knowledge-card skeleton-card"
          >
            <div class="skeleton-line title"></div>
            <div class="skeleton-line desc"></div>
            <div class="skeleton-line desc short"></div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="filteredCharts.length === 0"
          class="empty-panel"
        >
          <div class="empty-icon">📊</div>
          <div class="empty-text">未找到与「{{ searchQuery }}」匹配的图表类型</div>
          <button class="btn btn-secondary btn-sm" @click="searchQuery = ''">清除筛选</button>
        </div>

        <!-- Cards -->
        <div
          v-else
          class="card-grid"
        >
          <div
            v-for="chart in filteredCharts"
            :key="chart.id"
            class="knowledge-card chart-card"
          >
            <h3 class="card-title">{{ chart.name }}</h3>
            <p class="card-desc">{{ chart.description }}</p>
            <div class="card-tags">
              <span
                v-for="use in chart.best_for"
                :key="use"
                class="tag tag-chart"
                @click="searchQuery = use"
                title="按适用场景筛选"
              >
                {{ use }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 视觉风格 -->
      <div
        v-if="activeTab === 'styles'"
        class="content-section"
      >
        <div class="section-intro">
          <p class="section-desc">概念图出图调性与色彩配方预设（点击色块可快速复制十六进制色值）</p>
        </div>

        <!-- Skeleton Loading -->
        <div
          v-if="loading"
          class="style-grid"
        >
          <div
            v-for="i in 6"
            :key="i"
            class="style-card skeleton-card"
          >
            <div class="skeleton-preview"></div>
            <div style="padding: 16px;">
              <div class="skeleton-line title"></div>
              <div class="skeleton-line desc"></div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else-if="filteredStyles.length === 0"
          class="empty-panel"
        >
          <div class="empty-icon">🎨</div>
          <div class="empty-text">未找到与「{{ searchQuery }}」匹配的视觉风格</div>
          <button class="btn btn-secondary btn-sm" @click="searchQuery = ''">清除筛选</button>
        </div>

        <!-- Cards -->
        <div
          v-else
          class="style-grid"
        >
          <div
            v-for="style in filteredStyles"
            :key="style.id"
            class="style-card"
          >
            <div
              class="style-preview"
              :style="getStylePreview(style)"
            >
              <div class="preview-backdrop-grid"></div>
              <div class="preview-dot primary"></div>
              <div class="preview-dot secondary"></div>
              <div class="preview-line"></div>
            </div>
            <div class="style-info">
              <h3 class="style-title">{{ style.name }}</h3>
              <p class="style-desc">{{ style.description }}</p>
              <div class="color-swatches-row">
                <button
                  v-for="(color, key) in style.colors"
                  :key="key"
                  class="swatch-btn"
                  :style="{ backgroundColor: color }"
                  :title="`${key}: ${color} (点击复制)`"
                  @click="copyColorCode(color, String(key))"
                >
                  <span class="swatch-copy-hint">复制</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useMessage } from "naive-ui";
import {
  getKnowledgeFrameworks,
  getKnowledgeChartTypes,
  getKnowledgeVisualStyles,
} from "../api";

interface Framework {
  id: string;
  name: string;
  description: string;
  domains: string[];
  components?: string[];
}

interface ChartType {
  id: string;
  name: string;
  description: string;
  best_for: string[];
}

interface VisualStyle {
  id: string;
  name: string;
  description: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
  };
}

const message = useMessage();
const searchQuery = ref("");

const tabs = [
  { id: "frameworks", label: "理论框架" },
  { id: "charts", label: "图表类型" },
  { id: "styles", label: "视觉风格" },
];

const activeTab = ref("frameworks");
const loading = ref(true);
const frameworks = ref<Framework[]>([]);
const chartTypes = ref<ChartType[]>([]);
const visualStyles = ref<VisualStyle[]>([]);

const getSearchPlaceholder = computed(() => {
  switch (activeTab.value) {
    case "frameworks":
      return "搜索理论框架名称、领域或描述...";
    case "charts":
      return "搜索图表类型或适用场景...";
    case "styles":
      return "搜索视觉风格设计...";
    default:
      return "搜索知识库...";
  }
});

const filteredFrameworks = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return frameworks.value;
  return frameworks.value.filter((f) => {
    return (
      f.name.toLowerCase().includes(query) ||
      f.description.toLowerCase().includes(query) ||
      f.domains.some((d) => d.toLowerCase().includes(query))
    );
  });
});

const filteredCharts = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return chartTypes.value;
  return chartTypes.value.filter((c) => {
    return (
      c.name.toLowerCase().includes(query) ||
      c.description.toLowerCase().includes(query) ||
      c.best_for.some((b) => b.toLowerCase().includes(query))
    );
  });
});

const filteredStyles = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return visualStyles.value;
  return visualStyles.value.filter((s) => {
    return (
      s.name.toLowerCase().includes(query) ||
      s.description.toLowerCase().includes(query)
    );
  });
});

const currentFilteredCount = computed(() => {
  switch (activeTab.value) {
    case "frameworks":
      return filteredFrameworks.value.length;
    case "charts":
      return filteredCharts.value.length;
    case "styles":
      return filteredStyles.value.length;
    default:
      return 0;
  }
});

function getTabCount(tabId: string) {
  switch (tabId) {
    case "frameworks":
      return frameworks.value.length;
    case "charts":
      return chartTypes.value.length;
    case "styles":
      return visualStyles.value.length;
    default:
      return 0;
  }
}

async function fetchKnowledge() {
  loading.value = true;
  try {
    const [frameworksRes, chartsRes, stylesRes] = await Promise.all([
      getKnowledgeFrameworks(),
      getKnowledgeChartTypes(),
      getKnowledgeVisualStyles(),
    ]);

    if (frameworksRes.success && Array.isArray(frameworksRes.frameworks)) {
      frameworks.value = frameworksRes.frameworks;
    }
    if (chartsRes.success && Array.isArray(chartsRes.chart_types)) {
      chartTypes.value = chartsRes.chart_types;
    }
    if (stylesRes.success && Array.isArray(stylesRes.visual_styles)) {
      visualStyles.value = stylesRes.visual_styles;
    }
  } catch (err) {
    console.error("Failed to fetch knowledge:", err);
    message.error("获取知识库失败，请检查网络连接");
  } finally {
    loading.value = false;
  }
}

function getStylePreview(style: VisualStyle) {
  return {
    backgroundColor: style.colors.background || "#111",
    "--primary": style.colors.primary,
    "--secondary": style.colors.secondary,
  };
}

async function copyColorCode(color: string, label: string) {
  try {
    await navigator.clipboard.writeText(color);
    message.success(`已复制 ${label} 色值: ${color}`);
  } catch {
    message.warning(`色值: ${color}`);
  }
}

onMounted(() => {
  fetchKnowledge();
});
</script>

<style scoped>
.knowledge-container {
  padding-top: 0;
  max-width: 1200px;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.header-search-wrap {
  min-width: 280px;
  max-width: 380px;
  flex: 1;
}

.search-input-box {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 0 12px;
  transition: all var(--transition-fast) var(--ease-out);
}

.search-input-box:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.12);
}

.search-icon {
  color: var(--text-tertiary);
  margin-right: 8px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 9px 0;
  border: none;
  background: transparent;
  color: var(--text-main);
  font-size: 13px;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.clear-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
}

.clear-btn:hover {
  color: var(--text-main);
}

/* Tabs Bar */
.tabs-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-color);
}

.tabs-group {
  display: flex;
  gap: 8px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-sub);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast) var(--ease-out);
}

.tab-btn:hover {
  border-color: var(--text-secondary);
  color: var(--text-main);
  transform: translateY(-1px);
}

.tab-btn.active {
  background: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 600;
}

.tab-count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  background: var(--bg-hover);
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

.tab-btn.active .tab-count {
  background: rgba(255, 36, 66, 0.15);
  color: var(--primary);
}

.result-count-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.result-count-label .count-num {
  font-weight: 600;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}

.section-intro {
  margin-bottom: 16px;
}

.section-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Empty Panel */
.empty-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: var(--bg-card);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-lg);
  gap: 12px;
}

.empty-icon {
  font-size: 32px;
}

.empty-text {
  font-size: 14px;
  color: var(--text-sub);
}

/* Card Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 18px;
}

.knowledge-card {
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  transition: all var(--transition-fast) var(--ease-spring);
}

.knowledge-card:hover {
  border-color: rgba(255, 36, 66, 0.4);
  box-shadow: var(--shadow-card-hover), var(--shadow-glow-crimson);
  transform: translateY(-2px);
}

.card-header-line {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.4;
}

.component-pill {
  font-size: 11px;
  font-weight: 500;
  padding: 1px 7px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  border-radius: 12px;
  white-space: nowrap;
}

.card-desc {
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.55;
  margin-bottom: 14px;
  flex: 1;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
}

.tag {
  font-size: 11px;
  padding: 3px 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-sub);
  border-radius: var(--radius-xs);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.tag:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-light);
}

.tag-chart {
  background: var(--bg-input);
}

/* Style Grid */
.style-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.style-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  transition: all var(--transition-fast) var(--ease-spring);
}

.style-card:hover {
  border-color: rgba(255, 36, 66, 0.4);
  box-shadow: var(--shadow-card-hover), var(--shadow-glow-crimson);
  transform: translateY(-2px);
}

.style-preview {
  height: 110px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-backdrop-grid {
  position: absolute;
  inset: 0;
  opacity: 0.08;
  background-image: radial-gradient(circle, #fff 1px, transparent 1px);
  background-size: 12px 12px;
}

.preview-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  position: absolute;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s var(--ease-spring);
}

.style-card:hover .preview-dot {
  transform: scale(1.1);
}

.preview-dot.primary {
  background: var(--primary);
  left: 32%;
}

.preview-dot.secondary {
  background: var(--secondary);
  right: 32%;
}

.preview-line {
  position: absolute;
  width: 36%;
  height: 2px;
  background: var(--primary);
  opacity: 0.6;
}

.style-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.style-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 6px;
}

.style-desc {
  font-size: 12px;
  color: var(--text-sub);
  line-height: 1.5;
  margin-bottom: 14px;
  flex: 1;
}

.color-swatches-row {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.swatch-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.15s var(--ease-spring);
  padding: 0;
}

.swatch-btn:hover {
  transform: scale(1.18);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  z-index: 2;
}

.swatch-btn:active {
  transform: scale(0.95);
}

.swatch-copy-hint {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s;
}

.swatch-btn:hover .swatch-copy-hint {
  opacity: 1;
}

/* Skeleton Loaders */
.skeleton-card {
  pointer-events: none;
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-line.title {
  width: 60%;
  height: 18px;
  margin-bottom: 14px;
}

.skeleton-line.desc {
  width: 90%;
}

.skeleton-line.desc.short {
  width: 50%;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

.skeleton-tag {
  width: 48px;
  height: 20px;
  background: var(--bg-hover);
  border-radius: 4px;
}

.skeleton-preview {
  height: 110px;
  background: linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>