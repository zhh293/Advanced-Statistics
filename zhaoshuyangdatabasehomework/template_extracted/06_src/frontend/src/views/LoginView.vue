<template>
  <div class="auth-bg">
    <div class="auth-card">
      <!-- Logo区 -->
      <div class="auth-header">
        <el-icon :size="48" color="#1a3c6e"><FirstAidKit /></el-icon>
        <h1>医院预约系统</h1>
        <p class="subtitle">请登录您的账号</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="账号" prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock"
            show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="full-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth   = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res = await authApi.login(form)
    auth.setAuth(res.data.access_token, res.data.user)
    ElMessage.success('登录成功')
    const roleHome = { patient: '/patient/home', doctor: '/doctor/today', admin: '/admin/dashboard' }
    router.push(roleHome[res.data.user.role] || '/login')
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
  padding: 48px 40px;
  width: 420px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}
.auth-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a3c6e;
  margin: 12px 0 4px;
}
.subtitle {
  color: #888;
  font-size: 14px;
}
.full-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  border-radius: 8px;
}
.auth-footer {
  text-align: center;
  margin-top: 16px;
  color: #888;
  font-size: 14px;
}
.auth-footer a {
  color: #2d7dd2;
  text-decoration: none;
  font-weight: 500;
}
</style>
