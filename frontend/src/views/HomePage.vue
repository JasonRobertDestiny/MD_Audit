<template>
  <div class="space-y-8">
    <!-- Hero Section -->
    <div v-if="!currentReport" class="text-center py-8">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        AI 驱动的 SEO 分析
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        Markdown <span class="text-gradient">SEO 诊断</span>
      </h1>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto">
        上传你的 Markdown 文件，获得专业的 SEO 质量评估报告，包含元数据分析、结构检查和 AI 语义分析
      </p>
    </div>

    <!-- 文件上传器 -->
    <FileUploader @upload-success="handleUploadSuccess" />

    <!-- 诊断报告 -->
    <transition name="fade-slide">
      <div v-if="currentReport">
        <ReportViewer :report="currentReport.report" />

        <div class="mt-8 flex justify-center gap-4">
          <button @click="currentReport = null" class="btn-secondary">
            <svg class="w-5 h-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            再次分析
          </button>
          <router-link to="/history" class="btn-primary">
            <svg class="w-5 h-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            查看历史记录
          </router-link>
        </div>
      </div>
    </transition>

    <!-- 功能介绍 -->
    <div v-if="!currentReport" class="grid md:grid-cols-3 gap-6 mt-12">
      <div class="card hover-lift text-center">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-800 mb-2">元数据检查</h3>
        <p class="text-sm text-gray-600">
          分析 title、description 等 SEO 关键元数据的完整性和质量
        </p>
      </div>

      <div class="card hover-lift text-center">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-100 to-purple-200 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-800 mb-2">结构分析</h3>
        <p class="text-sm text-gray-600">
          检查标题层级、内容组织和文档结构的 SEO 友好性
        </p>
      </div>

      <div class="card hover-lift text-center">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-100 to-emerald-200 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-800 mb-2">AI 语义分析</h3>
        <p class="text-sm text-gray-600">
          使用 AI 模型进行深度内容分析和优化建议
        </p>
      </div>
    </div>

    <!-- 使用说明 -->
    <div v-if="!currentReport" class="card bg-gradient-to-r from-blue-50 to-purple-50 border-blue-100">
      <div class="flex items-start gap-4">
        <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
          <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 class="font-semibold text-gray-800 mb-2">使用说明</h3>
          <ul class="space-y-1.5 text-sm text-gray-600">
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              支持 .md、.txt、.markdown 格式文件
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              文件大小限制 10MB
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              获得 100 分制评分和详细优化建议
            </li>
            <li class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              历史记录自动保存，方便对比改进效果
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUploader from '../components/FileUploader.vue'
import ReportViewer from '../components/ReportViewer.vue'

const currentReport = ref(null)

const handleUploadSuccess = (data) => {
  currentReport.value = data
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
