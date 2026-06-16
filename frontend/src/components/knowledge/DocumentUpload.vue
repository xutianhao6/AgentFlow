<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { knowledgeApi } from '@/api/knowledge'
import ChunkSettings from './ChunkSettings.vue'

const props = defineProps<{ datasetId: string }>()
const emit = defineEmits<{ uploaded: [] }>()

const chunkStrategy = ref('general')
const uploading = ref(false)

async function customRequest({ file }: any) {
  uploading.value = true
  try {
    await knowledgeApi.uploadDocument(props.datasetId, file, chunkStrategy.value)
    message.success('上传并索引完成')
    emit('uploaded')
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div>
    <div style="margin-bottom:10px">
      <span style="margin-right:8px">切分策略：</span>
      <ChunkSettings v-model:value="chunkStrategy" />
    </div>
    <a-upload-dragger
      :custom-request="customRequest"
      :show-upload-list="false"
      accept=".txt,.md,.pdf,.docx"
    >
      <p style="font-size:32px;margin:8px 0">📄</p>
      <p>点击或拖拽文件到此上传（txt / md / pdf / docx）</p>
      <p style="color:#999;font-size:12px">上传后自动触发切分 + 向量化 / 索引</p>
    </a-upload-dragger>
    <a-spin v-if="uploading" style="margin-top:8px" />
  </div>
</template>
