<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useWorkflowStore } from '@/stores/workflow'

import Toolbar from '@/components/canvas/Toolbar.vue'
import NodePanel from '@/components/canvas/NodePanel.vue'
import FlowCanvas from '@/components/canvas/FlowCanvas.vue'
import ConfigPanel from '@/components/canvas/ConfigPanel.vue'
import DebugPanel from '@/components/debug/DebugPanel.vue'
import RunHistory from '@/components/debug/RunHistory.vue'

const route = useRoute()
const store = useWorkflowStore()

const debugOpen = ref(false)
const historyOpen = ref(false)

onMounted(async () => {
  await store.loadCatalog()
  await store.load(route.params.id as string)
})
</script>

<template>
  <div class="af-layout">
    <Toolbar @open-debug="debugOpen = true" @open-history="historyOpen = true" />
    <div style="flex:1;display:flex;min-height:0">
      <NodePanel />
      <FlowCanvas />
      <ConfigPanel />
    </div>
    <DebugPanel v-model:open="debugOpen" />
    <RunHistory v-model:open="historyOpen" />
  </div>
</template>
