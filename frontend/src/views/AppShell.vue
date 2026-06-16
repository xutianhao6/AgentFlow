<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  PartitionOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
  ApiOutlined,
  ShopOutlined,
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()

const selectedKeys = computed(() => {
  const p = route.path
  if (p.startsWith('/datasets')) return ['datasets']
  if (p.startsWith('/plugins/market')) return ['plugin-market']
  if (p.startsWith('/plugins/installed')) return ['plugin-installed']
  if (p.startsWith('/workflow-market')) return ['workflow-market']
  return ['workflows']
})

const routeMap: Record<string, string> = {
  workflows: '/workflows',
  datasets: '/datasets',
  'plugin-market': '/plugins/market',
  'plugin-installed': '/plugins/installed',
  'workflow-market': '/workflow-market',
}

function go(key: string) {
  if (routeMap[key]) router.push(routeMap[key])
}

// 分组菜单：编排 / 知识 / 生态
const groups = [
  {
    title: '工作流编排',
    items: [
      { key: 'workflows', label: '工作流', icon: PartitionOutlined },
      { key: 'workflow-market', label: '工作流市场', icon: ShopOutlined },
    ],
  },
  {
    title: '知识',
    items: [{ key: 'datasets', label: '知识库', icon: DatabaseOutlined }],
  },
  {
    title: '扩展生态',
    items: [
      { key: 'plugin-market', label: '插件市场', icon: AppstoreOutlined },
      { key: 'plugin-installed', label: '已安装插件', icon: ApiOutlined },
    ],
  },
]

const renderIcon = (icon: any) => () => h(icon)
</script>

<template>
  <a-layout class="shell">
    <a-layout-sider theme="light" width="232" class="shell__sider">
      <div class="brand">
        <span class="brand__logo">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">
            <path
              d="M12 2 3 7v10l9 5 9-5V7l-9-5Z"
              stroke="#fff"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
            <path d="m12 7-4 5h3l-1 5 5-7h-3l1-3Z" fill="#fff" />
          </svg>
        </span>
        <span class="brand__name">AgentFlow</span>
      </div>

      <nav class="nav">
        <template v-for="g in groups" :key="g.title">
          <div class="nav__group">{{ g.title }}</div>
          <a-menu
            :selected-keys="selectedKeys"
            mode="inline"
            class="nav__menu"
            @click="(e: any) => go(e.key)"
          >
            <a-menu-item v-for="it in g.items" :key="it.key" :icon="renderIcon(it.icon)">
              {{ it.label }}
            </a-menu-item>
          </a-menu>
        </template>
      </nav>

      <div class="shell__foot">
        <span class="shell__ver">v0.1.0</span>
        <span class="shell__hint">可视化 Agent 编排</span>
      </div>
    </a-layout-sider>

    <a-layout>
      <a-layout-content class="shell__content">
        <RouterView />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.shell {
  height: 100vh;
}
.shell__sider {
  border-right: 1px solid var(--af-border);
  display: flex;
  flex-direction: column;
}
.shell__sider :deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.brand {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  border-bottom: 1px solid var(--af-border-light);
}
.brand__logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--af-primary), var(--af-primary-active));
  box-shadow: var(--af-shadow-primary);
}
.brand__name {
  font-weight: 700;
  font-size: 17px;
  letter-spacing: -0.01em;
  background: linear-gradient(135deg, var(--af-primary), #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav {
  flex: 1;
  overflow: auto;
  padding: 8px 12px;
}
.nav__group {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--af-text-tertiary);
  padding: 14px 10px 4px;
}
.nav__menu {
  border-inline-end: none !important;
  background: transparent;
}

.shell__foot {
  padding: 12px 18px;
  border-top: 1px solid var(--af-border-light);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.shell__ver {
  font-family: var(--af-font-mono);
  font-size: 12px;
  color: var(--af-text-secondary);
}
.shell__hint {
  font-size: 11px;
  color: var(--af-text-tertiary);
}

.shell__content {
  overflow: auto;
  background: var(--af-bg);
}
</style>
