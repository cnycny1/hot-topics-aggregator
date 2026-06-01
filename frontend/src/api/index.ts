import axios from 'axios'
import type { HotTopic, PaginatedResponse, CrawlLog, Stats, PlatformInfo, AuditLog } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const hotTopicsApi = {
  getHotTopics(params: {
    platform?: string
    date?: string
    page?: number
    page_size?: number
  }) {
    return api.get<PaginatedResponse<HotTopic>>('/hot-topics', { params })
  },

  getDeletedHotTopics(params: {
    platform?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return api.get<PaginatedResponse<HotTopic>>('/hot-topics/deleted', { params })
  },

  getHotTopic(id: number) {
    return api.get<HotTopic>(`/hot-topics/${id}`)
  },

  searchHotTopics(params: {
    keyword: string
    page?: number
    page_size?: number
  }) {
    return api.get<PaginatedResponse<HotTopic>>('/hot-topics/search', { params })
  },

  deleteHotTopic(id: number) {
    return api.delete(`/hot-topics/${id}`)
  },

  batchDeleteHotTopics(ids: number[]) {
    return api.post('/hot-topics/batch-delete', { ids })
  },

  restoreHotTopic(id: number) {
    return api.post(`/hot-topics/${id}/restore`)
  },

  batchRestoreHotTopics(ids: number[]) {
    return api.post('/hot-topics/batch-restore', { ids })
  },

  batchPurgeHotTopics(ids: number[]) {
    return api.post('/hot-topics/batch-purge', { ids })
  },

  purgeAllDeletedHotTopics() {
    return api.post('/hot-topics/purge-all')
  }
}

export const adminApi = {
  triggerCrawl(platform?: string, force?: boolean) {
    return api.post('/crawl/trigger', null, { params: { platform, force } })
  },

  getCrawlLogs(limit?: number) {
    return api.get<{ items: CrawlLog[] }>('/crawl/logs', { params: { limit } })
  },

  getAuditLogs(params: {
    action?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return api.get<PaginatedResponse<AuditLog>>('/audit-logs', { params })
  },

  getStats() {
    return api.get<Stats>('/stats')
  },

  getPlatforms() {
    return api.get<{ platforms: PlatformInfo[] }>('/platforms')
  },

  cleanupOldData(days: number) {
    return api.delete('/cleanup', { params: { days } })
  }
}