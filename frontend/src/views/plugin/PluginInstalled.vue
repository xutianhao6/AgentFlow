<script setup lang="ts">
import { onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { pluginApi } from '@/api/plugin'
import { usePluginStore } from '@/stores/plugin'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { DeleteOutlined } from '@ant-design/icons-vue'

const store = usePluginStore()

async function uninstall(id: string) {
  await pluginApi.uninstall(id)
  message.success('已卸载')
  store.loadInstalled()
}

onMounted(() => store.loadInstalled())
</script>

<template>
  <div class="af-page">
    <PageHeader title="已安装插件" subtitle="安装的工具插件会作为节点出现在编辑器节点面板" />
    <div class="af-card" style="padding: 4px 4px 0">
      <a-table :data-source="store.installed" row-key="id" :pagination="false">
        <a-table-column title="名称" data-index="name">
          <template #default="{ record }">
            <strong>{{ record.name }}</strong>
          </template>
        </a-table-column>
        <a-table-column title="类型" width="130">
          <template #default="{ record }"><a-tag>{{ record.type }}</a-tag></template>
        </a-table-column>
        <a-table-column title="版本" width="100">
          <template #default="{ record }">
            <span class="af-mono af-muted">v{{ record.version }}</span>
          </template>
        </a-table-column>
        <a-table-column title="描述" data-index="description">
          <template #default="{ record }">
            <span class="af-muted">{{ record.description || '—' }}</span>
          </template>
        </a-table-column>
        <a-table-column title="操作" width="100" align="right">
          <template #default="{ record }">
            <a-tooltip title="卸载">
              <a-button type="text" size="small" danger @click="uninstall(record.id)">
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </a-tooltip>
          </template>
        </a-table-column>
      </a-table>
    </div>

    <EmptyState v-if="!store.installed.length" description="还没有安装任何插件，去插件市场看看" />
  </div>
</template>
