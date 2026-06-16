<script setup lang="ts">
import { ref } from 'vue'
import { knowledgeApi } from '@/api/knowledge'
import type { RetrieveResult } from '@/types/knowledge'

const props = defineProps<{ datasetId: string }>()

const query = ref('')
const config = ref({
  top_k: 3,
  score_threshold: 0.3,
  search_mode: 'hybrid',
  rerank_enabled: false,
  semantic_weight: 0.7,
  keyword_weight: 0.3,
})
const results = ref<RetrieveResult[]>([])
const loading = ref(false)

async function run() {
  loading.value = true
  try {
    const res = await knowledgeApi.retrieve(props.datasetId, { query: query.value, ...config.value })
    results.value = res.results
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <a-space style="width:100%;margin-bottom:10px">
      <a-input v-model:value="query" placeholder="输入查询进行检索测试" style="width:320px" @press-enter="run" />
      <a-select v-model:value="config.search_mode" style="width:120px">
        <a-select-option value="semantic">语义</a-select-option>
        <a-select-option value="keyword">全文</a-select-option>
        <a-select-option value="hybrid">混合</a-select-option>
      </a-select>
      <a-input-number v-model:value="config.top_k" :min="1" :max="20" addon-before="TopK" />
      <a-checkbox v-model:checked="config.rerank_enabled">Rerank</a-checkbox>
      <a-button type="primary" :loading="loading" @click="run">检索</a-button>
    </a-space>

    <a-list :data-source="results" size="small" bordered>
      <template #renderItem="{ item, index }">
        <a-list-item>
          <a-space direction="vertical" style="width:100%">
            <a-space><a-tag color="blue">#{{ index + 1 }}</a-tag><span>score: {{ item.score }}</span></a-space>
            <div>{{ item.content }}</div>
          </a-space>
        </a-list-item>
      </template>
    </a-list>
  </div>
</template>
