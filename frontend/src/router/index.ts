import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/workflows' },
  { path: '/login', component: () => import('@/views/Login.vue') },
  {
    path: '/',
    component: () => import('@/views/AppShell.vue'),
    children: [
      { path: 'workflows', name: 'workflow-list', component: () => import('@/views/workflow/WorkflowList.vue') },
      { path: 'workflows/:id/edit', name: 'workflow-editor', component: () => import('@/views/workflow/WorkflowEditor.vue') },
      { path: 'datasets', name: 'dataset-list', component: () => import('@/views/knowledge/DatasetList.vue') },
      { path: 'datasets/:id', name: 'dataset-detail', component: () => import('@/views/knowledge/DatasetDetail.vue') },
      { path: 'plugins/market', name: 'plugin-market', component: () => import('@/views/plugin/PluginMarket.vue') },
      { path: 'plugins/installed', name: 'plugin-installed', component: () => import('@/views/plugin/PluginInstalled.vue') },
      { path: 'workflow-market', name: 'workflow-market', component: () => import('@/views/marketplace/WorkflowMarket.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
