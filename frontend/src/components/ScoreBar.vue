<template>
  <div class="flex items-center gap-3">
    <span class="text-sm text-gray-600 w-20 shrink-0">{{ label }}</span>
    <div class="flex-1 h-2.5 bg-gray-100 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-700 ease-out"
        :class="barColorClass"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
    <span class="text-sm font-medium w-16 text-right" :class="textColorClass">
      {{ score.toFixed(1) }}/{{ max }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  score: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    required: true
  },
  color: {
    type: String,
    default: 'blue'
  }
})

const percentage = computed(() => {
  return Math.min((props.score / props.max) * 100, 100)
})

const barColorClass = computed(() => {
  const colors = {
    blue: 'bg-gradient-to-r from-blue-400 to-blue-500',
    purple: 'bg-gradient-to-r from-purple-400 to-purple-500',
    amber: 'bg-gradient-to-r from-amber-400 to-amber-500',
    emerald: 'bg-gradient-to-r from-emerald-400 to-emerald-500',
    red: 'bg-gradient-to-r from-red-400 to-red-500',
  }
  return colors[props.color] || colors.blue
})

const textColorClass = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    purple: 'text-purple-600',
    amber: 'text-amber-600',
    emerald: 'text-emerald-600',
    red: 'text-red-600',
  }
  return colors[props.color] || colors.blue
})
</script>
