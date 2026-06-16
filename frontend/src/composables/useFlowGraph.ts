import { useVueFlow } from '@vue-flow/core'
import { useWorkflowStore } from '@/stores/workflow'

type Node = any
import { genNodeId } from '@/utils/format'
import type { NodeCatalogItem } from '@/types/node'

// Node add / remove helpers built on top of the workflow store.
export function useFlowGraph() {
  const store = useWorkflowStore()
  const { addNodes, removeNodes, project } = useVueFlow()

  function addNodeFromCatalog(item: NodeCatalogItem, position: { x: number; y: number }) {
    const id = genNodeId(item.type)
    const node: Node = {
      id,
      type: item.type,
      position,
      data: {
        label: item.label,
        icon: item.icon,
        inputs: JSON.parse(JSON.stringify(item.default_io.inputs || [])),
        outputs: JSON.parse(JSON.stringify(item.default_io.outputs || [])),
      },
    }
    store.nodes.push(node)
    return id
  }

  function deleteNode(id: string) {
    store.nodes = store.nodes.filter((n) => n.id !== id)
    store.edges = store.edges.filter((e) => e.source !== id && e.target !== id)
    if (store.selectedNodeId === id) store.selectNode(null)
  }

  return { addNodeFromCatalog, deleteNode, project, addNodes, removeNodes }
}
