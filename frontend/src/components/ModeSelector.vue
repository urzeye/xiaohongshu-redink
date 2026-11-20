<template>
  <div class="mode-selector">
    <div class="mode-cards">
      <!-- 小红书模式 -->
      <div
        class="mode-card redbook"
        tabindex="0"
        role="button"
        aria-label="选择小红书图文模式"
        @click="$emit('select', 'redbook')"
        @keydown.enter.prevent="$emit('select', 'redbook')"
        @keydown.space.prevent="$emit('select', 'redbook')"
      >
        <span class="mode-badge redbook-badge">爆款优选</span>
        <div class="mode-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="3" ry="3"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <h2 class="mode-title">小红书图文</h2>
        <p class="mode-desc">工业级批量生产小红书爆款图文卡片，智能拆解大纲、封面排版与内页并发渲染</p>
        <div class="mode-features">
          <span class="feature-tag">3:4 原生比例</span>
          <span class="feature-tag">智能大纲</span>
          <span class="feature-tag">多图并发生成</span>
          <span class="feature-tag">一键直发</span>
        </div>
        <div class="mode-action">
          <span>进入创作工坊</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </div>
      </div>

      <!-- 概念图模式 -->
      <div
        class="mode-card concept"
        tabindex="0"
        role="button"
        aria-label="选择概念可视化模式"
        @click="$emit('select', 'concept')"
        @keydown.enter.prevent="$emit('select', 'concept')"
        @keydown.space.prevent="$emit('select', 'concept')"
      >
        <span class="mode-badge concept-badge">知识图解</span>
        <div class="mode-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <circle cx="4" cy="6" r="2"/>
            <circle cx="20" cy="6" r="2"/>
            <circle cx="4" cy="18" r="2"/>
            <circle cx="20" cy="18" r="2"/>
            <line x1="6" y1="6" x2="9.5" y2="10"/>
            <line x1="18" y1="6" x2="14.5" y2="10"/>
            <line x1="6" y1="18" x2="9.5" y2="14"/>
            <line x1="18" y1="18" x2="14.5" y2="14"/>
          </svg>
        </div>
        <h2 class="mode-title">概念可视化</h2>
        <p class="mode-desc">输入长篇论文或复杂业务理论，自动映射至经典分析模型，输出高精度蓝图图解</p>
        <div class="mode-features">
          <span class="feature-tag">27+ 理论框架</span>
          <span class="feature-tag">图表映射</span>
          <span class="feature-tag">蓝图视觉</span>
          <span class="feature-tag">学术严谨</span>
        </div>
        <div class="mode-action">
          <span>构建概念蓝图</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'select', mode: 'redbook' | 'concept'): void
}>()
</script>

<style scoped>
.mode-selector {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.mode-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 36px 32px;
  cursor: pointer;
  transition: all var(--transition-base);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mode-card::before {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.mode-card.redbook::before {
  background: radial-gradient(
    circle at 80% 20%,
    rgba(255, 36, 66, 0.08) 0%,
    transparent 60%
  );
}

.mode-card.concept::before {
  background: radial-gradient(
    circle at 80% 20%,
    rgba(59, 130, 246, 0.08) 0%,
    transparent 60%
  );
}

.mode-card:hover::before {
  opacity: 1;
}

.mode-card:active {
  transform: translateY(-2px) scale(0.99);
}

.mode-card:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 3px;
}

.mode-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 99px;
  letter-spacing: 0.02em;
}

.redbook-badge {
  background: rgba(255, 36, 66, 0.12);
  color: #ff4d63;
  border: 1px solid rgba(255, 36, 66, 0.25);
}

.concept-badge {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}

.mode-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
}

.mode-card.redbook:hover {
  border-color: rgba(255, 36, 66, 0.6);
  box-shadow: 0 16px 40px rgba(255, 36, 66, 0.08), 0 4px 16px rgba(0, 0, 0, 0.2);
}

.mode-card.concept:hover {
  border-color: rgba(59, 130, 246, 0.6);
  box-shadow: 0 16px 40px rgba(59, 130, 246, 0.08), 0 4px 16px rgba(0, 0, 0, 0.2);
}

.mode-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
}

.mode-card.redbook .mode-icon {
  background: linear-gradient(135deg, #ff2442 0%, #ff526a 100%);
  color: white;
}

.mode-card.concept .mode-icon {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: white;
}

.mode-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}

.mode-desc {
  font-size: 14px;
  color: var(--text-sub);
  line-height: 1.6;
  margin-bottom: 20px;
  flex: 1;
}

.mode-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.feature-tag {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  color: var(--text-sub);
  border: 1px solid var(--border-color);
  font-weight: 500;
}

.mode-card.redbook .feature-tag {
  background: rgba(255, 36, 66, 0.08);
  border-color: rgba(255, 36, 66, 0.16);
  color: #ff4d63;
}

.mode-card.concept .feature-tag {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.16);
  color: #60a5fa;
}

.mode-action {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-sub);
  transition: all var(--transition-fast);
  margin-top: auto;
}

.mode-action svg {
  transition: transform var(--transition-fast);
}

.mode-card:hover .mode-action svg {
  transform: translateX(4px);
}

.mode-card.redbook:hover .mode-action {
  color: #ff2442;
}

.mode-card.concept:hover .mode-action {
  color: #3b82f6;
}

/* 响应式 */
@media (max-width: 768px) {
  .mode-cards {
    grid-template-columns: 1fr;
  }
}
</style>
