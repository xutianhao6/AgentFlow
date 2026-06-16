<script setup lang="ts">
import { onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { pluginApi } from '@/api/plugin'
import { usePluginStore } from '@/stores/plugin'
import PageHeader from '@/components/common/PageHeader.vue'

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
    <a-table :data-source="store.installed" row-key="id" :pagination="false">
      <a-table-column title="名称" data-index="name" />
      <a-table-column title="类型" data-index="type" width="120" />
      <a-table-column title="版本" data-index="version" width="100" />
      <a-table-column title="描述" data-index="description" />
      <a-table-column title="操作" width="100">
        <template #default="{ record }"><a style="color:#ff4d4f" @click="uninstall(record.id)">卸载</a></template>
      </a-table-column>
    </a-table>
  </div>
</template>
