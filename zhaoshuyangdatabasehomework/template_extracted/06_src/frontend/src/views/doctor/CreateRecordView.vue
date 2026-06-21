<template>
  <div>
    <el-page-header @back="$router.back()" title="返回" content="录入病历 & 开具处方"
      style="margin-bottom:20px" />

    <el-row :gutter="20">
      <!-- 病历表单 -->
      <el-col :span="12">
        <el-card class="card-shadow" header="病历信息">
          <el-form ref="recordFormRef" :model="recordForm" label-width="90px">
            <el-form-item label="主诉">
              <el-input v-model="recordForm.chief_complaint" type="textarea" :rows="3"
                placeholder="患者自述症状" />
            </el-form-item>
            <el-form-item label="诊断结果">
              <el-input v-model="recordForm.diagnosis" type="textarea" :rows="3"
                placeholder="诊断结论" />
            </el-form-item>
            <el-form-item label="治疗方案">
              <el-input v-model="recordForm.treatment_plan" type="textarea" :rows="3"
                placeholder="治疗建议" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="recordForm.notes" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingRecord" @click="saveRecord">
                {{ recordId ? '病历已保存' : '保存病历' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 处方表单 -->
      <el-col :span="12">
        <el-card class="card-shadow" header="处方开具">
          <div v-if="!recordId" class="tip">请先保存病历，再开具处方</div>
          <template v-else>
            <el-form label-width="80px">
              <el-form-item label="备注">
                <el-input v-model="prescriptionForm.notes" type="textarea" :rows="2"
                  placeholder="用药注意事项" />
              </el-form-item>
            </el-form>

            <!-- 药品明细 -->
            <div v-for="(item, idx) in prescriptionForm.details" :key="idx" class="detail-row">
              <el-select v-model="item.medicine_id" placeholder="选择药品" style="width:160px"
                filterable @change="onMedChange(item)">
                <el-option v-for="m in medicines" :key="m.medicine_id"
                  :label="`${m.medicine_name}(${m.specification})`" :value="m.medicine_id" />
              </el-select>
              <el-input-number v-model="item.quantity" :min="1" :max="99" style="width:80px" />
              <el-input v-model="item.dosage" placeholder="用法用量" style="width:160px" />
              <el-input-number v-model="item.days" :min="1" placeholder="天数" style="width:80px" />
              <el-button type="danger" circle icon="Delete" @click="removeDetail(idx)" />
            </div>

            <el-button icon="Plus" @click="addDetail" style="margin:8px 0 16px">添加药品</el-button>

            <div>
              <el-button type="success" :loading="savingPresc" @click="savePresc">
                开具处方
              </el-button>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { medicalRecordApi } from '@/api/medicalRecord'
import { prescriptionApi } from '@/api/prescription'
import { medicineApi } from '@/api/medicine'

const route  = useRoute()
const router = useRouter()
const appointmentId = route.params.appointmentId

const recordFormRef = ref(null)
const recordId      = ref(null)
const savingRecord  = ref(false)
const savingPresc   = ref(false)
const medicines     = ref([])

const recordForm = reactive({
  appointment_id: Number(appointmentId),
  chief_complaint: '', diagnosis: '', treatment_plan: '', notes: ''
})

const prescriptionForm = reactive({ notes: '', details: [] })

onMounted(async () => {
  const res = await medicineApi.list({ in_stock: true, page_size: 100 })
  medicines.value = res.data.list
})

async function saveRecord() {
  savingRecord.value = true
  try {
    const res = await medicalRecordApi.create(recordForm)
    recordId.value = res.data.record_id
    ElMessage.success('病历保存成功')
  } finally {
    savingRecord.value = false
  }
}

function addDetail() {
  prescriptionForm.details.push({ medicine_id: null, quantity: 1, dosage: '', days: 3 })
}

function removeDetail(idx) {
  prescriptionForm.details.splice(idx, 1)
}

function onMedChange() { /* 可在此计算小计预览 */ }

async function savePresc() {
  if (!prescriptionForm.details.length) {
    return ElMessage.warning('请至少添加一种药品')
  }
  savingPresc.value = true
  try {
    await prescriptionApi.create({
      record_id: recordId.value,
      notes: prescriptionForm.notes,
      details: prescriptionForm.details,
    })
    ElMessage.success('处方开具成功')
    router.push('/doctor/today')
  } finally {
    savingPresc.value = false
  }
}
</script>

<style scoped>
.tip { color: #aaa; font-size: 14px; padding: 20px 0; text-align: center; }
.detail-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px; flex-wrap: wrap;
}
</style>
