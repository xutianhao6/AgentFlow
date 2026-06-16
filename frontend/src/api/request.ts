import axios from 'axios'
import { message } from 'ant-design-vue'

export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const request = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

request.interceptors.request.use((config) => {
  const userId = localStorage.getItem('user_id') || 'default'
  config.headers = config.headers || {}
  config.headers['X-User-Id'] = userId
  return config
})

request.interceptors.response.use(
  (resp) => resp.data,
  (error) => {
    const detail = error?.response?.data?.detail || error.message || '请求失败'
    message.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    return Promise.reject(error)
  },
)

export default request
