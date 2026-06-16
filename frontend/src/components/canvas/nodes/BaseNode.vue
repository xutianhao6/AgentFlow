<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { nodeMeta } from '@/theme'

const props = defineProps<{
  id: string
  data: Record<string, any>
  label: string
  type?: string
  icon?: string
  // for if_else: render multiple source handles
  branches?: string[]
  noSource?: boolean
  noTarget?: boolean
  selected?: boolean
}>()

const meta = computed(() => nodeMeta(props.type))
const status = computed(() => props.data?._status)
const statusClass = computed(() => (status.value ? `status-${status.value}` : ''))
</script>

<template>
  <div class="flow-node" :class="{ selected }" :style="{ '--node-accent': meta.color }">
    <Handle v-if="!noTarget" type="target" :position="Position.Left" />

    <div class="flow-node__header">
      <span class="flow-node__icon"><component :is="meta.icon" /></span>
      <span class="flow-node__title">{{ data.label || label }}</span>
      <span v-if="status" class="flow-node__status" :class="statusClass" />
    </div>
    <div class="flow-node__body">
      <slot>
        <span class="af-mono" style="color: #64748b">{{ id }}</span>
      </slot>
    </div>

    <template v-if="branches && branches.length">
      <Handle
        v-for="(b, i) in branches"
        :key="b"
        :id="b"
        type="source"
        :position="Position.Right"
        :style="{ top: `${30 + i * 22}px` }"
      />
    </template>
    <Handle v-else-if="!noSource" type="source" :position="Position.Right" />
  </div>
</template>
