import request from './request'
import type { Dataset, KnowledgeDocument, RetrieveResult } from '@/types/knowledge'

export const knowledgeApi = {
  listDatasets: (): Promise<{ items: Dataset[] }> => request.get('/datasets'),

  createDataset: (name: string, index_method: string, description = ''): Promise<Dataset> =>
    request.post('/datasets', { name, index_method, description }),

  getDataset: (id: string): Promise<Dataset> => request.get(`/datasets/${id}`),

  removeDataset: (id: string): Promise<{ deleted: boolean }> => request.delete(`/datasets/${id}`),

  listDocuments: (id: string): Promise<{ items: KnowledgeDocument[] }> =>
    request.get(`/datasets/${id}/documents`),

  uploadDocument: (id: string, file: File, chunk_strategy: string): Promise<KnowledgeDocument> => {
    const form = new FormData()
    form.append('file', file)
    form.append('chunk_strategy', chunk_strategy)
    return request.post(`/datasets/${id}/documents`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  removeDocument: (id: string, docId: string): Promise<{ deleted: boolean }> =>
    request.delete(`/datasets/${id}/documents/${docId}`),

  retrieve: (id: string, config: Record<string, any>): Promise<{ results: RetrieveResult[] }> =>
    request.post(`/datasets/${id}/retrieve`, config),
}
