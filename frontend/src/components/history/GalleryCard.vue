<template>
  <!-- 历史记录卡片 -->
  <div class="gallery-card">
    <!-- 封面区域 -->
    <div
      class="card-cover"
      @click="$emit('preview', record.id)"
    >
      <img
        v-if="thumbnailUrl"
        :src="thumbnailUrl"
        alt="cover"
        loading="lazy"
        decoding="async"
        @error="handleThumbnailError"
      />
      <div
        v-else
        class="cover-placeholder"
      >
        <span>{{ record.title.charAt(0) }}</span>
      </div>

      <!-- 悬浮操作按钮 -->
      <div class="card-overlay">
        <!-- 核心动作：一键发布 / 再次发布 -->
        <button
          v-if="canPublish"
          class="overlay-btn overlay-btn-primary"
          @click.stop="$emit('publish', record.id)"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="btn-icon"
          >
            <path d="M22 2L11 13"></path>
            <path d="M22 2l-7 20-4-9-9-4 20-7z"></path>
          </svg>
          {{ record.is_published ? "再次发布" : "一键发布" }}
        </button>

        <!-- 次级动作：快速预览 -->
        <button
          class="overlay-btn"
          @click.stop="$emit('preview', record.id)"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="btn-icon"
          >
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          快速预览
        </button>

        <!-- 细粒度操作行：编辑文案 / 成片视图 -->
        <div class="overlay-sub-row">
          <button
            class="overlay-sub-btn"
            @click.stop="$emit('edit', record.id)"
          >
            {{ record.recordType === "concept" ? "查看详情" : "编辑文案" }}
          </button>
          <button
            v-if="record.recordType !== 'concept'"
            class="overlay-sub-btn"
            @click.stop="$emit('result', record.id)"
          >
            成片视图
          </button>
        </div>
      </div>

      <!-- 类型标识 -->
      <div
        class="type-badge"
        :class="record.recordType"
      >
        {{ typeLabel }}
      </div>

      <!-- 状态标识 -->
      <div
        class="status-badge"
        :class="statusBadgeClass"
      >
        <span
          v-if="statusBadgeClass === 'published'"
          class="status-dot"
        ></span>
        {{ statusText }}
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="card-footer">
      <div
        class="card-title"
        :title="displayTitle"
      >
        {{ displayTitle }}
      </div>

      <div class="card-meta">
        <div class="meta-left">
          <span class="meta-chip">{{ record.page_count }}页</span>
          <span
            v-if="publishedAccountLabel"
            class="published-account-chip"
            :title="publishedAccountTooltip"
          >
            <svg
              width="8"
              height="8"
              viewBox="0 0 24 24"
              fill="currentColor"
              class="chip-dot"
            >
              <circle cx="12" cy="12" r="8" />
            </svg>
            {{ publishedAccountLabel }}
          </span>
          <span class="meta-time" :title="timeTooltip">{{ formattedDateTime }}</span>
        </div>

        <n-popconfirm
          @positive-click="$emit('delete', record)"
          positive-text="确认删除"
          negative-text="取消"
        >
          <template #trigger>
            <button
              class="more-btn"
              title="删除记录"
              @click.stop
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <polyline points="3 6 5 6 21 6"></polyline>
                <path
                  d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                ></path>
              </svg>
            </button>
          </template>
          确定删除「{{ record.title }}」吗？
        </n-popconfirm>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { NPopconfirm } from "naive-ui";
import { getImageUrl, getBackendBaseUrl, withAccessToken } from "../../api";

/**
 * 历史记录卡片组件
 *
 * 展示单个历史记录的封面、标题、发布状态等信息
 * 支持一键发布、快速预览、编辑文案、成片查看、删除等操作
 */

interface Record {
  id: string;
  title: string;
  status: "draft" | "completed" | "generating" | "error" | "in_progress" | string;
  page_count: number;
  created_at: string;
  updated_at: string;
  thumbnail?: string;
  task_id?: string;
  recordType?: "xiaohongshu" | "concept";
  is_published?: boolean;
  published_accounts?: string[];
  last_published_at?: string;
  post_url?: string;
}

const props = defineProps<{
  record: Record;
}>();

defineEmits<{
  (e: "preview", id: string): void;
  (e: "edit", id: string): void;
  (e: "result", id: string): void;
  (e: "publish", id: string): void;
  (e: "delete", record: Record): void;
}>();

const isPublished = computed(() => {
  return props.record.recordType !== "concept" && Boolean(props.record.is_published);
});

const canPublish = computed(() => {
  return props.record.recordType !== "concept" && props.record.status === "completed";
});

const statusBadgeClass = computed(() => {
  if (isPublished.value) return "published";
  if (props.record.recordType !== "concept" && props.record.status === "completed") {
    return "pending-publish";
  }
  return props.record.status;
});

const statusText = computed(() => {
  if (isPublished.value) {
    if (props.record.published_accounts && props.record.published_accounts.length > 0) {
      return `已发布 · ${props.record.published_accounts[0]}`;
    }
    return "已发布";
  }
  if (props.record.recordType !== "concept" && props.record.status === "completed") {
    return "待发布";
  }
  const map: Record<string, string> = {
    draft: "草稿",
    completed: "已完成",
    generating: "生成中",
    error: "出错",
    in_progress: "进行中",
  };
  return map[props.record.status] || props.record.status;
});

const publishedAccountLabel = computed(() => {
  if (!isPublished.value || !props.record.published_accounts?.length) return "";
  const first = props.record.published_accounts[0];
  if (props.record.published_accounts.length > 1) {
    return `@${first} +${props.record.published_accounts.length - 1}`;
  }
  return `@${first}`;
});

const publishedAccountTooltip = computed(() => {
  if (!isPublished.value || !props.record.published_accounts?.length) return "";
  const accountsStr = props.record.published_accounts.join(", ");
  const timeStr = props.record.last_published_at
    ? `\n最后发布时间：${formatFullTime(props.record.last_published_at)}`
    : "";
  return `已发布账号：${accountsStr}${timeStr}`;
});

const thumbFailed = ref(false);

const thumbnailUrl = computed(() => {
  if (!props.record.thumbnail || !props.record.task_id) return "";

  if (props.record.recordType === "concept") {
    return withAccessToken(
      `${getBackendBaseUrl()}/output/concepts/${props.record.task_id}/${props.record.thumbnail}`
    );
  }
  return getImageUrl(
    props.record.task_id,
    props.record.thumbnail,
    !thumbFailed.value
  );
});

function handleThumbnailError() {
  if (!thumbFailed.value) {
    thumbFailed.value = true;
  }
}

const typeLabel = computed(() => {
  return props.record.recordType === "concept" ? "概念图" : "图文";
});

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

function formatFullTime(timeStr?: string): string {
  if (!timeStr) return "--";
  const d = new Date(timeStr);
  if (Number.isNaN(d.getTime())) return timeStr;
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

const formattedDateTime = computed(() => {
  const timeStr = props.record.created_at || props.record.updated_at;
  const d = new Date(timeStr);
  if (Number.isNaN(d.getTime())) return "--/-- --:--";
  return `${pad2(d.getMonth() + 1)}/${pad2(d.getDate())} ${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
});

const timeTooltip = computed(() => {
  const created = formatFullTime(props.record.created_at);
  const updated = formatFullTime(props.record.updated_at);
  return `创建时间：${created}\n更新时间：${updated}`;
});

const displayTitle = computed(() => {
  const text = String(props.record.title || "").trim();
  return text || "未命名图文";
});
</script>

<style scoped>
/* 卡片容器 */
.gallery-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition:
    transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
    border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  will-change: transform;
  contain: layout style paint;
}

.gallery-card:hover {
  transform: translateY(-4px) translateZ(0);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

/* 封面区域 */
.card-cover {
  aspect-ratio: 3/4;
  background: var(--bg-secondary);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  backface-visibility: hidden;
}

.gallery-card:hover .card-cover img {
  transform: scale(1.05) translateZ(0);
}

/* 封面占位符 */
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: var(--text-placeholder);
  font-weight: 800;
  background: var(--bg-secondary);
}

/* 悬浮遮罩层 */
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.52);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  pointer-events: none;
  will-change: opacity;
  padding: 16px;
}

.gallery-card:hover .card-overlay {
  opacity: 1;
  pointer-events: auto;
}

/* 遮罩层按钮 */
.overlay-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 140px;
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color 0.2s,
    border-color 0.2s,
    transform 0.15s,
    box-shadow 0.2s;
  will-change: transform;
}

.overlay-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.overlay-btn-primary {
  background: linear-gradient(135deg, #ff2442 0%, #ff5277 100%);
  border-color: #ff2442;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(255, 36, 66, 0.45);
}

.overlay-btn-primary:hover {
  background: linear-gradient(135deg, #e61e3b 0%, #ff3b65 100%);
  border-color: #ff2442;
  box-shadow: 0 6px 18px rgba(255, 36, 66, 0.6);
  transform: translateY(-2px);
}

.overlay-sub-row {
  display: flex;
  gap: 8px;
  width: 140px;
}

.overlay-sub-btn {
  flex: 1;
  padding: 6px 0;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.15s ease;
}

.overlay-sub-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.8);
  color: #fff;
  transform: translateY(-1px);
}

/* 类型标识 */
.type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  font-size: 10px;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.65);
  color: #ffffff;
  backdrop-filter: blur(4px);
}

.type-badge.concept {
  background: rgba(114, 46, 209, 0.85);
}

.type-badge.xiaohongshu {
  background: rgba(255, 36, 66, 0.85);
}

/* 状态标识 */
.status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.65);
  color: #ffffff;
  backdrop-filter: blur(4px);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge.published {
  background: rgba(16, 185, 129, 0.92);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

.status-badge.pending-publish {
  background: rgba(99, 102, 241, 0.92);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.9);
}

.status-badge.draft {
  background: rgba(245, 158, 11, 0.9);
  color: #ffffff;
}

.status-badge.generating,
.status-badge.in_progress {
  background: rgba(59, 130, 246, 0.9);
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.9);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
  display: inline-block;
  flex-shrink: 0;
}

/* 底部区域 */
.card-footer {
  padding: 14px 16px 14px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  color: var(--text-main);
  text-wrap: balance;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-sub);
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 7px;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-sub);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.published-account-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 22px;
  padding: 0 7px;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 500;
  color: #059669;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.28);
  max-width: 105px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 1;
}

.chip-dot {
  flex-shrink: 0;
}

.meta-time {
  color: var(--text-secondary);
  letter-spacing: 0.2px;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.more-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-xs);
  transition:
    background-color 0.2s,
    color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.more-btn:hover {
  background: var(--color-error-bg);
  color: var(--color-error);
}
</style>