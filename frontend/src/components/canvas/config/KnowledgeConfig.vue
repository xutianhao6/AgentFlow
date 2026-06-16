<script setup lang="ts">
import { onMounted, ref } from 'vue'
import IOSchemaEditor from './IOSchemaEditor.vue'
import { knowledgeApi } from '@/api/knowledge'
import type { Dataset } from '@/types/knowledge'

const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }

const datasets = ref<Dataset[]>([])
onMounted(async () => {
  const res = await knowledgeApi.listDatasets()
  datasets.value = res.items
})
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="选择知识库">
      <a-select mode="multiple" :value="data.dataset_ids || []" @change="(v:any)=>set('dataset_ids', v)">
        <a-select-option v-for="d in datasets" :key="d.id" :value="d.id">{{ d.name }}</a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item label="检索方式">
      <a-radio-group :value="data.search_mode || 'hybrid'" @change="(e:any)=>set('search_mode', e.target.value)">
        <a-radio-button value="semantic">语义</a-radio-button>
        <a-radio-button value="keyword">全文</a-radio-button>
        <a-radio-button value="hybrid">混合</a-radio-button>
      </a-radio-group>
    </a-form-item>
    <a-form-item label="Top K">
      <a-input-number :value="data.top_k ?? 3" :min="1" :max="20" @change="(v:any)=>set('top_k', v)" />
    </a-form-item>
    <a-form-item label="相似度阈值">
      <a-input-number :value="data.score_threshold ?? 0.5" :min="0" :max="1" :step="0.05" @change="(v:any)=>set('score_threshold', v)" />
    </a-form-item>
    <a-form-item>
      <a-checkbox :checked="data.rerank_enabled" @change="(e:any)=>set('rerank_enabled', e.target.checked)">启用 Rerank 重排</a-checkbox>
    </a-form-item>
    <IOSchemaEditor :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
  </a-form>
</template>
