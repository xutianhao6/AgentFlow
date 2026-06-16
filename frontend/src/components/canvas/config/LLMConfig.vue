<script setup lang="ts">
import { computed } from 'vue'
import IOSchemaEditor from './IOSchemaEditor.vue'
import VarTextarea from './VarTextarea.vue'
const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }
const selfInputs = computed(() => (props.data.inputs || []).map((f: any) => ({ name: f.name, type: f.type })))
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="模型">
      <a-select :value="data.model || 'Qwen/Qwen2.5-7B-Instruct'" @change="(v:any)=>set('model', v)">
        <a-select-option value="Qwen/Qwen2.5-7B-Instruct">Qwen2.5-7B-Instruct</a-select-option>
        <a-select-option value="Qwen/Qwen2.5-72B-Instruct">Qwen2.5-72B-Instruct</a-select-option>
        <a-select-option value="deepseek-ai/DeepSeek-V3">DeepSeek-V3</a-select-option>
        <a-select-option value="THUDM/glm-4-9b-chat">GLM-4-9B-Chat</a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item label="System (可选)">
      <VarTextarea :model-value="data.system || ''" :rows="2" :self-inputs="selfInputs"
        placeholder="系统提示词，可输入 @ 或 {{ 插入变量" @update:model-value="(v)=>set('system', v)" />
    </a-form-item>

    <!-- 输入字段：绑定上游节点输出（query / context …） -->
    <IOSchemaEditor :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />

    <a-form-item label="Prompt（可留空：留空时用上面绑定的 query / context 自动生成）">
      <VarTextarea
        :model-value="data.prompt || ''"
        :rows="5"
        :self-inputs="selfInputs"
        placeholder="输入 @ 或 { / {{ 可弹出变量选择；留空则自动用绑定的输入"
        @update:model-value="(v)=>set('prompt', v)"
      />
      <div style="color:#999;font-size:12px;margin-top:4px">
        💡 输入 <b>@</b> 或 <b>{</b> 会弹出变量列表，选中即插入。
      </div>
    </a-form-item>
    <a-form-item label="Temperature">
      <a-input-number :value="data.temperature ?? 0.7" :min="0" :max="2" :step="0.1" @change="(v:any)=>set('temperature', v)" />
    </a-form-item>
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
  </a-form>
</template>
