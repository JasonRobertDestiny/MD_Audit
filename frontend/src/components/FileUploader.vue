<template>
  <div class="card">
    <h2 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      上传 Markdown 文件
    </h2>

    <!-- 拖拽上传区 -->
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      :class="[
        'upload-zone group',
        isDragging ? 'upload-zone-active' : 'upload-zone-default'
      ]"
      @click="$refs.fileInput.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".md,.txt,.markdown"
        @change="handleFileSelect"
        class="hidden"
      />

      <!-- 上传中状态 - 高级动画 -->
      <div v-if="uploading" class="flex flex-col items-center py-4">
        <!-- 高级加载器 -->
        <div class="relative mb-6">
          <!-- 外层光晕 -->
          <div class="absolute inset-0 w-20 h-20 -m-2 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 opacity-20 animate-ping"></div>
          <!-- 旋转渐变环 -->
          <div class="w-16 h-16 rounded-full border-4 border-gray-200 relative overflow-hidden">
            <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 border-r-purple-500 animate-spin"></div>
            <!-- 中心波浪加载器 -->
            <div class="absolute inset-2 flex items-end justify-center gap-0.5">
              <div class="w-1 h-3 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full wave-bar"></div>
              <div class="w-1 h-3 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full wave-bar"></div>
              <div class="w-1 h-3 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full wave-bar"></div>
              <div class="w-1 h-3 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full wave-bar"></div>
              <div class="w-1 h-3 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full wave-bar"></div>
            </div>
          </div>
        </div>

        <p class="text-lg font-semibold text-aurora">正在分析中...</p>
        <p class="text-sm text-gray-500 mt-1">智能诊断引擎工作中</p>

        <!-- 进度步骤 - 带动画 -->
        <div class="mt-6 flex items-center gap-4">
          <div class="flex items-center gap-2" :class="analysisStep >= 1 ? 'text-blue-600' : 'text-gray-400'">
            <div class="relative">
              <div class="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300"
                   :class="analysisStep >= 1 ? 'bg-blue-100' : 'bg-gray-100'">
                <svg v-if="analysisStep > 1" class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else class="w-2 h-2 rounded-full" :class="analysisStep === 1 ? 'bg-blue-500 animate-pulse' : 'bg-gray-300'"></span>
              </div>
              <div v-if="analysisStep === 1" class="absolute inset-0 w-8 h-8 rounded-full bg-blue-400 opacity-30 animate-ping"></div>
            </div>
            <span class="text-sm font-medium">解析</span>
          </div>

          <div class="w-8 h-0.5 rounded-full transition-all duration-500" :class="analysisStep >= 2 ? 'bg-blue-400' : 'bg-gray-200'"></div>

          <div class="flex items-center gap-2" :class="analysisStep >= 2 ? 'text-blue-600' : 'text-gray-400'">
            <div class="relative">
              <div class="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300"
                   :class="analysisStep >= 2 ? 'bg-blue-100' : 'bg-gray-100'">
                <svg v-if="analysisStep > 2" class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else class="w-2 h-2 rounded-full" :class="analysisStep === 2 ? 'bg-blue-500 animate-pulse' : 'bg-gray-300'"></span>
              </div>
              <div v-if="analysisStep === 2" class="absolute inset-0 w-8 h-8 rounded-full bg-blue-400 opacity-30 animate-ping"></div>
            </div>
            <span class="text-sm font-medium">规则</span>
          </div>

          <div class="w-8 h-0.5 rounded-full transition-all duration-500" :class="analysisStep >= 3 ? 'bg-blue-400' : 'bg-gray-200'"></div>

          <div class="flex items-center gap-2" :class="analysisStep >= 3 ? 'text-purple-600' : 'text-gray-400'">
            <div class="relative">
              <div class="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300"
                   :class="analysisStep >= 3 ? 'bg-purple-100' : 'bg-gray-100'">
                <span class="w-2 h-2 rounded-full" :class="analysisStep === 3 ? 'bg-purple-500 animate-pulse' : 'bg-gray-300'"></span>
              </div>
              <div v-if="analysisStep === 3" class="absolute inset-0 w-8 h-8 rounded-full bg-purple-400 opacity-30 animate-ping"></div>
            </div>
            <span class="text-sm font-medium">AI</span>
          </div>
        </div>

        <!-- Shimmer进度条 -->
        <div class="mt-6 w-full max-w-xs h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 rounded-full shimmer"
               :style="{ width: progressWidth + '%' }"></div>
        </div>
      </div>

      <!-- 默认状态 -->
      <div v-else class="flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
          <svg class="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <p class="mt-4 text-lg font-medium text-gray-700">
          拖拽文件到这里，或<span class="text-blue-600">点击选择</span>
        </p>
        <p class="text-sm text-gray-500 mt-2">
          支持 .md, .txt, .markdown 格式，最大 10MB
        </p>
      </div>
    </div>

    <!-- 已选择文件 -->
    <transition name="slide-up">
      <div v-if="selectedFile && !uploading" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-800 truncate">{{ selectedFile.name }}</p>
            <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <button
            @click.stop="selectedFile = null"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <button
          @click="uploadFile"
          class="btn-primary w-full mt-4"
        >
          <svg class="w-5 h-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          开始诊断分析
        </button>
      </div>
    </transition>

    <!-- 错误提示 -->
    <transition name="slide-up">
      <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
        <svg class="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <p class="font-medium text-red-800">上传失败</p>
          <p class="text-sm text-red-600 mt-1">{{ error }}</p>
        </div>
        <button
          @click="error = ''"
          class="p-1 text-red-400 hover:text-red-600 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { analyzeFile } from '../api/client'
import { validateFile } from '../utils/validation'
import { formatFileSize } from '../utils/format'

const emit = defineEmits(['upload-success', 'upload-error'])

const selectedFile = ref(null)
const uploading = ref(false)
const isDragging = ref(false)
const error = ref('')

// 进度动画状态
const analysisStep = ref(0)
const progressWidth = ref(0)
let progressInterval = null
let stepInterval = null

// 启动进度动画
const startProgressAnimation = () => {
  analysisStep.value = 1
  progressWidth.value = 0

  // 进度条动画
  progressInterval = setInterval(() => {
    if (progressWidth.value < 95) {
      // 模拟非线性进度（越来越慢）
      const remaining = 95 - progressWidth.value
      progressWidth.value += remaining * 0.05
    }
  }, 100)

  // 步骤动画
  stepInterval = setTimeout(() => {
    analysisStep.value = 2
    setTimeout(() => {
      analysisStep.value = 3
    }, 2000)
  }, 1500)
}

// 停止进度动画
const stopProgressAnimation = (success = true) => {
  if (progressInterval) clearInterval(progressInterval)
  if (stepInterval) clearTimeout(stepInterval)

  if (success) {
    progressWidth.value = 100
  }

  // 重置状态
  setTimeout(() => {
    analysisStep.value = 0
    progressWidth.value = 0
  }, 500)
}

// 组件卸载时清理
onUnmounted(() => {
  if (progressInterval) clearInterval(progressInterval)
  if (stepInterval) clearTimeout(stepInterval)
})

// 处理拖拽放置
const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

// 处理文件选择
const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    validateAndSetFile(files[0])
  }
}

// 校验并设置文件
const validateAndSetFile = (file) => {
  error.value = ''

  // 使用统一的验证工具
  const validation = validateFile(file)

  if (!validation.valid) {
    error.value = validation.errors.join('；')
    return
  }

  if (file.size === 0) {
    error.value = '文件为空（0字节）'
    return
  }

  selectedFile.value = file
}

// 上传文件
const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  error.value = ''
  startProgressAnimation()

  try {
    const data = await analyzeFile(selectedFile.value)
    stopProgressAnimation(true)
    emit('upload-success', data)
    selectedFile.value = null
  } catch (err) {
    stopProgressAnimation(false)
    error.value = err.message
    emit('upload-error', err)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
