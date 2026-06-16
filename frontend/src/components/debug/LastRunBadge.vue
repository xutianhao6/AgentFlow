<script setup lang="ts">
import { useDebugStore } from '@/stores/debug'
import { computed } from 'vue'

const props = defineProps<{ nodeId: string }>()
const debug = useDebugStore()
const last = computed(() => debug.lastRunByNode[props.nodeId])
</script>

<template>
  <a-tooltip v-if="last" title="Last Run（最近一次成功执行）">
    <a-tag color="green">✓ {{ last.elapsed_ms }}ms</a-tag>
  </a-tooltip>
</template>
