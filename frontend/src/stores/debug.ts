import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NodeRunLog, WorkflowRun } from '@/types/log'

export const useDebugStore = defineStore('debug', () => {
  const running = ref(false)
  const logs = ref<NodeRunLog[]>([])
  const lastRunByNode = ref<Record<string, NodeRunLog>>({})
  const finalResult = ref<any>(null)
  const history = ref<WorkflowRun[]>([])

  function reset() {
    logs.value = []
    finalResult.value = null
  }

  function pushLog(log: NodeRunLog) {
    logs.value.push(log)
    if (log.status === 'succeeded') {
      lastRunByNode.value[log.node_id] = log
    }
  }

  return { running, logs, lastRunByNode, finalResult, history, reset, pushLog }
})
