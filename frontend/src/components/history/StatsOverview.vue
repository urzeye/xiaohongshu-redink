<template>
  <!-- 统计概览卡片 -->
  <div
    class="stats-overview"
    v-if="stats"
  >
    <!-- 全部作品 -->
    <div
      class="stat-box"
      :class="{ active: activeTab === 'all' }"
      role="button"
      tabindex="0"
      @click="$emit('select-tab', 'all')"
    >
      <div class="stat-icon-circle primary">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
        </svg>
      </div>
      <div class="stat-content">
        <h4>全部作品</h4>
        <div class="number">{{ stats.total || 0 }}</div>
      </div>
    </div>

    <!-- 待发布 -->
    <div
      class="stat-box"
      :class="{ active: activeTab === 'pending' }"
      role="button"
      tabindex="0"
      @click="$emit('select-tab', 'pending')"
    >
      <div class="stat-icon-circle indigo">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <h4>待发布</h4>
        <div class="number">{{ stats.by_status?.pending || 0 }}</div>
      </div>
    </div>

    <!-- 已发布 -->
    <div
      class="stat-box"
      :class="{ active: activeTab === 'published' }"
      role="button"
      tabindex="0"
      @click="$emit('select-tab', 'published')"
    >
      <div class="stat-icon-circle green">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <h4>已发布</h4>
        <div class="number">{{ stats.by_status?.published || 0 }}</div>
      </div>
    </div>

    <!-- 草稿箱 -->
    <div
      class="stat-box"
      :class="{ active: activeTab === 'draft' }"
      role="button"
      tabindex="0"
      @click="$emit('select-tab', 'draft')"
    >
      <div class="stat-icon-circle orange">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 20h9"></path>
          <path
            d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"
          ></path>
        </svg>
      </div>
      <div class="stat-content">
        <h4>草稿箱</h4>
        <div class="number">{{ stats.by_status?.draft || 0 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 历史记录统计概览组件
 *
 * 显示四个可点击筛选统计卡片：
 * - 全部作品
 * - 待发布数量
 * - 已发布数量
 * - 草稿箱数量
 */

interface Stats {
  total?: number;
  by_status?: {
    completed?: number;
    published?: number;
    pending?: number;
    draft?: number;
    generating?: number;
  };
}

defineProps<{
  stats: Stats | null;
  activeTab?: string;
}>();

defineEmits<{
  (e: "select-tab", tab: string): void;
}>();
</script>

<style scoped>
/* 统计概览容器 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* 单个统计卡片 */
.stat-box {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  user-select: none;
  transition:
    transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-box:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  border-color: var(--border-hover);
}

.stat-box.active {
  border-color: var(--primary);
  background: var(--bg-elevated, var(--bg-card));
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.12);
}

/* 图标圆圈 */
.stat-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.stat-box:hover .stat-icon-circle {
  transform: scale(1.05);
}

.stat-icon-circle.primary {
  background: var(--primary-light, rgba(255, 36, 66, 0.12));
  color: var(--primary);
}

.stat-icon-circle.indigo {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
}

.stat-icon-circle.green {
  background: var(--color-success-bg, rgba(16, 185, 129, 0.15));
  color: var(--color-success);
}

.stat-icon-circle.orange {
  background: var(--color-warning-bg, rgba(245, 158, 11, 0.15));
  color: var(--color-warning);
}

/* 统计内容 */
.stat-content h4 {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub);
  margin: 0 0 4px 0;
}

.stat-content .number {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1;
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum" 1;
}

/* 响应式布局 */
@media (max-width: 1100px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (max-width: 600px) {
  .stats-overview {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .stat-box {
    padding: 14px 16px;
  }

  .stat-content .number {
    font-size: 22px;
  }
}
</style>