<template>
  <div class="container">
    <!-- Header Area -->
    <div class="page-header">
      <div>
        <h1 class="page-title">我的创作</h1>
      </div>
      <div style="display: flex; gap: 10px">
        <button
          class="btn btn-secondary"
          @click="handleScanAll"
          :disabled="isScanning"
        >
          <svg
            v-if="!isScanning"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            style="margin-right: 6px"
          >
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          <div
            v-else
            class="spinner-small"
            style="margin-right: 6px"
          ></div>
          {{ isScanning ? "同步中..." : "同步历史" }}
        </button>
        <button
          class="btn btn-primary"
          @click="router.push('/redbook')"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            style="margin-right: 6px"
          >
            <line
              x1="12"
              y1="5"
              x2="12"
              y2="19"
            ></line>
            <line
              x1="5"
              y1="12"
              x2="19"
              y2="12"
            ></line>
          </svg>
          新建图文
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <StatsOverview
      v-if="stats"
      :stats="stats"
      :active-tab="currentTab"
      @select-tab="switchTab"
    />

    <!-- Toolbar: Tabs & Search & Sort -->
    <div
      class="toolbar-wrapper card"
      style="padding: 16px 24px; margin-bottom: 24px"
    >
      <div
        class="tabs-container"
        style="border-bottom: none"
      >
        <div
          class="tab-item"
          :class="{ active: currentTab === 'all' }"
          @click="switchTab('all')"
        >
          全部
        </div>
        <div
          class="tab-item"
          :class="{ active: currentTab === 'pending' }"
          @click="switchTab('pending')"
        >
          待发布
        </div>
        <div
          class="tab-item"
          :class="{ active: currentTab === 'published' }"
          @click="switchTab('published')"
        >
          已发布
        </div>
        <div
          class="tab-item"
          :class="{ active: currentTab === 'draft' }"
          @click="switchTab('draft')"
        >
          草稿箱
        </div>
      </div>

      <div class="toolbar-right">
        <!-- 排序选择器 -->
        <div class="sort-selector-group">
          <span class="sort-prefix">
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
              <line x1="21" y1="6" x2="3" y2="6"></line>
              <line x1="15" y1="12" x2="3" y2="12"></line>
              <line x1="9" y1="18" x2="3" y2="18"></line>
            </svg>
            排序
          </span>
          <n-select
            v-model:value="sortBy"
            :options="sortOptions"
            size="small"
            class="history-sort-select"
            @update:value="handleSortChange"
          />
        </div>

        <div class="search-mini">
          <svg
            class="icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle
              cx="11"
              cy="11"
              r="8"
            ></circle>
            <line
              x1="21"
              y1="21"
              x2="16.65"
              y2="16.65"
            ></line>
          </svg>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索标题..."
            @keyup.enter="handleSearch"
            @input="handleSearchInput"
          />
        </div>
      </div>
    </div>

    <!-- Content Area -->
    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="spinner"></div>
    </div>

    <div
      v-else-if="records.length === 0"
      class="empty-state-large"
    >
      <div class="empty-img">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
          ></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line
            x1="12"
            y1="22.08"
            x2="12"
            y2="12"
          ></line>
        </svg>
      </div>
      <h3>暂无相关记录</h3>
      <p class="empty-tips">去创建一个新的作品吧</p>
    </div>

    <div
      v-else
      class="gallery-grid"
    >
      <GalleryCard
        v-for="record in records"
        :key="record.id"
        :record="record as any"
        @preview="viewImages"
        @edit="loadRecord"
        @result="openResultPage"
        @publish="openPublishPage"
        @delete="confirmDelete"
      />
    </div>

    <!-- Pagination -->
    <div
      v-if="totalPages > 1"
      class="pagination-wrapper"
    >
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        Previous
      </button>
      <span class="page-indicator">{{ currentPage }} / {{ totalPages }}</span>
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        Next
      </button>
    </div>

    <!-- Image Viewer Modal -->
    <ImageGalleryModal
      v-if="viewingRecord"
      :visible="!!viewingRecord"
      :record="viewingRecord"
      :regeneratingImages="regeneratingImages"
      @close="closeGallery"
      @showOutline="showOutlineModal = true"
      @showContent="showContentModal = true"
      @regenerate="regenerateHistoryImage"
      @downloadAll="downloadAllImages"
      @download="downloadImage"
      @publish="openPublishPage"
    />

    <!-- 大纲查看模态框 -->
    <OutlineModal
      v-if="showOutlineModal && viewingRecord"
      :visible="showOutlineModal"
      :pages="viewingRecord.outline.pages"
      @close="showOutlineModal = false"
    />

    <!-- 文案查看模态框 -->
    <div
      v-if="showContentModal && viewingRecord"
      class="content-modal-overlay"
      @click="showContentModal = false"
    >
      <div
        class="content-modal-card"
        @click.stop
      >
        <div class="content-modal-header">
          <h3>生成的标题与文案</h3>
          <button
            class="content-modal-close"
            @click="showContentModal = false"
          >
            ×
          </button>
        </div>

        <div class="content-modal-body">
          <div
            v-if="
              !viewingRecord.content ||
              ((!viewingRecord.content.titles ||
                viewingRecord.content.titles.length === 0) &&
                !viewingRecord.content.copywriting &&
                (!viewingRecord.content.tags ||
                  viewingRecord.content.tags.length === 0))
            "
            class="content-empty-tip"
          >
            暂无生成内容，请先在结果页生成标题、文案和标签。
          </div>

          <template v-else>
            <div class="content-copy-actions">
              <button
                class="btn btn-small content-copy-btn"
                @click="
                  copyHistoryContent(
                    getHistoryFullContentText(viewingRecord),
                    '全文',
                  )
                "
              >
                复制全文
              </button>
              <button
                v-if="viewingRecord.content.titles?.length"
                class="btn btn-small content-copy-btn"
                @click="
                  copyHistoryContent(
                    getHistoryTitlesText(viewingRecord),
                    '标题',
                  )
                "
              >
                复制标题
              </button>
              <button
                v-if="viewingRecord.content.copywriting"
                class="btn btn-small content-copy-btn"
                @click="
                  copyHistoryContent(viewingRecord.content.copywriting, '正文')
                "
              >
                复制正文
              </button>
              <button
                v-if="viewingRecord.content.tags?.length"
                class="btn btn-small content-copy-btn"
                @click="
                  copyHistoryContent(getHistoryTagsText(viewingRecord), '标签')
                "
              >
                复制标签
              </button>
            </div>

            <section
              v-if="viewingRecord.content.titles?.length"
              class="content-section"
            >
              <div class="content-section-head">
                <h4>标题建议</h4>
              </div>
              <div class="content-title-list">
                <div
                  v-for="(title, idx) in viewingRecord.content.titles"
                  :key="`${viewingRecord.id}-title-${idx}`"
                  class="content-title-item"
                >
                  <span class="content-title-badge">{{
                    idx === 0 ? "推荐" : `备选${idx}`
                  }}</span>
                  <span>{{ title }}</span>
                </div>
              </div>
            </section>

            <section
              v-if="viewingRecord.content.copywriting"
              class="content-section"
            >
              <div class="content-section-head">
                <h4>正文文案</h4>
              </div>
              <div class="content-copywriting-box">
                {{ viewingRecord.content.copywriting }}
              </div>
            </section>

            <section
              v-if="viewingRecord.content.tags?.length"
              class="content-section"
            >
              <div class="content-section-head">
                <h4>话题标签</h4>
              </div>
              <div class="content-tag-list">
                <span
                  v-for="tag in viewingRecord.content.tags"
                  :key="`${viewingRecord.id}-tag-${tag}`"
                  class="content-tag"
                >
                  #{{ tag }}
                </span>
              </div>
            </section>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  appendUrlParams,
  getHistoryList,
  deleteHistory,
  getHistory,
  getImageUrl,
  type HistoryRecord,
  regenerateImage as apiRegenerateImage,
  updateHistory,
  scanAllTasks,
  withAccessToken,
  // 概念可视化 API
  getConceptHistoryList,
  deleteConceptHistory,
  type ConceptHistoryRecord,
} from "../api";
import { useGeneratorStore } from "../stores/generator";

import StatsOverview from "../components/history/StatsOverview.vue";
import GalleryCard from "../components/history/GalleryCard.vue";
import ImageGalleryModal from "../components/history/ImageGalleryModal.vue";
import OutlineModal from "../components/history/OutlineModal.vue";
import { useMessage, NSelect } from "naive-ui";

const router = useRouter();
const route = useRoute();
const store = useGeneratorStore();
const message = useMessage();

// 统一记录类型（整合小红书和概念可视化）
interface UnifiedRecord {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  status: "draft" | "in_progress" | "generating" | "completed" | "error";
  thumbnail: string | null | undefined;
  page_count: number;
  task_id: string | null;
  recordType: "xiaohongshu" | "concept";
  is_published?: boolean;
  published_accounts?: string[];
  last_published_at?: string;
  post_url?: string;
  publish_info?: any;
}

// 数据状态
const records = ref<UnifiedRecord[]>([]);
const allUnifiedRecords = ref<UnifiedRecord[]>([]);
const loading = ref(false);
const stats = ref<any>(null);
const currentTab = ref("all");
const searchKeyword = ref("");
const currentPage = ref(1);
const totalPages = ref(1);

// 排序状态与选项
const sortBy = ref<string>("created_desc");
const sortOptions = [
  { label: "最新创建", value: "created_desc" },
  { label: "最近更新", value: "updated_desc" },
  { label: "最早创建", value: "created_asc" },
  { label: "页数最多", value: "pages_desc" },
  { label: "页数最少", value: "pages_asc" },
  { label: "标题 (A-Z)", value: "title_asc" },
];

// 查看器状态
const viewingRecord = ref<any>(null);
const regeneratingImages = ref<Set<number>>(new Set());
const showOutlineModal = ref(false);
const showContentModal = ref(false);
const isScanning = ref(false);

/**
 * 将小红书记录转换为统一格式
 */
function convertXiaohongshuRecord(record: HistoryRecord): UnifiedRecord {
  return {
    id: record.id,
    title: record.title,
    created_at: record.created_at,
    updated_at: record.updated_at,
    status: record.status as UnifiedRecord["status"],
    thumbnail: record.thumbnail || undefined,
    page_count: record.page_count,
    task_id: record.task_id,
    recordType: "xiaohongshu",
    is_published: record.is_published,
    published_accounts: record.published_accounts,
    last_published_at: record.last_published_at,
    post_url: record.post_url,
    publish_info: record.publish_info,
  };
}

/**
 * 将概念可视化记录转换为统一格式
 */
function convertConceptRecord(record: ConceptHistoryRecord): UnifiedRecord {
  return {
    id: record.id,
    title: record.title,
    created_at: record.created_at,
    updated_at: record.updated_at,
    status: record.status as UnifiedRecord["status"],
    thumbnail: record.thumbnail || undefined,
    page_count: record.image_count || 0,
    task_id: record.task_id,
    recordType: "concept",
  };
}

function parseRecordTime(timeStr?: string): number {
  if (!timeStr) return 0;
  const t = new Date(timeStr).getTime();
  return Number.isNaN(t) ? 0 : t;
}

/**
 * 排序记录列表
 */
function sortRecordsList(list: UnifiedRecord[], sortKey: string): UnifiedRecord[] {
  return [...list].sort((a, b) => {
    const timeA_create = parseRecordTime(a.created_at || a.updated_at);
    const timeB_create = parseRecordTime(b.created_at || b.updated_at);
    const timeA_update = parseRecordTime(a.updated_at || a.created_at);
    const timeB_update = parseRecordTime(b.updated_at || b.created_at);

    if (sortKey === "created_desc") {
      if (timeB_create !== timeA_create) return timeB_create - timeA_create;
      return timeB_update - timeA_update;
    }
    if (sortKey === "created_asc") {
      if (timeA_create !== timeB_create) return timeA_create - timeB_create;
      return timeA_update - timeB_update;
    }
    if (sortKey === "updated_desc") {
      if (timeB_update !== timeA_update) return timeB_update - timeA_update;
      return timeB_create - timeA_create;
    }
    if (sortKey === "updated_asc") {
      if (timeA_update !== timeB_update) return timeA_update - timeB_update;
      return timeA_create - timeB_create;
    }
    if (sortKey === "pages_desc") {
      const pA = a.page_count || 0;
      const pB = b.page_count || 0;
      if (pB !== pA) return pB - pA;
      return timeB_create - timeA_create;
    }
    if (sortKey === "pages_asc") {
      const pA = a.page_count || 0;
      const pB = b.page_count || 0;
      if (pA !== pB) return pA - pB;
      return timeB_create - timeA_create;
    }
    if (sortKey === "title_asc") {
      const tA = (a.title || "").trim();
      const tB = (b.title || "").trim();
      const cmp = tA.localeCompare(tB, "zh-CN");
      if (cmp !== 0) return cmp;
      return timeB_create - timeA_create;
    }
    return timeB_create - timeA_create;
  });
}

function applyCurrentPageSlice() {
  const sorted = sortRecordsList(allUnifiedRecords.value, sortBy.value);
  const pageSize = 12;
  totalPages.value = Math.max(1, Math.ceil(sorted.length / pageSize));
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1;
  }
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  records.value = sorted.slice(start, end);
}

function handleSortChange(value: string) {
  sortBy.value = value;
  currentPage.value = 1;
  applyCurrentPageSlice();
}

/**
 * 加载历史记录列表（整合小红书和概念可视化）
 */
async function loadData() {
  loading.value = true;
  try {
    let xiaohongshuStatusFilter: string | undefined = undefined;
    let conceptStatusFilter: string | undefined = undefined;

    if (currentTab.value === "published") {
      xiaohongshuStatusFilter = "published";
      conceptStatusFilter = "__none__"; // 概念图暂无发布状态
    } else if (currentTab.value === "pending") {
      xiaohongshuStatusFilter = "pending";
      conceptStatusFilter = "completed";
    } else if (currentTab.value === "draft") {
      xiaohongshuStatusFilter = "draft";
      conceptStatusFilter = "draft";
    }

    // 并行请求两种历史记录
    const [xiaohongshuRes, conceptRes] = await Promise.all([
      getHistoryList(1, 100, xiaohongshuStatusFilter), // 获取更多以便合并排序
      conceptStatusFilter === "__none__"
        ? Promise.resolve({ success: true, data: { records: [] } })
        : getConceptHistoryList(1, 100, conceptStatusFilter),
    ]);

    // 合并记录
    const allRecords: UnifiedRecord[] = [];

    if (xiaohongshuRes.success && xiaohongshuRes.records) {
      allRecords.push(...xiaohongshuRes.records.map(convertXiaohongshuRecord));
    }

    if (conceptRes.success && (conceptRes as any).data?.records) {
      allRecords.push(...(conceptRes as any).data.records.map(convertConceptRecord));
    }

    const kw = searchKeyword.value.trim().toLowerCase();
    allUnifiedRecords.value = kw
      ? allRecords.filter((r) => r.title.toLowerCase().includes(kw))
      : allRecords;

    applyCurrentPageSlice();
  } catch (e) {
    console.error("加载历史记录失败:", e);
  } finally {
    loading.value = false;
  }
}

/**
 * 加载统计数据（合并小红书和概念可视化）
 */
async function loadStats() {
  try {
    // 并行获取两种记录用于统计
    const [xiaohongshuRes, conceptRes] = await Promise.all([
      getHistoryList(1, 100),
      getConceptHistoryList(1, 100),
    ]);

    let total = 0;
    let completed = 0;
    let published = 0;
    let pending = 0;
    let draft = 0;

    // 统计小红书记录
    if (xiaohongshuRes.success && xiaohongshuRes.records) {
      xiaohongshuRes.records.forEach((r) => {
        total++;
        if (r.is_published) {
          published++;
        } else if (r.status === "completed") {
          pending++;
        } else if (r.status === "draft") {
          draft++;
        }
        if (r.status === "completed") completed++;
      });
    }

    // 统计概念可视化记录
    if (conceptRes.success && conceptRes.data?.records) {
      conceptRes.data.records.forEach((r) => {
        total++;
        if (r.status === "completed") {
          completed++;
          pending++;
        } else if (r.status === "draft" || r.status === "in_progress") {
          draft++;
        }
      });
    }

    stats.value = {
      total,
      by_status: { completed, published, pending, draft },
    };
  } catch (e) {
    console.error("加载统计数据失败:", e);
  }
}

/**
 * 切换标签页
 */
function switchTab(tab: string) {
  currentTab.value = tab;
  currentPage.value = 1;
  loadData();
}

/**
 * 搜索历史记录
 */
function handleSearch() {
  currentPage.value = 1;
  loadData();
}

function handleSearchInput() {
  if (!searchKeyword.value.trim()) {
    handleSearch();
  }
}

/**
 * 根据记录 ID 查找统一记录
 */
function findUnifiedRecord(id: string): UnifiedRecord | undefined {
  return records.value.find((r) => r.id === id);
}

/**
 * 加载记录并跳转到编辑/查看页
 */
async function loadRecord(id: string) {
  const unifiedRecord = findUnifiedRecord(id);

  if (unifiedRecord?.recordType === "concept") {
    // 概念可视化记录：跳转到概念历史详情页
    router.push(`/concept/history?view=${id}`);
    return;
  }

  // 小红书记录：原有逻辑
  const res = await getHistory(id);
  if (res.success && res.record) {
    store.setTopic(res.record.title);
    store.setOutline(res.record.outline.raw, res.record.outline.pages);
    store.setRecordId(res.record.id);
    if (res.record.content) {
      store.setContent(
        res.record.content.titles || [],
        res.record.content.copywriting || "",
        res.record.content.tags || [],
      );
    } else {
      store.clearContent();
    }
    if (res.record.images.generated.length > 0) {
      store.taskId = res.record.images.task_id;
      store.images = res.record.outline.pages.map((_page, idx) => {
        const filename = res.record!.images.generated[idx];
        return {
          index: idx,
          url: filename ? getImageUrl(res.record!.images.task_id!, filename) : "",
          status: filename ? ("done" as const) : ("error" as const),
          retryable: !filename,
        };
      });
    }
    router.push("/redbook/outline");
  }
}

/**
 * 查看图片/预览
 */
async function viewImages(id: string) {
  const unifiedRecord = findUnifiedRecord(id);

  if (unifiedRecord?.recordType === "concept") {
    // 概念可视化记录：跳转到概念历史详情页
    router.push(`/concept/history?view=${id}`);
    return;
  }

  // 小红书记录：打开图片查看器
  const res = await getHistory(id);
  if (res.success) viewingRecord.value = res.record;
}

function openResultPage(id: string) {
  const unifiedRecord = findUnifiedRecord(id);

  if (unifiedRecord?.recordType === "concept") {
    router.push(`/concept/history?view=${id}`);
    return;
  }

  router.push({
    path: "/redbook/result",
    query: { recordId: id },
  });
}

function openPublishPage(id: string) {
  const unifiedRecord = findUnifiedRecord(id);

  if (unifiedRecord?.recordType === "concept") {
    message.info("概念图暂不支持直接发布到小红书");
    return;
  }

  closeGallery();
  router.push({
    path: "/redbook/publish",
    query: { recordId: id },
  });
}

/**
 * 关闭图片查看器
 */
function closeGallery() {
  viewingRecord.value = null;
  showOutlineModal.value = false;
  showContentModal.value = false;
}

async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      return true;
    } catch {
      return false;
    } finally {
      document.body.removeChild(textarea);
    }
  }
}

function getHistoryTitlesText(record: any): string {
  const titles: string[] = record?.content?.titles || [];
  return titles
    .map((title, index) => `${index === 0 ? "推荐" : `备选${index}`}：${title}`)
    .join("\n");
}

function getHistoryTagsText(record: any): string {
  const tags: string[] = record?.content?.tags || [];
  return tags.map((tag) => `#${tag}`).join(" ");
}

function getHistoryFullContentText(record: any): string {
  const lines: string[] = [];
  const titlesText = getHistoryTitlesText(record);
  const copywriting = (record?.content?.copywriting || "").trim();
  const tagsText = getHistoryTagsText(record);

  if (titlesText) {
    lines.push("【标题】");
    lines.push(titlesText);
  }
  if (copywriting) {
    if (lines.length > 0) lines.push("");
    lines.push("【正文】");
    lines.push(copywriting);
  }
  if (tagsText) {
    if (lines.length > 0) lines.push("");
    lines.push("【话题标签】");
    lines.push(tagsText);
  }
  return lines.join("\n");
}

async function copyHistoryContent(text: string, label: string) {
  if (!text || !text.trim()) {
    message.warning(`暂无${label}可复制`);
    return;
  }

  const success = await copyToClipboard(text);
  if (success) {
    message.success(`${label}已复制到剪贴板`);
  } else {
    message.error("复制失败，请手动复制");
  }
}

/**
 * 确认删除
 */
async function confirmDelete(record: any) {
  try {
    if (record.recordType === "concept") {
      // 删除概念可视化记录
      await deleteConceptHistory(record.id);
    } else {
      // 删除小红书记录
      await deleteHistory(record.id);
    }
    message.success("记录已成功删除");
    await loadData();
    await loadStats();
  } catch (err: any) {
    message.error("删除失败: " + (err?.message || String(err)));
  }
}

/**
 * 切换页码
 */
function changePage(p: number) {
  if (p < 1 || p > totalPages.value) return;
  currentPage.value = p;
  applyCurrentPageSlice();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * 重新生成历史记录中的图片
 */
async function regenerateHistoryImage(index: number) {
  if (!viewingRecord.value || !viewingRecord.value.images.task_id) {
    message.warning("无法重新生成：缺少任务信息");
    return;
  }

  const page = viewingRecord.value.outline.pages[index];
  if (!page) return;

  regeneratingImages.value.add(index);

  try {
    const context = {
      fullOutline: viewingRecord.value.outline.raw || "",
      userTopic: viewingRecord.value.title || "",
    };

    const result = await apiRegenerateImage(
      viewingRecord.value.images.task_id,
      page,
      true,
      context,
    );

    if (result.success && result.image_url) {
      const filename = result.image_url.split("/").pop();
      viewingRecord.value.images.generated[index] = filename;

      // 刷新图片
      const timestamp = Date.now();
      const imgElements = document.querySelectorAll(
        `img[src*="${viewingRecord.value.images.task_id}/${filename}"]`,
      );
      imgElements.forEach((img) => {
        const baseUrl = (img as HTMLImageElement).src.split("?")[0];
        (img as HTMLImageElement).src = appendUrlParams(
          withAccessToken(baseUrl),
          { t: timestamp },
        );
      });

      await updateHistory(viewingRecord.value.id, {
        images: {
          task_id: viewingRecord.value.images.task_id,
          generated: viewingRecord.value.images.generated,
        },
      });

      regeneratingImages.value.delete(index);
    } else {
      regeneratingImages.value.delete(index);
      message.error("重新生成失败: " + (result.error || "未知错误"));
    }
  } catch (e) {
    regeneratingImages.value.delete(index);
    message.error("重新生成失败: " + String(e));
  }
}

/**
 * 下载单张图片
 */
function downloadImage(filename: string, index: number) {
  if (!viewingRecord.value) return;
  const link = document.createElement("a");
  link.href = getImageUrl(viewingRecord.value.images.task_id, filename, false);
  link.download = `page_${index + 1}.png`;
  link.click();
}

/**
 * 打包下载所有图片
 */
function downloadAllImages() {
  if (!viewingRecord.value) return;
  const link = document.createElement("a");
  link.href = withAccessToken(`/api/history/${viewingRecord.value.id}/download`);
  link.click();
}

/**
 * 扫描所有任务并同步
 */
async function handleScanAll() {
  isScanning.value = true;
  try {
    const result = await scanAllTasks();
    if (result.success) {
      let msgText = `扫描完成！\n`;
      msgText += `- 总任务数: ${result.total_tasks || 0}\n`;
      msgText += `- 同步成功: ${result.synced || 0}\n`;
      msgText += `- 同步失败: ${result.failed || 0}\n`;

      if (result.orphan_tasks && result.orphan_tasks.length > 0) {
        msgText += `- 孤立任务（无记录）: ${result.orphan_tasks.length} 个\n`;
      }

      message.success(msgText);
      await loadData();
      await loadStats();
    } else {
      message.error("扫描失败: " + (result.error || "未知错误"));
    }
  } catch (e) {
    console.error("扫描失败:", e);
    message.error("扫描失败: " + String(e));
  } finally {
    isScanning.value = false;
  }
}

onMounted(async () => {
  await loadData();
  await loadStats();

  // 检查路由参数，如果有 ID 则自动打开图片查看器
  if (route.params.id) {
    await viewImages(route.params.id as string);
  }

  // 自动执行一次扫描（静默，不显示结果）
  try {
    const result = await scanAllTasks();
    if (result.success && (result.synced || 0) > 0) {
      await loadData();
      await loadStats();
    }
  } catch (e) {
    console.error("自动扫描失败:", e);
  }
});
</script>

<style scoped>
/* Small Spinner */
.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid var(--primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Toolbar */
.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0;
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.sort-selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-prefix {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--text-sub);
  white-space: nowrap;
}

.history-sort-select {
  width: 135px;
}

.search-mini {
  position: relative;
  width: 240px;
}

.search-mini input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border-radius: 100px;
  border: 1px solid var(--border-color);
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-main);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.search-mini input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px var(--primary-light);
}

.search-mini .icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-placeholder);
}

/* Gallery Grid */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-main);
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Empty State */
.empty-state-large {
  text-align: center;
  padding: 80px 0;
  color: var(--text-sub);
}

.empty-img {
  font-size: 64px;
  opacity: 0.5;
}

.empty-state-large .empty-tips {
  margin-top: 10px;
  color: var(--text-placeholder);
}

/* 历史文案弹窗 */
.content-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.content-modal-card {
  width: 100%;
  max-width: 720px;
  max-height: 86vh;
  background: var(--bg-card);
  color: var(--text-main);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.content-modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.content-modal-close {
  background: transparent;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: var(--text-sub);
}

.content-modal-body {
  padding: 18px 20px 20px;
  overflow-y: auto;
}

.content-empty-tip {
  text-align: center;
  color: var(--text-sub);
  padding: 28px 12px;
}

.content-section + .content-section {
  margin-top: 18px;
}

.content-copy-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.content-copy-btn {
  padding: 6px 12px;
}

.content-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.content-section h4 {
  margin: 0;
  color: var(--text-main);
  font-size: 15px;
}

.content-title-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.content-title-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

.content-title-badge {
  flex-shrink: 0;
  background: var(--bg-input);
  color: var(--text-sub);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
}

.content-copywriting-box {
  white-space: pre-wrap;
  line-height: 1.7;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  color: var(--text-main);
  font-size: 14px;
}

.content-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.content-tag {
  font-size: 13px;
  color: var(--primary);
  background: var(--primary-light);
  border-radius: 999px;
  padding: 4px 10px;
}
</style>
