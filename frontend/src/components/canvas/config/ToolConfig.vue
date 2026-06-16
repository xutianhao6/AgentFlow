<script setup lang="ts">
import { onMounted, ref } from 'vue'
import IOSchemaEditor from './IOSchemaEditor.vue'
import { pluginApi } from '@/api/plugin'
import type { Plugin } from '@/types/plugin'

const props = defineProps<{ data: Record<string, any> }>()
const emit = defineEmits<{ update: [Record<string, any>] }>()
function set(key: string, val: any) { emit('update', { [key]: val }) }

const plugins = ref<Plugin[]>([])
onMounted(async () => {
  const res = await pluginApi.installed()
  plugins.value = res.items.filter((p) => p.type === 'tool')
})

function onSelect(pid: string) {
  const plugin = plugins.value.find((p) => p.id === pid)
  const io = plugin?.manifest?.io_spec || {}
  emit('update', { plugin_id: pid, inputs: io.inputs || [], outputs: io.outputs || [] })
}
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="选择已安装工具插件">
      <a-select :value="data.plugin_id" @change="onSelect">
        <a-select-option v-for="p in plugins" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
      </a-select>
    </a-form-item>
    <div v-if="!plugins.length" style="color:#999;font-size:12px">尚未安装工具插件，请先到插件市场安装。</div>
    <IOSchemaEditor :model-value="data.inputs || []" kind="inputs" @update:model-value="(v)=>set('inputs', v)" />
    <IOSchemaEditor :model-value="data.outputs || []" kind="outputs" @update:model-value="(v)=>set('outputs', v)" />
  </a-form>
</template>
