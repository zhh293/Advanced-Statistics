<template>
  <div>
    <div class="page-title">今日就诊列表</div>

    <!-- 过滤栏 -->
    <el-card class="card-shadow" style="margin-bottom:16px">
      <el-form inline>
        <el-form-item label="日期">
          <el-date-picker v-model="dateStr" type="date" value-format="YYYY-MM-DD"
            style="width:160px" @change="fetchList" />
        </el-form-item>
        <el-form-item label="时段">
          <el-select v-model="timePeriod" placeholder="全部" clearable style="width:100px"
            @change="fetchList">
            <el-option label="上午" value="上午" />
            <el-option label="下午" value="下午" />
            <el-option label="晚上" value="晚上" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Refresh" @click="fetchList">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card-shadow">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="序号" prop="queue_no" width="60" />
        <el-table-column label="患者姓名" prop="patient_name" width="100" />
        <el-table-column label="性别"    prop="gender"       width="60" />
        <el-table-column label="年龄"    prop="age"          width="60">
          <template #default="{ row }">{{ row.age || '—' }}岁</template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.has_record && row.status === '待就诊'"
              type="primary" size="small"
              @click="$router.push(`/doctor/record/create/${row.appointment_id}`)">
              录入病历
            </el-button>
            <el-button v-else-if="row.has_record"
              type="success" size="small" @click="viewRecord(row)">
              查看病历
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="total-tip">共 {{ list.length }} 位患者</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { appointmentApi } from '@/api/appointment'
import { medicalRecordApi } from '@/api/medicalRecord'

const router     = useRouter()
const list       = ref([])
const loading    = ref(false)
const dateStr    = ref('')
const timePeriod = ref('')

function statusType(s) {
  const m = { '待就诊': 'primary', '已就诊': 'success', '已取消': 'info', '爽约': 'danger' }
  return m[s] || 'info'
}

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const params = {}
  if (dateStr.value)    params.date_str    = dateStr.value
  if (timePeriod.value) params.time_period = timePeriod.value
  const res = await appointmentApi.today(params)
  list.value = res.data.list
  loading.value = false
}

async function viewRecord(row) {
  // 通过 appointment_id 找到 record_id（由后端 appointment.medical_record 关联）
  // 此处简单跳转 today 并提示
  router.push(`/doctor/today`)
  ElMessage.info('请在预约详情中查看病历')
}
</script>

<style scoped>
.total-tip { margin-top: 12px; color: #888; font-size: 13px; }
</style>
