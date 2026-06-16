<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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

function go(key: string) {
  const map: Record<string, string> = {
    workflows: '/workflows',
    datasets: '/datasets',
    'plugin-market': '/plugins/market',
    'plugin-installed': '/plugins/installed',
    'workflow-market': '/workflow-market',
  }
  router.push(map[key])
}
</script>

<template>
  <a-layout style="height:100vh">
    <a-layout-sider theme="light" width="200" style="border-right:1px solid #f0f0f0">
      <div style="height:56px;display:flex;align-items:center;padding:0 16px;font-weight:700;font-size:18px;color:#1677ff">
        ⚡ AgentFlow
      </div>
      <a-menu :selected-keys="selectedKeys" mode="inline" @click="(e:any) => go(e.key)">
        <a-menu-item key="workflows">工作流</a-menu-item>
        <a-menu-item key="datasets">知识库</a-menu-item>
        <a-menu-item key="plugin-market">插件市场</a-menu-item>
        <a-menu-item key="plugin-installed">已安装插件</a-menu-item>
        <a-menu-item key="workflow-market">工作流市场</a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-content style="overflow:auto">
        <RouterView />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
