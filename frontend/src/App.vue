<script setup lang="ts">
import { RouterView } from 'vue-router'
import { afTheme } from '@/theme'
</script>

<template>
  <a-config-provider :theme="afTheme">
    <RouterView />
  </a-config-provider>
</template>
