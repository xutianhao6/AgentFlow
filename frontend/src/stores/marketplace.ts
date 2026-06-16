import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import type { WorkflowTemplate } from '@/types/plugin'

export const useMarketplaceStore = defineStore('marketplace', () => {
  const templates = ref<WorkflowTemplate[]>([])

  async function load(category?: string, keyword?: string) {
    const res = await marketplaceApi.list(category, keyword)
    templates.value = res.items
  }
  return { templates, load }
})
