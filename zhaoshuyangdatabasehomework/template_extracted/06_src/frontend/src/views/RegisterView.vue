<template>
  <div class="auth-bg">
    <div class="auth-card">
      <div class="auth-header">
        <el-icon :size="48" color="#1a3c6e"><FirstAidKit /></el-icon>
        <h1>注册账号</h1>
        <p class="subtitle">创建您的医院预约账号</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="账号（3-50位字母/数字/下划线）" prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（8-32位）" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="role">
          <el-select v-model="form.role" placeholder="注册类型" style="width:100%">
            <el-option label="患者" value="patient" />
            <el-option label="医生" value="doctor" />
          </el-select>
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（选填）" prefix-icon="Message" clearable />
        </el-form-item>
        <el-form-item prop="phone">
          <el-input v-model="form.phone" placeholder="手机号（选填）" prefix-icon="Phone" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="full-btn" :loading="loading" @click="handleRegister">
            立即注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        已有账号？<router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'

const router  = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '', role: 'patient', email: '', phone: '' })
const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]{3,50}$/, message: '3-50位字母/数字/下划线', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码8-32位', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择注册类型', trigger: 'change' }],
}

async function handleRegister() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await authApi.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a3c6e 0%, #2d7dd2 100%);
}
.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 420px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.auth-header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-header h1 { font-size: 22px; font-weight: 700; color: #1a3c6e; margin: 10px 0 4px; }
.subtitle { color: #888; font-size: 14px; }
.full-btn { width: 100%; height: 46px; font-size: 16px; border-radius: 8px; }
.auth-footer { text-align: center; margin-top: 14px; color: #888; font-size: 14px; }
.auth-footer a { color: #2d7dd2; text-decoration: none; font-weight: 500; }
</style>
