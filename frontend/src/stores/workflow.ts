import { defineStore } from 'pinia'
import { ref } from 'vue'
import { workflowApi } from '@/api/workflow'
import type { NodeCatalogItem } from '@/types/node'
import type { WorkflowDSL } from '@/types/dsl'
import { flowToDsl, dslToFlow } from '@/utils/dsl'

// Vue Flow Node/Edge are heavily generic; use loose types in the store to avoid
// excessively-deep type instantiation while keeping runtime behaviour identical.
type Node = any
type Edge = any

export const useWorkflowStore = defineStore('workflow', () => {
  const workflowId = ref<string>('')
  const name = ref<string>('未命名工作流')
  const description = ref<string>('')
  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])
  const selectedNodeId = ref<string | null>(null)
  const catalog = ref<NodeCatalogItem[]>([])

  async function loadCatalog() {
    if (catalog.value.length) return
    const res = await workflowApi.nodeCatalog()
    catalog.value = res.nodes
  }

  async function load(id: string) {
    const wf = await workflowApi.get(id)
    workflowId.value = wf.id
    name.value = wf.name
    description.value = wf.description
    const { nodes: n, edges: e } = dslToFlow(wf.dsl)
    nodes.value = n
    edges.value = e
  }

  function toDsl(): WorkflowDSL {
    return {
      workflow_id: workflowId.value,
      name: name.value,
      description: description.value,
      graph: flowToDsl(nodes.value, edges.value),
    }
  }

  async function save() {
    await workflowApi.update(workflowId.value, toDsl(), name.value, description.value)
  }

  function selectNode(id: string | null) {
    selectedNodeId.value = id
  }

  function updateNodeData(id: string, data: Record<string, any>) {
    const node = nodes.value.find((n) => n.id === id)
    if (node) node.data = { ...node.data, ...data }
  }

  function setNodeStatus(id: string, status: string) {
    const node = nodes.value.find((n) => n.id === id)
    if (node) node.data = { ...node.data, _status: status }
  }

  function clearStatuses() {
    nodes.value.forEach((n) => {
      if (n.data) n.data._status = undefined
    })
  }

  return {
    workflowId, name, description, nodes, edges, selectedNodeId, catalog,
    loadCatalog, load, toDsl, save, selectNode, updateNodeData, setNodeStatus, clearStatuses,
  }
})
