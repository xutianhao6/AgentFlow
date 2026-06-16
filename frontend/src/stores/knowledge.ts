import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeApi } from '@/api/knowledge'
import type { Dataset, KnowledgeDocument } from '@/types/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const datasets = ref<Dataset[]>([])
  const documents = ref<KnowledgeDocument[]>([])

  async function loadDatasets() {
    const res = await knowledgeApi.listDatasets()
    datasets.value = res.items
  }

  async function loadDocuments(id: string) {
    const res = await knowledgeApi.listDocuments(id)
    documents.value = res.items
  }

  return { datasets, documents, loadDatasets, loadDocuments }
})
