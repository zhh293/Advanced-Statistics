<template>
  <div>
    <div class="page-title">个人档案</div>

    <el-card class="card-shadow" style="max-width:600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" size="default">
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" :disabled="hasProfile" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" :disabled="hasProfile" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender" :disabled="hasProfile">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="form.birth_date" type="date" value-format="YYYY-MM-DD"
            :disabled="hasProfile" style="width:100%" />
        </el-form-item>
        <el-form-item label="家庭住址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="紧急联系人">
          <el-input v-model="form.emergency_contact" />
        </el-form-item>
        <el-form-item label="紧急电话">
          <el-input v-model="form.emergency_phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ hasProfile ? '更新档案' : '创建档案' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { patientApi } from '@/api/patient'

const formRef    = ref(null)
const hasProfile = ref(false)
const saving     = ref(false)

const form = reactive({
  real_name: '', id_card: '', gender: '男', birth_date: null,
  address: '', emergency_contact: '', emergency_phone: ''
})

const rules = {
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  id_card:   [{ required: true, message: '请输入身份证号', trigger: 'blur' },
              { len: 18, message: '身份证号应为18位', trigger: 'blur' }],
  gender:    [{ required: true, message: '请选择性别', trigger: 'change' }],
}

onMounted(async () => {
  try {
    const res = await patientApi.getProfile()
    Object.assign(form, res.data)
    hasProfile.value = true
  } catch { /* 尚未创建档案 */ }
})

async function handleSave() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (hasProfile.value) {
      await patientApi.updateProfile({
        address: form.address,
        emergency_contact: form.emergency_contact,
        emergency_phone: form.emergency_phone,
      })
    } else {
      await patientApi.createProfile(form)
      hasProfile.value = true
    }
    ElMessage.success('档案已保存')
  } finally {
    saving.value = false
  }
}
</script>
