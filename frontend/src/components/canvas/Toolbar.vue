<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useWorkflowStore } from '@/stores/workflow'
import { useDebugRun } from '@/composables/useDebugRun'
import { useDslValidate } from '@/composables/useDslValidate'
import { workflowApi } from '@/api/workflow'
import {
  ArrowLeftOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  HistoryOutlined,
  SaveOutlined,
  CaretRightOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons-vue'

const store = useWorkflowStore()
const router = useRouter()
const { run } = useDebugRun()
const { validate } = useDslValidate()

const emit = defineEmits<{ 'open-debug': []; 'open-history': [] }>()

const runOpen = ref(false)
const runInputs = ref('{"query":"你好"}')

async function save() {
  await store.save()
  message.success('已保存')
}

async function doValidate() {
  const res = await validate()
  if (res.valid) message.success('校验通过')
  else message.error('校验失败: ' + res.errors.join('; '))
}

async function startDebug() {
  let inputs = {}
  try { inputs = JSON.parse(runInputs.value) } catch { return message.error('输入不是合法 JSON') }
  runOpen.value = false
  emit('open-debug')
  await run(inputs)
}

async function publish() {
  await store.save()
  await workflowApi.publish(store.workflowId)
  message.success('已发布到工作流市场')
}
</script>

<template>
  <div class="toolbar">
    <a-button type="text" size="small" @click="router.push('/workflows')">
      <template #icon><ArrowLeftOutlined /></template>
      返回
    </a-button>
    <span class="toolbar__divider" />
    <a-input v-model:value="store.name" class="toolbar__name" :bordered="false" />
    <a-popover placement="bottomLeft" title="画布快捷键">
      <template #content>
        <div class="af-shortcuts">
          <div><kbd>Delete</kbd> / <kbd>Backspace</kbd><span>删除选中节点/连线</span></div>
          <div><kbd>Ctrl/⌘</kbd>+<kbd>C</kbd> / <kbd>V</kbd><span>复制 / 粘贴节点</span></div>
          <div><kbd>Ctrl/⌘</kbd>+<kbd>D</kbd><span>复制为副本</span></div>
          <div><kbd>Ctrl/⌘</kbd>+<kbd>A</kbd><span>全选节点</span></div>
          <div><kbd>Esc</kbd><span>取消选中</span></div>
          <div><kbd>Ctrl/⌘</kbd>+<kbd>Z</kbd><span>撤销</span></div>
          <div><kbd>Ctrl/⌘</kbd>+<kbd>Shift</kbd>+<kbd>Z</kbd><span>重做</span></div>
          <div class="af-shortcuts__hint">开始/结束节点受保护，不可删除</div>
        </div>
      </template>
      <a-button type="text" size="small">快捷键</a-button>
    </a-popover>
    <div style="flex: 1" />
    <a-button @click="doValidate">
      <template #icon><CheckCircleOutlined /></template>
      校验
    </a-button>
    <a-button @click="emit('open-history')">
      <template #icon><HistoryOutlined /></template>
      运行历史
    </a-button>
    <a-button @click="save">
      <template #icon><SaveOutlined /></template>
      保存
    </a-button>
    <a-button class="toolbar__run" @click="runOpen = true">
      <template #icon><CaretRightOutlined /></template>
      调试运行
    </a-button>
    <a-button type="primary" @click="publish">
      <template #icon><CloudUploadOutlined /></template>
      发布
    </a-button>

    <a-modal v-model:open="runOpen" title="调试运行输入" @ok="startDebug">
      <div class="af-muted" style="font-size: 12px; margin-bottom: 6px">
        填入开始节点的入参（JSON）
      </div>
      <a-textarea v-model:value="runInputs" class="af-mono" :rows="4" />
    </a-modal>
  </div>
</template>

<style scoped>
.toolbar {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid var(--af-border);
  background: var(--af-surface);
}
.toolbar__divider {
  width: 1px;
  height: 20px;
  background: var(--af-border);
}
.toolbar__name {
  width: 220px;
  font-weight: 600;
  font-size: 15px;
}
.toolbar__name:hover {
  background: var(--af-border-light);
  border-radius: var(--af-radius-sm);
}
/* 调试运行 = 运行/成功绿 */
.toolbar__run {
  color: #fff;
  background: var(--af-success);
  border-color: var(--af-success);
}
.toolbar__run:hover {
  color: #fff !important;
  background: #16a34a !important;
  border-color: #16a34a !important;
}

.af-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 220px;
  font-size: 13px;
}
.af-shortcuts > div {
  display: flex;
  align-items: center;
  gap: 6px;
}
.af-shortcuts span {
  margin-left: auto;
  color: var(--af-text-secondary);
}
.af-shortcuts kbd {
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid var(--af-border);
  border-bottom-width: 2px;
  border-radius: 4px;
  background: var(--af-bg);
  font-family: var(--af-font-mono);
  font-size: 12px;
  line-height: 18px;
}
.af-shortcuts__hint {
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px dashed var(--af-border);
  color: var(--af-text-tertiary);
  font-size: 12px;
}
</style>
