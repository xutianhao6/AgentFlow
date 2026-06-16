<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { workflowApi } from '@/api/workflow'
import type { WorkflowSummary } from '@/types/dsl'
import PageHeader from '@/components/common/PageHeader.vue'
import { formatTime } from '@/utils/format'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const items = ref<WorkflowSummary[]>([])
const loading = ref(false)
const createOpen = ref(false)
const newName = ref('')

async function load() {
  loading.value = true
  try {
    const res = await workflowApi.list()
    items.value = res.items
  } finally {
    loading.value = false
  }
}

async function create() {
  if (!newName.value) return message.warning('请输入名称')
  const wf = await workflowApi.create(newName.value)
  createOpen.value = false
  newName.value = ''
  router.push(`/workflows/${wf.id}/edit`)
}

function edit(id: string) {
  router.push(`/workflows/${id}/edit`)
}

function remove(id: string) {
  Modal.confirm({
    title: '确认删除该工作流？',
    onOk: async () => {
      await workflowApi.remove(id)
      message.success('已删除')
      load()
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="af-page">
    <PageHeader title="工作流" subtitle="拖拽节点、连线、配置，编排你的 AI 工作流">
      <template #extra>
        <a-button type="primary" @click="createOpen = true">
          <template #icon><PlusOutlined /></template>
          新建工作流
        </a-button>
      </template>
    </PageHeader>

    <div class="af-card" style="padding: 4px 4px 0">
      <a-table :data-source="items" :loading="loading" row-key="id" :pagination="false">
        <a-table-column title="名称" data-index="name">
          <template #default="{ record }">
            <a class="wf-name" @click="edit(record.id)">{{ record.name }}</a>
          </template>
        </a-table-column>
        <a-table-column title="描述" data-index="description">
          <template #default="{ record }">
            <span class="af-muted">{{ record.description || '—' }}</span>
          </template>
        </a-table-column>
        <a-table-column title="版本" width="90">
          <template #default="{ record }">
            <a-tag color="processing" class="af-mono">v{{ record.version }}</a-tag>
          </template>
        </a-table-column>
        <a-table-column title="更新时间" width="200">
          <template #default="{ record }">
            <span class="af-muted">{{ formatTime(record.updated_at) }}</span>
          </template>
        </a-table-column>
        <a-table-column title="操作" width="120" align="right">
          <template #default="{ record }">
            <a-tooltip title="编辑">
              <a-button type="text" size="small" @click="edit(record.id)">
                <template #icon><EditOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="删除">
              <a-button type="text" size="small" danger @click="remove(record.id)">
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </a-tooltip>
          </template>
        </a-table-column>
      </a-table>
    </div>

    <a-modal v-model:open="createOpen" title="新建工作流" @ok="create">
      <a-input v-model:value="newName" placeholder="工作流名称" />
    </a-modal>
  </div>
</template>

<style scoped>
.wf-name {
  font-weight: 600;
  color: var(--af-text);
}
.wf-name:hover {
  color: var(--af-primary);
}
</style>
