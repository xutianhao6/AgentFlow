<script setup lang="ts">
/**
 * 带变量自动补全的文本框。
 * 触发方式：输入 `@`、`{`、`{{` 时弹出变量列表（本节点输入 + 上游节点输出）。
 * 选中后在光标处插入 `{{node.field}}`（或本节点输入 `{{field}}`）。
 */
import { computed, nextTick, ref } from 'vue'
import { useVariableRef } from '@/composables/useVariableRef'
import { useWorkflowStore } from '@/stores/workflow'

const props = withDefaults(
  defineProps<{
    modelValue: string
    rows?: number
    placeholder?: string
    // 本节点自身的输入字段名（可用 {{field}} 引用），可选
    selfInputs?: { name: string; type?: string }[]
  }>(),
  { rows: 5, placeholder: '', selfInputs: () => [] },
)
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const store = useWorkflowStore()
const { availableRefs } = useVariableRef(() => store.selectedNodeId)

const taRef = ref<any>(null)
const showMenu = ref(false)
const menuPos = ref({ top: 0, left: 0 })
const filter = ref('')
const triggerStart = ref(-1) // 触发符在文本中的起始位置
const activeIndex = ref(0)

// 候选项：本节点输入(用 {{name}}) + 上游输出(用 {{node.field}})
const candidates = computed(() => {
  const list: { label: string; insert: string; type: string }[] = []
  for (const f of props.selfInputs || []) {
    list.push({ label: `输入 · ${f.name}`, insert: `{{${f.name}}}`, type: f.type || 'string' })
  }
  for (const r of availableRefs.value) {
    list.push({ label: `上游 · ${r.label}`, insert: r.value, type: r.type })
  }
  const kw = filter.value.toLowerCase()
  return kw ? list.filter((c) => c.label.toLowerCase().includes(kw)) : list
})

function onInput(e: Event) {
  const ta = e.target as HTMLTextAreaElement
  emit('update:modelValue', ta.value)
  detectTrigger(ta)
}

function detectTrigger(ta: HTMLTextAreaElement) {
  const pos = ta.selectionStart
  const text = ta.value.slice(0, pos)
  // 匹配光标前最近的触发：@xxx 或 {xxx 或 {{xxx
  const m = /(?:@|\{\{?)([\w一-龥.]*)$/.exec(text)
  if (m) {
    triggerStart.value = pos - m[0].length
    filter.value = m[1] || ''
    activeIndex.value = 0
    openMenu(ta)
  } else {
    showMenu.value = false
  }
}

function openMenu(ta: HTMLTextAreaElement) {
  // 简单定位：弹在文本框左下方
  showMenu.value = true
  nextTick(() => {
    const rect = ta.getBoundingClientRect()
    menuPos.value = { top: rect.bottom + window.scrollY + 2, left: rect.left + window.scrollX }
  })
}

function pick(item: { insert: string }) {
  const ta = taRef.value?.resizableTextArea?.textArea || taRef.value?.$el?.querySelector('textarea')
  const value = props.modelValue
  const cursor = ta ? ta.selectionStart : value.length
  const before = value.slice(0, triggerStart.value)
  const after = value.slice(cursor)
  const next = before + item.insert + after
  emit('update:modelValue', next)
  showMenu.value = false
  nextTick(() => {
    if (ta) {
      const np = (before + item.insert).length
      ta.focus()
      ta.selectionStart = ta.selectionEnd = np
    }
  })
}

function onBlur() {
  // 延迟关闭，给 mousedown 选项留出时间
  window.setTimeout(() => (showMenu.value = false), 150)
}

function onKeydown(e: KeyboardEvent) {
  if (!showMenu.value || !candidates.value.length) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % candidates.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value - 1 + candidates.value.length) % candidates.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    pick(candidates.value[activeIndex.value])
  } else if (e.key === 'Escape') {
    showMenu.value = false
  }
}
</script>

<template>
  <div style="position:relative">
    <a-textarea
      ref="taRef"
      :value="modelValue"
      :rows="rows"
      :placeholder="placeholder"
      @input="onInput"
      @keydown="onKeydown"
      @blur="onBlur"
    />
    <teleport to="body">
      <div
        v-if="showMenu && candidates.length"
        class="var-menu"
        :style="{ top: menuPos.top + 'px', left: menuPos.left + 'px' }"
      >
        <div
          v-for="(c, i) in candidates"
          :key="c.insert + i"
          class="var-item"
          :class="{ active: i === activeIndex }"
          @mousedown.prevent="pick(c)"
          @mouseenter="activeIndex = i"
        >
          <span>{{ c.label }}</span>
          <span class="var-type">{{ c.type }}</span>
        </div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.var-menu {
  position: absolute;
  z-index: 2000;
  min-width: 240px;
  max-height: 240px;
  overflow: auto;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  padding: 4px;
}
.var-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.var-item.active,
.var-item:hover {
  background: #e6f4ff;
}
.var-type {
  color: #999;
  font-size: 11px;
}
</style>
