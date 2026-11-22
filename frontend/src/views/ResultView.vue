<template>
  <div class="container result-page-container">
    <!-- 创作流程指示器 -->
    <CreationStepper current-step="result" />

    <div class="page-header">
      <div>
        <h1 class="page-title">{{ isGenerating ? "正在生成" : "创作完成" }}</h1>
        <p class="page-subtitle">
          <span v-if="isGenerating">
            图片生成中：{{ store.progress.current }} /
            {{ store.progress.total }}，文案并行生成中
          </span>
          <span v-else-if="failedCount > 0">
            已完成 {{ doneCount }} 张，失败 {{ failedCount }} 张，可单张重试
          </span>
          <span v-else>
            恭喜，你的小红书图文已全部生成完成，共 {{ store.images.length }} 张
          </span>
        </p>
      </div>
      <div class="header-actions" style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <n-popconfirm
          v-if="isGenerating"
          positive-text="放弃并重新开始"
          negative-text="继续生成"
          @positive-click="handleStartOver"
        >
          <template #trigger>
            <button class="btn btn-secondary">再来一篇</button>
          </template>
          当前图文正在后台并发生成中，重新开始将中断当前进度，确定放弃吗？
        </n-popconfirm>
        <button
          v-else
          class="btn btn-secondary"
          @click="handleStartOver"
        >
          再来一篇
        </button>
        <button
          v-if="failedCount > 0 && !isGenerating"
          class="btn btn-secondary"
          @click="retryAllFailed"
          :disabled="isRetryingAll"
        >
          <span
            v-if="isRetryingAll"
            class="spinner-sm"
            style="margin-right: 6px"
          ></span>
          <svg
            v-else
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          {{ isRetryingAll ? "重试中..." : `重试全部失败页 (${failedCount})` }}
        </button>

        <n-tooltip trigger="hover">
          <template #trigger>
            <button
              class="btn btn-secondary"
              @click="downloadAll"
              :disabled="isGenerating || doneCount === 0"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              一键下载
            </button>
          </template>
          {{ isGenerating ? "图片后台并发生成中，完成后即可一键下载" : "打包下载所有卡片与文案" }}
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <button
              class="btn btn-primary"
              @click="goToPublish"
              :disabled="!canPublish"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M22 2L11 13"></path>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
              <span v-if="isGenerating">渲染中 ({{ store.progress.current }}/{{ store.progress.total }})...</span>
              <span v-else>发布到小红书</span>
            </button>
          </template>
          {{
            isGenerating
              ? "后台正在并发渲染中，请等待渲染完成"
              : failedCount > 0
                ? "存在失败图片，请重试失败页后再发布"
                : "全套图文已就绪，一键前往小红书发布中心"
          }}
        </n-tooltip>
      </div>
    </div>

    <div
      class="card"
      style="padding: 20px 32px"
      v-if="store.progress.total > 0"
    >
      <div class="progress-row">
        <span class="progress-label">图片生成进度</span>
        <span class="progress-value" :class="{ done: progressPercent >= 100 }">
          {{ Math.round(progressPercent) }}%
        </span>
      </div>
      <div class="progress-track">
        <div
          class="progress-bar"
          :class="{ done: progressPercent >= 100 }"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
      <div v-if="errorText" style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px; flex-wrap: wrap; gap: 8px;">
        <p class="error-text" style="margin: 0;">
          {{ errorText }}
        </p>
        <button
          v-if="store.imageJobId && !pollingActive"
          class="btn btn-secondary"
          style="padding: 4px 12px; font-size: 13px"
          @click="resumePolling"
        >
          继续监听进度
        </button>
      </div>
    </div>

    <div class="card" style="padding: 32px">
      <div class="grid-cols-4">
        <div
          v-for="image in store.images"
          :key="image.index"
          class="image-card group"
        >
          <div
            v-if="image.url"
            class="result-image-wrap"
            @click="openPreview(image.index)"
          >
            <img
              :src="image.url"
              :alt="`第 ${image.index + 1} 页`"
              class="result-image"
            />
            <div
              v-if="regeneratingIndex === image.index"
              class="result-image-overlay regenerating-overlay"
              @click.stop
            >
              <div class="spinner"></div>
              <span class="overlay-text">重绘中...</span>
            </div>
            <div v-else class="result-image-overlay hover-overlay">
              <div class="glass-zoom-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  <line x1="11" y1="8" x2="11" y2="14"></line>
                  <line x1="8" y1="11" x2="14" y2="11"></line>
                </svg>
              </div>
            </div>
            <button
              v-if="regeneratingIndex !== image.index"
              class="overlay-regenerate-btn floating-regenerate-btn always-visible"
              @click.stop="handleRegenerate(image)"
              :disabled="regeneratingIndex === image.index || isGenerating"
              :title="isGenerating ? '正在并发渲染全组中，请稍候' : '重绘此页'"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M23 4v6h-6"></path>
                <path d="M1 20v-6h6"></path>
                <path
                  d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
                ></path>
              </svg>
              <span>{{
                regeneratingIndex === image.index ? "重绘中..." : "重绘此页"
              }}</span>
            </button>
          </div>

          <div v-else class="result-image-wrap placeholder-wrap">
            <div
              v-if="
                image.status === 'generating' || image.status === 'retrying'
              "
              class="placeholder-state"
            >
              <div class="spinner"></div>
              <span>{{
                image.status === "retrying" ? "重试中..." : "生成中..."
              }}</span>
            </div>
            <div
              v-else-if="image.status === 'error'"
              class="placeholder-state error-state"
              style="display: flex; flex-direction: column; align-items: center; gap: 8px;"
            >
              <span style="font-size: 13px; color: var(--color-error)">生成失败</span>
              <button
                class="btn btn-secondary"
                style="padding: 4px 12px; font-size: 12px; border-radius: 6px"
                @click.stop="handleRegenerate(image)"
                :disabled="regeneratingIndex === image.index || isGenerating"
              >
                {{ regeneratingIndex === image.index ? "重试中..." : "重试此页" }}
              </button>
            </div>
            <div v-else class="placeholder-state">
              <span>等待中</span>
            </div>
          </div>

          <div class="result-image-footer">
            <span class="footer-page-info">
              <i>Page {{ image.index + 1 }}</i>
            </span>
            <button
              class="pill-download-btn"
              @click="downloadOne(image)"
              :disabled="!image.url"
            >
              下载
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 全屏沉浸式图片预览画廊 (Lightbox) -->
    <div
      v-if="previewVisible"
      class="preview-modal"
      @click="closePreview"
      role="dialog"
      aria-modal="true"
      aria-label="图片全屏画廊预览"
    >
      <div class="preview-header-bar" @click.stop>
        <div class="preview-counter">
          Page {{ (currentPreviewImage?.index ?? previewIndex) + 1 }} / {{ store.images.length }}
        </div>
        <div class="preview-actions">
          <button
            class="preview-action-btn"
            type="button"
            @click.stop="downloadCurrentPreview"
            title="下载此页原图"
          >
            <svg
              width="15"
              height="15"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>下载</span>
          </button>
          <button
            class="preview-action-btn preview-close-btn"
            type="button"
            @click.stop="closePreview"
            title="关闭 (ESC)"
            aria-label="关闭预览"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 上一张 -->
      <button
        v-if="hasPrevPreview"
        class="preview-nav-btn prev-btn"
        type="button"
        @click.stop="previewPrev"
        title="上一张 (←)"
        aria-label="上一张图片"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <!-- 居中大图 -->
      <div class="preview-image-container" @click.stop>
        <img
          class="preview-image"
          :src="currentPreviewUrl"
          :alt="`第 ${(currentPreviewImage?.index ?? previewIndex) + 1} 页`"
        />
      </div>

      <!-- 下一张 -->
      <button
        v-if="hasNextPreview"
        class="preview-nav-btn next-btn"
        type="button"
        @click.stop="previewNext"
        title="下一张 (→)"
        aria-label="下一张图片"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>

    <ContentDisplay />
  </div>
</template>

<style scoped>
.header-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: var(--radius-md);
}

.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-label {
  font-size: 13px;
  color: var(--text-sub);
}

.progress-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--primary);
  font-variant-numeric: tabular-nums;
}

.progress-value.done {
  color: var(--color-success);
}

.progress-track {
  height: 8px;
  border-radius: 999px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(255, 36, 66, 0.4);
}

.progress-bar.done {
  background: var(--color-success);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

.error-text {
  margin-top: 10px;
  color: var(--color-error, #ff4d4f);
  font-size: 13px;
}

.image-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
  transition: all var(--transition-base);
}

.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: var(--border-hover);
}

.result-image-wrap {
  position: relative;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  cursor: pointer;
  line-height: 0;
  background: var(--bg-elevated);
}

.placeholder-wrap {
  cursor: default;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-sub);
  font-size: 12px;
}

.placeholder-state.error-state {
  color: var(--color-error, #ff4d4f);
}

.result-image {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  transition: transform 0.3s;
}

.result-image-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-main);
  font-weight: 600;
  transition: opacity 0.2s;
  pointer-events: none;
}

.regenerating-overlay {
  flex-direction: column;
  background: var(--bg-active);
  backdrop-filter: blur(2px);
  z-index: 10;
  pointer-events: auto;
}

.hover-overlay {
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.05) 0%,
    rgba(0, 0, 0, 0.4) 100%
  );
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-zoom-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transform: scale(0.8) translateY(10px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.image-card:hover .glass-zoom-icon {
  transform: scale(1) translateY(0);
}

.overlay-text {
  margin-top: 8px;
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
}

.overlay-regenerate-btn {
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  pointer-events: auto;
}

.overlay-regenerate-btn svg {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.overlay-regenerate-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.overlay-regenerate-btn:hover svg {
  transform: rotate(180deg);
}

.overlay-regenerate-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.floating-regenerate-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 12;
}

.result-image-footer {
  padding: 14px 16px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-page-info {
  font-size: 13px;
  color: var(--text-sub);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.footer-page-info i {
  font-style: normal;
  opacity: 0.8;
}

.pill-download-btn {
  border: none;
  background: var(--primary-light, rgba(255, 36, 66, 0.08));
  color: var(--primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 32px;
  padding: 0 18px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.pill-download-btn:hover {
  background: var(--primary);
  color: #fff;
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3);
  transform: translateY(-2px);
}

.pill-download-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.image-action-btn {
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 10px;
  border-radius: 8px;
  font-size: 12px;
  transition: all 0.18s ease;
}

.image-action-btn:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
}

.image-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.image-card:hover img {
  transform: scale(1.05);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.preview-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: fadeIn 0.2s ease-out;
}

.preview-header-bar {
  position: absolute;
  top: 20px;
  left: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 2010;
}

.preview-counter {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  padding: 6px 14px;
  border-radius: 99px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border-radius: 99px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preview-action-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.preview-close-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  justify-content: center;
  font-size: 15px;
}

.preview-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2010;
  transition: all var(--transition-fast);
}

.preview-nav-btn:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: translateY(-50%) scale(1.08);
}

.preview-nav-btn.prev-btn {
  left: 24px;
}

.preview-nav-btn.next-btn {
  right: 24px;
}

.preview-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90vw;
  max-height: 85vh;
}

.preview-image {
  max-width: min(1000px, 90vw);
  max-height: 85vh;
  object-fit: contain;
  border-radius: 12px;
  background: #111;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

@media (max-width: 768px) {
  .floating-regenerate-btn {
    top: 8px;
    right: 8px;
    height: 30px;
    padding: 0 10px;
    font-size: 11px;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useGeneratorStore } from "../stores/generator";
import {
  appendUrlParams,
  downloadHistoryZip,
  getImageJob,
  getImageUrl,
  getHistory,
  regenerateImage,
  updateHistory,
  withAccessToken,
} from "../api";
import ContentDisplay from "../components/result/ContentDisplay.vue";
import CreationStepper from "../components/home/CreationStepper.vue";
import { useMessage, NTooltip, NPopconfirm } from "naive-ui";

const router = useRouter();
const route = useRoute();
const store = useGeneratorStore();
const message = useMessage();

const regeneratingIndex = ref<number | null>(null);
const isRetryingAll = ref(false);
const errorText = ref("");
const pollingActive = ref(false);
const previewVisible = ref(false);
const previewIndex = ref(0);
let stopPolling = false;

const validImages = computed(() => {
  return store.images.filter((img) => Boolean(img.url));
});

const currentPreviewImage = computed(() => {
  return validImages.value[previewIndex.value] || null;
});

const currentPreviewUrl = computed(() => {
  if (!currentPreviewImage.value?.url) return "";
  const baseUrl = currentPreviewImage.value.url.split("?")[0];
  return appendUrlParams(withAccessToken(baseUrl), {
    thumbnail: false,
  });
});

const hasPrevPreview = computed(() => previewIndex.value > 0);
const hasNextPreview = computed(
  () => previewIndex.value < validImages.value.length - 1,
);

const resumePolling = async () => {
  stopPolling = false;
  await startPollingIfNeeded();
};

const doneCount = computed(
  () => store.images.filter((img) => img.status === "done" && !!img.url).length,
);
const failedCount = computed(
  () => store.images.filter((img) => img.status === "error").length,
);
const isGenerating = computed(
  () => store.progress.status === "generating" && !!store.imageJobId,
);
const progressPercent = computed(() => {
  if (store.progress.total <= 0) return 0;
  return (store.progress.current / store.progress.total) * 100;
});
const canPublish = computed(() => {
  if (isGenerating.value) return false;
  return (
    store.images.length > 0 &&
    store.images.every((img) => img.status === "done" && !!img.url)
  );
});

const openPreview = (pageIndex: number) => {
  const targetIdx = validImages.value.findIndex(
    (img) => img.index === pageIndex,
  );
  if (targetIdx >= 0) {
    previewIndex.value = targetIdx;
  } else {
    previewIndex.value = 0;
  }
  previewVisible.value = true;
};

const closePreview = () => {
  previewVisible.value = false;
};

const previewPrev = () => {
  if (hasPrevPreview.value) {
    previewIndex.value -= 1;
  }
};

const previewNext = () => {
  if (hasNextPreview.value) {
    previewIndex.value += 1;
  }
};

const downloadCurrentPreview = () => {
  if (currentPreviewImage.value) {
    downloadOne(currentPreviewImage.value);
  }
};

const onPreviewKeydown = (event: KeyboardEvent) => {
  if (!previewVisible.value) return;
  if (event.key === "Escape") {
    closePreview();
  } else if (event.key === "ArrowLeft") {
    previewPrev();
  } else if (event.key === "ArrowRight") {
    previewNext();
  }
};

const handleStartOver = () => {
  store.reset();
  router.push("/redbook");
};

const goToPublish = () => {
  if (!canPublish.value) {
    message.warning("图片仍在生成或存在失败，暂不可发布");
    return;
  }
  router.push("/redbook/publish");
};

const downloadOne = (image: any) => {
  if (!image.url) return;
  const link = document.createElement("a");
  const baseUrl = image.url.split("?")[0];
  link.href = appendUrlParams(withAccessToken(baseUrl), { thumbnail: false });
  link.download = `rednote_page_${image.index + 1}.png`;
  link.click();
};

function hasPersistableContent() {
  const hasTitles =
    Array.isArray(store.content.titles) &&
    store.content.titles.some((t) => String(t || "").trim());
  const hasCopywriting = Boolean(
    String(store.content.copywriting || "").trim(),
  );
  const hasTags =
    Array.isArray(store.content.tags) &&
    store.content.tags.some((t) => String(t || "").trim());
  return hasTitles || hasCopywriting || hasTags;
}

async function syncContentToHistory() {
  if (!store.recordId || !hasPersistableContent()) return;
  try {
    await updateHistory(store.recordId, {
      content: {
        titles: [...(store.content.titles || [])],
        copywriting: String(store.content.copywriting || ""),
        tags: [...(store.content.tags || [])],
      },
    });
  } catch (error) {
    console.error("下载前同步文案到历史记录失败:", error);
  }
}

const downloadAll = async () => {
  if (isGenerating.value) {
    message.warning("图片仍在生成中，请稍后再下载");
    return;
  }

  if (store.recordId) {
    await syncContentToHistory();

    const fallbackLink = document.createElement("a");
    fallbackLink.href = appendUrlParams(
      withAccessToken(`/api/history/${store.recordId}/download`),
      { _: Date.now() },
    );

    try {
      const contentPayload = hasPersistableContent()
        ? {
            titles: [...(store.content.titles || [])],
            copywriting: String(store.content.copywriting || ""),
            tags: [...(store.content.tags || [])],
          }
        : undefined;

      const { blob, filename } = await downloadHistoryZip(
        store.recordId,
        contentPayload,
      );
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("打包下载失败，回退到直链下载:", error);
      fallbackLink.click();
    }
    return;
  }

  store.images.forEach((image, index) => {
    if (!image.url) return;
    setTimeout(() => {
      const link = document.createElement("a");
      const baseUrl = image.url.split("?")[0];
      link.href = appendUrlParams(withAccessToken(baseUrl), {
        thumbnail: false,
      });
      link.download = `rednote_page_${image.index + 1}.png`;
      link.click();
    }, index * 300);
  });
};

async function syncImageStateToHistory(taskId: string) {
  if (!store.recordId) return;
  try {
    const generated = store.outline.pages.map((p) => {
      const img = store.images.find((i) => i.index === p.index);
      if (img && img.status === "done" && img.url) {
        return img.url.split("/").pop()?.split("?")[0] || "";
      }
      return "";
    });

    const completedCount = generated.filter((name) => name !== "").length;
    let status = "completed";
    if (failedCount.value > 0) {
      status = completedCount > 0 ? "partial" : "draft";
    }

    const firstPage = store.images.find((img) => img.index === 0);
    const thumbnail =
      firstPage && firstPage.status === "done" && firstPage.url
        ? firstPage.url.split("/").pop()?.split("?")[0]
        : generated.find((name) => name !== "") || null;

    await updateHistory(store.recordId, {
      images: {
        task_id: taskId,
        generated,
      },
      status,
      thumbnail: thumbnail || undefined,
    });
  } catch (e) {
    console.error("同步图片状态到历史记录失败:", e);
  }
}

const handleRegenerate = async (image: any) => {
  if (regeneratingIndex.value !== null || isGenerating.value) return;

  // 若缺失 taskId，自动分配一个以支持单页重绘落盘
  if (!store.taskId) {
    store.taskId = `task_${Date.now()}`;
  }

  regeneratingIndex.value = image.index;
  try {
    const pageContent = store.outline.pages.find(
      (p) => p.index === image.index,
    );
    if (!pageContent) {
      message.warning("无法找到对应页面内容");
      return;
    }

    const context = {
      fullOutline: store.outline.raw || "",
      userTopic: store.topic || "",
      userPrompt: store.imagePrompt.userPrompt || "",
      systemPrompt: store.imagePrompt.systemPrompt || "",
    };

    const result = await regenerateImage(
      store.taskId,
      pageContent,
      true,
      context,
    );
    if (result.success && result.image_url) {
      store.updateImage(image.index, result.image_url);
      message.success(`第 ${image.index + 1} 页重绘成功`);
      await syncImageStateToHistory(store.taskId);
    } else {
      message.error("重绘失败: " + (result.error || "未知错误"));
    }
  } catch (e: any) {
    message.error("重绘失败: " + e.message);
  } finally {
    regeneratingIndex.value = null;
  }
};

const retryAllFailed = async () => {
  if (isRetryingAll.value || isGenerating.value) return;
  const failedImgs = store.images.filter((img) => img.status === "error");
  if (failedImgs.length === 0) return;

  isRetryingAll.value = true;
  message.info(`开始重试 ${failedImgs.length} 张失败图片...`);
  try {
    for (const img of failedImgs) {
      await handleRegenerate(img);
    }
  } finally {
    isRetryingAll.value = false;
  }
};

function resolveRouteRecordId() {
  const queryId =
    typeof route.query.recordId === "string" ? route.query.recordId.trim() : "";
  if (queryId) return queryId;
  const paramId =
    typeof route.params.recordId === "string"
      ? route.params.recordId.trim()
      : "";
  return paramId;
}

async function hydrateFromHistoryRecord(recordId: string) {
  const res = await getHistory(recordId);
  if (!res.success || !res.record) {
    message.error("无法加载结果页：历史记录不存在或已被删除");
    router.push("/history");
    return;
  }

  const record = res.record;
  store.setTopic(record.title);
  store.setOutline(record.outline.raw, record.outline.pages);
  store.setRecordId(record.id);
  store.imageJobId = null;

  if (record.content) {
    store.setContent(
      record.content.titles || [],
      record.content.copywriting || "",
      record.content.tags || [],
    );
  } else {
    store.clearContent();
  }

  let taskId = record.images?.task_id || null;
  const generated = Array.isArray(record.images?.generated)
    ? record.images.generated
    : [];

  // 兜底推导任务ID：若历史记录中无显式 task_id 但有缩略图路径
  if (!taskId && record.thumbnail && String(record.thumbnail).includes("/")) {
    const parts = String(record.thumbnail).split("/");
    taskId = parts[parts.length - 2] || null;
  }
  store.taskId = taskId;

  const rawPages = Array.isArray(record.outline?.pages) ? record.outline.pages : [];
  const maxPages = Math.max(rawPages.length, generated.length);
  const totalPages = maxPages;
  const pageList = rawPages.length >= maxPages
    ? rawPages
    : Array.from({ length: maxPages }, (_, i) => rawPages[i] || { index: i, type: "content", content: "" });

  // 为所有页面恢复卡片状态，绝不置空
  store.images = pageList.map((_, idx) => {
    const filename = generated[idx];
    if (taskId && filename) {
      return {
        index: idx,
        url: getImageUrl(taskId, filename),
        status: "done" as const,
        retryable: false,
      };
    }
    return {
      index: idx,
      url: "",
      status: "error" as const,
      retryable: true,
      error: "图片未生成或已失效",
    };
  });

  const completedCount = store.images.filter((img) => img.status === "done" && !!img.url).length;
  store.progress.current = completedCount;
  store.progress.total = totalPages;
  store.progress.status = completedCount >= totalPages && totalPages > 0 ? "done" : "error";
  store.stage = "result";
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pollImageJobUntilFinished(jobId: string): Promise<{
  taskId: string;
  status: "success" | "failed" | "cancelled";
}> {
  const seenSuccess = new Set<number>();
  const seenFailed = new Set<number>();
  let finalTaskId = store.taskId || `task_${Date.now()}_job`;
  let consecutiveErrors = 0;

  while (!stopPolling) {
    const result = await getImageJob(jobId);
    if (!result.success || !result.data) {
      consecutiveErrors += 1;
      // 容错提升至 30 次（约 1-2 分钟重试缓冲），防止生图高负荷时瞬发断联中断任务
      if (consecutiveErrors >= 30) {
        throw new Error(result.error || "轮询图片任务失败：网络持续无响应");
      }
      const backoff = Math.min(3000, 1200 + consecutiveErrors * 200);
      errorText.value = `同步进度中，正在自动重连 (${consecutiveErrors}/30)...`;
      await sleep(backoff);
      continue;
    }

    if (consecutiveErrors > 0) {
      errorText.value = "";
    }
    consecutiveErrors = 0;
    const job = result.data;
    const items = Array.isArray(job.items) ? job.items : [];
    for (const item of items) {
      const index = Number(item.page_index);
      if (!Number.isFinite(index) || index < 0) continue;

      if (
        item.status === "success" &&
        !seenSuccess.has(index) &&
        item.image_url
      ) {
        seenSuccess.add(index);
        seenFailed.delete(index);
        store.updateProgress(index, "done", item.image_url);
        // ★★★ 增量同步：每生成完成一张，即刻落库保存，永不丢失！★★★
        void syncImageStateToHistory(finalTaskId);
      } else if (
        item.status === "failed" &&
        !seenFailed.has(index) &&
        !seenSuccess.has(index)
      ) {
        seenFailed.add(index);
        store.updateProgress(
          index,
          "error",
          undefined,
          item.error || "生成失败",
        );
        void syncImageStateToHistory(finalTaskId);
      }
    }

    const candidateTaskId =
      String(job.task_id || "") || String((job.result as any)?.task_id || "");
    if (candidateTaskId) {
      finalTaskId = candidateTaskId;
    }

    if (
      job.status === "success" ||
      job.status === "failed" ||
      job.status === "cancelled"
    ) {
      store.finishGeneration(finalTaskId);
      return {
        taskId: finalTaskId,
        status: job.status,
      };
    }

    await sleep(1000);
  }

  return {
    taskId: finalTaskId,
    status: "cancelled",
  };
}

async function startPollingIfNeeded() {
  if (!store.imageJobId || pollingActive.value) return;
  pollingActive.value = true;
  errorText.value = "";

  try {
    const finished = await pollImageJobUntilFinished(store.imageJobId);
    if (finished.status === "cancelled") {
      // 用户离开页面时中断局部轮询，不把任务标记为 error，以便切回时恢复
      return;
    }
    await syncImageStateToHistory(finished.taskId);
  } catch (err: any) {
    errorText.value = "图片轮询受阻: " + (err?.message || String(err));
    // 保持进度状态为可恢复
  } finally {
    pollingActive.value = false;
  }
}

onMounted(async () => {
  stopPolling = false;
  const recordId = resolveRouteRecordId();
  if (recordId) {
    await hydrateFromHistoryRecord(recordId);
    return;
  }

  if (store.outline.pages.length === 0) {
    router.push("/redbook");
    return;
  }

  // 页面加载或从其他菜单切回时，若任务仍在生成中，自动恢复轮询
  if (store.imageJobId && (store.progress.status === "generating" || store.progress.status === "idle")) {
    await startPollingIfNeeded();
  }
});

onMounted(() => {
  window.addEventListener("keydown", onPreviewKeydown);
});

onUnmounted(() => {
  stopPolling = true;
  window.removeEventListener("keydown", onPreviewKeydown);
  closePreview();
});
</script>
