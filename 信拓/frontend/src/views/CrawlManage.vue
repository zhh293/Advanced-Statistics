<template>
  <div class="manage-page">
    <el-row :gutter="16">
      <!-- 数据导入 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>数据导入</template>
          <p style="color: #909399; margin-bottom: 12px;">从 CSV 文件导入交通事故数据到数据库（自动去重 + 特征提取）</p>
          <el-button type="primary" @click="doImport" :loading="importing">
            <el-icon><Upload /></el-icon> 从 CSV 导入
          </el-button>
          <div v-if="importMsg" style="margin-top: 12px;">
            <el-alert :title="importMsg.message" :type="importMsg.message.includes('失败') ? 'error' : 'success'"
              :description="importMsg.detail" show-icon :closable="false" />
          </div>
        </el-card>
      </el-col>

      <!-- 爬虫管理 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>爬虫管理</template>
          <p style="color: #909399; margin-bottom: 12px;">手动触发爬虫抓取最新交通事故数据（温州/福建/铜仁/南京交警网）</p>
          <el-button type="success" @click="doCrawl" :loading="crawling">
            <el-icon><VideoPlay /></el-icon> 立即爬取
          </el-button>
          <div v-if="crawlStatus" style="margin-top: 12px;">
            <el-tag :type="crawlStatus.status === 'SUCCESS' ? 'success' : crawlStatus.status === 'RUNNING' ? 'warning' : 'danger'">
              {{ crawlStatus.status }}
            </el-tag>
            <span style="margin-left: 8px; color: #909399;">
              {{ crawlStatus.start_time?.slice(0, 16) }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 爬虫日志 -->
    <el-card shadow="never" style="margin-top: 16px;">
      <template #header>爬虫执行日志</template>
      <el-table :data="logs" stripe v-loading="logLoading" max-height="400">
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'SUCCESS' ? 'success' : row.status === 'RUNNING' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="总数" width="80" />
        <el-table-column prop="new_count" label="新增" width="80" />
        <el-table-column prop="start_time" label="开始时间" width="160" />
        <el-table-column prop="end_time" label="结束时间" width="160" />
        <el-table-column prop="error_msg" label="错误信息" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { importData, triggerCrawl, getCrawlLogs, getCrawlStatus } from '../api'

const importing = ref(false)
const crawling = ref(false)
const importMsg = ref(null)
const crawlStatus = ref(null)
const logs = ref([])
const logLoading = ref(false)

onMounted(async () => {
  crawlStatus.value = await getCrawlStatus()
  await loadLogs()
})

async function doImport() {
  importing.value = true
  try {
    importMsg.value = await importData()
    await loadLogs()
  } finally {
    importing.value = false
  }
}

async function doCrawl() {
  crawling.value = true
  try {
    await triggerCrawl()
    // 轮询状态
    const timer = setInterval(async () => {
      crawlStatus.value = await getCrawlStatus()
      if (crawlStatus.value?.status !== 'RUNNING') {
        clearInterval(timer)
        await loadLogs()
        crawling.value = false
      }
    }, 2000)
  } catch {
    crawling.value = false
  }
}

async function loadLogs() {
  logLoading.value = true
  try {
    logs.value = await getCrawlLogs()
  } finally {
    logLoading.value = false
  }
}
</script>
