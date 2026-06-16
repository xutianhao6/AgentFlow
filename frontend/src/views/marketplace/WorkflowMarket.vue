<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { marketplaceApi } from '@/api/marketplace'
import { useMarketplaceStore } from '@/stores/marketplace'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import {
  SearchOutlined,
  DownloadOutlined,
  WarningOutlined,
  PartitionOutlined,
} from '@ant-design/icons-vue'

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
    <a-space style="margin-bottom: 16px">
      <a-input v-model:value="keyword" placeholder="搜索模板" allow-clear style="width: 280px" @press-enter="load">
        <template #prefix><SearchOutlined style="color: var(--af-text-tertiary)" /></template>
      </a-input>
      <a-button @click="load">搜索</a-button>
    </a-space>

    <a-row :gutter="16">
      <a-col v-for="t in store.templates" :key="t.id" :xs="24" :sm="12" :lg="8" style="margin-bottom: 16px">
        <a-card class="tpl-card af-card af-card--hover">
          <div class="tpl-card__head">
            <span class="tpl-card__icon"><PartitionOutlined /></span>
            <span class="tpl-card__name">{{ t.name }}</span>
            <a-tag>{{ t.category }}</a-tag>
          </div>
          <div class="tpl-card__desc af-muted">{{ t.description }}</div>
          <div v-if="t.dependencies?.plugins?.length" class="tpl-card__dep">
            <WarningOutlined /> 依赖插件：{{ t.dependencies.plugins.join(', ') }}
          </div>
          <div class="tpl-card__foot">
            <span class="af-dim" style="font-size: 12px">
              <DownloadOutlined /> {{ t.downloads }} · {{ t.author }}
            </span>
            <a-button type="primary" size="small" @click="importTpl(t.id)">导入</a-button>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <EmptyState v-if="!store.templates.length" description="没有匹配的模板" />
  </div>
</template>

<style scoped>
.tpl-card :deep(.ant-card-body) {
  padding: 16px;
}
.tpl-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.tpl-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--af-radius);
  background: var(--af-primary-soft);
  color: var(--af-primary);
  font-size: 16px;
  flex: none;
}
.tpl-card__name {
  font-weight: 600;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tpl-card__desc {
  min-height: 42px;
  font-size: 13px;
  line-height: 1.6;
}
.tpl-card__dep {
  font-size: 12px;
  color: var(--af-warning);
  margin-top: 6px;
}
.tpl-card__foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--af-border-light);
}
</style>
