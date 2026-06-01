<template>
  <div class="recycle-bin-view">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🗑️ 回收站</h1>
          <div class="header-actions">
            <el-button @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
          </div>
        </div>
      </el-header>

      <el-main>
        <el-card>
          <div class="filters">
            <el-radio-group v-model="selectedPlatform" @change="handlePlatformChange">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="weibo">微博</el-radio-button>
              <el-radio-button value="douyin">抖音</el-radio-button>
              <el-radio-button value="zhihu">知乎</el-radio-button>
              <el-radio-button value="toutiao">头条</el-radio-button>
            </el-radio-group>

            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              :clearable="true"
            />

            <el-button
              v-if="selectedIds.length > 0"
              type="primary"
              @click="handleBatchRestore"
            >
              <el-icon><RefreshLeft /></el-icon>
              批量恢复 ({{ selectedIds.length }})
            </el-button>
            <el-button
              v-if="selectedIds.length > 0"
              type="danger"
              @click="handleBatchPurge"
            >
              <el-icon><Delete /></el-icon>
              批量清空 ({{ selectedIds.length }})
            </el-button>
            <el-button
              v-if="selectedIds.length > 0"
              @click="clearSelection"
            >
              取消选择
            </el-button>
            <el-button
              v-if="total > 0 && selectedIds.length === 0"
              type="danger"
              plain
              @click="handlePurgeAll"
            >
              <el-icon><Delete /></el-icon>
              清空所有 ({{ total }})
            </el-button>
          </div>

          <el-table
            v-loading="loading"
            :data="deletedTopics"
            style="width: 100%"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
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
            <el-table-column prop="hot_value" label="热度值" width="120">
              <template #default="{ row }">
                {{ formatHotValue(row.hot_value) }}
              </template>
            </el-table-column>
            <el-table-column prop="deleted_at" label="删除时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.deleted_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="deleted_by" label="操作者" width="150" show-overflow-tooltip />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleRestore(row.id)"
                >
                  恢复
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handlePurge(row.id)"
                >
                  清空
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="20"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, RefreshLeft, Delete } from '@element-plus/icons-vue'
import { hotTopicsApi } from '../api'
import type { HotTopic, Platform } from '../types'

const router = useRouter()

const deletedTopics = ref<HotTopic[]>([])
const loading = ref(false)
const selectedPlatform = ref('')
const dateRange = ref<string[]>([])
const currentPage = ref(1)
const total = ref(0)
const selectedIds = ref<number[]>([])

const platformNames: Record<Platform, string> = {
  'weibo': '微博',
  'douyin': '抖音',
  'zhihu': '知乎',
  'toutiao': '头条'
}

function goBack() {
  router.push('/')
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

function formatHotValue(value: number): string {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(1) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(1) + '万'
  }
  return value.toString()
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

async function fetchDeletedTopics() {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: 20
    }
    
    if (selectedPlatform.value) {
      params.platform = selectedPlatform.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await hotTopicsApi.getDeletedHotTopics(params)
    deletedTopics.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取已删除热点失败')
    console.error('Failed to fetch deleted topics:', error)
  } finally {
    loading.value = false
  }
}

function handlePlatformChange() {
  currentPage.value = 1
  fetchDeletedTopics()
}

function handleDateChange() {
  currentPage.value = 1
  fetchDeletedTopics()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchDeletedTopics()
}

async function handleRestore(id: number) {
  try {
    await ElMessageBox.confirm(
      '确定要恢复这条热点信息吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await hotTopicsApi.restoreHotTopic(id)
    ElMessage.success('恢复成功')
    fetchDeletedTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败')
    }
  }
}

function handleSelectionChange(selection: HotTopic[]) {
  selectedIds.value = selection.map(item => item.id)
}

function clearSelection() {
  selectedIds.value = []
}

async function handleBatchRestore() {
  try {
    await ElMessageBox.confirm(
      `确定要恢复选中的 ${selectedIds.value.length} 条热点信息吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await hotTopicsApi.batchRestoreHotTopics(selectedIds.value)
    ElMessage.success(`成功恢复 ${selectedIds.value.length} 条热点`)
    selectedIds.value = []
    fetchDeletedTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量恢复失败')
    }
  }
}

async function handlePurge(id: number) {
  try {
    await ElMessageBox.confirm(
      '确定要永久删除这条热点信息吗？此操作不可恢复！',
      '危险操作',
      {
        confirmButtonText: '永久删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await hotTopicsApi.batchPurgeHotTopics([id])
    ElMessage.success('永久删除成功')
    fetchDeletedTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('永久删除失败')
    }
  }
}

async function handleBatchPurge() {
  try {
    await ElMessageBox.confirm(
      `确定要永久删除选中的 ${selectedIds.value.length} 条热点信息吗？此操作不可恢复！`,
      '危险操作',
      {
        confirmButtonText: '永久删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await hotTopicsApi.batchPurgeHotTopics(selectedIds.value)
    ElMessage.success(`成功永久删除 ${selectedIds.value.length} 条热点`)
    selectedIds.value = []
    fetchDeletedTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量永久删除失败')
    }
  }
}

async function handlePurgeAll() {
  try {
    await ElMessageBox.confirm(
      `确定要永久删除所有 ${total.value} 条已删除的热点信息吗？此操作不可恢复！`,
      '危险操作',
      {
        confirmButtonText: '永久删除全部',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await hotTopicsApi.purgeAllDeletedHotTopics()
    ElMessage.success('成功永久删除所有已删除热点')
    selectedIds.value = []
    fetchDeletedTopics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空所有失败')
    }
  }
}

onMounted(() => {
  fetchDeletedTopics()
})
</script>

<style scoped>
.recycle-bin-view {
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

.summary-text {
  color: #666;
  font-size: 13px;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>