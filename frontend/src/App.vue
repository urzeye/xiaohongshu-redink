<template>
  <div
    id="app"
    :class="{ 'sidebar-collapsed': sidebarCollapsed }"
  >
    <n-config-provider
      :theme="isDark ? darkTheme : null"
      :theme-overrides="themeOverrides"
      style="display: contents"
    >
      <n-message-provider style="display: contents">
        <!-- 移动端顶部顶栏 -->
        <header class="mobile-header">
          <RouterLink
            to="/"
            class="mobile-brand"
            @click="sidebarMobileOpen = false"
          >
            <img
              src="/logo.png"
              alt="RedInk"
              class="mobile-brand-logo"
            />
            <span>RedInk 红墨</span>
          </RouterLink>
          <button
            class="mobile-menu-btn"
            @click="sidebarMobileOpen = !sidebarMobileOpen"
            :aria-label="sidebarMobileOpen ? '关闭菜单' : '打开菜单'"
          >
            <svg
              v-if="!sidebarMobileOpen"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
            <svg
              v-else
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </header>

        <!-- 移动端侧边栏遮罩 -->
        <div
          v-if="sidebarMobileOpen"
          class="mobile-backdrop"
          @click="sidebarMobileOpen = false"
        ></div>

        <!-- 侧边栏 Sidebar -->
        <aside
          class="layout-sidebar"
          :class="{
            collapsed: sidebarCollapsed,
            'mobile-open': sidebarMobileOpen,
          }"
        >
          <div class="logo-area">
            <RouterLink to="/" class="logo-link">
              <img
                src="/logo-banner.png"
                alt="RedInk"
                class="logo-icon"
              />
            </RouterLink>
          </div>

          <nav class="nav-menu">
            <RouterLink
              to="/"
              class="nav-item"
              active-class="active"
              exact
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span class="nav-text">首页</span>
            </RouterLink>
            <a
              href="/redbook"
              class="nav-item"
              :class="{ active: route.path.startsWith('/redbook') }"
              @click="navigateRedbook"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect
                  x="3"
                  y="3"
                  width="18"
                  height="18"
                  rx="2"
                  ry="2"
                ></rect>
                <circle
                  cx="8.5"
                  cy="8.5"
                  r="1.5"
                ></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <span class="nav-text">小红书图文</span>
            </a>
            <RouterLink
              to="/templates"
              class="nav-item"
              active-class="active"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
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
              <span class="nav-text">模板市集</span>
            </RouterLink>
            <RouterLink
              to="/concept"
              class="nav-item"
              active-class="active"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="3"
                ></circle>
                <circle
                  cx="4"
                  cy="6"
                  r="2"
                ></circle>
                <circle
                  cx="20"
                  cy="6"
                  r="2"
                ></circle>
                <line
                  x1="6"
                  y1="6"
                  x2="9.5"
                  y2="10"
                ></line>
                <line
                  x1="18"
                  y1="6"
                  x2="14.5"
                  y2="10"
                ></line>
              </svg>
              <span class="nav-text">概念可视化</span>
            </RouterLink>
            <div class="nav-divider"></div>
            <RouterLink
              to="/history"
              class="nav-item"
              active-class="active"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
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
              <span class="nav-text">历史记录</span>
            </RouterLink>
            <RouterLink
              to="/knowledge"
              class="nav-item"
              active-class="active"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path
                  d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"
                ></path>
              </svg>
              <span class="nav-text">知识库</span>
            </RouterLink>
            <RouterLink
              to="/settings"
              class="nav-item"
              active-class="active"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="3"
                ></circle>
                <path
                  d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
                ></path>
              </svg>
              <span class="nav-text">系统设置</span>
            </RouterLink>
          </nav>

          <!-- 主题切换 -->
          <div
            class="theme-switcher-container"
            :class="{ 'is-collapsed': sidebarCollapsed }"
          >
            <template v-if="!sidebarCollapsed">
              <button
                class="theme-btn"
                :class="{ active: theme === 'system' }"
                @click="setTheme('system')"
                title="跟随系统设置"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect
                    x="2"
                    y="3"
                    width="20"
                    height="14"
                    rx="2"
                    ry="2"
                  ></rect>
                  <line
                    x1="8"
                    y1="21"
                    x2="16"
                    y2="21"
                  ></line>
                  <line
                    x1="12"
                    y1="17"
                    x2="12"
                    y2="21"
                  ></line>
                </svg>
              </button>
              <button
                class="theme-btn"
                :class="{ active: theme === 'light' }"
                @click="setTheme('light')"
                title="浅色模式"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="5"
                  ></circle>
                  <line
                    x1="12"
                    y1="1"
                    x2="12"
                    y2="3"
                  ></line>
                  <line
                    x1="12"
                    y1="21"
                    x2="12"
                    y2="23"
                  ></line>
                  <line
                    x1="4.22"
                    y1="4.22"
                    x2="5.64"
                    y2="5.64"
                  ></line>
                  <line
                    x1="18.36"
                    y1="18.36"
                    x2="19.78"
                    y2="19.78"
                  ></line>
                  <line
                    x1="1"
                    y1="12"
                    x2="3"
                    y2="12"
                  ></line>
                  <line
                    x1="21"
                    y1="12"
                    x2="23"
                    y2="12"
                  ></line>
                  <line
                    x1="4.22"
                    y1="19.78"
                    x2="5.64"
                    y2="18.36"
                  ></line>
                  <line
                    x1="18.36"
                    y1="5.64"
                    x2="19.78"
                    y2="4.22"
                  ></line>
                </svg>
              </button>
              <button
                class="theme-btn"
                :class="{ active: theme === 'dark' }"
                @click="setTheme('dark')"
                title="深色模式"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
                  ></path>
                </svg>
              </button>
            </template>
            <template v-else>
              <button
                class="theme-btn active current-theme"
                @click="toggleTheme"
                :title="
                  theme === 'dark'
                    ? '深色模式'
                    : theme === 'light'
                      ? '浅色模式'
                      : '跟随系统'
                "
              >
                <svg
                  v-if="theme === 'dark'"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
                  ></path>
                </svg>
                <svg
                  v-else-if="theme === 'light'"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="5"
                  ></circle>
                  <line
                    x1="12"
                    y1="1"
                    x2="12"
                    y2="3"
                  ></line>
                  <line
                    x1="12"
                    y1="21"
                    x2="12"
                    y2="23"
                  ></line>
                  <line
                    x1="4.22"
                    y1="4.22"
                    x2="5.64"
                    y2="5.64"
                  ></line>
                  <line
                    x1="18.36"
                    y1="18.36"
                    x2="19.78"
                    y2="19.78"
                  ></line>
                  <line
                    x1="1"
                    y1="12"
                    x2="3"
                    y2="12"
                  ></line>
                  <line
                    x1="21"
                    y1="12"
                    x2="23"
                    y2="12"
                  ></line>
                  <line
                    x1="4.22"
                    y1="19.78"
                    x2="5.64"
                    y2="18.36"
                  ></line>
                  <line
                    x1="18.36"
                    y1="5.64"
                    x2="19.78"
                    y2="4.22"
                  ></line>
                </svg>
                <svg
                  v-else
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect
                    x="2"
                    y="3"
                    width="20"
                    height="14"
                    rx="2"
                    ry="2"
                  ></rect>
                  <line
                    x1="8"
                    y1="21"
                    x2="16"
                    y2="21"
                  ></line>
                  <line
                    x1="12"
                    y1="17"
                    x2="12"
                    y2="21"
                  ></line>
                </svg>
              </button>
            </template>
          </div>

          <!-- 折叠按钮 -->
          <button
            class="collapse-btn"
            @click="toggleSidebar"
            :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
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
            >
              <polyline
                v-if="sidebarCollapsed"
                points="9 18 15 12 9 6"
              ></polyline>
              <polyline
                v-else
                points="15 18 9 12 15 6"
              ></polyline>
            </svg>
          </button>

          <div class="sidebar-footer">
            <!-- 桌面端本地引擎状态胶囊 -->
            <RouterLink
              v-if="isTauri"
              to="/settings"
              class="desktop-engine-pill"
              :class="{
                'pill-running': engineStatus?.is_running,
                'pill-starting': !engineStatus?.is_running && !engineError,
                'pill-error': !engineStatus?.is_running && engineError,
                collapsed: sidebarCollapsed,
              }"
              :title="
                engineStatus?.is_running
                  ? `本地引擎正常运行中 (监听端口: ${engineStatus.port})`
                  : engineError
                    ? `本地引擎启动失败: ${engineError}`
                    : '本地引擎正在启动中...'
              "
            >
              <span class="engine-dot"></span>
              <span v-if="!sidebarCollapsed" class="engine-text">
                {{
                  engineStatus?.is_running
                    ? `引擎就绪 :${engineStatus.port}`
                    : engineError
                      ? "引擎离线"
                      : "引擎启动中..."
                }}
              </span>
            </RouterLink>

            <div class="brand-badge">
              <div class="brand-icon">
                <img
                  src="/assets/avatars/avatar.gif"
                  alt="小爱同学"
                  class="brand-avatar"
                />
              </div>
              <div
                class="brand-info"
                v-show="!sidebarCollapsed"
              >
                <div class="brand-name">小爱同学</div>
              </div>
            </div>
          </div>
        </aside>

        <!-- 主内容区 -->
        <main class="layout-main">
          <RouterView v-slot="{ Component, route }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" :key="route.fullPath" />
            </transition>

            <!-- 全局页脚版权信息（首页与小红书创作首页除外） -->
            <footer
              v-if="!['/', '/redbook'].includes(route.path)"
              class="global-footer"
            >
              <div class="footer-content">
                <div class="footer-tip">RedInk (红墨) · 小红书 AI 驱动的爆款图文创作引擎</div>
                <div class="footer-text">© 2026 RedInk (xiaohongshu-redink)</div>
                <div class="footer-license">
                  Licensed under
                  <a
                    href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
                    target="_blank"
                    rel="noopener noreferrer"
                    >CC BY-NC-SA 4.0</a
                  >
                </div>
              </div>
            </footer>
          </RouterView>
        </main>
      </n-message-provider>
    </n-config-provider>
  </div>
</template>

<script setup lang="ts">
import { RouterView, RouterLink, useRoute, useRouter } from "vue-router";
import { ref, watch, onMounted } from "vue";
import {
  NConfigProvider,
  NMessageProvider,
  darkTheme,
  type GlobalThemeOverrides,
} from "naive-ui";
import { setupAutoSave, useGeneratorStore } from "./stores/generator";
import { useTheme } from "./composables/useTheme";

const router = useRouter();
const generatorStore = useGeneratorStore();

function navigateRedbook(e: Event) {
  e.preventDefault();
  if (
    generatorStore.stage === "generating" ||
    (generatorStore.stage === "result" &&
      (generatorStore.images.length > 0 ||
        generatorStore.taskId ||
        generatorStore.recordId))
  ) {
    router.push("/redbook/result");
  } else if (
    generatorStore.stage === "outline" &&
    generatorStore.outline.pages.length > 0
  ) {
    router.push("/redbook/outline");
  } else {
    router.push("/redbook");
  }
}

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: "#ff2442",
    primaryColorHover: "#ff4d63",
    primaryColorPressed: "#e61731",
    primaryColorSuppl: "#ff4d63",
    borderRadius: "8px",
    borderRadiusSmall: "6px",
    fontFamily:
      '"Inter", -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
  },
};

const route = useRoute();
const { isDark, theme, setTheme } = useTheme();

const toggleTheme = () => {
  if (theme.value === "system") {
    setTheme("light");
  } else if (theme.value === "light") {
    setTheme("dark");
  } else {
    setTheme("system");
  }
};

// 侧边栏折叠与移动端抽屉状态
const sidebarCollapsed = ref(false);
const sidebarMobileOpen = ref(false);

// 路由变化时自动关闭移动端侧边栏抽屉
watch(
  () => route.path,
  () => {
    sidebarMobileOpen.value = false;
  }
);

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem("sidebarCollapsed", String(sidebarCollapsed.value));
};

// 启用自动保存到 localStorage
import { isTauriEnvironment, getBackendStatus, openExternalUrl, type BackendStatus } from "./utils/tauri";

const isTauri = ref(isTauriEnvironment());
const engineStatus = ref<BackendStatus | null>(null);
const engineError = ref<string | null>(null);

let enginePollTimer: any = null;

async function checkEngine() {
  if (!isTauri.value) return;
  try {
    const status = await getBackendStatus();
    if (status) {
      engineStatus.value = status;
      engineError.value = status.error || null;
    }
  } catch (e: any) {
    engineError.value = e?.message || String(e);
  }
}

onMounted(() => {
  setupAutoSave();
  const saved = localStorage.getItem("sidebarCollapsed");
  if (saved === "true") {
    sidebarCollapsed.value = true;
  }

  if (isTauri.value) {
    checkEngine();
    enginePollTimer = setInterval(() => {
      checkEngine();
    }, 4000);

    // 全局拦截外部链接，使用系统原生默认浏览器打开
    document.addEventListener("click", (e: MouseEvent) => {
      const target = (e.target as HTMLElement)?.closest("a");
      if (!target) return;
      const href = target.getAttribute("href");
      const targetAttr = target.getAttribute("target");
      if (href && (href.startsWith("http://") || href.startsWith("https://"))) {
        try {
          const parsed = new URL(href);
          const isLocal =
            parsed.hostname === "127.0.0.1" ||
            parsed.hostname === "localhost" ||
            parsed.hostname === "tauri.localhost";
          if (!isLocal || targetAttr === "_blank") {
            e.preventDefault();
            openExternalUrl(href);
          }
        } catch {}
      }
    });
  }
});
</script>

<style scoped>
.logo-link {
  display: block;
  text-decoration: none;
}
.theme-switcher-container {
  margin-top: auto;
  margin-bottom: 24px;
  display: flex;
  gap: 8px;
  padding: 4px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 99px;
  justify-content: space-between;
  align-items: center;
}

.theme-switcher-container.is-collapsed {
  background: transparent;
  border-color: transparent;
  padding: 0;
  justify-content: center;
}

.theme-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  border: none;
  background: transparent;
  color: var(--text-sub);
  border-radius: 99px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-btn:hover {
  color: var(--text-main);
  background: var(--bg-hover);
}

.theme-btn.active {
  background: var(--bg-card);
  color: var(--primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.theme-switcher-container.is-collapsed .theme-btn.active {
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
}

/* 覆盖全局样式解决部分布局问题 */
.layout-sidebar {
  padding-bottom: 24px;
}
.sidebar-footer {
  margin-top: 0; /* 之前是 auto，现在交给 theme-switcher 推下去了 */
  padding-top: 16px;
}

/* 桌面端本地引擎状态胶囊 */
.desktop-engine-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  margin-bottom: 12px;
  border-radius: 999px;
  font-size: 12px;
  text-decoration: none;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-sub);
  transition: all var(--transition-fast);
}

.desktop-engine-pill:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
  color: var(--text-main);
}

.desktop-engine-pill.collapsed {
  justify-content: center;
  padding: 6px;
  width: 32px;
  height: 32px;
  margin: 0 auto 12px;
}

.engine-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pill-running .engine-dot {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
}

.pill-starting .engine-dot {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);
  animation: pulse 1.5s infinite ease-in-out;
}

.pill-error .engine-dot {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.6);
}

.engine-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}
</style>
