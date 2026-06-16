<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useWorkflowStore } from '@/stores/workflow'
import { useDebugRun } from '@/composables/useDebugRun'
import { useDslValidate } from '@/composables/useDslValidate'
import { workflowApi } from '@/api/workflow'

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
  <div style="height:52px;display:flex;align-items:center;gap:10px;padding:0 16px;border-bottom:1px solid #f0f0f0;background:#fff">
    <a @click="router.push('/workflows')">← 返回</a>
    <a-input v-model:value="store.name" style="width:220px" />
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
      <a-button size="small" style="margin-left:4px">⌨ 快捷键</a-button>
    </a-popover>
    <div style="flex:1" />
    <a-button @click="doValidate">校验</a-button>
    <a-button @click="emit('open-history')">运行历史</a-button>
    <a-button @click="save">保存</a-button>
    <a-button type="primary" @click="runOpen = true">调试运行</a-button>
    <a-button @click="publish">发布</a-button>

    <a-modal v-model:open="runOpen" title="调试运行输入" @ok="startDebug">
      <div style="color:#999;font-size:12px;margin-bottom:6px">填入开始节点的入参（JSON）</div>
      <a-textarea v-model:value="runInputs" :rows="4" />
    </a-modal>
  </div>
</template>

<style scoped>
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
  color: #666;
}
.af-shortcuts kbd {
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid #d9d9d9;
  border-bottom-width: 2px;
  border-radius: 4px;
  background: #fafafa;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  line-height: 18px;
}
.af-shortcuts__hint {
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px dashed #eee;
  color: #999;
  font-size: 12px;
}
</style>
