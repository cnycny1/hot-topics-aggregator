<template>
  <div class="history-view">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>📅 历史热点</h1>
          <div class="header-actions">
            <el-button @click="goBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
          </div>
        </div>
      </el-header>

      <el-main>
        <el-card>
          <div class="filters">
            <el-date-picker
              v-model="selectedDate"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
            />

            <el-input
              v-model="searchKeyword"
              placeholder="搜索热点关键词"
              clearable
              @clear="handleSearch"
              style="width: 200px"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
          </div>

          <el-table
            v-loading="loading"
            :data="topics"
            style="width: 100%"
          >
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag :type="row.platform === 'weibo' ? 'danger' : 'primary'" size="small">
                  {{ row.platform === 'weibo' ? '微博' : '抖音' }}
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
            <el-table-column prop="hot_value" label="热度值" width="150">
              <template #default="{ row }">
                {{ formatHotValue(row.hot_value) }}
              </template>
            </el-table-column>
            <el-table-column prop="crawl_time" label="爬取时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.crawl_time) }}
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="total"
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
import { hotTopicsApi } from '../api'
import { Search, Back } from '@element-plus/icons-vue'
import type { HotTopic } from '../types'
import { ElMessage } from 'element-plus'

const router = useRouter()

const topics = ref<HotTopic[]>([])
const loading = ref(false)
const selectedDate = ref<string[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

function goBack() {
  router.push('/')
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

async function fetchHistory() {
  loading.value = true
  try {
    if (searchKeyword.value) {
      const response = await hotTopicsApi.searchHotTopics({
        keyword: searchKeyword.value,
        page: currentPage.value,
        page_size: pageSize.value
      })
      topics.value = response.data.items
      total.value = response.data.total
    } else {
      const date = selectedDate.value?.[0] || undefined
      const response = await hotTopicsApi.getHotTopics({
        date,
        page: currentPage.value,
        page_size: pageSize.value
      })
      topics.value = response.data.items
      total.value = response.data.total
    }
  } catch (error) {
    console.error('Failed to fetch history:', error)
    ElMessage.error('获取历史数据失败')
  } finally {
    loading.value = false
  }
}

function handleDateChange() {
  currentPage.value = 1
  fetchHistory()
}

function handleSearch() {
  currentPage.value = 1
  fetchHistory()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchHistory()
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history-view {
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

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 20px;
  }

  .el-main {
    padding: 15px 10px;
  }

  .filters {
    gap: 10px;
  }
}
</style>