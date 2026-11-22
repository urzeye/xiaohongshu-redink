<template>
  <nav class="creation-stepper" aria-label="创作流程进度">
    <div class="stepper-track">
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        class="stepper-item"
        :class="{
          active: normalizedStep === step.key,
          completed: isStepCompleted(step.key),
          clickable: isStepClickable(step.key),
        }"
        @click="handleStepClick(step.key)"
      >
        <div class="step-indicator">
          <span v-if="isStepCompleted(step.key)" class="step-check">✓</span>
          <span
            v-else-if="step.key === 'result' && isRenderingImages"
            class="step-spinner"
            title="图文并发渲染中"
          ></span>
          <span v-else class="step-num">{{ idx + 1 }}</span>
        </div>
        <div class="step-meta">
          <span class="step-title">{{ step.title }}</span>
          <span class="step-sub">{{ step.sub }}</span>
        </div>
        <div v-if="idx < steps.length - 1" class="step-divider"></div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useGeneratorStore } from "../../stores/generator";

const props = defineProps<{
  currentStep: "topic" | "outline" | "result" | "publish" | number | string;
}>();

const router = useRouter();
const store = useGeneratorStore();

const steps = [
  { key: "topic", title: "灵感选题", sub: "输入主题与参考", path: "/redbook" },
  { key: "outline", title: "编辑大纲", sub: "调整图文内容", path: "/redbook/outline" },
  { key: "result", title: "渲染出图", sub: "卡片与文案生成", path: "/redbook/result" },
  { key: "publish", title: "发布笔记", sub: "一键直达小红书", path: "/redbook/publish" },
] as const;

type StepKey = (typeof steps)[number]["key"];

const normalizedStep = computed<StepKey>(() => {
  const raw = props.currentStep;
  if (raw === "publish" || raw === 4 || raw === "4") return "publish";
  if (raw === "result" || raw === 3 || raw === "3") return "result";
  if (raw === "outline" || raw === 2 || raw === "2") return "outline";
  return "topic";
});

const stepOrder: Record<StepKey, number> = {
  topic: 0,
  outline: 1,
  result: 2,
  publish: 3,
};

const isRenderingImages = computed(() => {
  return (
    (store.progress?.status === "generating" || store.stage === "generating") &&
    Boolean(store.imageJobId)
  );
});

function isStepCompleted(key: StepKey): boolean {
  if (stepOrder[normalizedStep.value] <= stepOrder[key]) return false;
  // 完成态需有对应数据支撑，避免空流程下展示虚假进度
  if (key === "outline") return (store.outline?.pages?.length ?? 0) > 0;
  if (key === "result") return (store.images?.length ?? 0) > 0;
  if (key === "topic") {
    return Boolean(store.topic?.trim()) || (store.outline?.pages?.length ?? 0) > 0;
  }
  return true;
}

function isStepClickable(key: StepKey): boolean {
  // 允许随时回到前面的步骤
  if (stepOrder[key] < stepOrder[normalizedStep.value]) return true;
  // 如果大纲已有内容，允许点击到大纲
  if (key === "outline" && store.outline?.pages?.length > 0) return true;
  // 如果已经有生成的图片或正在渲染中，允许点击到结果
  if (
    key === "result" &&
    (store.images?.length > 0 || isRenderingImages.value)
  ) {
    return true;
  }
  // 如果已满足发布条件且图片全部就绪，允许直达发布
  if (
    key === "publish" &&
    store.images?.length > 0 &&
    store.images.every((img) => img.status === "done" && img.url)
  ) {
    return true;
  }
  return false;
}

function handleStepClick(key: StepKey) {
  if (!isStepClickable(key)) return;
  const target = steps.find((s) => s.key === key);
  if (target) {
    router.push(target.path);
  }
}
</script>

<style scoped>
.creation-stepper {
  width: 100%;
  margin-bottom: 18px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 10px 20px;
  box-shadow: var(--shadow-sm);
}

.stepper-track {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.stepper-item {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  flex: 1;
  color: var(--text-sub);
  user-select: none;
  transition: all var(--transition-fast);
}

.stepper-item.clickable {
  cursor: pointer;
}

.stepper-item.clickable:hover .step-indicator {
  border-color: var(--primary);
  color: var(--primary);
}

.stepper-item.clickable:hover .step-title {
  color: var(--text-main);
}

.step-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  transition: all var(--transition-fast);
  font-variant-numeric: tabular-nums;
}

.step-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-sub);
  transition: color var(--transition-fast);
  white-space: nowrap;
}

.step-sub {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* 激活态 */
.stepper-item.active {
  color: var(--text-main);
}

.stepper-item.active .step-indicator {
  background: var(--primary);
  border-color: var(--primary);
  color: #ffffff;
  box-shadow: 0 0 16px rgba(255, 36, 66, 0.4);
}

.stepper-item.active .step-title {
  color: var(--text-main);
  font-weight: 700;
}

/* 完成态 */
.stepper-item.completed .step-indicator {
  background: rgba(16, 185, 129, 0.15);
  border-color: var(--color-success);
  color: var(--color-success);
}

.step-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: stepperSpin 0.8s linear infinite;
}

@keyframes stepperSpin {
  to {
    transform: rotate(360deg);
  }
}

.step-check {
  font-weight: 800;
}

.stepper-item.completed .step-title {
  color: var(--text-main);
}

/* 分隔线 */
.step-divider {
  flex: 1;
  height: 2px;
  background: var(--border-color);
  margin: 0 16px;
  min-width: 24px;
}

.stepper-item.completed .step-divider {
  background: var(--color-success);
  opacity: 0.5;
}

/* 移动端收敛 */
@media (max-width: 768px) {
  .creation-stepper {
    padding: 10px 14px;
    margin-bottom: 20px;
  }

  .step-sub {
    display: none;
  }

  .step-divider {
    margin: 0 8px;
    min-width: 12px;
  }

  .step-indicator {
    width: 26px;
    height: 26px;
    font-size: 12px;
  }

  .step-title {
    font-size: 12px;
  }
}
</style>
