<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { knowledgeApi } from '@/api/knowledge'
import { useKnowledgeStore } from '@/stores/knowledge'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { PlusOutlined, DatabaseOutlined, DeleteOutlined } from '@ant-design/icons-vue'

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
      <template #extra>
        <a-button type="primary" @click="createOpen = true">
          <template #icon><PlusOutlined /></template>
          新建知识库
        </a-button>
      </template>
    </PageHeader>

    <a-row :gutter="16">
      <a-col v-for="d in store.datasets" :key="d.id" :xs="24" :sm="12" :lg="8" style="margin-bottom: 16px">
        <a-card hoverable class="ds-card" @click="router.push(`/datasets/${d.id}`)">
          <div class="ds-card__head">
            <span class="ds-card__icon"><DatabaseOutlined /></span>
            <span class="ds-card__name">{{ d.name }}</span>
            <a-tag :color="d.index_method === 'high_quality' ? 'processing' : 'orange'">
              {{ d.index_method === 'high_quality' ? '高质量' : '经济' }}
            </a-tag>
          </div>
          <div class="ds-card__desc af-muted">{{ d.description || '暂无描述' }}</div>
          <div class="ds-card__foot">
            <a-button type="text" size="small" danger @click.stop="remove(d.id)">
              <template #icon><DeleteOutlined /></template>
              删除
            </a-button>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <EmptyState v-if="!store.datasets.length" description="还没有知识库，点击右上角新建" />

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

<style scoped>
.ds-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.ds-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--af-radius);
  background: var(--af-primary-soft);
  color: var(--af-primary);
  font-size: 17px;
  flex: none;
}
.ds-card__name {
  font-weight: 600;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ds-card__desc {
  min-height: 40px;
  font-size: 13px;
  line-height: 1.6;
}
.ds-card__foot {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--af-border-light);
}
</style>
