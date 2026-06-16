<script setup lang="ts">
// Fallback config: just edit IO schema (used by start/end/iteration/aggregator).
import IOSchemaEditor from './IOSchemaEditor.vue'
const props = defineProps<{ data: Record<string, any>; nodeType: string }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }

const isStart = props.nodeType === 'start'
const isEnd = props.nodeType === 'end'
const showInputs = !isStart
const showOutputs = !isEnd
</script>

<template>
  <a-form layout="vertical">
    <!-- 开始节点：定义工作流入参（作为下游可引用的输出） -->
    <a-alert
      v-if="isStart"
      type="info"
      show-icon
      message="开始节点：定义工作流的入参。这些字段会作为输出，供下游节点绑定 {{开始节点.字段}}。"
      style="margin-bottom:12px"
    />
    <!-- 结束节点：定义工作流出参（从上游取值） -->
    <a-alert
      v-if="isEnd"
      type="info"
      show-icon
      message="结束节点：定义工作流的最终输出参数。每个参数从上游节点取值（绑定 {{节点.字段}}），运行结束后作为工作流结果返回。"
      style="margin-bottom:12px"
    />

    <a-form-item v-if="nodeType === 'iteration'" label="提取字段 (item_field)">
      <a-input :value="data.item_field" @input="(e:any)=>set('item_field', e.target.value)" />
    </a-form-item>

    <!-- start 节点：把 outputs 当成“入参”展示 -->
    <IOSchemaEditor
      v-if="isStart"
      :model-value="data.outputs || []"
      kind="outputs"
      title="工作流入参"
      @update:model-value="(v)=>set('outputs', v)"
    />

    <!-- end 节点：技术上是 inputs（绑定上游），但展示为“工作流输出参数” -->
    <IOSchemaEditor
      v-else-if="isEnd"
      :model-value="data.inputs || []"
      kind="inputs"
      title="工作流输出参数（从上游取值）"
      @update:model-value="(v)=>set('inputs', v)"
    />

    <!-- 其它通用节点：标准 inputs + outputs -->
    <template v-else>
      <IOSchemaEditor v-if="showInputs" :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />
      <IOSchemaEditor v-if="showOutputs" :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
    </template>
  </a-form>
</template>
