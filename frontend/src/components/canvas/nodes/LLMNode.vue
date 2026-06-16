<script setup lang="ts">
import BaseNode from './BaseNode.vue'
const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" type="llm" label="LLM" :selected="selected" />
</template>
