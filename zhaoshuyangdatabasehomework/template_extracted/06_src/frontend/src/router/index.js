import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login',    component: () => import('@/views/LoginView.vue') },
  { path: '/register', component: () => import('@/views/RegisterView.vue') },

  // ── 患者 ─────────────────────────────────────────────
  {
    path: '/patient',
    component: () => import('@/layouts/PatientLayout.vue'),
    meta: { role: 'patient' },
    children: [
      { path: '',         redirect: '/patient/home' },
      { path: 'home',     component: () => import('@/views/patient/HomeView.vue') },
      { path: 'profile',  component: () => import('@/views/patient/ProfileView.vue') },
      { path: 'appointments', component: () => import('@/views/patient/AppointmentsView.vue') },
      { path: 'records',  component: () => import('@/views/patient/RecordsView.vue') },
      { path: 'records/:id', component: () => import('@/views/patient/RecordDetailView.vue') },
    ]
  },

  // ── 医生 ─────────────────────────────────────────────
  {
    path: '/doctor',
    component: () => import('@/layouts/DoctorLayout.vue'),
    meta: { role: 'doctor' },
    children: [
      { path: '',      redirect: '/doctor/today' },
      { path: 'today', component: () => import('@/views/doctor/TodayView.vue') },
      { path: 'record/create/:appointmentId', component: () => import('@/views/doctor/CreateRecordView.vue') },
      { path: 'record/:recordId',             component: () => import('@/views/doctor/RecordDetailView.vue') },
    ]
  },

  // ── 管理员 ───────────────────────────────────────────
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { role: 'admin' },
    children: [
      { path: '',             redirect: '/admin/dashboard' },
      { path: 'dashboard',   component: () => import('@/views/admin/DashboardView.vue') },
      { path: 'departments', component: () => import('@/views/admin/DepartmentsView.vue') },
      { path: 'schedules',   component: () => import('@/views/admin/SchedulesView.vue') },
      { path: 'medicines',   component: () => import('@/views/admin/MedicinesView.vue') },
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to) => {
  const auth = useAuthStore()
  const requiresRole = to.meta.role

  if (!requiresRole) return true           // 公开页面

  if (!auth.token) {
    return '/login'                         // 未登录
  }

  if (auth.user?.role !== requiresRole) {
    // 角色不匹配，重定向到对应角色首页
    const roleHome = { patient: '/patient/home', doctor: '/doctor/today', admin: '/admin/dashboard' }
    return roleHome[auth.user?.role] || '/login'
  }

  return true
})

export default router
