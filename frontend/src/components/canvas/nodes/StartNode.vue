<script setup lang="ts">
import BaseNode from './BaseNode.vue'
defineProps<{ id: string; data: Record<string, any>; selected?: boolean }>()
</script>
<template>
  <BaseNode :id="id" :data="data" label="开始" icon="▶" :selected="selected" no-target>
    <span style="color:#888">入参：{{ (data.outputs || []).map((o:any)=>o.name).join(', ') || '未定义' }}</span>
  </BaseNode>
</template>
