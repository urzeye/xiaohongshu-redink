<template>
  <!-- 图片画廊模态框 -->
  <div
    v-if="visible && record"
    class="modal-fullscreen"
    @click="$emit('close')"
  >
    <div
      class="modal-body"
      @click.stop
    >
      <!-- 头部区域 -->
      <div class="modal-header">
        <div style="flex: 1">
          <!-- 标题区域 -->
          <div class="title-section">
            <h3
              class="modal-title"
              :class="{ collapsed: !titleExpanded && record.title.length > 80 }"
            >
              {{ record.title }}
            </h3>
            <button
              v-if="record.title.length > 80"
              class="title-expand-btn"
              @click="titleExpanded = !titleExpanded"
            >
              {{ titleExpanded ? "收起" : "展开" }}
            </button>
          </div>

          <div class="modal-meta">
            <span
              >{{ record.outline.pages.length }} 张图片 ·
              {{ formattedDate }}</span
            >
            <span
              v-if="record.is_published"
              class="published-meta-badge"
              :title="publishedAccountsTooltip"
            >
              <span class="badge-dot"></span>
              已发布至 {{ publishedAccountSummary }}
            </span>
            <span
              v-else-if="record.status === 'completed'"
              class="pending-meta-badge"
            >
              🟣 待发布
            </span>
            <a
              v-if="record.post_url"
              :href="record.post_url"
              target="_blank"
              rel="noopener noreferrer"
              class="view-outline-btn post-link-btn"
              title="前往小红书查看已发布的笔记"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
              查看小红书帖子
            </a>
            <button
              class="view-outline-btn"
              @click="$emit('showOutline')"
              title="查看完整大纲"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                ></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line
                  x1="16"
                  y1="13"
                  x2="8"
                  y2="13"
                ></line>
                <line
                  x1="16"
                  y1="17"
                  x2="8"
                  y2="17"
                ></line>
              </svg>
              查看大纲
            </button>
            <button
              class="view-outline-btn"
              @click="$emit('showContent')"
              title="查看生成文案"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                ></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line
                  x1="16"
                  y1="13"
                  x2="8"
                  y2="13"
                ></line>
                <line
                  x1="16"
                  y1="17"
                  x2="8"
                  y2="17"
                ></line>
              </svg>
              查看文案
            </button>
          </div>
        </div>

        <div class="header-actions">
          <button
            v-if="record.status === 'completed'"
            class="btn btn-primary publish-direct-btn"
            @click="$emit('publish', record.id)"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M22 2L11 13"></path>
              <path d="M22 2l-7 20-4-9-9-4 20-7z"></path>
            </svg>
            {{ record.is_published ? "再次发布" : "一键发布" }}
          </button>
          <button
            class="btn btn-secondary download-btn"
            @click="$emit('downloadAll')"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line
                x1="12"
                y1="15"
                x2="12"
                y2="3"
              ></line>
            </svg>
            打包下载
          </button>
          <button
            class="close-icon"
            @click="$emit('close')"
          >
            ×
          </button>
        </div>
      </div>

      <!-- 图片网格 -->
      <n-image-group>
        <div class="modal-gallery-grid">
          <div
            v-for="(img, idx) in record.images.generated"
            :key="idx"
            class="modal-img-item"
          >
            <div
              class="modal-img-preview"
              v-if="img"
              :class="{ regenerating: regeneratingImages.has(idx) }"
            >
              <n-image
                :src="getImageUrl(img, record.images.task_id)"
                :preview-src="getOriginalImageUrl(img, record.images.task_id)"
                lazy
                :img-props="{
                  loading: 'lazy',
                  decoding: 'async',
                  style: 'width: 100%; height: 100%; object-fit: cover;',
                }"
                @error="handleImageError(img)"
                object-fit="cover"
                style="width: 100%; height: 100%; display: block"
              />
              <div class="modal-img-overlay">
                <button
                  class="modal-overlay-btn"
                  @click="$emit('regenerate', idx)"
                  :disabled="regeneratingImages.has(idx)"
                >
                  <svg
                    class="regenerate-icon"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M23 4v6h-6"></path>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                  </svg>
                  {{ regeneratingImages.has(idx) ? "重绘中..." : "重新生成" }}
                </button>
              </div>
            </div>
            <div
              class="placeholder"
              v-else
            >
              Waiting...
            </div>

            <div class="img-footer">
              <span>Page {{ idx + 1 }}</span>
              <span
                v-if="img"
                class="download-link"
                @click="$emit('download', img, idx)"
              >
                下载
              </span>
            </div>
          </div>
        </div>
      </n-image-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { NImage, NImageGroup } from "naive-ui";
import { appendUrlParams, getImageUrl as buildImageUrl } from "../../api";

/**
 * 图片画廊模态框组件
 *
 * 功能：
 * - 展示历史记录的所有生成图片
 * - 支持重新生成单张图片
 * - 支持下载单张/全部图片
 * - 可展开查看完整大纲
 */

// 定义记录类型
interface ViewingRecord {
  id: string;
  title: string;
  updated_at: string;
  status?: string;
  outline: {
    raw: string;
    pages: Array<{ type: string; content: string }>;
  };
  images: {
    task_id: string;
    generated: string[];
  };
  content?: {
    titles: string[];
    copywriting: string;
    tags: string[];
  };
  is_published?: boolean;
  published_accounts?: string[];
  last_published_at?: string;
  post_url?: string;
}

// 定义 Props
const props = defineProps<{
  visible: boolean;
  record: ViewingRecord | null;
  regeneratingImages: Set<number>;
}>();

// 定义 Emits
const emit = defineEmits<{
  (e: "close"): void;
  (e: "showOutline"): void;
  (e: "showContent"): void;
  (e: "downloadAll"): void;
  (e: "download", filename: string, index: number): void;
  (e: "regenerate", index: number): void;
  (e: "publish", id: string): void;
}>();

const publishedAccountSummary = computed(() => {
  if (!props.record?.published_accounts?.length) return "小红书";
  return `@${props.record.published_accounts.join(", @")}`;
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

const publishedAccountsTooltip = computed(() => {
  if (!props.record?.is_published) return "";
  const accountsStr = props.record.published_accounts?.join(", ") || "小红书已绑定账号";
  const timeStr = props.record.last_published_at
    ? `\n发布时间：${formatFullTime(props.record.last_published_at)}`
    : "";
  return `已发布至：${accountsStr}${timeStr}`;
});

// 标题展开状态
const titleExpanded = ref(false);
// 记录加载失败的缩略图，失败后回退原图
const failedThumbs = ref(new Set<string>());

function handleEsc(e: KeyboardEvent) {
  if (e.key === "Escape" && props.visible) {
    emit("close");
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleEsc);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleEsc);
});

function getImageUrl(filename: string, taskId: string) {
  const baseUrl = buildImageUrl(
    taskId,
    filename,
    !failedThumbs.value.has(filename),
  );
  if (failedThumbs.value.has(filename)) {
    return appendUrlParams(baseUrl, { retry: Date.now() });
  }
  return baseUrl;
}

function getOriginalImageUrl(filename: string, taskId: string) {
  return buildImageUrl(taskId, filename, false);
}

function handleImageError(filename: string) {
  if (!failedThumbs.value.has(filename)) {
    console.warn(`缩略图加载失败，尝试加载原图: ${filename}`);
    failedThumbs.value.add(filename);
  }
}

// 格式化日期
const formattedDate = computed(() => {
  if (!props.record) return "";
  const d = new Date(props.record.updated_at);
  return `${d.getMonth() + 1}/${d.getDate()}`;
});
</script>

<style scoped>
/* 全屏模态框遮罩 */
.modal-fullscreen {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* 模态框主体 */
.modal-body {
  background: var(--bg-card);
  width: 100%;
  max-width: 1000px;
  height: 90vh;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部区域 */
.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
  gap: 20px;
}

/* 标题区域 */
.title-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 4px;
}

.modal-title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-main);
  word-break: break-word;
  transition: max-height 0.3s ease;
}

.modal-title.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title-expand-btn {
  flex-shrink: 0;
  padding: 2px 8px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  color: var(--text-sub);
  background: var(--bg-elevated);
  transition: all 0.2s;
  margin-top: 2px;
}

.title-expand-btn:hover {
  background: var(--primary, #ff2442);
  color: white;
}

/* 元信息 */
.modal-meta {
  font-size: 12px;
  color: var(--text-sub);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

/* 查看大纲按钮 */
.view-outline-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-main);
  transition: all 0.2s;
}

.view-outline-btn:hover {
  background: var(--primary, #ff2442);
  color: white;
  border-color: var(--primary, #ff2442);
}

/* 头部操作区 */
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.download-btn {
  padding: 8px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.close-icon {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-sub);
  padding: 0;
  line-height: 1;
}

.close-icon:hover {
  color: var(--text-main);
}

/* 图片网格 */
.modal-gallery-grid {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

/* 单个图片项 */
.modal-img-item {
  display: flex;
  flex-direction: column;
}

/* 图片预览容器 */
.modal-img-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  border-radius: 8px;
  contain: layout style paint;
}

.modal-img-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 悬浮遮罩 */
.modal-img-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s ease-out;
  pointer-events: none;
  will-change: opacity;
}

.modal-img-preview:hover .modal-img-overlay {
  opacity: 1;
}

/* 重绘中状态 */
.modal-img-preview.regenerating .modal-img-overlay {
  opacity: 1;
  pointer-events: auto;
}

.modal-img-preview.regenerating .regenerate-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 遮罩层按钮 */
.modal-overlay-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  cursor: pointer;
  pointer-events: auto;
  font-size: 13px;
  font-weight: 500;
  color: white;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  will-change: transform;
}

.modal-overlay-btn:hover {
  background: var(--primary, #ff2442);
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.4);
}

.modal-overlay-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  background: rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.1);
}

/* 占位符 */
.placeholder {
  width: 100%;
  aspect-ratio: 3/4;
  background: var(--bg-elevated);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-placeholder);
  font-size: 14px;
}

/* 图片底部信息 */
.img-footer {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-sub);
}

.download-link {
  cursor: pointer;
  color: var(--primary, #ff2442);
  transition: opacity 0.2s;
}

.download-link:hover {
  opacity: 0.7;
}

/* 状态徽章与发布链接 */
.published-meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 500;
  color: #059669;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.28);
}

.pending-meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 500;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.28);
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.post-link-btn {
  color: #059669 !important;
  border-color: rgba(16, 185, 129, 0.3) !important;
  text-decoration: none;
}

.post-link-btn:hover {
  background: rgba(16, 185, 129, 0.1) !important;
  border-color: #10b981 !important;
}

.publish-direct-btn {
  background: linear-gradient(135deg, #ff2442 0%, #ff5277 100%);
  color: #ffffff;
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.35);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.publish-direct-btn:hover {
  background: linear-gradient(135deg, #e61e3b 0%, #ff3b65 100%);
  box-shadow: 0 6px 16px rgba(255, 36, 66, 0.5);
  transform: translateY(-1px);
}

/* 响应式 */
@media (max-width: 768px) {
  .modal-fullscreen {
    padding: 20px;
  }

  .modal-gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
    padding: 12px;
  }
}
</style>
