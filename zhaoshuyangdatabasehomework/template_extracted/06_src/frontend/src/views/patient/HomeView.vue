<template>
  <div>
    <div class="page-title">找医生 · 在线预约</div>

    <!-- 搜索栏 -->
    <el-card class="search-card card-shadow">
      <el-form inline>
        <el-form-item label="科室">
          <el-select v-model="filter.dept_id" placeholder="全部科室" clearable style="width:140px"
            @change="fetchSchedules">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="filter.date_str" type="date" placeholder="选择日期"
            value-format="YYYY-MM-DD" style="width:160px" @change="fetchSchedules" />
        </el-form-item>
        <el-form-item label="时段">
          <el-select v-model="filter.time_period" placeholder="全部时段" clearable style="width:110px"
            @change="fetchSchedules">
            <el-option label="上午" value="上午" />
            <el-option label="下午" value="下午" />
            <el-option label="晚上" value="晚上" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="fetchSchedules">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 排班列表 -->
    <el-card class="card-shadow" style="margin-top:16px">
      <el-table :data="schedules" v-loading="loading" stripe>
        <el-table-column label="科室"   prop="dept_name"   width="100" />
        <el-table-column label="医生"   prop="doctor_name" width="100" />
        <el-table-column label="职称"   prop="title"       width="110" />
        <el-table-column label="诊室"   prop="room_no"     width="80" />
        <el-table-column label="日期"   prop="work_date"   width="110" />
        <el-table-column label="时段"   prop="time_period" width="80" />
        <el-table-column label="余号">
          <template #default="{ row }">
            <el-tag :type="row.remaining > 0 ? 'success' : 'danger'">
              {{ row.remaining > 0 ? `剩余 ${row.remaining}` : '已约满' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : row.status === '约满' ? 'warning' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" :disabled="row.status !== '正常'"
              @click="openBooking(row)">
              预约
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 预约确认弹窗 -->
    <el-dialog v-model="bookingVisible" title="确认预约" width="400px">
      <div v-if="selected" class="booking-info">
        <div><b>医生：</b>{{ selected.doctor_name }}（{{ selected.title }}）</div>
        <div><b>科室：</b>{{ selected.dept_name }}</div>
        <div><b>诊室：</b>{{ selected.room_no }}</div>
        <div><b>时间：</b>{{ selected.work_date }} {{ selected.time_period }}</div>
        <div><b>剩余号源：</b>{{ selected.remaining }}</div>
      </div>
      <template #footer>
        <el-button @click="bookingVisible = false">取消</el-button>
        <el-button type="primary" :loading="booking" @click="confirmBook">确认预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { departmentApi } from '@/api/department'
import { scheduleApi } from '@/api/schedule'
import { appointmentApi } from '@/api/appointment'

const departments = ref([])
const schedules   = ref([])
const loading     = ref(false)
const filter = reactive({ dept_id: null, date_str: null, time_period: null })

const bookingVisible = ref(false)
const selected = ref(null)
const booking  = ref(false)

onMounted(async () => {
  const res = await departmentApi.list()
  departments.value = res.data
  fetchSchedules()
})

async function fetchSchedules() {
  loading.value = true
  const params = {}
  if (filter.dept_id)    params.dept_id    = filter.dept_id
  if (filter.date_str)   params.date_str   = filter.date_str
  if (filter.time_period) params.time_period = filter.time_period
  const res = await scheduleApi.list(params)
  schedules.value = res.data
  loading.value = false
}

function openBooking(row) {
  selected.value = row
  bookingVisible.value = true
}

async function confirmBook() {
  booking.value = true
  try {
    await appointmentApi.create({ schedule_id: selected.value.schedule_id })
    ElMessage.success('预约成功！')
    bookingVisible.value = false
    fetchSchedules()
  } finally {
    booking.value = false
  }
}
</script>

<style scoped>
.search-card { margin-bottom: 0; }
.booking-info { display: flex; flex-direction: column; gap: 10px; font-size: 15px; }
</style>
