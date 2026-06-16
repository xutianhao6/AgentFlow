<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { knowledgeApi } from '@/api/knowledge'
import { useKnowledgeStore } from '@/stores/knowledge'
import PageHeader from '@/components/common/PageHeader.vue'

const router = useRouter()
const store = useKnowledgeStore()
const createOpen = ref(false)
const form = ref({ name: '', index_method: 'high_quality', description: '' })

async function create() {
  if (!form.value.name) return message.warning('请输入名称')
  await knowledgeApi.createDataset(form.value.name, form.value.index_method, form.value.description)
  createOpen.value = false
  form.value = { name: '', index_method: 'high_quality', description: '' }
  store.loadDatasets()
}

function remove(id: string) {
  Modal.confirm({
    title: '删除知识库及其所有文档？',
    onOk: async () => { await knowledgeApi.removeDataset(id); store.loadDatasets() },
  })
}

onMounted(() => store.loadDatasets())
</script>

<template>
  <div class="af-page">
    <PageHeader title="知识库" subtitle="上传文档构建知识库，供「知识检索节点」做 RAG">
      <template #extra><a-button type="primary" @click="createOpen = true">+ 新建知识库</a-button></template>
    </PageHeader>

    <a-row :gutter="16">
      <a-col v-for="d in store.datasets" :key="d.id" :span="8" style="margin-bottom:16px">
        <a-card hoverable @click="router.push(`/datasets/${d.id}`)">
          <template #title>{{ d.name }}</template>
          <template #extra>
            <a-tag :color="d.index_method === 'high_quality' ? 'blue' : 'orange'">
              {{ d.index_method === 'high_quality' ? '高质量' : '经济' }}
            </a-tag>
          </template>
          <div style="color:#999;min-height:40px">{{ d.description || '暂无描述' }}</div>
          <a style="color:#ff4d4f" @click.stop="remove(d.id)">删除</a>
        </a-card>
      </a-col>
    </a-row>

    <a-modal v-model:open="createOpen" title="新建知识库" @ok="create">
      <a-form layout="vertical">
        <a-form-item label="名称"><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="索引方法">
          <a-radio-group v-model:value="form.index_method">
            <a-radio value="high_quality">高质量（向量语义检索）</a-radio>
            <a-radio value="economy">经济（关键词全文）</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="描述"><a-textarea v-model:value="form.description" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
