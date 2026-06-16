import { computed } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'

// Read/write the currently selected node's config.
export function useNodeConfig() {
  const store = useWorkflowStore()

  const selectedNode = computed(() =>
    store.nodes.find((n) => n.id === store.selectedNodeId) || null,
  )

  function update(data: Record<string, any>) {
    if (store.selectedNodeId) store.updateNodeData(store.selectedNodeId, data)
  }

  return { selectedNode, update }
}
