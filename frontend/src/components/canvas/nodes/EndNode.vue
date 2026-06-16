<script setup lang="ts">
import BaseNode from './BaseNode.vue'
defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" type="end" label="结束" :selected="selected" no-source>
    <span>出参：{{ (data.inputs || []).map((o: any) => o.name).join(', ') || '未定义' }}</span>
  </BaseNode>
</template>
