<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center py-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">历史记录</h1>
      <p class="text-gray-600">
        查看过去的诊断记录，对比改进效果
      </p>
    </div>

    <!-- 历史记录列表 -->
    <HistoryList
      ref="historyListRef"
      @view-detail="viewDetail"
    />

    <!-- 历史记录详情弹窗 -->
    <transition name="modal">
      <div
        v-if="showDetail"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="closeDetail"
      >
        <!-- 遮罩 -->
        <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="closeDetail"></div>

        <!-- 弹窗内容 -->
        <div class="relative min-h-screen flex items-center justify-center p-4">
          <div class="relative bg-white rounded-2xl max-w-4xl w-full max-h-[85vh] overflow-hidden shadow-2xl animate-scale-in">
            <!-- Header -->
            <div class="sticky top-0 bg-white/90 backdrop-blur-sm border-b border-gray-100 p-4 flex items-center justify-between z-10">
              <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
                <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                诊断报告详情
              </h2>
              <button
                @click="closeDetail"
                class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Loading -->
            <div v-if="loadingDetail" class="p-16 flex flex-col items-center justify-center">
              <div class="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-500 animate-spin"></div>
              <p class="mt-4 text-gray-500">加载中...</p>
            </div>

            <!-- Content -->
            <div v-else-if="detailReport" class="p-6 overflow-y-auto max-h-[calc(85vh-80px)]">
              <ReportViewer :report="detailReport" />
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import HistoryList from '../components/HistoryList.vue'
import ReportViewer from '../components/ReportViewer.vue'
import { getHistoryDetail } from '../api/client'

const historyListRef = ref(null)
const showDetail = ref(false)
const loadingDetail = ref(false)
const detailReport = ref(null)

// 查看详情
const viewDetail = async (recordId) => {
  showDetail.value = true
  loadingDetail.value = true
  detailReport.value = null

  try {
    const data = await getHistoryDetail(recordId)
    detailReport.value = data.report
  } catch (err) {
    console.error('历史记录详情加载失败:', err)
    alert('加载失败，请稍后重试')
    closeDetail()
  } finally {
    loadingDetail.value = false
  }
}

// 关闭详情
const closeDetail = () => {
  showDetail.value = false
  detailReport.value = null
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .animate-scale-in,
.modal-leave-to .animate-scale-in {
  transform: scale(0.95);
}
</style>
