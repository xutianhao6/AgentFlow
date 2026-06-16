// Debug logs — mirrors backend schemas/log.py
export interface LLMDebug {
  model?: string
  system?: string
  prompt?: string
  raw_response?: string
  resolved_inputs?: Record<string, any>
  llm_available?: boolean
}

export interface NodeRunLog {
  id?: number
  run_id: string
  workflow_id?: string
  node_id: string
  node_type: string
  status: 'running' | 'succeeded' | 'failed'
  inputs: Record<string, any>
  outputs: Record<string, any>
  debug?: LLMDebug & Record<string, any>
  error?: string | null
  elapsed_ms: number
  created_at?: string
}

export interface WorkflowRun {
  run_id: string
  workflow_id: string
  mode: string
  status: string
  inputs: Record<string, any>
  outputs: Record<string, any>
  error?: string | null
  total_ms: number
  created_at?: string
}
