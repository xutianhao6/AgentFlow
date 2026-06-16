<script setup lang="ts">
defineProps<{ open: boolean }>()
const emit = defineEmits<{ select: [string]; 'update:open': [boolean] }>()
function pick(lang: string) {
  emit('select', lang)
  emit('update:open', false)
}
</script>

<template>
  <a-modal :open="open" title="选择代码语言" :footer="null" @cancel="emit('update:open', false)">
    <div style="display:flex;gap:16px;justify-content:center;padding:16px 0">
      <a-button size="large" @click="pick('python')">🐍 Python</a-button>
      <a-button size="large" @click="pick('javascript')">🟨 TypeScript / JavaScript</a-button>
    </div>
    <div style="color:#999;font-size:12px;text-align:center">选择后将生成含输入输出的模板，你只需修改核心逻辑。</div>
  </a-modal>
</template>
