<script setup lang="ts">
import BaseNode from './BaseNode.vue'
const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" label="代码执行" icon="💻" :selected="selected" />
</template>
