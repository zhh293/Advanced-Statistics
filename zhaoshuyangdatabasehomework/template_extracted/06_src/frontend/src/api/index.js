import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 请求拦截：自动附加 Bearer Token
http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截：统一错误处理
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const code = err.response?.data?.code
    const msg  = err.response?.data?.message || '网络错误，请稍后重试'

    if (code === 40102 || code === 40103) {
      const auth = useAuthStore()
      auth.clearAuth()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(err.response?.data || err)
  }
)

export default http
