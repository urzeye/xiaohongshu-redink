<template>
  <div class="container launch-page">
    <CreationStepper current-step="result" />

    <div class="card launch-card">
      <div class="launch-icon-pulse">
        <svg
          width="36"
          height="36"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path>
          <line x1="16" y1="8" x2="2" y2="22"></line>
          <line x1="17.5" y1="15" x2="9" y2="15"></line>
        </svg>
      </div>

      <h1 class="page-title">准备并行渲染</h1>
      <p class="page-subtitle" v-if="!errorText">
        正在建立多图并发任务通道，即将进入实时渲染面板并同步生成爆款文案...
      </p>

      <div v-if="!errorText" class="launch-loading">
        <div class="spinner"></div>
        <span class="loading-hint">正在调度模型与图像提供商...</span>
      </div>

      <div v-else class="launch-error">
        <p>{{ errorText }}</p>
        <div class="actions">
          <button class="btn btn-primary" @click="launch" :disabled="launching">
            立即重试
          </button>
          <button class="btn btn-secondary" @click="router.push('/redbook/outline')">
            返回大纲编辑
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useGeneratorStore } from "../stores/generator";
import { createHistory, createImageJob, updateHistory } from "../api";
import CreationStepper from "../components/home/CreationStepper.vue";

const router = useRouter();
const store = useGeneratorStore();

const launching = ref(false);
const errorText = ref("");

async function ensureHistoryRecord() {
  if (store.recordId) {
    await updateHistory(store.recordId, { status: "generating" });
    return;
  }

  const result = await createHistory(store.topic, {
    raw: store.outline.raw,
    pages: store.outline.pages,
  });
  if (result.success && result.record_id) {
    store.setRecordId(result.record_id);
  }
}

async function launch() {
  if (launching.value) return;
  launching.value = true;
  errorText.value = "";

  try {
    if (!store.outline.pages || store.outline.pages.length === 0) {
      router.push("/redbook");
      return;
    }

    await ensureHistoryRecord();

    store.startGeneration();
    const pagesToGenerate = store.outline.pages.filter((page) => {
      const existing = store.images.find((img) => img.index === page.index);
      return !existing || existing.status !== "done" || !existing.url;
    });

    if (pagesToGenerate.length === 0) {
      if (!store.taskId) {
        store.taskId = `task_${Date.now()}_existing`;
      }
      store.imageJobId = null;
      store.finishGeneration(store.taskId);
      router.replace("/redbook/result");
      return;
    }

    const createResult = await createImageJob(
      pagesToGenerate,
      store.taskId,
      store.outline.raw,
      store.userImages.length > 0 ? store.userImages : undefined,
      store.topic,
      {
        userPrompt: store.imagePrompt.userPrompt || "",
        systemPrompt: store.imagePrompt.systemPrompt || "",
      },
      store.recordId,
    );

    if (!createResult.success || !createResult.job_id) {
      throw new Error(createResult.error || "创建图片任务失败");
    }

    store.imageJobId = createResult.job_id;
    router.replace("/redbook/result");
  } catch (err: any) {
    store.progress.status = "error";
    errorText.value = "生成任务创建失败: " + (err?.message || String(err));
  } finally {
    launching.value = false;
  }
}

onMounted(() => {
  launch();
});
</script>

<style scoped>
.launch-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 65vh;
  max-width: 800px;
}

.launch-card {
  width: min(640px, 100%);
  text-align: center;
  padding: 48px 36px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}

.launch-icon-pulse {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(255, 36, 66, 0.1);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 0 24px rgba(255, 36, 66, 0.2);
  animation: pulseGlow 2s infinite ease-in-out;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 12px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-sub);
  line-height: 1.6;
  max-width: 480px;
  margin: 0 auto 28px;
}

.launch-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.launch-error {
  margin-top: 20px;
  color: var(--color-error);
  font-size: 14px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 16px;
  border-radius: var(--radius-md);
}

.actions {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

@keyframes pulseGlow {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(255, 36, 66, 0.2);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 32px rgba(255, 36, 66, 0.4);
  }
}
</style>
