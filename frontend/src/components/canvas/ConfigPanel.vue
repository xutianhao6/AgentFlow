<script setup lang="ts">
import { computed, ref } from 'vue'
import { useNodeConfig } from '@/composables/useNodeConfig'
import { useFlowGraph } from '@/composables/useFlowGraph'
import { workflowApi } from '@/api/workflow'
import { useWorkflowStore } from '@/stores/workflow'
import { message } from 'ant-design-vue'

import LLMConfig from './config/LLMConfig.vue'
import KnowledgeConfig from './config/KnowledgeConfig.vue'
import IfElseConfig from './config/IfElseConfig.vue'
import HttpConfig from './config/HttpConfig.vue'
import ToolConfig from './config/ToolConfig.vue'
import CodeConfig from './config/CodeConfig.vue'
import TemplateConfig from './config/TemplateConfig.vue'
import GenericConfig from './config/GenericConfig.vue'

const { selectedNode, update } = useNodeConfig()
const { deleteNode } = useFlowGraph()
const store = useWorkflowStore()

const singleRunOpen = ref(false)
const singleInputs = ref('{}')
const singleResult = ref<any>(null)

const nodeType = computed(() => selectedNode.value?.type as string)

function onUpdate(patch: Record<string, any>) {
  update(patch)
}

async function runSingle() {
  let inputs = {}
  try { inputs = JSON.parse(singleInputs.value) } catch { return message.error('输入不是合法 JSON') }
  await store.save()
  singleResult.value = await workflowApi.runSingleNode(store.workflowId, selectedNode.value!.id, inputs)
}
</script>

<template>
  <div v-if="selectedNode" style="width:380px;border-left:1px solid #f0f0f0;background:#fff;overflow:auto;padding:14px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <strong>{{ selectedNode.data.label || nodeType }} 配置</strong>
      <a-space>
        <a @click="singleRunOpen = true">单步运行</a>
        <a style="color:#ff4d4f" @click="deleteNode(selectedNode.id)">删除节点</a>
      </a-space>
    </div>
    <div style="font-size:11px;color:#bbb;margin-bottom:10px">节点 ID：{{ selectedNode.id }}</div>

    <LLMConfig v-if="nodeType === 'llm'" :data="selectedNode.data" @update="onUpdate" />
    <KnowledgeConfig v-else-if="nodeType === 'knowledge_retrieval'" :data="selectedNode.data" @update="onUpdate" />
    <IfElseConfig v-else-if="nodeType === 'if_else'" :data="selectedNode.data" @update="onUpdate" />
    <HttpConfig v-else-if="nodeType === 'http_request'" :data="selectedNode.data" @update="onUpdate" />
    <ToolConfig v-else-if="nodeType === 'tool'" :data="selectedNode.data" @update="onUpdate" />
    <CodeConfig v-else-if="nodeType === 'code'" :data="selectedNode.data" @update="onUpdate" />
    <TemplateConfig v-else-if="nodeType === 'template'" :data="selectedNode.data" @update="onUpdate" />
    <GenericConfig v-else :data="selectedNode.data" :node-type="nodeType" @update="onUpdate" />

    <a-modal v-model:open="singleRunOpen" title="单步运行（仅执行此节点）" :footer="null">
      <a-textarea v-model:value="singleInputs" :rows="4" placeholder='{"query":"测试输入"}' />
      <a-button type="primary" style="margin:10px 0" @click="runSingle">运行</a-button>
      <pre v-if="singleResult" style="background:#f5f5f5;padding:10px;border-radius:6px;max-height:300px;overflow:auto">{{ JSON.stringify(singleResult, null, 2) }}</pre>
    </a-modal>
  </div>
  <div v-else style="width:280px;border-left:1px solid #f0f0f0;background:#fff;padding:20px;color:#999">
    选择一个节点以编辑配置
  </div>
</template>
