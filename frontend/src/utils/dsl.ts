// Bidirectional conversion between Vue Flow nodes/edges and the backend DSL graph.
import type { WorkflowDSL, WorkflowGraph } from '@/types/dsl'

type Node = any
type Edge = any

// Vue Flow -> DSL
export function flowToDsl(nodes: Node[], edges: Edge[]): WorkflowGraph {
  return {
    nodes: nodes.map((n) => {
      const { _status, ...data } = n.data || {}
      return {
        id: n.id,
        type: (n.type as string) || 'default',
        data,
        position: n.position ? { x: n.position.x, y: n.position.y } : undefined,
      }
    }),
    edges: edges.map((e) => ({
      source: e.source,
      target: e.target,
      sourceHandle: e.sourceHandle ?? null,
    })),
  }
}

// DSL -> Vue Flow
export function dslToFlow(dsl: WorkflowDSL): { nodes: Node[]; edges: Edge[] } {
  const graph = dsl.graph || { nodes: [], edges: [] }
  const nodes: Node[] = graph.nodes.map((n, i) => ({
    id: n.id,
    type: n.type,
    position: n.position || { x: 80 + i * 220, y: 160 },
    data: { ...n.data },
  }))
  const edges: Edge[] = graph.edges.map((e, i) => ({
    id: `e_${e.source}_${e.target}_${i}`,
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceHandle ?? undefined,
    type: 'custom',
    label: e.sourceHandle || undefined,
  }))
  return { nodes, edges }
}
