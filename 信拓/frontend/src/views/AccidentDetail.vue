<template>
  <div class="detail-page" v-loading="loading">
    <el-page-header @back="$router.back()" :content="detail?.title || '事故详情'" style="margin-bottom: 16px;" />

    <el-result v-if="error" icon="error" title="加载失败" :sub-title="error">
      <template #extra>
        <el-button type="primary" @click="$router.back()">返回列表</el-button>
      </template>
    </el-result>

    <el-card v-if="detail" shadow="never">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="标题" :span="2">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="发布时间">{{ detail.pub_time }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ detail.source }}</el-descriptions-item>
        <el-descriptions-item label="事故原因">
          <el-tag :type="tagType(detail.accident_reason)">{{ detail.accident_reason }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="车辆类型">{{ detail.vehicle_type }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ detail.time_period }}</el-descriptions-item>
        <el-descriptions-item label="事故地点">{{ detail.location || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="原文链接">
          <a :href="detail.url" target="_blank" style="color: #409EFF;">查看原文</a>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />
      <div class="content-text">{{ detail.content }}</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAccidentDetail } from '../api'

const route = useRoute()
const detail = ref(null)
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    detail.value = await getAccidentDetail(route.params.id)
  } catch (e) {
    error.value = e?.response?.data?.detail || '事故记录不存在或加载失败'
  } finally {
    loading.value = false
  }
})

function tagType(reason) {
  const map = {
    '酒驾': 'danger', '闯红灯': 'warning', '超速': '',
    '分心驾驶': 'info', '疲劳驾驶': 'warning', '逆向行驶': 'danger',
    '抢黄灯': 'warning', '信号灯故障': 'info',
  }
  return map[reason] || ''
}
</script>

<style scoped>
.detail-page { max-width: 900px; margin: 0 auto; }
.content-text { line-height: 2; text-indent: 2em; white-space: pre-wrap; color: #303133; }
</style>
