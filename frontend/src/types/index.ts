export type Platform = 'weibo' | 'douyin' | 'zhihu' | 'toutiao'

export interface HotTopic {
  id: number
  platform: Platform
  title: string
  hot_value: number
  rank: number
  url: string
  summary: string
  crawl_time: string
  created_at: string
  is_deleted: boolean
  deleted_at: string | null
  deleted_by: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CrawlLog {
  id: number
  platform: Platform
  status: string
  count: number
  error_message: string | null
  started_at: string
  finished_at: string | null
}

export interface AuditLog {
  id: number
  action: 'DELETE' | 'RESTORE'
  entity_type: string
  entity_id: number
  operator: string
  operation_time: string
  details: string | null
  old_value: string | null
  new_value: string | null
}

export interface PlatformInfo {
  id: Platform
  name: string
  icon: string
}

export interface Stats {
  total_topics: number
  deleted_count: number
  today_topics: number
  platform_counts: Record<Platform, number>
  recent_logs: CrawlLog[]
}