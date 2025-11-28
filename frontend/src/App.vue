<template>
  <div id="app" class="min-h-screen flex flex-col relative">
    <!-- Aurora动态背景 -->
    <div class="aurora-bg" aria-hidden="true">
      <!-- 额外的渐变层 -->
      <div class="aurora-layer aurora-layer-1"></div>
      <div class="aurora-layer aurora-layer-2"></div>
    </div>

    <!-- 浮动装饰元素 -->
    <div class="floating-decorations" aria-hidden="true">
      <div class="floating-decoration decoration-circle floating" style="top: 15%; left: 10%;"></div>
      <div class="floating-decoration decoration-square floating-delayed" style="top: 25%; right: 15%;"></div>
      <div class="floating-decoration decoration-ring floating" style="top: 60%; left: 5%;"></div>
      <div class="floating-decoration decoration-circle floating-delayed" style="top: 70%; right: 8%;"></div>
      <div class="floating-decoration decoration-square floating" style="top: 40%; left: 20%;"></div>
      <div class="floating-decoration decoration-ring floating-delayed" style="top: 85%; right: 20%;"></div>
    </div>

    <!-- 顶部导航 -->
    <nav class="sticky top-0 z-50 glass-premium border-b border-white/20">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-aurora">MD Audit</h1>
              <span class="text-xs text-gray-500 hidden sm:block">Markdown SEO 诊断工具</span>
            </div>
          </div>

          <!-- 导航链接 -->
          <div class="flex items-center gap-2">
            <router-link
              to="/"
              class="nav-link"
              :class="$route.path === '/' ? 'nav-link-active' : 'nav-link-inactive'"
            >
              <svg class="w-4 h-4 inline-block mr-1.5 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              首页
            </router-link>
            <router-link
              to="/history"
              class="nav-link"
              :class="$route.path === '/history' ? 'nav-link-active' : 'nav-link-inactive'"
            >
              <svg class="w-4 h-4 inline-block mr-1.5 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              历史
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚 -->
    <footer class="py-6 text-center">
      <p class="text-sm text-gray-400">
        MD Audit v1.0.0
        <span class="mx-2 text-gray-300">|</span>
        FastAPI + Vue 3 + TailwindCSS
      </p>
    </footer>
  </div>
</template>

<script setup>
// Vue 3 Composition API
</script>

<style>
/* 页面切换动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Aurora额外层 */
.aurora-layer {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  pointer-events: none;
}

.aurora-layer-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #22d3d3 0%, #60a5fa 100%);
  top: 30%;
  left: 50%;
  transform: translateX(-50%);
  animation: auroraPulse1 15s ease-in-out infinite;
}

.aurora-layer-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #f472b6 0%, #a78bfa 100%);
  bottom: 20%;
  right: 10%;
  animation: auroraPulse2 12s ease-in-out infinite;
}

@keyframes auroraPulse1 {
  0%, 100% {
    transform: translateX(-50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateX(-50%) scale(1.2);
    opacity: 0.4;
  }
}

@keyframes auroraPulse2 {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.25;
  }
  50% {
    transform: scale(1.15) rotate(10deg);
    opacity: 0.35;
  }
}

/* 浮动装饰容器 */
.floating-decorations {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
</style>
