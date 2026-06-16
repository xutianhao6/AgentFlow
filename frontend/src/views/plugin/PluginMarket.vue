<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { message } from 'ant-design-vue'
import { pluginApi } from '@/api/plugin'
import { usePluginStore } from '@/stores/plugin'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import {
  SearchOutlined,
  DownloadOutlined,
  AppstoreOutlined,
  CheckOutlined,
} from '@ant-design/icons-vue'

const store = usePluginStore()
const keyword = ref('')
const typeFilter = ref<string | undefined>(undefined)
const publishOpen = ref(false)
const pubForm = ref({ name: '', type: 'tool', description: '' })

async function load() { await store.loadMarket(typeFilter.value, keyword.value) }

async function install(id: string) {
  await pluginApi.install(id)
  message.success('安装成功，节点已加入节点面板')
  load()
}

async function publish() {
  if (!pubForm.value.name) return message.warning('请输入名称')
  await pluginApi.publish({
    name: pubForm.value.name,
    type: pubForm.value.type,
    description: pubForm.value.description,
    manifest: { name: pubForm.value.name, type: pubForm.value.type, io_spec: { inputs: [], outputs: [] } },
  })
  publishOpen.value = false
  message.success('已发布')
  load()
}

onMounted(load)
</script>

<template>
  <div class="af-page">
    <PageHeader title="插件市场" subtitle="下载插件，每个插件即一个可拖入画布的节点">
      <template #extra><a-button @click="publishOpen = true">发布插件</a-button></template>
    </PageHeader>

    <a-space style="margin-bottom: 16px">
      <a-input v-model:value="keyword" placeholder="搜索插件" allow-clear style="width: 280px" @press-enter="load">
        <template #prefix><SearchOutlined style="color: var(--af-text-tertiary)" /></template>
      </a-input>
      <a-select v-model:value="typeFilter" placeholder="类型" style="width: 160px" allow-clear @change="load">
        <a-select-option value="tool">Tool 工具</a-select-option>
        <a-select-option value="model">Model 模型</a-select-option>
        <a-select-option value="extension">Extension 扩展</a-select-option>
        <a-select-option value="agent_strategy">Agent 策略</a-select-option>
      </a-select>
      <a-button @click="load">搜索</a-button>
    </a-space>

    <a-row :gutter="16">
      <a-col v-for="p in store.market" :key="p.id" :xs="24" :sm="12" :lg="8" style="margin-bottom: 16px">
        <a-card class="pl-card af-card af-card--hover">
          <div class="pl-card__head">
            <span class="pl-card__icon"><AppstoreOutlined /></span>
            <span class="pl-card__name">{{ p.name }}</span>
            <a-tag>{{ p.type }}</a-tag>
          </div>
          <div class="pl-card__desc af-muted">{{ p.description }}</div>
          <div class="pl-card__foot">
            <span class="af-dim" style="font-size: 12px">
              <DownloadOutlined /> {{ p.downloads }} · {{ p.author }}
            </span>
            <a-button v-if="!p.installed" type="primary" size="small" @click="install(p.id)">安装</a-button>
            <a-tag v-else color="success"><CheckOutlined /> 已安装</a-tag>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <EmptyState v-if="!store.market.length" description="没有匹配的插件" />

    <a-modal v-model:open="publishOpen" title="发布插件" @ok="publish">
      <a-form layout="vertical">
        <a-form-item label="名称"><a-input v-model:value="pubForm.name" /></a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="pubForm.type">
            <a-select-option value="tool">tool</a-select-option>
            <a-select-option value="model">model</a-select-option>
            <a-select-option value="extension">extension</a-select-option>
            <a-select-option value="agent_strategy">agent_strategy</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="描述"><a-textarea v-model:value="pubForm.description" /></a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.pl-card :deep(.ant-card-body) {
  padding: 16px;
}
.pl-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.pl-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--af-radius);
  background: #fff7ed;
  color: var(--af-warning);
  font-size: 16px;
  flex: none;
}
.pl-card__name {
  font-weight: 600;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pl-card__desc {
  min-height: 42px;
  font-size: 13px;
  line-height: 1.6;
}
.pl-card__foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--af-border-light);
}
</style>
