<script setup lang="ts">
import { markRaw, onMounted, onUnmounted } from 'vue'
import { VueFlow, useVueFlow, type Connection } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import MiniMap from './MiniMap.vue'

import { useWorkflowStore } from '@/stores/workflow'
import { useFlowGraph } from '@/composables/useFlowGraph'
import { useCanvasShortcuts } from '@/composables/useCanvasShortcuts'

import StartNode from './nodes/StartNode.vue'
import EndNode from './nodes/EndNode.vue'
import LLMNode from './nodes/LLMNode.vue'
import KnowledgeNode from './nodes/KnowledgeNode.vue'
import IfElseNode from './nodes/IfElseNode.vue'
import IterationNode from './nodes/IterationNode.vue'
import HttpNode from './nodes/HttpNode.vue'
import ToolNode from './nodes/ToolNode.vue'
import CodeNode from './nodes/CodeNode.vue'
import TemplateNode from './nodes/TemplateNode.vue'
import AggregatorNode from './nodes/AggregatorNode.vue'
import CustomEdge from './edges/CustomEdge.vue'

const store = useWorkflowStore()
const { addNodeFromCatalog } = useFlowGraph()
const { onConnect, addEdges, screenToFlowCoordinate, onNodeClick, onPaneClick, onNodeDragStart } =
  useVueFlow()
const { register, unregister, snapshot } = useCanvasShortcuts()

onMounted(register)
onUnmounted(unregister)

// Snapshot the pre-move graph so node drags are undoable.
onNodeDragStart(() => snapshot())

// cast to any — Vue Flow's strict NodeComponent generic doesn't accept SFCs cleanly
const nodeTypes: any = {
  start: markRaw(StartNode),
  end: markRaw(EndNode),
  llm: markRaw(LLMNode),
  knowledge_retrieval: markRaw(KnowledgeNode),
  if_else: markRaw(IfElseNode),
  iteration: markRaw(IterationNode),
  http_request: markRaw(HttpNode),
  tool: markRaw(ToolNode),
  code: markRaw(CodeNode),
  template: markRaw(TemplateNode),
  aggregator: markRaw(AggregatorNode),
}
const edgeTypes: any = { custom: markRaw(CustomEdge) }

import { typeCompatible } from '@/composables/useVariableRef'
import { message } from 'ant-design-vue'

onConnect((conn: Connection) => {
  snapshot()
  addEdges([
    {
      id: `e_${conn.source}_${conn.target}_${Date.now()}`,
      source: conn.source!,
      target: conn.target!,
      sourceHandle: conn.sourceHandle ?? undefined,
      type: 'custom',
      label: conn.sourceHandle || undefined,
    },
  ])
  autoBind(conn.source!, conn.target!)
})

// 连线后自动把下游节点未绑定的输入，绑定到上游同名/兼容类型的输出。
function autoBind(sourceId: string, targetId: string) {
  const src = store.nodes.find((n) => n.id === sourceId)
  const tgt = store.nodes.find((n) => n.id === targetId)
  if (!src || !tgt) return
  const outputs = (src.data?.outputs || []) as any[]
  const inputs = (tgt.data?.inputs || []) as any[]
  if (!outputs.length || !inputs.length) return

  let bound = 0
  const nextInputs = inputs.map((inp) => {
    if (inp.value) return inp // 已绑定/已填，保留
    // 1) 优先同名匹配
    let match = outputs.find((o) => o.name === inp.name && typeCompatible(o.type, inp.type))
    // 2) 否则当上游只有一个输出且类型兼容时，直接绑定
    if (!match && outputs.length === 1 && typeCompatible(outputs[0].type, inp.type)) {
      match = outputs[0]
    }
    if (match) {
      bound++
      return { ...inp, value: `{{${sourceId}.${match.name}}}` }
    }
    return inp
  })

  if (bound > 0) {
    store.updateNodeData(targetId, { inputs: nextInputs })
    message.success(`已自动绑定 ${bound} 个输入字段到上游「${src.data?.label || src.type}」`)
  }
}

onNodeClick(({ node }) => store.selectNode(node.id))
onPaneClick(() => store.selectNode(null))

function onDrop(e: DragEvent) {
  const raw = e.dataTransfer?.getData('application/agentflow-node')
  if (!raw) return
  const item = JSON.parse(raw)
  const position = screenToFlowCoordinate({ x: e.clientX, y: e.clientY })
  snapshot()
  addNodeFromCatalog(item, position)
}
function onDragOver(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
}
</script>

<template>
  <div style="flex:1;height:100%" @drop="onDrop" @dragover="onDragOver">
    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="nodeTypes"
      :edge-types="edgeTypes"
      :default-viewport="{ zoom: 0.9, x: 0, y: 0 }"
      :delete-key-code="null"
      :multi-selection-key-code="['Shift', 'Meta', 'Control']"
      fit-view-on-init
    >
      <Background pattern-color="#ddd" :gap="16" />
      <Controls />
      <MiniMap />
    </VueFlow>
  </div>
</template>
