<template>
  <div class="hot-topics-view">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🔥 热点聚合</h1>
          <div class="header-actions">
            <el-button @click="toggleTheme">
              <el-icon v-if="settingsStore.isDark"><Sunny /></el-icon>
              <el-icon v-else><Moon /></el-icon>
            </el-button>
            <el-button @click="goToAdmin">
              <el-icon><Setting /></el-icon>
              管理
            </el-button>
          </div>
        </div>
      </el-header>

      <el-main>
        <el-card>
          <div class="filters">
            <el-radio-group v-model="selectedPlatform" @change="handlePlatformChange">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="weibo">微博</el-radio-button>
              <el-radio-button label="douyin">抖音</el-radio-button>
              <el-radio-button label="zhihu">知乎</el-radio-button>
              <el-radio-button label="toutiao">头条</el-radio-button>
            </el-radio-group>

            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              :clearable="true"
            />

            <el-button @click="goToHistory">
              <el-icon><Clock /></el-icon>
              历史记录
            </el-button>
            <el-button @click="goToRecycleBin">
              <el-icon><Delete /></el-icon>
              回收站
            </el-button>

            <el-button
              v-if="selectedIds.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedIds.length }})
            </el-button>
            <el-button
              v-if="selectedIds.length > 0"
              @click="clearSelection"
            >
              取消选择
            </el-button>
          </div>

          <el-table
            v-loading="store.loading"
            :data="store.topics"
            style="width: 100%"
            :row-class-name="getRowClass"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="rank" label="排名" width="80" sortable>
              <template #default="{ row }">
                <span :class="getRankClass(row.rank)">{{ row.rank }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag :type="getPlatformType(row.platform)" size="small">
                  {{ getPlatformName(row.platform) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="热点标题" min-width="300">
              <template #default="{ row }">
                <a :href="row.url" target="_blank" class="topic-link">
                  {{ row.title }}
                </a>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="摘要" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="summary-text">{{ row.summary || '暂无摘要' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="hot_value" label="热度值" width="120" sortable>
              <template #default="{ row }">
                {{ formatHotValue(row.hot_value) }}
              </template>
            </el-table-column>
            <el-table-column prop="crawl_time" label="爬取时间" width="150">
              <template #default="{ row }">
                {{ formatTime(row.crawl_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDelete(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="store.pageSize"
              :total="store.total"
              layout="total, prev, pager, next"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '../stores/settings'
import { useHotTopicsStore } from '../stores/hotTopics'
import { Sunny, Moon, Setting, Clock, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { hotTopicsApi } from '../api'
import type { Platform, HotTopic } from '../types'

const router = useRouter()
const settingsStore = useSettingsStore()
const store = useHotTopicsStore()

const selectedPlatform = ref('')
const selectedDate = ref('')
const currentPage = ref(1)
const selectedIds = ref<number[]>([])

function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const platformNames: Record<Platform, string> = {
  'weibo': '微博',
  'douyin': '抖音',
  'zhihu': '知乎',
  'toutiao': '头条'
}

function toggleTheme() {
  settingsStore.toggleTheme()
}

function goToAdmin() {
  router.push('/admin')
}

function goToHistory() {
  router.push('/history')
}

function goToRecycleBin() {
  router.push('/recycle-bin')
}

function handlePlatformChange(value: string) {
  store.setPlatform(value || undefined)
}

function handleDateChange(value: string) {
  store.setDate(value || undefined)
}

function handlePageChange(page: number) {
  store.setPage(page)
}

function formatHotValue(value: number): string {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(1) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(1) + '万'
  }
  return value.toString()
}

function formatTime(timeStr: string): string {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getRankClass(rank: number): string {
  if (rank <= 3) return 'rank-top'
  return ''
}

function getRowClass({ row }: { row: { rank: number } }): string {
  if (row.rank <= 3) return 'row-top'
  return ''
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

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条热点信息吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await hotTopicsApi.deleteHotTopic(id)
    ElMessage.success('删除成功')
    store.fetchTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleSelectionChange(selection: HotTopic[]) {
  selectedIds.value = selection.map(item => item.id)
}

function clearSelection() {
  selectedIds.value = []
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条热点信息吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await hotTopicsApi.batchDeleteHotTopics(selectedIds.value)
    ElMessage.success(`成功删除 ${selectedIds.value.length} 条热点`)
    selectedIds.value = []
    store.fetchTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

onMounted(() => {
  const today = formatDate(new Date())
  selectedDate.value = today
  store.setDate(today)
})
</script>

<style scoped>
.hot-topics-view {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.el-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.topic-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.topic-link:hover {
  color: #764ba2;
  text-decoration: underline;
  transform: translateX(5px);
}

.summary-text {
  color: #666;
  font-size: 13px;
}

.rank-top {
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 18px;
}

:deep(.row-top) {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
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
  transform: scale(1.01);
}

:deep(.el-tag) {
  border-radius: 8px;
  padding: 4px 10px;
  font-weight: 500;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-radio-button__inner) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 8px;
}

:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dark-mode .el-header {
  background: rgba(45, 45, 45, 0.95);
  border-bottom-color: rgba(102, 126, 234, 0.3);
}

.dark-mode .el-card {
  background: rgba(45, 45, 45, 0.9);
}

.dark-mode .header-content h1 {
  color: #e0e0e0;
}

.dark-mode .topic-link {
  color: #8b9fe8;
}

.dark-mode .rank-top {
  background: linear-gradient(135deg, #8b9fe8, #9f7aea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark-mode .summary-text {
  color: #aaa;
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 20px;
  }

  .filters {
    gap: 10px;
  }

  .el-main {
    padding: 15px 10px;
  }
}
</style>