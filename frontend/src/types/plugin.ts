export type PluginType = 'tool' | 'model' | 'extension' | 'agent_strategy'

export interface Plugin {
  id: string
  name: string
  type: PluginType
  version: string
  description: string
  icon: string
  author: string
  manifest: Record<string, any>
  downloads: number
  status: string
  installed: boolean
  created_at?: string
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  dependencies: { plugins?: string[]; datasets?: string[] }
  author: string
  downloads: number
  category: string
  created_at?: string
}
