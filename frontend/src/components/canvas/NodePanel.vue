<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { NodeCatalogItem } from '@/types/node'
import { nodeMeta } from '@/theme'

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
  <div class="panel">
    <div class="panel__title">节点库</div>
    <div class="panel__hint">拖拽节点到画布</div>
    <template v-for="(items, cat) in grouped" :key="cat">
      <div class="cat-tag">{{ cat }}</div>
      <div
        v-for="item in items"
        :key="item.type"
        class="node-item"
        draggable="true"
        :title="item.label"
        @dragstart="(e) => onDragStart(e, item)"
      >
        <span class="node-item__icon" :style="{ color: nodeMeta(item.type).color }">
          <component :is="nodeMeta(item.type).icon" />
        </span>
        <span>{{ item.label }}</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.panel {
  width: 208px;
  border-right: 1px solid var(--af-border);
  background: var(--af-surface);
  overflow: auto;
  padding: 14px;
}
.panel__title {
  font-weight: 600;
  font-size: 14px;
  color: var(--af-text);
}
.panel__hint {
  font-size: 12px;
  color: var(--af-text-tertiary);
  margin-top: 2px;
}
</style>
