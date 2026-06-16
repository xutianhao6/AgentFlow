<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { workflowApi } from '@/api/workflow'
import type { WorkflowSummary } from '@/types/dsl'
import PageHeader from '@/components/common/PageHeader.vue'
import { formatTime } from '@/utils/format'

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
        <a-button type="primary" @click="createOpen = true">+ 新建工作流</a-button>
      </template>
    </PageHeader>

    <a-table :data-source="items" :loading="loading" row-key="id" :pagination="false">
      <a-table-column title="名称" data-index="name" />
      <a-table-column title="描述" data-index="description" />
      <a-table-column title="版本" data-index="version" width="80" />
      <a-table-column title="更新时间" width="200">
        <template #default="{ record }">{{ formatTime(record.updated_at) }}</template>
      </a-table-column>
      <a-table-column title="操作" width="160">
        <template #default="{ record }">
          <a @click="edit(record.id)">编辑</a>
          <a-divider type="vertical" />
          <a style="color:#ff4d4f" @click="remove(record.id)">删除</a>
        </template>
      </a-table-column>
    </a-table>

    <a-modal v-model:open="createOpen" title="新建工作流" @ok="create">
      <a-input v-model:value="newName" placeholder="工作流名称" />
    </a-modal>
  </div>
</template>
