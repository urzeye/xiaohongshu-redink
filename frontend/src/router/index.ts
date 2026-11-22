import { createRouter, createWebHistory } from 'vue-router'

// 路由级代码分割：首屏只加载落地页，其余视图按需加载，加快首次进入与切换
const LandingView = () => import('../views/LandingView.vue')

// 小红书模式页面
const HomeView = () => import('../views/HomeView.vue')
const OutlineView = () => import('../views/OutlineView.vue')
const GenerateView = () => import('../views/GenerateView.vue')
const ResultView = () => import('../views/ResultView.vue')
const PublishView = () => import('../views/PublishView.vue')

// 概念图模式页面
const ConceptView = () => import('../views/ConceptView.vue')
const ConceptHistoryView = () => import('../views/ConceptHistoryView.vue')

// 通用页面
const HistoryView = () => import('../views/HistoryView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const KnowledgeView = () => import('../views/KnowledgeView.vue')
const TemplateMarketView = () => import('../views/TemplateMarketView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // 前进/后退时恢复滚动位置；主动导航一律回到顶部，避免新页面继承旧页面的滚动偏移
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  },
  routes: [
    // 首页 - 模式选择
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },

    // ============ 小红书模式 ============
    {
      path: '/redbook',
      name: 'redbook',
      component: HomeView
    },
    {
      path: '/redbook/outline',
      name: 'redbook-outline',
      component: OutlineView
    },
    {
      path: '/redbook/generate',
      name: 'redbook-generate',
      component: GenerateView
    },
    {
      path: '/redbook/result',
      name: 'redbook-result',
      component: ResultView
    },
    {
      path: '/redbook/result/:recordId',
      name: 'redbook-result-record',
      component: ResultView
    },
    {
      path: '/redbook/publish',
      name: 'redbook-publish',
      component: PublishView
    },

    // ============ 概念图模式 ============
    {
      path: '/concept',
      name: 'concept',
      component: ConceptView
    },
    {
      path: '/concept/history',
      name: 'concept-history',
      component: ConceptHistoryView
    },

    // ============ 通用页面 ============
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/history/:id',
      name: 'history-detail',
      component: HistoryView
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgeView
    },
    {
      path: '/templates',
      name: 'template-market',
      component: TemplateMarketView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    },

    // ============ 向后兼容旧路由 ============
    // 保持旧路由可用，重定向到新路径
    {
      path: '/outline',
      redirect: '/redbook/outline'
    },
    {
      path: '/generate',
      redirect: '/redbook/generate'
    },
    {
      path: '/result',
      redirect: '/redbook/result'
    },
    {
      path: '/result/:recordId',
      redirect: to => `/redbook/result/${to.params.recordId}`
    },
    {
      path: '/publish',
      redirect: '/redbook/publish'
    },
  ]
})

export default router
