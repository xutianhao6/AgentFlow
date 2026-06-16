<script setup lang="ts">
import { computed } from 'vue'
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@vue-flow/core'

const props = defineProps<{
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition: any
  targetPosition: any
  label?: string
}>()

const path = computed(() =>
  getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition,
  }),
)
</script>

<template>
  <BaseEdge :id="id" :path="path[0]" :style="{ stroke: '#475569', strokeWidth: 1.5 }" />
  <EdgeLabelRenderer v-if="label">
    <div
      class="edge-label"
      :style="{
        transform: `translate(-50%, -50%) translate(${path[1]}px, ${path[2]}px)`,
      }"
    >
      {{ label }}
    </div>
  </EdgeLabelRenderer>
</template>

<style scoped>
.edge-label {
  position: absolute;
  background: #1e293b;
  color: #e2e8f0;
  font-family: var(--af-font-mono);
  font-size: 11px;
  padding: 2px 7px;
  border: 1px solid #334155;
  border-radius: 8px;
  pointer-events: none;
}
</style>
