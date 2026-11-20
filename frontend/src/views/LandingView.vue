<template>
  <div class="container landing-container">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-ambient-glow"></div>
      <div class="hero-content">
        <h1 class="page-title">选择创作模式</h1>
        <p class="page-subtitle">
          RedInk 双核创作引擎 · 从 3:4 社媒爆款图文卡片到经典理论概念蓝图，让 AI 将你的创意一键高质量落地
        </p>
      </div>

      <!-- 模式选择 -->
      <ModeSelector @select="handleModeSelect" />
    </div>

    <!-- 快捷入口 -->
    <div class="quick-actions">
      <router-link
        to="/templates"
        class="quick-action"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M20 7h-9"></path>
          <path d="M14 17H5"></path>
          <circle
            cx="17"
            cy="17"
            r="3"
          ></circle>
          <circle
            cx="7"
            cy="7"
            r="3"
          ></circle>
        </svg>
        <span>模板市集</span>
        <span class="quick-badge">HOT</span>
      </router-link>
      <router-link
        to="/history"
        class="quick-action"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
          />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        <span>历史记录</span>
      </router-link>
      <router-link
        to="/knowledge"
        class="quick-action"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path
            d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"
          />
        </svg>
        <span>知识库</span>
      </router-link>
      <router-link
        to="/settings"
        class="quick-action"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle
            cx="12"
            cy="12"
            r="3"
          />
          <path
            d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
          />
        </svg>
        <span>系统设置</span>
      </router-link>
    </div>

    <!-- 页脚 -->
    <div class="page-footer">
      <div class="footer-tip">RedInk (红墨) · 让传播不再需要门槛，让创作从未如此简单</div>
      <div class="footer-copyright">© 2026 RedInk (xiaohongshu-redink)</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import ModeSelector from '../components/ModeSelector.vue'

const router = useRouter()

function handleModeSelect(mode: 'redbook' | 'concept') {
  if (mode === 'redbook') {
    router.push('/redbook')
  } else {
    router.push('/concept')
  }
}
</script>

<style scoped>
.landing-container {
  max-width: 1040px;
  padding-top: 16px;
  position: relative;
}

.hero-section {
  text-align: center;
  margin-bottom: 48px;
  position: relative;
  animation: fadeIn 0.5s ease-out;
}

.hero-ambient-glow {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  width: 500px;
  height: 240px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 36, 66, 0.08) 0%,
    rgba(255, 36, 66, 0) 70%
  );
  pointer-events: none;
  z-index: 0;
}

.hero-content {
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 38px;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 14px;
  letter-spacing: -0.025em;
  text-wrap: balance;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-sub);
  line-height: 1.65;
  max-width: 640px;
  margin: 0 auto;
  text-wrap: pretty;
}

/* 快捷入口 */
.quick-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-sub);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
}

.quick-action:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.quick-action:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-fade);
  transform: translateY(-2px);
}

.quick-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 99px;
  background: var(--primary);
  color: #ffffff;
  line-height: 1;
  box-shadow: 0 0 8px rgba(255, 36, 66, 0.4);
  animation: badgeGlow 2.4s infinite ease-in-out;
}

@keyframes badgeGlow {
  0%, 100% {
    opacity: 0.85;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.06);
    box-shadow: 0 0 12px rgba(255, 36, 66, 0.65);
  }
}

/* 页脚 */
.page-footer {
  text-align: center;
  padding: 40px 0 24px;
}

.footer-tip {
  font-size: 13px;
  color: var(--text-sub);
  margin-bottom: 6px;
}

.footer-copyright {
  font-size: 12px;
  color: var(--text-secondary);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 28px;
  }
  .page-subtitle {
    font-size: 14px;
  }
  .quick-actions {
    gap: 10px;
  }
  .quick-action {
    padding: 8px 14px;
    font-size: 13px;
  }
}
</style>
