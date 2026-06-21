<template>
  <div>
    <div class="page-title">我的预约</div>

    <!-- 状态过滤 -->
    <el-card class="card-shadow" style="margin-bottom:16px">
      <el-radio-group v-model="statusFilter" @change="fetchList">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="待就诊">待就诊</el-radio-button>
        <el-radio-button value="已就诊">已就诊</el-radio-button>
        <el-radio-button value="已取消">已取消</el-radio-button>
        <el-radio-button value="爽约">爽约</el-radio-button>
      </el-radio-group>
    </el-card>

    <el-card class="card-shadow">
      <el-table :data="appointments" v-loading="loading" stripe>
        <el-table-column label="医生"   prop="doctor_name"  width="100" />
        <el-table-column label="科室"   prop="dept_name"    width="100" />
        <el-table-column label="日期"   prop="work_date"    width="110" />
        <el-table-column label="时段"   prop="time_period"  width="80" />
        <el-table-column label="序号"   prop="queue_no"     width="70" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预约时间" prop="created_at" min-width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === '待就诊'" type="danger" size="small"
              @click="openCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-if="total > pageSize" layout="prev,pager,next"
        :total="total" :page-size="pageSize" v-model:current-page="page"
        @current-change="fetchList" style="margin-top:16px;justify-content:flex-end;display:flex" />
    </el-card>

    <!-- 取消弹窗 -->
    <el-dialog v-model="cancelVisible" title="取消预约" width="400px">
      <el-input v-model="cancelReason" type="textarea" placeholder="取消原因（选填）" :rows="3" />
      <template #footer>
        <el-button @click="cancelVisible = false">关闭</el-button>
        <el-button type="danger" :loading="cancelling" @click="confirmCancel">确认取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { appointmentApi } from '@/api/appointment'

const appointments = ref([])
const loading      = ref(false)
const statusFilter = ref('')
const page         = ref(1)
const pageSize     = ref(20)
const total        = ref(0)

const cancelVisible = ref(false)
const cancelReason  = ref('')
const cancelling    = ref(false)
const currentAppt   = ref(null)

function statusType(s) {
  const map = { '待就诊': 'primary', '已就诊': 'success', '已取消': 'info', '爽约': 'danger' }
  return map[s] || 'info'
}

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const params = { page: page.value, page_size: pageSize.value }
  if (statusFilter.value) params.status = statusFilter.value
  const res = await appointmentApi.list(params)
  appointments.value = res.data.list
  total.value        = res.data.total
  loading.value = false
}

function openCancel(row) {
  currentAppt.value = row
  cancelReason.value = ''
  cancelVisible.value = true
}

async function confirmCancel() {
  cancelling.value = true
  try {
    await appointmentApi.cancel(currentAppt.value.appointment_id, { cancel_reason: cancelReason.value })
    ElMessage.success('预约已取消')
    cancelVisible.value = false
    fetchList()
  } finally {
    cancelling.value = false
  }
}
</script>
