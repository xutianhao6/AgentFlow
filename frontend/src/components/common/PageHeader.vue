<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

<template>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div>
      <h2 style="margin:0">{{ title }}</h2>
      <div v-if="subtitle" style="color:#999;font-size:13px">{{ subtitle }}</div>
    </div>
    <div><slot name="extra" /></div>
  </div>
</template>
