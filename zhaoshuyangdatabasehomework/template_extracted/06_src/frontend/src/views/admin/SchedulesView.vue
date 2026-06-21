<template>
  <div>
    <div class="flex-header">
      <div class="page-title" style="margin:0">排班管理</div>
      <el-button type="primary" icon="Plus" @click="openCreateDialog">新增排班</el-button>
    </div>

    <!-- 过滤 -->
    <el-card class="card-shadow" style="margin:12px 0">
      <el-form inline>
        <el-form-item label="科室">
          <el-select v-model="filter.dept_id" placeholder="全部" clearable style="width:120px"
            @change="fetchList">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="filter.date_str" type="date" value-format="YYYY-MM-DD"
            style="width:150px" @change="fetchList" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="fetchList">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card-shadow">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="医生"   prop="doctor_name"  width="100" />
        <el-table-column label="科室"   prop="dept_name"    width="100" />
        <el-table-column label="诊室"   prop="room_no"      width="80" />
        <el-table-column label="日期"   prop="work_date"    width="110" />
        <el-table-column label="时段"   prop="time_period"  width="80" />
        <el-table-column label="已/总" width="80">
          <template #default="{ row }">{{ row.registered_count }}/{{ row.max_patients }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : row.status === '约满' ? 'warning' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status !== '停诊'" type="warning" size="small"
              @click="updateStatus(row, '停诊')">停诊</el-button>
            <el-button v-if="row.status === '停诊'" type="success" size="small"
              @click="updateStatus(row, '正常')">恢复</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增排班弹窗 -->
    <el-dialog v-model="createVisible" title="新增排班" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="医生" prop="doctor_id">
          <el-select v-model="form.doctor_id" placeholder="选择医生" filterable style="width:100%">
            <el-option v-for="d in doctors" :key="d.doctor_id"
              :label="`${d.real_name}（${d.dept_name}）`" :value="d.doctor_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="诊室" prop="room_id">
          <el-select v-model="form.room_id" placeholder="选择诊室" style="width:100%">
            <el-option v-for="r in rooms" :key="r.room_id"
              :label="`${r.room_name}（${r.room_no}）`" :value="r.room_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出诊日期" prop="work_date">
          <el-date-picker v-model="form.work_date" type="date" value-format="YYYY-MM-DD"
            style="width:100%" />
        </el-form-item>
        <el-form-item label="时间段" prop="time_period">
          <el-select v-model="form.time_period" style="width:100%">
            <el-option label="上午" value="上午" />
            <el-option label="下午" value="下午" />
            <el-option label="晚上" value="晚上" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大接诊">
          <el-input-number v-model="form.max_patients" :min="1" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { departmentApi } from '@/api/department'
import { doctorApi } from '@/api/doctor'
import { scheduleApi } from '@/api/schedule'

const list        = ref([])
const departments = ref([])
const doctors     = ref([])
const rooms       = ref([])
const loading     = ref(false)
const saving      = ref(false)
const createVisible = ref(false)
const formRef     = ref(null)

const filter = reactive({ dept_id: null, date_str: null })
const form   = reactive({ doctor_id: null, room_id: null, work_date: '', time_period: '上午', max_patients: 20 })
const rules  = {
  doctor_id:   [{ required: true, message: '请选择医生',   trigger: 'change' }],
  room_id:     [{ required: true, message: '请选择诊室',   trigger: 'change' }],
  work_date:   [{ required: true, message: '请选择日期',   trigger: 'change' }],
  time_period: [{ required: true, message: '请选择时间段', trigger: 'change' }],
}

onMounted(async () => {
  const [deptRes, docRes] = await Promise.all([departmentApi.list(), doctorApi.list({ page_size: 200 })])
  departments.value = deptRes.data
  doctors.value     = docRes.data.list

  // 获取所有诊室（从科室详情里合并）
  const allRooms = []
  for (const d of departments.value) {
    const detail = await departmentApi.getById(d.dept_id)
    allRooms.push(...detail.data.rooms)
  }
  rooms.value = allRooms

  fetchList()
})

async function fetchList() {
  loading.value = true
  const params = {}
  if (filter.dept_id)  params.dept_id  = filter.dept_id
  if (filter.date_str) params.date_str = filter.date_str
  const res = await scheduleApi.list(params)
  list.value = res.data
  loading.value = false
}

function openCreateDialog() {
  Object.assign(form, { doctor_id: null, room_id: null, work_date: '', time_period: '上午', max_patients: 20 })
  createVisible.value = true
}

async function handleCreate() {
  await formRef.value?.validate()
  saving.value = true
  try {
    await scheduleApi.create(form)
    ElMessage.success('排班创建成功')
    createVisible.value = false
    fetchList()
  } finally {
    saving.value = false
  }
}

async function updateStatus(row, status) {
  await scheduleApi.updateStatus(row.schedule_id, { status })
  ElMessage.success(`已${status === '停诊' ? '停诊' : '恢复正常'}`)
  fetchList()
}
</script>

<style scoped>
.flex-header { display: flex; align-items: center; justify-content: space-between; }
</style>
