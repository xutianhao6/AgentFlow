import request from './request'
import type { Plugin } from '@/types/plugin'

export const pluginApi = {
  market: (type?: string, keyword?: string): Promise<{ items: Plugin[] }> =>
    request.get('/plugins/market', { params: { type, keyword } }),

  installed: (): Promise<{ items: Plugin[] }> => request.get('/plugins/installed'),

  install: (plugin_id: string): Promise<Plugin> => request.post('/plugins/install', { plugin_id }),

  uninstall: (id: string): Promise<{ uninstalled: boolean }> => request.delete(`/plugins/${id}`),

  publish: (payload: Record<string, any>): Promise<Plugin> => request.post('/plugins/publish', payload),
}
