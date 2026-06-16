<script setup lang="ts">
import { useDebugStore } from '@/stores/debug'
import NodeLogItem from './NodeLogItem.vue'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [boolean] }>()
const debug = useDebugStore()
</script>

<template>
  <a-drawer
    :open="open"
    title="调试日志（测试态）"
    placement="bottom"
    :height="360"
    @close="emit('update:open', false)"
  >
    <a-spin :spinning="debug.running">
      <div v-if="debug.finalResult" style="margin-bottom:12px">
        <a-tag :color="debug.finalResult.status === 'succeeded' ? 'green' : 'red'">
          {{ debug.finalResult.status }}
        </a-tag>
        <span style="color:#999">总耗时 {{ debug.finalResult.total_ms }}ms</span>
        <pre class="result-pre">最终输出：{{ JSON.stringify(debug.finalResult.outputs, null, 2) }}</pre>
      </div>

      <a-collapse v-if="debug.logs.length">
        <NodeLogItem v-for="(log, i) in debug.logs" :key="i" :log="log" />
      </a-collapse>
      <div v-else style="color:#999">点击「调试运行」后，每个节点的输入/输出/状态/耗时会显示在这里。</div>
    </a-spin>
  </a-drawer>
</template>

<style scoped>
.result-pre { background:#f5f5f5; padding:8px; border-radius:4px; font-size:12px; max-height:120px; overflow:auto; }
</style>
