<script setup lang="ts">
import { computed } from 'vue'
import type { NodeRunLog } from '@/types/log'
const props = defineProps<{ log: NodeRunLog }>()
const color: Record<string, string> = {
  succeeded: 'success',
  failed: 'error',
  running: 'processing',
}

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
        <span class="log-meta af-mono">{{ log.node_type }}</span>
        <span class="log-meta af-mono">{{ log.elapsed_ms }}ms</span>
      </a-space>
    </template>

    <div v-if="log.error" class="log-error">错误：{{ log.error }}</div>

    <!-- LLM 真实调试：实际发送的 prompt / system / model + 模型原始返回 -->
    <template v-if="hasLLM">
      <a-divider style="margin: 6px 0" orientation="left" orientation-margin="0">
        <span style="font-size: 12px; color: var(--af-primary)">LLM 真实调试</span>
      </a-divider>
      <div class="kv">
        <span class="k">模型</span><span class="v">{{ dbg.model || '-' }}</span>
        <a-tag v-if="dbg.llm_available === false" color="orange" style="margin-left: 8px"
          >mock 模式（未配置 Key）</a-tag
        >
      </div>
      <div v-if="dbg.system" class="log-label">System：</div>
      <pre v-if="dbg.system" class="log-pre">{{ dbg.system }}</pre>
      <div class="log-label">实际发送的 Prompt：</div>
      <pre class="log-pre prompt">{{ dbg.prompt }}</pre>
      <div class="log-label">模型原始返回：</div>
      <pre class="log-pre resp">{{ dbg.raw_response }}</pre>
      <a-divider style="margin: 6px 0" />
    </template>

    <div class="log-label">输入（解析后）：</div>
    <pre class="log-pre">{{ JSON.stringify(log.inputs, null, 2) }}</pre>
    <div class="log-label">输出：</div>
    <pre class="log-pre">{{ JSON.stringify(log.outputs, null, 2) }}</pre>
  </a-collapse-panel>
</template>

<style scoped>
.log-meta {
  color: var(--af-text-tertiary);
}
.log-error {
  color: var(--af-danger);
  margin-bottom: 6px;
}
.log-label {
  font-size: 12px;
  color: var(--af-text-secondary);
  margin-top: 6px;
}
.log-pre {
  font-family: var(--af-font-mono);
  font-size: 12px;
  line-height: 1.6;
  background: #0f172a;
  color: #e2e8f0;
  padding: 8px;
  border-radius: 6px;
  max-height: 200px;
  overflow: auto;
  margin: 4px 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.log-pre.prompt {
  background: #111c33;
  border: 1px solid #1e3a5f;
}
.log-pre.resp {
  background: #0e1f16;
  border: 1px solid #14532d;
}
.kv {
  font-size: 12px;
}
.kv .k {
  color: var(--af-text-secondary);
  margin-right: 8px;
}
.kv .v {
  font-family: var(--af-font-mono);
}
</style>
