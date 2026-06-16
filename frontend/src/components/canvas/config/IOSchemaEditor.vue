<script setup lang="ts">
import { computed } from 'vue'
import type { FieldSchema, VarType } from '@/types/node'
import { useVariableRef, typeCompatible } from '@/composables/useVariableRef'
import { useWorkflowStore } from '@/stores/workflow'

const props = defineProps<{
  modelValue: FieldSchema[]
  kind: 'inputs' | 'outputs'
  nodeId?: string // the node these fields belong to (enables upstream binding)
  title?: string // 覆盖默认标题（如 end 节点显示“工作流输出参数”）
}>()
const emit = defineEmits<{ 'update:modelValue': [FieldSchema[]] }>()

const store = useWorkflowStore()
const { availableRefs } = useVariableRef(() => props.nodeId ?? store.selectedNodeId)

const types: VarType[] = ['string', 'number', 'boolean', 'object', 'array[string]', 'array[object]', 'file']

const fields = computed({
  get: () => props.modelValue || [],
  set: (v) => emit('update:modelValue', v),
})

// For an input of a given type, which upstream outputs can it bind to?
function optionsFor(fieldType: string) {
  return availableRefs.value.map((r) => ({
    value: r.value,
    label: `${r.label}  ·  ${r.type}`,
    disabled: !typeCompatible(r.type, fieldType),
  }))
}

// Is the current bound value valid (references an existing upstream output)?
function bindingState(f: FieldSchema): 'ok' | 'invalid' | 'incompatible' | 'none' {
  if (!f.value) return 'none'
  const ref = availableRefs.value.find((r) => r.value === f.value)
  if (!ref) {
    // could be a literal or a stale reference
    const isRef = /\{\{.*\}\}/.test(f.value)
    return isRef ? 'invalid' : 'ok'
  }
  return typeCompatible(ref.type, f.type) ? 'ok' : 'incompatible'
}

function add() {
  fields.value = [...fields.value, { name: `field_${fields.value.length + 1}`, type: 'string' }]
}
function remove(i: number) {
  const next = [...fields.value]
  next.splice(i, 1)
  fields.value = next
}
function update(i: number, key: keyof FieldSchema, val: any) {
  const next = [...fields.value]
  ;(next[i] as any)[key] = val
  fields.value = next
}
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <strong>{{ title || (kind === 'inputs' ? '输入字段（绑定上游输出）' : '输出字段') }}</strong>
      <a-button size="small" @click="add">+ 添加</a-button>
    </div>

    <div v-for="(f, i) in fields" :key="i" style="border:1px solid #f0f0f0;border-radius:6px;padding:8px;margin-bottom:6px">
      <a-space style="width:100%" direction="vertical" size="small">
        <a-space>
          <a-input :value="f.name" placeholder="字段名" style="width:120px" @input="(e:any)=>update(i,'name',e.target.value)" />
          <a-select :value="f.type" style="width:120px" @change="(v:any)=>update(i,'type',v)">
            <a-select-option v-for="t in types" :key="t" :value="t">{{ t }}</a-select-option>
          </a-select>
          <a-checkbox :checked="f.required" @change="(e:any)=>update(i,'required',e.target.checked)">必填</a-checkbox>
          <a @click="remove(i)" style="color:#ff4d4f">删除</a>
        </a-space>

        <template v-if="kind === 'inputs'">
          <!-- 绑定上游输出：下拉选择 = 连线传值，仅显示上游节点的输出，类型不兼容的禁用 -->
          <a-select
            :value="f.value"
            :options="optionsFor(f.type)"
            placeholder="绑定上游节点输出 {{node.field}}"
            style="width:100%"
            allow-clear
            show-search
            :filter-option="(input:string, opt:any)=>opt.label.toLowerCase().includes(input.toLowerCase())"
            @change="(v:any)=>update(i,'value',v)"
          />
          <div v-if="bindingState(f) === 'invalid'" style="color:#ff4d4f;font-size:12px">
            ⚠ 引用的上游字段不存在（请检查连线或重新绑定）
          </div>
          <div v-else-if="bindingState(f) === 'incompatible'" style="color:#fa8c16;font-size:12px">
            ⚠ 类型不兼容：上游输出与本字段类型不一致
          </div>
          <div v-else-if="bindingState(f) === 'none' && f.required" style="color:#bfbfbf;font-size:12px">
            必填字段，请绑定上游输出或填默认值
          </div>
          <!-- 也允许直接填字面量/手写表达式 -->
          <a-input
            :value="typeof f.value === 'string' && !/\{\{.*\}\}/.test(f.value) ? f.value : ''"
            placeholder="或填字面量/默认值"
            size="small"
            @input="(e:any)=>update(i,'value', e.target.value)"
          />
        </template>
      </a-space>
    </div>
    <div v-if="kind === 'inputs' && !availableRefs.length" style="color:#bfbfbf;font-size:12px">
      暂无可绑定的上游输出——请先把上游节点连线到本节点。
    </div>
  </div>
</template>
