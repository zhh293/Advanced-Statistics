import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/accidents', name: 'AccidentList', component: () => import('../views/AccidentList.vue') },
  { path: '/accidents/:id', name: 'AccidentDetail', component: () => import('../views/AccidentDetail.vue') },
  { path: '/heatmap', name: 'HeatmapView', component: () => import('../views/HeatmapView.vue') },
  { path: '/sankey', name: 'SankeyView', component: () => import('../views/SankeyView.vue') },
  { path: '/mining', name: 'MiningView', component: () => import('../views/MiningView.vue') },
  { path: '/manage', name: 'CrawlManage', component: () => import('../views/CrawlManage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
