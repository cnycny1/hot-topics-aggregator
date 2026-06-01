import { defineStore } from 'pinia'
import { ref } from 'vue'
import { hotTopicsApi } from '../api'
import type { HotTopic } from '../types'

export const useHotTopicsStore = defineStore('hotTopics', () => {
  const topics = ref<HotTopic[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const platform = ref<string | undefined>(undefined)
  const date = ref<string | undefined>(undefined)

  async function fetchTopics() {
    loading.value = true
    try {
      const response = await hotTopicsApi.getHotTopics({
        platform: platform.value,
        date: date.value,
        page: page.value,
        page_size: pageSize.value
      })
      topics.value = response.data.items
      total.value = response.data.total
    } catch (error) {
      console.error('Failed to fetch topics:', error)
    } finally {
      loading.value = false
    }
  }

  function setPlatform(p: string | undefined) {
    platform.value = p
    page.value = 1
    fetchTopics()
  }

  function setDate(d: string | undefined) {
    date.value = d
    page.value = 1
    fetchTopics()
  }

  function setPage(p: number) {
    page.value = p
    fetchTopics()
  }

  return {
    topics,
    total,
    page,
    pageSize,
    loading,
    platform,
    date,
    fetchTopics,
    setPlatform,
    setDate,
    setPage
  }
})