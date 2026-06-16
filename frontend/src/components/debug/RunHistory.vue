<script setup lang="ts">
import { ref, watch } from 'vue'
import { logsApi } from '@/api/logs'
import { useWorkflowStore } from '@/stores/workflow'
import type { WorkflowRun, NodeRunLog } from '@/types/log'
import { formatTime } from '@/utils/format'
import NodeLogItem from './NodeLogItem.vue'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [boolean] }>()
const store = useWorkflowStore()

const runs = ref<WorkflowRun[]>([])
const detailLogs = ref<NodeRunLog[]>([])
const activeRun = ref<string | null>(null)

watch(
  () => props.open,
  async (v) => {
    if (v && store.workflowId) {
      const res = await logsApi.listRuns(store.workflowId)
      runs.value = res.items
    }
  },
)

async function openDetail(runId: string) {
  activeRun.value = runId
  const res = await logsApi.runDetail(runId)
  detailLogs.value = res.node_logs
}
</script>

<template>
  <a-drawer :open="open" title="运行历史 (Run History)" placement="right" :width="520" @close="emit('update:open', false)">
    <a-list :data-source="runs" size="small">
      <template #renderItem="{ item }">
        <a-list-item>
          <a-space direction="vertical" style="width:100%">
            <a-space>
              <a-tag :color="item.status === 'succeeded' ? 'success' : 'error'">{{ item.status }}</a-tag>
              <span class="af-mono af-dim">{{ item.mode }}</span>
              <span class="af-mono af-dim">{{ item.total_ms }}ms</span>
              <span class="af-dim">{{ formatTime(item.created_at) }}</span>
              <a @click="openDetail(item.run_id)">查看轨迹</a>
            </a-space>
            <a-collapse v-if="activeRun === item.run_id && detailLogs.length">
              <NodeLogItem v-for="(log, i) in detailLogs" :key="i" :log="log" />
            </a-collapse>
          </a-space>
        </a-list-item>
      </template>
    </a-list>
  </a-drawer>
</template>
