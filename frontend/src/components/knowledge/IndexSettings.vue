<script setup lang="ts">
defineProps<{ method: string }>()
</script>

<template>
  <a-alert
    :message="method === 'high_quality' ? '高质量索引：Embedding 向量化，支持语义/混合检索' : '经济索引：关键词倒排，全文精确匹配'"
    :type="method === 'high_quality' ? 'info' : 'warning'"
    show-icon
  />
  <div style="color:#999;font-size:12px;margin-top:6px">注：高质量索引一经创建不可降级为经济（与 Dify 一致）。</div>
</template>
