<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()

const ops = ['==', '!=', '>', '>=', '<', '<=', 'contains', 'not_contains', 'is_empty', 'is_not_empty']

const cases = computed(() => props.data.cases || [])

function commit(next: any[]) { emit('update', { cases: next }) }

function addCase() {
  commit([...cases.value, { key: `case_${cases.value.length + 1}`, logic: 'and', conditions: [{ value: '', op: '==', target: '' }] }])
}
function removeCase(i: number) {
  const next = [...cases.value]; next.splice(i, 1); commit(next)
}
function updateCase(i: number, key: string, val: any) {
  const next = JSON.parse(JSON.stringify(cases.value)); next[i][key] = val; commit(next)
}
function addCond(ci: number) {
  const next = JSON.parse(JSON.stringify(cases.value)); next[ci].conditions.push({ value: '', op: '==', target: '' }); commit(next)
}
function updateCond(ci: number, condi: number, key: string, val: any) {
  const next = JSON.parse(JSON.stringify(cases.value)); next[ci].conditions[condi][key] = val; commit(next)
}
</script>

<template>
  <a-form layout="vertical">
    <div v-for="(c, ci) in cases" :key="ci" style="border:1px solid #f0f0f0;border-radius:6px;padding:8px;margin-bottom:8px">
      <a-space style="margin-bottom:6px">
        <a-input :value="c.key" placeholder="分支 key" style="width:110px" @input="(e:any)=>updateCase(ci,'key',e.target.value)" />
        <a-select :value="c.logic" style="width:80px" @change="(v:any)=>updateCase(ci,'logic',v)">
          <a-select-option value="and">且</a-select-option>
          <a-select-option value="or">或</a-select-option>
        </a-select>
        <a style="color:#ff4d4f" @click="removeCase(ci)">删除分支</a>
      </a-space>
      <div v-for="(cond, condi) in c.conditions" :key="condi" style="margin-bottom:4px">
        <a-space>
          <a-input :value="cond.value" placeholder="{{node.field}}" style="width:140px" @input="(e:any)=>updateCond(ci,condi,'value',e.target.value)" />
          <a-select :value="cond.op" style="width:110px" @change="(v:any)=>updateCond(ci,condi,'op',v)">
            <a-select-option v-for="o in ops" :key="o" :value="o">{{ o }}</a-select-option>
          </a-select>
          <a-input :value="cond.target" placeholder="比较值" style="width:100px" @input="(e:any)=>updateCond(ci,condi,'target',e.target.value)" />
        </a-space>
      </div>
      <a-button size="small" @click="addCond(ci)">+ 条件</a-button>
    </div>
    <a-button @click="addCase">+ 添加分支</a-button>
    <a-form-item label="ELSE 分支 key" style="margin-top:8px">
      <a-input :value="data.else_key || 'else'" @input="(e:any)=>emit('update',{else_key:e.target.value})" />
    </a-form-item>
  </a-form>
</template>
