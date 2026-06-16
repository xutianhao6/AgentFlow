<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { marketplaceApi } from '@/api/marketplace'
import { useMarketplaceStore } from '@/stores/marketplace'
import PageHeader from '@/components/common/PageHeader.vue'

const store = useMarketplaceStore()
const router = useRouter()
const keyword = ref('')

async function load() { await store.load(undefined, keyword.value) }

async function importTpl(id: string) {
  try {
    const res = await marketplaceApi.import(id)
    message.success('导入成功，正在打开副本')
    router.push(`/workflows/${res.workflow_id}/edit`)
  } catch (e: any) {
    // dependency error (409) handled by interceptor message; nothing else needed
  }
}

onMounted(load)
</script>

<template>
  <div class="af-page">
    <PageHeader title="工作流市场" subtitle="下载现成工作流模板，一键导入为你的私有副本" />
    <a-space style="margin-bottom:16px">
      <a-input v-model:value="keyword" placeholder="搜索模板" @press-enter="load" />
      <a-button @click="load">搜索</a-button>
    </a-space>

    <a-row :gutter="16">
      <a-col v-for="t in store.templates" :key="t.id" :span="8" style="margin-bottom:16px">
        <a-card>
          <template #title>{{ t.name }}</template>
          <template #extra><a-tag>{{ t.category }}</a-tag></template>
          <div style="color:#999;min-height:42px">{{ t.description }}</div>
          <div v-if="t.dependencies?.plugins?.length" style="font-size:12px;color:#fa8c16;margin-top:6px">
            依赖插件：{{ t.dependencies.plugins.join(', ') }}
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
            <span style="color:#bbb;font-size:12px">⬇ {{ t.downloads }} · {{ t.author }}</span>
            <a-button type="primary" size="small" @click="importTpl(t.id)">导入</a-button>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>
