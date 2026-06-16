<script setup lang="ts">
import IOSchemaEditor from './IOSchemaEditor.vue'
const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="方法">
      <a-select :value="data.method || 'GET'" @change="(v:any)=>set('method', v)">
        <a-select-option v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m" :value="m">{{ m }}</a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item label="URL（支持 {{node.field}}）">
      <a-input :value="data.url" @input="(e:any)=>set('url', e.target.value)" />
    </a-form-item>
    <a-form-item label="Body（可选）">
      <a-textarea :value="data.body" :rows="3" @input="(e:any)=>set('body', e.target.value)" />
    </a-form-item>
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
  </a-form>
</template>
