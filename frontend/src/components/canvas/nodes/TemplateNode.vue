<script setup lang="ts">
import BaseNode from './BaseNode.vue'
const props = defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" type="template" label="模板转换" :selected="selected" />
</template>
