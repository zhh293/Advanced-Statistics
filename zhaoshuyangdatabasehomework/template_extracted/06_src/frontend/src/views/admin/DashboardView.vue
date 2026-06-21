<template>
  <div>
    <div class="page-title">统计总览</div>

    <!-- 日期筛选 -->
    <el-card class="card-shadow" style="margin-bottom:16px">
      <el-form inline>
        <el-form-item label="开始日期">
          <el-date-picker v-model="dateFrom" type="date" value-format="YYYY-MM-DD"
            style="width:160px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="dateTo" type="date" value-format="YYYY-MM-DD"
            style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchStats">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 指标卡片 -->
    <el-row :gutter="16" v-loading="loading" style="margin-bottom:16px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card class="stat-card card-shadow">
          <div class="stat-icon" :style="{ background: card.color }">
            <el-icon :size="28" color="#fff"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预约统计 -->
    <el-row :gutter="16" v-if="stats">
      <el-col :span="12">
        <el-card class="card-shadow" header="预约状态分布">
          <el-table :data="apptRows" border size="small">
            <el-table-column label="状态" prop="status" />
            <el-table-column label="数量" prop="count" />
            <el-table-column label="占比">
              <template #default="{ row }">
                <el-progress :percentage="row.pct" :color="row.color" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="card-shadow" header="今日数据">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="今日预约总数">
              {{ stats.today.appointments }}
            </el-descriptions-item>
            <el-descriptions-item label="今日已就诊">
              {{ stats.today.completed }}
            </el-descriptions-item>
            <el-descriptions-item label="今日完成率">
              {{ stats.today.appointments
                ? ((stats.today.completed / stats.today.appointments) * 100).toFixed(1) + '%'
                : '—' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'

const stats    = ref(null)
const loading  = ref(false)
const dateFrom = ref('')
const dateTo   = ref('')

const statCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: '注册患者', value: stats.value.total_patients,    icon: 'User',          color: '#2d7dd2' },
    { label: '在职医生', value: stats.value.total_doctors,     icon: 'UserFilled',    color: '#0d6e4e' },
    { label: '科室数量', value: stats.value.total_departments, icon: 'OfficeBuilding', color: '#7b68ee' },
    { label: '总预约量', value: stats.value.appointments.total, icon: 'Calendar',      color: '#e6a817' },
  ]
})

const apptRows = computed(() => {
  if (!stats.value) return []
  const a = stats.value.appointments
  const t = a.total || 1
  return [
    { status: '已就诊', count: a.completed, pct: Math.round(a.completed / t * 100), color: '#67c23a' },
    { status: '已取消', count: a.cancelled, pct: Math.round(a.cancelled / t * 100), color: '#909399' },
    { status: '爽约',   count: a.absent,    pct: Math.round(a.absent    / t * 100), color: '#f56c6c' },
  ]
})

onMounted(fetchStats)

async function fetchStats() {
  loading.value = true
  const params = {}
  if (dateFrom.value) params.date_from = dateFrom.value
  if (dateTo.value)   params.date_to   = dateTo.value
  const res = await adminApi.statistics(params)
  stats.value = res.data
  loading.value = false
}

function resetFilter() {
  dateFrom.value = ''
  dateTo.value   = ''
  fetchStats()
}
</script>

<style scoped>
.stat-card { display: flex; align-items: center; gap: 16px; padding: 20px; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a3c6e; }
.stat-label { font-size: 13px; color: #888; margin-top: 4px; }
</style>
