import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '',
  timeout: 15000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 根据状态码生成友好提示
function getErrorMessage(status: number, detail: string): string {
  // 后端返回了具体错误信息，直接使用
  if (detail && detail !== 'Internal Server Error' && detail !== String(status)) {
    return detail
  }
  // 通用状态码映射
  const map: Record<number, string> = {
    400: '请求参数不正确，请检查填写内容',
    401: '登录信息已过期，请重新登录',
    403: '您没有权限执行此操作',
    404: '请求的资源不存在或已被删除',
    409: '数据冲突，请检查后重试',
    422: '提交的数据格式不正确',
    500: '服务器繁忙，请稍后重试',
    502: '网关错误，请稍后重试',
    503: '服务暂不可用，请稍后重试',
  }
  return map[status] || `请求失败（错误码：${status}）`
}

// 响应拦截器
request.interceptors.response.use(
  (response) => response,
  (error) => {
    // 网络错误（无响应）
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请检查网络后重试')
      } else if (error.message?.includes('Network Error')) {
        ElMessage.error('网络连接失败，请检查网络后重试')
      } else {
        ElMessage.error('网络异常，请稍后重试')
      }
      return Promise.reject(error)
    }

    const { status, data } = error.response

    // 401 统一跳转登录页
    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
      ElMessage.error('登录信息已过期，请重新登录')
      return Promise.reject(error)
    }

    // 其他错误：优先使用后端返回的 detail
    const msg = getErrorMessage(status, data?.detail || '')
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

export default request