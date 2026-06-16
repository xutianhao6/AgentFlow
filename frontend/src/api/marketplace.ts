import request from './request'
import type { WorkflowTemplate } from '@/types/plugin'

export const marketplaceApi = {
  list: (category?: string, keyword?: string): Promise<{ items: WorkflowTemplate[] }> =>
    request.get('/workflows/market', { params: { category, keyword } }),

  import: (template_id: string): Promise<{ workflow_id: string; name: string }> =>
    request.post('/workflows/import', { template_id }),
}
