<script setup lang="ts">
import BaseNode from './BaseNode.vue'
const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" label="LLM" icon="🤖" :selected="selected" />
</template>
