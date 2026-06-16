<script setup lang="ts">
import BaseNode from './BaseNode.vue'
defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" label="结束" icon="⏹" :selected="selected" no-source>
    <span style="color:#888">出参：{{ (data.inputs || []).map((o:any)=>o.name).join(', ') || '未定义' }}</span>
  </BaseNode>
</template>
