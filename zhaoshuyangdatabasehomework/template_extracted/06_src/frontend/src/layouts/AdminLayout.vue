<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="28" color="#fff"><Setting /></el-icon>
        <span>管理后台</span>
      </div>
      <el-menu :default-active="activeMenu" router background-color="#2c2c54"
        text-color="#c8c8e8" active-text-color="#ffffff">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataBoard /></el-icon><span>统计总览</span>
        </el-menu-item>
        <el-menu-item index="/admin/departments">
          <el-icon><OfficeBuilding /></el-icon><span>科室管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/schedules">
          <el-icon><Calendar /></el-icon><span>排班管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/medicines">
          <el-icon><Box /></el-icon><span>药品管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="top-bar">
        <span class="welcome">管理员：{{ auth.user?.username }}</span>
        <el-button type="danger" plain size="small" @click="handleLogout">退出登录</el-button>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const activeMenu = computed(() => route.path)

async function handleLogout() {
  await authApi.logout().catch(() => {})
  auth.clearAuth()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.app-layout { height: 100vh; }
.sidebar { background: #2c2c54; }
.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 24px; color: #fff; font-size: 17px; font-weight: 700;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.el-menu { border-right: none; }
.el-menu-item { margin: 4px 8px; border-radius: 8px; }
.top-bar {
  display: flex; align-items: center; justify-content: flex-end; gap: 16px;
  background: #fff; border-bottom: 1px solid #eee; padding: 0 24px;
}
.welcome { color: #555; font-size: 14px; }
.main-content { padding: 24px; background: #f0f2f5; overflow-y: auto; }
</style>
