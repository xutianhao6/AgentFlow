import request from './request'
import type { NodeRunLog, WorkflowRun } from '@/types/log'

export const logsApi = {
  listRuns: (wfId: string): Promise<{ items: WorkflowRun[] }> =>
    request.get(`/workflows/${wfId}/runs`),

  runDetail: (runId: string): Promise<{ run: WorkflowRun; node_logs: NodeRunLog[] }> =>
    request.get(`/runs/${runId}`),

  nodeLastRun: (runId: string, nodeId: string): Promise<NodeRunLog> =>
    request.get(`/runs/${runId}/nodes/${nodeId}`),
}
