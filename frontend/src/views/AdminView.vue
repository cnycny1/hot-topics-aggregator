<template>
  <div class="admin-view">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>⚙️ 系统管理</h1>
          <div class="header-actions">
            <el-button @click="goBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
          </div>
        </div>
      </el-header>

      <el-main>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="stats-card">
              <template #header>
                <div class="card-header">
                  <span>📊 数据统计</span>
                  <el-button type="primary" size="small" @click="goToRecycleBin">
                    <el-icon><Delete /></el-icon>
                    回收站 ({{ stats.deleted_count || 0 }})
                  </el-button>
                </div>
              </template>
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.total_topics || 0 }}</div>
                    <div class="stat-label">总热点数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value" style="color: #f56c6c">{{ stats.deleted_count || 0 }}</div>
                    <div class="stat-label">已删除</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.today_topics || 0 }}</div>
                    <div class="stat-label">今日新增</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ getPlatformCount('weibo') }}</div>
                    <div class="stat-label">微博热点</div>
                  </div>
                </el-col>
              </el-row>
              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ getPlatformCount('douyin') }}</div>
                    <div class="stat-label">抖音热点</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ getPlatformCount('zhihu') }}</div>
                    <div class="stat-label">知乎热点</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ getPlatformCount('toutiao') }}</div>
                    <div class="stat-label">头条热点</div>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>🚀 爬取控制</span>
                </div>
              </template>
              <div class="crawl-actions">
                <el-button type="primary" @click="triggerCrawl('weibo')" :loading="crawling.weibo">
                  爬取微博
                </el-button>
                <el-button type="primary" @click="triggerCrawl('douyin')" :loading="crawling.douyin">
                  爬取抖音
                </el-button>
                <el-button type="success" @click="triggerCrawl('zhihu')" :loading="crawling.zhihu">
                  爬取知乎
                </el-button>
                <el-button type="success" @click="triggerCrawl('toutiao')" :loading="crawling.toutiao">
                  爬取头条
                </el-button>
                <el-button type="success" @click="triggerCrawl('all')" :loading="crawling.all">
                  爬取全部
                </el-button>
                <el-button type="danger" @click="handleCleanup" :loading="cleaning">
                  清理7天前数据
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>📋 爬取日志</span>
                  <el-button size="small" @click="fetchLogs">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <el-table :data="logs" style="width: 100%" v-loading="loadingLogs">
                <el-table-column prop="platform" label="平台" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getPlatformType(row.platform)" size="small">
                      {{ getPlatformName(row.platform) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="爬取数量" width="100" />
                <el-table-column prop="error_message" label="错误信息" min-width="200" />
                <el-table-column prop="started_at" label="开始时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.started_at) }}
                  </template>
                </el-table-column>
                <el-table-column prop="finished_at" label="结束时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.finished_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>📝 审计日志</span>
                  <el-button size="small" @click="fetchAuditLogs">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <div class="audit-filters">
                <el-radio-group v-model="selectedAction" @change="handleActionChange" size="small">
                  <el-radio-button value="">全部</el-radio-button>
                  <el-radio-button value="DELETE">删除</el-radio-button>
                  <el-radio-button value="RESTORE">恢复</el-radio-button>
                </el-radio-group>
              </div>
              <el-table :data="auditLogs" style="width: 100%" v-loading="loadingAuditLogs">
                <el-table-column prop="action" label="操作" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.action === 'DELETE' ? 'danger' : 'success'" size="small">
                      {{ row.action === 'DELETE' ? '删除' : '恢复' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="entity_type" label="对象类型" width="120" />
                <el-table-column prop="entity_id" label="对象ID" width="100" />
                <el-table-column prop="operator" label="操作者" width="200" show-overflow-tooltip />
                <el-table-column prop="details" label="详情" min-width="300" show-overflow-tooltip />
                <el-table-column prop="operation_time" label="操作时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.operation_time) }}
                  </template>
                </el-table-column>
              </el-table>
              <div class="pagination">
                <el-pagination
                  v-model:current-page="auditPage"
                  :page-size="20"
                  :total="auditTotal"
                  layout="total, prev, pager, next"
                  @current-change="handleAuditPageChange"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi } from '../api'
import { Back, Refresh, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Stats, CrawlLog, Platform, AuditLog } from '../types'

const router = useRouter()

const stats = ref<Stats>({
  total_topics: 0,
  deleted_count: 0,
  today_topics: 0,
  platform_counts: {
    'weibo': 0,
    'douyin': 0,
    'zhihu': 0,
    'toutiao': 0
  },
  recent_logs: []
})

const logs = ref<CrawlLog[]>([])
const loadingLogs = ref(false)
const cleaning = ref(false)

const auditLogs = ref<AuditLog[]>([])
const loadingAuditLogs = ref(false)
const selectedAction = ref('')
const auditPage = ref(1)
const auditTotal = ref(0)

const crawling = ref({
  weibo: false,
  douyin: false,
  zhihu: false,
  toutiao: false,
  all: false
})

const platformNames: Record<Platform, string> = {
  'weibo': '微博',
  'douyin': '抖音',
  'zhihu': '知乎',
  'toutiao': '头条'
}

function goBack() {
  router.push('/')
}

function goToRecycleBin() {
  router.push('/recycle-bin')
}

async function fetchAuditLogs() {
  loadingAuditLogs.value = true
  try {
    const params: any = {
      page: auditPage.value,
      page_size: 20
    }
    
    if (selectedAction.value) {
      params.action = selectedAction.value
    }
    
    const response = await adminApi.getAuditLogs(params)
    auditLogs.value = response.data.items
    auditTotal.value = response.data.total
  } catch (error) {
    ElMessage.error('获取审计日志失败')
    console.error('Failed to fetch audit logs:', error)
  } finally {
    loadingAuditLogs.value = false
  }
}

function handleActionChange() {
  auditPage.value = 1
  fetchAuditLogs()
}

function handleAuditPageChange(page: number) {
  auditPage.value = page
  fetchAuditLogs()
}

function getPlatformCount(platform: Platform): number {
  return stats.value.platform_counts?.[platform] || 0
}

function getPlatformName(platform: Platform): string {
  return platformNames[platform] || platform
}

function getPlatformType(platform: Platform): string {
  const typeMap: Record<Platform, string> = {
    'weibo': 'danger',
    'douyin': 'primary',
    'zhihu': 'success',
    'toutiao': 'warning'
  }
  return typeMap[platform] || 'info'
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getStatusType(status: string): string {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

function getStatusText(status: string): string {
  switch (status) {
    case 'success': return '成功'
    case 'failed': return '失败'
    case 'running': return '运行中'
    default: return status
  }
}

async function fetchStats() {
  try {
    const response = await adminApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

async function fetchLogs() {
  loadingLogs.value = true
  try {
    const response = await adminApi.getCrawlLogs(50)
    logs.value = response.data.items
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  } finally {
    loadingLogs.value = false
  }
}

async function triggerCrawl(platform: string) {
  const key = platform as keyof typeof crawling.value
  crawling.value[key] = true
  try {
    const response = await adminApi.triggerCrawl(platform === 'all' ? undefined : platform)
    ElMessage.success(response.data.message)
    setTimeout(() => {
      fetchLogs()
      fetchStats()
    }, 1000)
  } catch (error) {
    ElMessage.error('触发爬取失败')
  } finally {
    crawling.value[key] = false
  }
}

async function handleCleanup() {
  cleaning.value = true
  try {
    const response = await adminApi.cleanupOldData(7)
    ElMessage.success(response.data.message)
    fetchStats()
  } catch (error) {
    ElMessage.error('清理数据失败')
  } finally {
    cleaning.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchLogs()
  fetchAuditLogs()
})
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.el-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content h1 {
  font-size: 28px;
  color: #667eea;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(102, 126, 234, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

:deep(.el-card) {
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: none;
  overflow: hidden;
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
  transform: translateY(-5px);
}

.stats-card .stat-item {
  text-align: center;
  padding: 25px 15px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stats-card .stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 8px;
  font-weight: 500;
}

.crawl-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.audit-filters {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
  padding: 15px 10px;
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover) {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
}

:deep(.el-tag) {
  border-radius: 8px;
  padding: 4px 10px;
  font-weight: 500;
}

:deep(.el-row) {
  margin-bottom: 0 !important;
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 20px;
  }

  .el-main {
    padding: 15px 10px;
  }

  .stat-value {
    font-size: 28px;
  }

  .crawl-actions {
    gap: 8px;
  }
}
</style>