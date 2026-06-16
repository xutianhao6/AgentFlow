<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { knowledgeApi } from '@/api/knowledge'
import { useKnowledgeStore } from '@/stores/knowledge'
import type { Dataset } from '@/types/knowledge'
import PageHeader from '@/components/common/PageHeader.vue'
import DocumentUpload from '@/components/knowledge/DocumentUpload.vue'
import IndexSettings from '@/components/knowledge/IndexSettings.vue'
import RetrievalTest from '@/components/knowledge/RetrievalTest.vue'
import { formatTime } from '@/utils/format'

const route = useRoute()
const store = useKnowledgeStore()
const dsId = route.params.id as string
const dataset = ref<Dataset | null>(null)

const statusColor: Record<string, string> = { done: 'green', indexing: 'blue', pending: 'default', failed: 'red' }

async function loadDocs() { await store.loadDocuments(dsId) }

async function removeDoc(docId: string) {
  await knowledgeApi.removeDocument(dsId, docId)
  message.success('已删除')
  loadDocs()
}

onMounted(async () => {
  dataset.value = await knowledgeApi.getDataset(dsId)
  loadDocs()
})
</script>

<template>
  <div class="af-page">
    <PageHeader :title="dataset?.name || '知识库'" :subtitle="dataset?.description">
      <template #extra>
        <a-tag :color="dataset?.index_method === 'high_quality' ? 'blue' : 'orange'">
          {{ dataset?.index_method === 'high_quality' ? '高质量索引' : '经济索引' }}
        </a-tag>
      </template>
    </PageHeader>

    <a-row :gutter="16">
      <a-col :span="14">
        <a-card title="文档" size="small" style="margin-bottom:16px">
          <DocumentUpload :dataset-id="dsId" @uploaded="loadDocs" />
          <a-table :data-source="store.documents" row-key="id" size="small" :pagination="false" style="margin-top:12px">
            <a-table-column title="文件名" data-index="name" />
            <a-table-column title="切分" data-index="chunk_strategy" width="110" />
            <a-table-column title="块数" data-index="chunk_count" width="70" />
            <a-table-column title="状态" width="100">
              <template #default="{ record }">
                <a-tag :color="statusColor[record.status]">{{ record.status }}</a-tag>
              </template>
            </a-table-column>
            <a-table-column title="操作" width="80">
              <template #default="{ record }"><a style="color:#ff4d4f" @click="removeDoc(record.id)">删除</a></template>
            </a-table-column>
          </a-table>
        </a-card>
      </a-col>
      <a-col :span="10">
        <a-card title="索引设置" size="small" style="margin-bottom:16px">
          <IndexSettings :method="dataset?.index_method || 'high_quality'" />
        </a-card>
        <a-card title="检索测试" size="small">
          <RetrievalTest :dataset-id="dsId" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>
