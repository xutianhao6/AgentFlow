export interface Dataset {
  id: string
  name: string
  description: string
  index_method: 'high_quality' | 'economy'
  embedding_model: string
  created_at?: string
}

export interface KnowledgeDocument {
  id: string
  dataset_id: string
  name: string
  chunk_strategy: 'general' | 'parent_child' | 'qa'
  status: 'pending' | 'indexing' | 'done' | 'failed'
  chunk_count: number
  created_at?: string
}

export interface RetrieveResult {
  content: string
  score: number
  metadata: Record<string, any>
}

export interface RetrievalConfig {
  query: string
  top_k: number
  score_threshold: number
  search_mode: 'semantic' | 'keyword' | 'hybrid'
  rerank_enabled: boolean
  semantic_weight: number
  keyword_weight: number
}
