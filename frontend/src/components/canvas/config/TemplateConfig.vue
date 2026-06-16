<script setup lang="ts">
import IOSchemaEditor from './IOSchemaEditor.vue'
const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="Jinja2 模板（变量名取自输入字段）">
      <a-textarea :value="data.template" :rows="5" @input="(e:any)=>set('template', e.target.value)" />
    </a-form-item>
    <IOSchemaEditor :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
  </a-form>
</template>
