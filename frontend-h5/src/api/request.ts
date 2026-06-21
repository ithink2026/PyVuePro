/**
 * 统一请求封装（基于 uni.request）
 *
 * 功能：
 * - 请求拦截：自动注入 Token、统一请求头
 * - 响应拦截：错误统一处理、401 自动跳转登录
 * - 文件上传：基于 uni.uploadFile 封装
 */

// ─── 类型定义 ───
interface RequestConfig {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  data?: any
  params?: Record<string, any>
  header?: Record<string, string>
  timeout?: number
}

interface UniResponse {
  data: any
  statusCode: number
  header: Record<string, string>
}

// ─── 错误码友好提示映射 ───
const ERROR_MAP: Record<number, string> = {
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

// ─── 请求拦截器 ───
function requestInterceptor(config: RequestConfig): RequestConfig {
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
    ...config.header,
  }

  try {
    const token = uni.getStorageSync('access_token')
    if (token) {
      header.Authorization = `Bearer ${token}`
    }
  } catch {}

  return { ...config, header }
}

// ─── 响应拦截器 ───
function responseInterceptor(res: UniResponse): UniResponse | never {
  // 成功响应，直接返回
  if (res.statusCode >= 200 && res.statusCode < 300) {
    return res
  }

  // 401 Token过期 → 清除登录态并跳转登录页
  if (res.statusCode === 401) {
    try {
      uni.removeStorageSync('access_token')
      uni.removeStorageSync('refresh_token')
    } catch {}
    uni.reLaunch({ url: '/pages/login/index' })
    uni.showToast({ title: '登录信息已过期，请重新登录', icon: 'none', duration: 2500 })
    throw { statusCode: 401, message: '登录信息已过期，请重新登录' }
  }

  // 其他错误：优先使用后端返回的 detail
  let msg = ''
  if (res.data && typeof res.data === 'object') {
    msg = res.data.detail || res.data.message || ''
  }
  if (!msg || msg === 'Internal Server Error') {
    msg = ERROR_MAP[res.statusCode] || `请求失败（错误码：${res.statusCode}）`
  }

  uni.showToast({ title: msg, icon: 'none', duration: 2500 })
  throw { statusCode: res.statusCode, message: msg, data: res.data }
}

// ─── 核心请求函数 ───
function doRequest(config: RequestConfig): Promise<UniResponse> {
  // 请求拦截
  const processed = requestInterceptor(config)

  // 处理查询参数
  let url = processed.url
  if (processed.params && Object.keys(processed.params).length > 0) {
    const query = Object.entries(processed.params)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&')
    url += (url.includes('?') ? '&' : '?') + query
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method: processed.method || 'GET',
      data: processed.data,
      header: processed.header,
      timeout: processed.timeout || 15000,
      success: (res) => {
        try {
          const result = responseInterceptor(res as UniResponse)
          resolve(result)
        } catch (err) {
          reject(err)
        }
      },
      fail: (err) => {
        let msg = '网络异常，请稍后重试'
        if (err.errMsg) {
          if (err.errMsg.includes('timeout')) {
            msg = '请求超时，请检查网络后重试'
          } else if (err.errMsg.includes('fail')) {
            msg = '网络连接失败，请检查网络后重试'
          }
        }
        uni.showToast({ title: msg, icon: 'none', duration: 2500 })
        reject({ statusCode: 0, message: msg, err })
      },
    })
  })
}

// ─── 文件上传 ───
export interface UploadConfig {
  url: string
  filePath: string
  name?: string
  formData?: Record<string, any>
  onProgress?: (progress: number) => void
}

function doUpload(config: UploadConfig): Promise<UniResponse> {
  const header: Record<string, string> = {}
  try {
    const token = uni.getStorageSync('access_token')
    if (token) {
      header.Authorization = `Bearer ${token}`
    }
  } catch {}

  return new Promise((resolve, reject) => {
    const uploadTask = uni.uploadFile({
      url: config.url,
      filePath: config.filePath,
      name: config.name || 'file',
      formData: config.formData,
      header,
      success: (res) => {
        try {
          // uni.uploadFile 返回的 data 是字符串，需要解析
          const parsed = JSON.parse(res.data)
          const result: UniResponse = {
            data: parsed,
            statusCode: res.statusCode,
            header: {},
          }
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(result)
          } else {
            const msg = parsed?.detail || ERROR_MAP[res.statusCode] || '上传失败'
            uni.showToast({ title: msg, icon: 'none', duration: 2500 })
            reject({ statusCode: res.statusCode, message: msg, data: parsed })
          }
        } catch {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve({ data: res.data, statusCode: res.statusCode, header: {} })
          } else {
            uni.showToast({ title: '上传失败，请稍后重试', icon: 'none', duration: 2500 })
            reject({ statusCode: res.statusCode, message: '上传失败' })
          }
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败，请检查网络后重试', icon: 'none', duration: 2500 })
        reject({ statusCode: 0, message: '上传失败', err })
      },
    })

    // 上传进度监听
    if (config.onProgress) {
      uploadTask.onProgressUpdate((res) => {
        config.onProgress?.(res.progress)
      })
    }
  })
}

// ─── 导出请求方法 ───
const request = {
  get(url: string, params?: Record<string, any>) {
    return doRequest({ url, method: 'GET', params })
  },
  post(url: string, data?: any) {
    return doRequest({ url, method: 'POST', data })
  },
  put(url: string, data?: any) {
    return doRequest({ url, method: 'PUT', data })
  },
  delete(url: string, params?: Record<string, any>) {
    return doRequest({ url, method: 'DELETE', params })
  },
  upload(config: UploadConfig) {
    return doUpload(config)
  },
}

export default request
export type { UniResponse, RequestConfig, UploadConfig }