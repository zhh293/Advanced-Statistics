<template>
  <div>
    <div class="page-title">就诊记录</div>
    <el-card class="card-shadow">
      <el-table :data="records" v-loading="loading" stripe @row-click="goDetail">
        <el-table-column label="就诊时间" prop="visit_time" min-width="160" />
        <el-table-column label="医生"     prop="doctor_name" width="100" />
        <el-table-column label="科室"     prop="dept_name"   width="100" />
        <el-table-column label="诊断结果" prop="diagnosis"   min-width="200" show-overflow-tooltip />
        <el-table-column label="处方" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.has_prescription" type="success">有</el-tag>
            <el-tag v-else type="info">无</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="goDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" layout="prev,pager,next"
        :total="total" :page-size="pageSize" v-model:current-page="page"
        @current-change="fetchList" style="margin-top:16px;justify-content:flex-end;display:flex" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { patientApi } from '@/api/patient'

const router  = useRouter()
const records = ref([])
const loading = ref(false)
const page    = ref(1)
const pageSize = ref(20)
const total   = ref(0)

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await patientApi.getRecords({ page: page.value, page_size: pageSize.value })
  records.value = res.data.list
  total.value   = res.data.total
  loading.value = false
}

function goDetail(row) {
  router.push(`/patient/records/${row.record_id}`)
}
</script>
