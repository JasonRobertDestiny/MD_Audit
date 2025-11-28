<template>
  <div
    :class="['diagnostic-card', cardClass]"
    @click="showDetails = !showDetails"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <!-- 标题行 -->
        <div class="flex items-center gap-2 flex-wrap">
          <span :class="['text-sm font-medium', textClass]">
            {{ item.check_name }}
          </span>
          <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">
            {{ item.category }}
          </span>
        </div>

        <!-- 消息 -->
        <p class="text-sm text-gray-600 mt-1.5 line-clamp-2">{{ item.message }}</p>

        <!-- 展开详情 -->
        <transition name="expand">
          <div v-if="showDetails && (item.current_value || item.expected_value)" class="mt-3 space-y-2">
            <div v-if="item.current_value" class="flex items-start gap-2 text-sm">
              <span class="text-gray-500 shrink-0">当前:</span>
              <code class="px-2 py-0.5 bg-gray-100 rounded text-gray-700 text-xs break-all">
                {{ item.current_value }}
              </code>
            </div>
            <div v-if="item.expected_value" class="flex items-start gap-2 text-sm">
              <span class="text-gray-500 shrink-0">建议:</span>
              <code class="px-2 py-0.5 bg-blue-50 rounded text-blue-700 text-xs break-all">
                {{ item.expected_value }}
              </code>
            </div>
          </div>
        </transition>
      </div>

      <!-- 分数 -->
      <div class="flex flex-col items-end shrink-0">
        <span :class="['text-lg font-bold', scoreClass]">
          {{ item.score.toFixed(1) }}
        </span>
        <span class="text-xs text-gray-400">分</span>
      </div>
    </div>

    <!-- 展开提示 -->
    <div v-if="item.current_value || item.expected_value" class="flex justify-center mt-2">
      <svg
        class="w-4 h-4 text-gray-400 transition-transform duration-200"
        :class="{ 'rotate-180': showDetails }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  severity: {
    type: String,
    required: true
  }
})

const showDetails = ref(false)

const cardClass = computed(() => {
  const classes = {
    error: 'diagnostic-card-error',
    warning: 'diagnostic-card-warning',
    success: 'diagnostic-card-success'
  }
  return classes[props.severity] || 'diagnostic-card-success'
})

const textClass = computed(() => {
  const classes = {
    error: 'text-red-700',
    warning: 'text-amber-700',
    success: 'text-emerald-700'
  }
  return classes[props.severity] || 'text-gray-700'
})

const scoreClass = computed(() => {
  const classes = {
    error: 'text-red-600',
    warning: 'text-amber-600',
    success: 'text-emerald-600'
  }
  return classes[props.severity] || 'text-gray-600'
})
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
