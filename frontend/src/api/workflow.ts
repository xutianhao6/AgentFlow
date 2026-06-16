import request from './request'
import type { WorkflowDSL, WorkflowSummary } from '@/types/dsl'
import type { NodeCatalogItem } from '@/types/node'

export const workflowApi = {
  list: (): Promise<{ items: WorkflowSummary[] }> => request.get('/workflows'),

  get: (id: string): Promise<WorkflowSummary> => request.get(`/workflows/${id}`),

  create: (name: string, description = ''): Promise<WorkflowSummary> =>
    request.post('/workflows', { name, description }),

  update: (id: string, dsl: WorkflowDSL, name?: string, description?: string): Promise<WorkflowSummary> =>
    request.put(`/workflows/${id}`, { dsl, name, description }),

  remove: (id: string): Promise<{ deleted: boolean }> => request.delete(`/workflows/${id}`),

  validate: (dsl: WorkflowDSL): Promise<{ valid: boolean; errors: string[] }> =>
    request.post('/workflows/validate', { dsl }),

  run: (id: string, inputs: Record<string, any>): Promise<any> =>
    request.post(`/workflows/${id}/run`, { inputs }),

  runSingleNode: (id: string, nodeId: string, inputs: Record<string, any>): Promise<any> =>
    request.post(`/workflows/${id}/nodes/${nodeId}/run`, { inputs }),

  nodeCatalog: (): Promise<{ nodes: NodeCatalogItem[] }> => request.get('/workflows/node-catalog'),

  codeTemplate: (language: string): Promise<{ language: string; template: string }> =>
    request.get('/workflows/code-template', { params: { language } }),

  // marketplace
  exportDsl: (id: string): Promise<any> => request.get(`/workflows/${id}/export`),
  publish: (id: string, category = '通用'): Promise<any> =>
    request.post(`/workflows/${id}/publish`, { category }),
}
