<template>
  <div class="card">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        诊断历史
      </h2>
      <select
        v-model="severityFilter"
        @change="loadHistory"
        class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 transition-all"
      >
        <option value="all">全部记录</option>
        <option value="error">有严重问题</option>
        <option value="warning">有建议优化</option>
      </select>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center py-16">
      <div class="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-500 animate-spin"></div>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="items.length === 0" class="empty-state">
      <div class="w-20 h-20 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
        <svg class="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p class="text-lg font-medium text-gray-700">暂无诊断记录</p>
      <p class="text-sm text-gray-500 mt-1">上传你的第一个 Markdown 文件开始分析</p>
      <router-link to="/" class="btn-primary mt-6">
        <svg class="w-5 h-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        开始诊断
      </router-link>
    </div>

    <!-- 记录列表 -->
    <div v-else class="space-y-3">
      <div
        v-for="item in items"
        :key="item.id"
        @click="$emit('view-detail', item.id)"
        class="group p-4 bg-gray-50/50 border border-gray-100 rounded-xl hover:bg-white hover:border-blue-200 hover:shadow-md transition-all cursor-pointer"
      >
        <div class="flex items-center gap-4">
          <!-- 评分 -->
          <div :class="['w-16 h-16 rounded-xl flex flex-col items-center justify-center shrink-0', getScoreBgClass(item.total_score)]">
            <span :class="['text-2xl font-bold', getScoreTextClass(item.total_score)]">
              {{ Math.round(item.total_score) }}
            </span>
            <span class="text-xs text-gray-500">分</span>
          </div>

          <!-- 文件信息 -->
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-800 truncate group-hover:text-blue-600 transition-colors">
              {{ item.file_name }}
            </h3>
            <p class="text-sm text-gray-500 mt-1 flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ formatTime(item.timestamp) }}
            </p>
          </div>

          <!-- 问题统计 -->
          <div class="flex items-center gap-2 shrink-0">
            <span v-if="item.severity_counts.error > 0" class="badge badge-error">
              {{ item.severity_counts.error }} 严重
            </span>
            <span v-if="item.severity_counts.warning > 0" class="badge badge-warning">
              {{ item.severity_counts.warning }} 建议
            </span>
            <span v-if="!item.severity_counts.error && !item.severity_counts.warning" class="badge badge-success">
              全部通过
            </span>
          </div>

          <!-- 箭头 -->
          <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-6">
        <button
          @click="loadHistory(currentPage - 1)"
          :disabled="currentPage === 1"
          class="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div class="flex items-center gap-1">
          <template v-for="page in visiblePages" :key="page">
            <button
              v-if="page !== '...'"
              @click="loadHistory(page)"
              :class="[
                'w-10 h-10 rounded-lg font-medium transition-all',
                page === currentPage
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-600'
              ]"
            >
              {{ page }}
            </button>
            <span v-else class="w-10 h-10 flex items-center justify-center text-gray-400">...</span>
          </template>
        </div>

        <button
          @click="loadHistory(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getHistory } from '../api/client'
import { formatRelativeTime } from '../utils/format'

const emit = defineEmits(['view-detail'])

const items = ref([])
const loading = ref(false)
const severityFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 计算可见页码
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

// 加载历史记录
const loadHistory = async (page = currentPage.value) => {
  loading.value = true
  try {
    const data = await getHistory(page, pageSize.value, severityFilter.value)
    items.value = data.items
    total.value = data.total
    currentPage.value = data.page
  } catch (err) {
    console.error('历史记录加载失败:', err)
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => formatRelativeTime(timestamp)

// 评分背景样式
const getScoreBgClass = (score) => {
  if (score >= 90) return 'bg-emerald-100'
  if (score >= 70) return 'bg-blue-100'
  if (score >= 50) return 'bg-amber-100'
  return 'bg-red-100'
}

// 评分文字样式
const getScoreTextClass = (score) => {
  if (score >= 90) return 'text-emerald-600'
  if (score >= 70) return 'text-blue-600'
  if (score >= 50) return 'text-amber-600'
  return 'text-red-600'
}

onMounted(() => {
  loadHistory()
})

defineExpose({ loadHistory })
</script>
