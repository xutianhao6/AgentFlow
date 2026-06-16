<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

<template>
  <div class="page-header">
    <div class="page-header__text">
      <h2 class="page-header__title">{{ title }}</h2>
      <div v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</div>
    </div>
    <div class="page-header__extra"><slot name="extra" /></div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--af-sp-4);
  margin-bottom: var(--af-sp-6);
}
.page-header__title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--af-text);
}
.page-header__subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: var(--af-text-secondary);
}
.page-header__extra {
  flex: none;
}
</style>
