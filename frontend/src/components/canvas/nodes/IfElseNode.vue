<script setup lang="ts">
import { computed } from 'vue'
import BaseNode from './BaseNode.vue'

const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()

const branches = computed(() => {
  const keys = (props.data.cases || []).map((c: any) => c.key)
  keys.push(props.data.else_key || 'else')
  return keys
})
</script>
<template>
  <BaseNode
    :id="id"
    :data="data"
    type="if_else"
    label="条件分支"
    :selected="selected"
    :branches="branches"
  >
    <div v-for="b in branches" :key="b" class="af-mono" style="font-size: 11px">↳ {{ b }}</div>
  </BaseNode>
</template>
