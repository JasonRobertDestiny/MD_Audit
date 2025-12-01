<template>
  <!-- Fixed: use relevance_score instead of keyword_score -->
  <div v-if="report" class="space-y-6 animate-fade-in">
    <!-- 总分卡片 -->
    <div class="card-glass relative overflow-hidden">
      <!-- 庆祝粒子效果 - 仅在高分时显示 -->
      <div v-if="isExcellent && showCelebration" class="celebration-particles">
        <div v-for="i in 12" :key="i"
             class="confetti-particle"
             :style="getConfettiStyle(i)"></div>
      </div>

      <div class="flex flex-col md:flex-row items-center gap-8">
        <!-- 环形分数 -->
        <div class="relative" :class="{ 'celebrate': showCelebration && isExcellent }">
          <!-- 高分光晕效果 -->
          <div v-if="isExcellent"
               class="absolute inset-0 rounded-full"
               :class="showCelebration ? 'success-glow' : ''"></div>

          <svg class="w-40 h-40 transform -rotate-90 relative z-10">
            <!-- 背景环 -->
            <circle
              cx="80" cy="80" r="70"
              fill="none"
              stroke-width="12"
              class="stroke-gray-200"
            />
            <!-- 进度环 - 带渐变 -->
            <defs>
              <linearGradient :id="'scoreGradient-' + report.total_score" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" :stop-color="scoreGradientStart" />
                <stop offset="100%" :stop-color="scoreGradientEnd" />
              </linearGradient>
            </defs>
            <circle
              cx="80" cy="80" r="70"
              fill="none"
              stroke-width="12"
              stroke-linecap="round"
              :stroke="isExcellent ? `url(#scoreGradient-${report.total_score})` : scoreColor"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="animatedOffset"
              class="transition-all duration-1000 ease-out"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center z-10">
            <span class="text-4xl font-bold transition-all duration-500"
                  :class="{ 'text-aurora': isExcellent }"
                  :style="!isExcellent ? { color: scoreColor } : {}">
              {{ displayScore }}
            </span>
            <span class="text-sm text-gray-500">总分</span>
            <!-- 高分时显示星星 -->
            <div v-if="isExcellent && showCelebration" class="flex gap-1 mt-1">
              <svg v-for="star in 3" :key="star"
                   class="w-4 h-4 text-amber-400 twinkle"
                   :style="{ animationDelay: `${star * 0.2}s` }"
                   fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- 分项得分 -->
        <div class="flex-1 w-full">
          <div class="flex items-center justify-between gap-4 mb-4">
            <h2 class="text-xl font-bold text-gray-800 flex items-center gap-2">
              <span :class="['badge', scoreBadgeClass]">{{ scoreLabel }}</span>
              SEO 质量评估
            </h2>

            <!-- 下载报告按钮 -->
            <button
              @click="downloadReport"
              :disabled="isDownloading"
              class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                v-if="!isDownloading"
                class="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <svg
                v-else
                class="w-5 h-5 mr-2 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              {{ isDownloading ? '生成中...' : '下载报告' }}
            </button>
          </div>

          <div class="space-y-3">
            <ScoreBar label="元数据" :score="report.metadata_score" :max="15" color="blue" />
            <ScoreBar label="搜索意图" :score="report.intent_score || 0" :max="5" color="rose" />
            <ScoreBar label="内容深度" :score="report.content_depth_score || 0" :max="20" color="cyan" />
            <ScoreBar label="E-E-A-T" :score="report.eeat_score || 0" :max="15" color="violet" />
            <ScoreBar label="内容结构" :score="report.structure_score" :max="15" color="purple" />
            <ScoreBar label="AI搜索优化" :score="report.ai_search_score || 0" :max="10" color="amber" />
            <ScoreBar label="关键词" :score="report.keyword_score || 0" :max="10" color="orange" />
            <ScoreBar label="AI语义" :score="report.ai_score" :max="10" color="emerald" />
          </div>
        </div>
      </div>
    </div>

    <!-- 问题分类 -->
    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <!-- 严重问题 -->
      <div v-if="errorItems.length > 0" class="card hover:shadow-lg">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-red-700">
            严重问题
            <span class="badge badge-error ml-2">{{ errorItems.length }}</span>
          </h3>
        </div>
        <div class="space-y-2 max-h-80 overflow-y-auto pr-2">
          <DiagnosticItem
            v-for="(item, index) in errorItems"
            :key="'error-' + index"
            :item="item"
            severity="error"
          />
        </div>
      </div>

      <!-- 建议优化 -->
      <div v-if="warningItems.length > 0" class="card hover:shadow-lg">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-amber-700">
            建议优化
            <span class="badge badge-warning ml-2">{{ warningItems.length }}</span>
          </h3>
        </div>
        <div class="space-y-2 max-h-80 overflow-y-auto pr-2">
          <DiagnosticItem
            v-for="(item, index) in warningItems"
            :key="'warning-' + index"
            :item="item"
            severity="warning"
          />
        </div>
      </div>

      <!-- 检查通过 -->
      <div v-if="successItems.length > 0" class="card hover:shadow-lg">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-emerald-700">
            检查通过
            <span class="badge badge-success ml-2">{{ successItems.length }}</span>
          </h3>
        </div>
        <div class="space-y-2 max-h-80 overflow-y-auto pr-2">
          <DiagnosticItem
            v-for="(item, index) in successItems"
            :key="'success-' + index"
            :item="item"
            severity="success"
          />
        </div>
      </div>
    </div>

    <!-- AI 智能分析 -->
    <div v-if="report.ai_analysis" class="card-glass border border-emerald-200/50">
      <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        AI 智能分析
        <span class="badge badge-success text-xs">GPT-4o</span>
      </h3>

      <!-- AI 综合评价 -->
      <div v-if="report.ai_analysis.overall_feedback" class="mb-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-100">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <div>
            <h4 class="text-sm font-medium text-emerald-700 mb-1">AI 综合评价</h4>
            <p class="text-gray-700">{{ report.ai_analysis.overall_feedback }}</p>
          </div>
        </div>
      </div>

      <!-- AI 详细评分 - 2024 SEO 4维度 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="text-center p-3 bg-white/60 rounded-lg border border-gray-100">
          <div class="text-2xl font-bold" :class="getAIScoreColor(report.ai_analysis.eeat_score)">
            {{ Math.round(report.ai_analysis.eeat_score || 0) }}
          </div>
          <div class="text-xs text-gray-500 mt-1">E-E-A-T</div>
        </div>
        <div class="text-center p-3 bg-white/60 rounded-lg border border-gray-100">
          <div class="text-2xl font-bold" :class="getAIScoreColor(report.ai_analysis.depth_score)">
            {{ Math.round(report.ai_analysis.depth_score || 0) }}
          </div>
          <div class="text-xs text-gray-500 mt-1">内容深度</div>
        </div>
        <div class="text-center p-3 bg-white/60 rounded-lg border border-gray-100">
          <div class="text-2xl font-bold" :class="getAIScoreColor(report.ai_analysis.readability_score)">
            {{ Math.round(report.ai_analysis.readability_score || 0) }}
          </div>
          <div class="text-xs text-gray-500 mt-1">可读性</div>
        </div>
        <div class="text-center p-3 bg-white/60 rounded-lg border border-gray-100">
          <div class="text-2xl font-bold" :class="getAIScoreColor(report.ai_analysis.topical_relevance_score)">
            {{ Math.round(report.ai_analysis.topical_relevance_score || 0) }}
          </div>
          <div class="text-xs text-gray-500 mt-1">主题相关性</div>
        </div>
      </div>

      <!-- E-E-A-T 详细评价 -->
      <div v-if="report.ai_analysis.eeat_details" class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
        <h4 class="text-sm font-medium text-blue-700 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          E-E-A-T 详细评价（Google 2025 SEO核心标准）
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div class="flex items-start gap-2">
            <span class="font-medium text-blue-600 whitespace-nowrap">Experience:</span>
            <span class="text-gray-700">{{ report.ai_analysis.eeat_details.experience || '未评估' }}</span>
          </div>
          <div class="flex items-start gap-2">
            <span class="font-medium text-blue-600 whitespace-nowrap">Expertise:</span>
            <span class="text-gray-700">{{ report.ai_analysis.eeat_details.expertise || '未评估' }}</span>
          </div>
          <div class="flex items-start gap-2">
            <span class="font-medium text-blue-600 whitespace-nowrap">Authoritativeness:</span>
            <span class="text-gray-700">{{ report.ai_analysis.eeat_details.authoritativeness || '未评估' }}</span>
          </div>
          <div class="flex items-start gap-2">
            <span class="font-medium text-blue-600 whitespace-nowrap">Trustworthiness:</span>
            <span class="text-gray-700">{{ report.ai_analysis.eeat_details.trustworthiness || '未评估' }}</span>
          </div>
        </div>
      </div>

      <!-- AI 改进建议 -->
      <div v-if="report.ai_analysis.improvement_suggestions?.length > 0">
        <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI 改进建议
        </h4>
        <ul class="space-y-2">
          <li
            v-for="(suggestion, index) in report.ai_analysis.improvement_suggestions"
            :key="index"
            class="flex items-start gap-2 p-3 bg-amber-50/50 rounded-lg border border-amber-100"
          >
            <span class="w-5 h-5 rounded-full bg-amber-100 text-amber-700 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              {{ index + 1 }}
            </span>
            <span class="text-gray-700 text-sm">{{ suggestion }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 无 AI 分析时的提示 -->
    <div v-else-if="report.ai_score === 0" class="card border border-gray-200 bg-gray-50/50">
      <div class="flex items-center gap-3 text-gray-500">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm">AI 分析未启用或暂时不可用，当前显示基于规则的诊断结果</span>
      </div>
    </div>

    <!-- 关键词信息 -->
    <div v-if="report.extracted_keywords?.length > 0" class="card">
      <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
        提取的关键词
      </h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="keyword in report.extracted_keywords.slice(0, 15)"
          :key="keyword"
          class="keyword-tag"
        >
          {{ keyword }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import DiagnosticItem from './DiagnosticItem.vue'
import ScoreBar from './ScoreBar.vue'
import { getScoreGrade } from '../utils/format'
import apiClient from '../api/client'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

// 环形进度条参数
const circumference = 2 * Math.PI * 70 // 约439.8

// 动画状态
const showCelebration = ref(false)
const displayScore = ref(0)
const animatedOffset = ref(circumference)
const isDownloading = ref(false)

// 是否是优秀分数
const isExcellent = computed(() => props.report.total_score >= 85)

// 分数渐变色 - 用于高分
const scoreGradientStart = computed(() => {
  const score = props.report.total_score
  if (score >= 90) return '#10b981'
  if (score >= 85) return '#22c55e'
  return '#3b82f6'
})

const scoreGradientEnd = computed(() => {
  const score = props.report.total_score
  if (score >= 90) return '#34d399'
  if (score >= 85) return '#4ade80'
  return '#60a5fa'
})

// 生成彩纸粒子样式
const getConfettiStyle = (index) => {
  const colors = ['#10b981', '#3b82f6', '#a78bfa', '#f472b6', '#fbbf24', '#22d3d3']
  const color = colors[index % colors.length]
  const left = 10 + (index * 7) % 80
  const delay = (index * 0.1) % 1
  const duration = 1 + (index % 3) * 0.3

  return {
    backgroundColor: color,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
  }
}

// 数字滚动动画
const animateScore = () => {
  const targetScore = Math.round(props.report.total_score)
  const duration = 1000
  const startTime = Date.now()

  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // 缓动函数 - easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3)

    displayScore.value = Math.round(targetScore * eased)
    animatedOffset.value = circumference * (1 - (props.report.total_score / 100) * eased)

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      // 动画完成，触发庆祝效果
      if (isExcellent.value) {
        showCelebration.value = true
      }
    }
  }

  requestAnimationFrame(animate)
}

// 监听 report 变化
watch(() => props.report, () => {
  showCelebration.value = false
  displayScore.value = 0
  animatedOffset.value = circumference
  setTimeout(animateScore, 100)
}, { immediate: true })

onMounted(() => {
  animateScore()
})

const progressOffset = computed(() => {
  const progress = props.report.total_score / 100
  return circumference * (1 - progress)
})

// 分数颜色
const scoreColor = computed(() => {
  const score = props.report.total_score
  if (score >= 90) return '#10b981' // emerald
  if (score >= 70) return '#3b82f6' // blue
  if (score >= 50) return '#f59e0b' // amber
  return '#ef4444' // red
})

// 分数标签样式
const scoreBadgeClass = computed(() => {
  const score = props.report.total_score
  if (score >= 90) return 'badge-success'
  if (score >= 70) return 'badge-primary'
  if (score >= 50) return 'badge-warning'
  return 'badge-error'
})

// 分数标签
const scoreLabel = computed(() => getScoreGrade(props.report.total_score))

// 分类诊断项（后端使用 critical/warning/info/success）
const errorItems = computed(() =>
  props.report.diagnostics?.filter(d => d.severity === 'critical') || []
)

const warningItems = computed(() =>
  props.report.diagnostics?.filter(d => d.severity === 'warning' || d.severity === 'info') || []
)

const successItems = computed(() =>
  props.report.diagnostics?.filter(d => d.severity === 'success') || []
)

// AI 分数颜色
const getAIScoreColor = (score) => {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-amber-600'
  return 'text-red-600'
}

// 下载Markdown报告
const downloadReport = async () => {
  if (isDownloading.value) return

  isDownloading.value = true
  try {
    // 调用后端导出接口获取Markdown内容
    const blob = await apiClient.exportMarkdownReport(props.report)

    // 构造下载链接，兼容不同路径分隔符
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const fileName = props.report.file_path
      ? props.report.file_path.split(/[\\/]/).pop().replace('.md', '') + '_seo_report.md'
      : 'seo_report.md'

    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()

    // 清理临时节点与对象URL
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载报告失败:', error)
    alert('下载报告失败，请重试')
  } finally {
    isDownloading.value = false
  }
}
</script>

<style scoped>
/* 庆祝粒子容器 */
.celebration-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

/* 彩纸粒子 */
.confetti-particle {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  top: 50%;
  opacity: 0;
  animation: confettiPop 1.5s ease-out forwards;
}

@keyframes confettiPop {
  0% {
    transform: translateY(0) rotate(0deg) scale(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
    transform: translateY(-20px) rotate(90deg) scale(1);
  }
  100% {
    transform: translateY(-120px) rotate(720deg) scale(0.5);
    opacity: 0;
  }
}
</style>
