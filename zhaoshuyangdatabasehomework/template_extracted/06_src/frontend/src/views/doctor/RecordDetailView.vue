<template>
  <div>
    <el-page-header @back="$router.back()" title="返回" content="病历详情" style="margin-bottom:20px" />

    <el-card v-loading="loading" class="card-shadow">
      <template v-if="record">
        <el-descriptions title="病历信息" :column="2" border>
          <el-descriptions-item label="患者">{{ record.patient_name }}（{{ record.gender }}）</el-descriptions-item>
          <el-descriptions-item label="就诊时间">{{ record.visit_time }}</el-descriptions-item>
          <el-descriptions-item label="主诉" :span="2">{{ record.chief_complaint || '—' }}</el-descriptions-item>
          <el-descriptions-item label="诊断结果" :span="2">{{ record.diagnosis || '—' }}</el-descriptions-item>
          <el-descriptions-item label="治疗方案" :span="2">{{ record.treatment_plan || '—' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ record.notes || '—' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="record.prescription" style="margin-top:24px">
          <div style="font-size:15px;font-weight:600;color:#0d6e4e;margin-bottom:12px">处方信息</div>
          <el-descriptions :column="2" border style="margin-bottom:12px">
            <el-descriptions-item label="开具时间">{{ record.prescription.issued_at }}</el-descriptions-item>
            <el-descriptions-item label="总金额">
              <span style="color:#e6423d;font-weight:600">¥{{ record.prescription.total_price }}</span>
            </el-descriptions-item>
          </el-descriptions>
          <el-table :data="record.prescription.details" border size="small">
            <el-table-column label="药品"   prop="medicine_name" />
            <el-table-column label="规格"   prop="specification" width="140" />
            <el-table-column label="数量"   prop="quantity"      width="70" />
            <el-table-column label="用法"   prop="dosage"        min-width="140" />
            <el-table-column label="天数"   prop="days"          width="60" />
            <el-table-column label="小计" width="90">
              <template #default="{ row }">¥{{ row.subtotal }}</template>
            </el-table-column>
          </el-table>
        </div>
        <el-empty v-else description="本次就诊无处方" />
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { medicalRecordApi } from '@/api/medicalRecord'

const route   = useRoute()
const record  = ref(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  const res = await medicalRecordApi.getById(route.params.recordId)
  record.value = res.data
  loading.value = false
})
</script>
