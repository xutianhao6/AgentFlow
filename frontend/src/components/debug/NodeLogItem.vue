<script setup lang="ts">
import { computed } from 'vue'
import type { NodeRunLog } from '@/types/log'
const props = defineProps<{ log: NodeRunLog }>()
const color: Record<string, string> = { succeeded: 'green', failed: 'red', running: 'orange' }

// LLM 节点：是否有真实 prompt / 原始返回 可展示
const dbg = computed(() => props.log.debug || {})
const hasLLM = computed(() => !!(dbg.value.prompt || dbg.value.raw_response))
</script>

<template>
  <a-collapse-panel :key="log.node_id + (log.id || '')">
    <template #header>
      <a-space>
        <a-tag :color="color[log.status]">{{ log.status }}</a-tag>
        <strong>{{ log.node_id }}</strong>
        <span style="color:#999">{{ log.node_type }}</span>
        <span style="color:#999">{{ log.elapsed_ms }}ms</span>
      </a-space>
    </template>

    <div v-if="log.error" style="color:#ff4d4f;margin-bottom:6px">错误：{{ log.error }}</div>

    <!-- LLM 真实调试：实际发送的 prompt / system / model + 模型原始返回 -->
    <template v-if="hasLLM">
      <a-divider style="margin:6px 0" orientation="left" orientation-margin="0">
        <span style="font-size:12px;color:#1677ff">LLM 真实调试</span>
      </a-divider>
      <div class="kv">
        <span class="k">模型</span><span class="v">{{ dbg.model || '-' }}</span>
        <a-tag v-if="dbg.llm_available === false" color="orange" style="margin-left:8px">mock 模式（未配置 Key）</a-tag>
      </div>
      <div v-if="dbg.system" style="font-size:12px;color:#888;margin-top:6px">System：</div>
      <pre v-if="dbg.system" class="log-pre">{{ dbg.system }}</pre>
      <div style="font-size:12px;color:#888;margin-top:6px">实际发送的 Prompt：</div>
      <pre class="log-pre prompt">{{ dbg.prompt }}</pre>
      <div style="font-size:12px;color:#888;margin-top:6px">模型原始返回：</div>
      <pre class="log-pre resp">{{ dbg.raw_response }}</pre>
      <a-divider style="margin:6px 0" />
    </template>

    <div style="font-size:12px;color:#888">输入（解析后）：</div>
    <pre class="log-pre">{{ JSON.stringify(log.inputs, null, 2) }}</pre>
    <div style="font-size:12px;color:#888">输出：</div>
    <pre class="log-pre">{{ JSON.stringify(log.outputs, null, 2) }}</pre>
  </a-collapse-panel>
</template>

<style scoped>
.log-pre { background:#f5f5f5; padding:8px; border-radius:4px; font-size:12px; max-height:200px; overflow:auto; margin:4px 0; white-space:pre-wrap; word-break:break-word; }
.log-pre.prompt { background:#f0f7ff; border:1px solid #d6e8ff; }
.log-pre.resp { background:#f6ffed; border:1px solid #d9f7be; }
.kv { font-size:12px; }
.kv .k { color:#888; margin-right:8px; }
.kv .v { font-family:monospace; }
</style>
