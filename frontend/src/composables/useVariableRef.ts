import { computed } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'

export interface VarRef {
  nodeId: string
  field: string
  label: string
  value: string // {{node.field}}
  type: string
}

// Compute, for a given node, the variable refs it is ALLOWED to bind to:
// only the outputs of its UPSTREAM (transitively connected) nodes — enforcing
// real edge-based binding (a node can't reference a sibling/downstream node).
export function useVariableRef(nodeId?: () => string | null) {
  const store = useWorkflowStore()

  // adjacency: target -> list of sources (reverse edges)
  const upstreamOutputs = computed<VarRef[]>(() => {
    const id = nodeId?.()
    if (!id) {
      // no specific node: expose everything (used by generic editors)
      return collectOutputs(store.nodes)
    }

    // BFS backwards over edges to find all upstream node ids
    const incoming: Record<string, string[]> = {}
    for (const e of store.edges) {
      ;(incoming[e.target] = incoming[e.target] || []).push(e.source)
    }
    const visited = new Set<string>()
    const queue = [...(incoming[id] || [])]
    while (queue.length) {
      const cur = queue.shift()!
      if (visited.has(cur)) continue
      visited.add(cur)
      for (const src of incoming[cur] || []) queue.push(src)
    }
    const upstreamNodes = store.nodes.filter((n) => visited.has(n.id))
    return collectOutputs(upstreamNodes)
  })

  // direct (one-hop) upstream nodes — used for auto-binding suggestions
  const directUpstream = computed(() => {
    const id = nodeId?.()
    if (!id) return [] as any[]
    const sources = store.edges.filter((e) => e.target === id).map((e) => e.source)
    return store.nodes.filter((n) => sources.includes(n.id))
  })

  function validateRef(expr: string): boolean {
    const m = /\{\{\s*(\w+)\.([\w.]+)\s*\}\}/.exec(expr)
    if (!m) return true
    return upstreamOutputs.value.some((r) => r.nodeId === m[1] && r.field === m[2])
  }

  return { availableRefs: upstreamOutputs, directUpstream, validateRef }
}

function collectOutputs(nodes: any[]): VarRef[] {
  const refs: VarRef[] = []
  for (const n of nodes) {
    const outputs = (n.data?.outputs || []) as { name: string; type: string }[]
    for (const out of outputs) {
      refs.push({
        nodeId: n.id,
        field: out.name,
        label: `${n.data?.label || n.type}.${out.name}`,
        value: `{{${n.id}.${out.name}}}`,
        type: out.type,
      })
    }
  }
  return refs
}

// Type compatibility (mirrors backend engine/validator.py _compatible)
export function typeCompatible(srcType: string, dstType: string): boolean {
  if (!srcType || !dstType) return true
  if (dstType === 'object' || srcType === 'object') return true
  if (srcType === dstType) return true
  if (srcType.startsWith('array') && dstType.startsWith('array')) return true
  return false
}
