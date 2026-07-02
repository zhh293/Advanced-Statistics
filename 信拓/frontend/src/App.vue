<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="logo">
        <el-icon :size="24"><WarningFilled /></el-icon>
        <span>交通事故数据挖掘分析平台</span>
      </div>
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        router
        class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/accidents">
          <el-icon><List /></el-icon>
          <span>事故列表</span>
        </el-menu-item>
        <el-menu-item index="/heatmap">
          <el-icon><MapLocation /></el-icon>
          <span>热力地图</span>
        </el-menu-item>
        <el-menu-item index="/sankey">
          <el-icon><Connection /></el-icon>
          <span>流向分析</span>
        </el-menu-item>
        <el-menu-item index="/mining">
          <el-icon><Search /></el-icon>
          <span>关联规则</span>
        </el-menu-item>
        <el-menu-item index="/manage">
          <el-icon><Setting /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; background: #f0f2f5; }
.layout { min-height: 100vh; }
.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-right: 40px;
  white-space: nowrap;
}
.nav-menu {
  border-bottom: none !important;
  flex: 1;
}
.main-content {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
