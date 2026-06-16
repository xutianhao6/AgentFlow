<script setup lang="ts">
defineProps<{ description?: string }>()
</script>

<template>
  <a-empty :description="description || '暂无数据'">
    <slot />
  </a-empty>
</template>
