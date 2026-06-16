<script setup lang="ts">
import BaseNode from './BaseNode.vue'
const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" label="HTTP 请求" icon="🌐" :selected="selected" />
</template>
