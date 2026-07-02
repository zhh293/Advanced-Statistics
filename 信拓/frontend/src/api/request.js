import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

request.interceptors.response.use(
  (res) => res.data,
  (err) => {
    ElMessage.error(err.message || '请求失败')
    return Promise.reject(err)
  }
)

export default request
