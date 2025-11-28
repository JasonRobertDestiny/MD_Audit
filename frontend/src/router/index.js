import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import HistoryPage from '../views/HistoryPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryPage,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
