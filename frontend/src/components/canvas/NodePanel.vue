<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { NodeCatalogItem } from '@/types/node'

const store = useWorkflowStore()
onMounted(() => store.loadCatalog())

const grouped = computed(() => {
  const g: Record<string, NodeCatalogItem[]> = {}
  for (const n of store.catalog) {
    ;(g[n.category] = g[n.category] || []).push(n)
  }
  return g
})

function onDragStart(e: DragEvent, item: NodeCatalogItem) {
  e.dataTransfer?.setData('application/agentflow-node', JSON.stringify(item))
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}
</script>

<template>
  <div style="width:200px;border-right:1px solid #f0f0f0;background:#fafafa;overflow:auto;padding:10px">
    <div style="font-weight:600;margin-bottom:8px">节点面板</div>
    <template v-for="(items, cat) in grouped" :key="cat">
      <div class="cat-tag">{{ cat }}</div>
      <div
        v-for="item in items"
        :key="item.type"
        class="node-item"
        draggable="true"
        @dragstart="(e) => onDragStart(e, item)"
      >
        <span>{{ item.icon ? '●' : '' }}</span>
        <span>{{ item.label }}</span>
      </div>
    </template>
  </div>
</template>
