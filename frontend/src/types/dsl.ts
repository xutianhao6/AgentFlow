// Workflow DSL — mirrors backend engine/dsl.py
import type { FieldSchema } from './node'

export interface GraphNodeData {
  inputs?: FieldSchema[]
  outputs?: FieldSchema[]
  [key: string]: any
}

export interface GraphNode {
  id: string
  type: string
  data: GraphNodeData
  position?: { x: number; y: number }
}

export interface GraphEdge {
  source: string
  target: string
  sourceHandle?: string | null
  condition?: Record<string, any> | null
}

export interface WorkflowGraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface WorkflowDSL {
  workflow_id?: string
  name: string
  description?: string
  version?: number
  graph: WorkflowGraph
}

export interface WorkflowSummary {
  id: string
  name: string
  description: string
  version: number
  dsl: WorkflowDSL
  created_at?: string
  updated_at?: string
}
