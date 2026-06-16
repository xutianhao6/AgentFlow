<script setup lang="ts">
defineProps<{ value: string }>()
const emit = defineEmits<{ 'update:value': [string] }>()
</script>

<template>
  <a-radio-group :value="value" @change="(e:any)=>emit('update:value', e.target.value)">
    <a-radio value="general">General（通用）</a-radio>
    <a-radio value="parent_child">Parent-Child（父子）</a-radio>
    <a-radio value="qa">Q&A（问答）</a-radio>
  </a-radio-group>
</template>
