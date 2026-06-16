import { message } from 'ant-design-vue'
import { useDebugStore } from '@/stores/debug'
import { useWorkflowStore } from '@/stores/workflow'
import { postSSE } from '@/utils/sse'

// Debug run with SSE: streams node status into the canvas + debug panel.
export function useDebugRun() {
  const debug = useDebugStore()
  const wf = useWorkflowStore()

  async function run(inputs: Record<string, any>) {
    await wf.save()
    debug.reset()
    debug.running = true
    wf.clearStatuses()

    try {
      await postSSE(`/workflows/${wf.workflowId}/debug`, { inputs }, (evt) => {
        if (evt.event === 'node_started') {
          wf.setNodeStatus(evt.data.node_id, 'running')
        } else if (evt.event === 'node_finished') {
          const log = evt.data
          debug.pushLog(log)
          wf.setNodeStatus(log.node_id, log.status)
        } else if (evt.event === 'node_failed') {
          wf.setNodeStatus(evt.data.node_id, 'failed')
        } else if (evt.event === 'run_finished') {
          debug.finalResult = evt.data
        } else if (evt.event === 'error') {
          message.error('校验失败: ' + (evt.data.errors || []).join('; '))
        }
      })
    } finally {
      debug.running = false
    }
  }

  return { run }
}
