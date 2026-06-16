import { defineStore } from 'pinia'
import { ref } from 'vue'
import { pluginApi } from '@/api/plugin'
import type { Plugin } from '@/types/plugin'

export const usePluginStore = defineStore('plugin', () => {
  const market = ref<Plugin[]>([])
  const installed = ref<Plugin[]>([])

  async function loadMarket(type?: string, keyword?: string) {
    const res = await pluginApi.market(type, keyword)
    market.value = res.items
  }
  async function loadInstalled() {
    const res = await pluginApi.installed()
    installed.value = res.items
  }
  return { market, installed, loadMarket, loadInstalled }
})
