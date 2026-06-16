<script setup lang="ts">
// Lightweight code editor (textarea-based). Monaco is available as a dependency
// and can be swapped in; a textarea keeps worker setup out of the critical path.
const props = defineProps<{ modelValue: string; language?: string }>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}
function onTab(e: KeyboardEvent) {
  if (e.key === 'Tab') {
    e.preventDefault()
    const ta = e.target as HTMLTextAreaElement
    const start = ta.selectionStart
    const val = ta.value
    emit('update:modelValue', val.slice(0, start) + '    ' + val.slice(ta.selectionEnd))
    requestAnimationFrame(() => (ta.selectionStart = ta.selectionEnd = start + 4))
  }
}
</script>

<template>
  <div>
    <div style="font-size:11px;color:#999;margin-bottom:4px">语言：{{ language || 'python' }}</div>
    <textarea
      :value="modelValue"
      spellcheck="false"
      style="width:100%;height:280px;font-family:'Fira Code',Consolas,monospace;font-size:13px;
             line-height:1.5;padding:10px;border:1px solid #d9d9d9;border-radius:6px;
             background:#1e1e1e;color:#d4d4d4;resize:vertical;outline:none"
      @input="onInput"
      @keydown="onTab"
    />
  </div>
</template>
