<script setup lang="ts">
import { ref, watch } from 'vue'
import CodeEditor from '@/components/code-editor/CodeEditor.vue'
import LangSelectModal from '@/components/code-editor/LangSelectModal.vue'
import IOSchemaEditor from './IOSchemaEditor.vue'
import { getTemplate } from '@/components/code-editor/templates'

const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }

const langModal = ref(false)

// Prompt for language the first time a code node has no language set.
watch(
  () => props.data,
  (d) => {
    if (!d.language) langModal.value = true
  },
  { immediate: true },
)

function onLang(lang: string) {
  emit('update', { language: lang, code: getTemplate(lang) })
}
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="语言">
      <a-space>
        <a-tag color="blue">{{ data.language || '未选择' }}</a-tag>
        <a @click="langModal = true">切换语言（重置模板）</a>
      </a-space>
    </a-form-item>
    <a-form-item label="代码（只改核心逻辑）">
      <CodeEditor :model-value="data.code || ''" :language="data.language" @update:model-value="(v)=>set('code', v)" />
    </a-form-item>
    <IOSchemaEditor :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />

    <LangSelectModal v-model:open="langModal" @select="onLang" />
  </a-form>
</template>
