<template>
  <div class="accident-list">
    <!-- 筛选区 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="5">
          <el-input v-model="filters.keyword" placeholder="搜索标题/正文" clearable @clear="search" @keyup.enter="search">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filters.reason" placeholder="事故原因" clearable @change="onFilterChange">
            <el-option v-for="r in options.reasons" :key="r" :label="r" :value="r" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filters.vehicle_type" placeholder="车辆类型" clearable @change="onFilterChange">
            <el-option v-for="v in options.vehicle_types" :key="v" :label="v" :value="v" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filters.time_period" placeholder="时段" clearable @change="onFilterChange">
            <el-option v-for="p in options.time_periods" :key="p" :label="p" :value="p" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filters.source" placeholder="来源" clearable @change="onFilterChange">
            <el-option v-for="s in options.sources" :key="s" :label="s" :value="s" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-date-picker
            v-model="dateRange" type="daterange" range-separator="至"
            start-placeholder="开始日期" end-placeholder="结束日期"
            value-format="YYYY-MM-DD" @change="onFilterChange"
            style="width: 100%;"
          />
        </el-col>
        <el-col :span="3">
          <el-button type="primary" @click="search">搜索</el-button>
          <el-button @click="reset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top: 12px;">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span>事故列表</span>
          <el-button type="success" size="small" @click="doExport">
            <el-icon><Download /></el-icon> 导出 CSV
          </el-button>
        </div>
      </template>
      <el-table :data="tableData" stripe v-loading="loading" @row-click="goDetail" style="cursor: pointer;">
        <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="accident_reason" label="事故原因" width="100">
          <template #default="{ row }">
            <el-tag :type="reasonTagType(row.accident_reason)" size="small">
              {{ row.accident_reason }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vehicle_type" label="车辆类型" width="120" />
        <el-table-column prop="time_period" label="时段" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.time_period }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地点" width="120" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="140" show-overflow-tooltip />
        <el-table-column prop="pub_time" label="发布时间" width="160" />
      </el-table>

      <div style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="page" v-model:page-size="size"
          :total="total" :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="search" @current-change="search"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAccidents, getFilterOptions, exportAccidents } from '../api'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const dateRange = ref([])

const filters = reactive({
  keyword: '', reason: '', vehicle_type: '', time_period: '', source: '',
})
const options = reactive({
  reasons: [], vehicle_types: [], time_periods: [], sources: [],
})

onMounted(async () => {
  const opts = await getFilterOptions()
  Object.assign(options, opts)
  search()
})

function onFilterChange() {
  page.value = 1
  search()
}

async function search() {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value, ...filters }
    if (dateRange.value?.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    // 清理空值
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })

    const res = await getAccidents(params)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.keys(filters).forEach(k => filters[k] = '')
  dateRange.value = []
  page.value = 1
  search()
}

function goDetail(row) {
  router.push(`/accidents/${row.id}`)
}

function doExport() {
  const params = { ...filters }
  if (dateRange.value?.length === 2) {
    params.date_from = dateRange.value[0]
    params.date_to = dateRange.value[1]
  }
  exportAccidents(params)
}

function reasonTagType(reason) {
  const map = {
    '酒驾': 'danger', '闯红灯': 'warning', '超速': '',
    '分心驾驶': 'info', '疲劳驾驶': 'warning', '逆向行驶': 'danger',
    '抢黄灯': 'warning', '信号灯故障': 'info',
  }
  return map[reason] || ''
}
</script>

<style scoped>
.filter-card { margin-bottom: 0; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
</style>
