import request from '../request'
import type { UniResponse } from '../request'

export const authApi = {
  /** 获取 H5 登录方式 */
  getLoginMode(): Promise<UniResponse> {
    return request.get('/api/v1/auth/h5/login-mode')
  },
  /** H5 端用户名+密码登录 */
  login(username: string, password: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/login', { username, password })
  },
  /** IP 自动登录 */
  ipLogin(): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/ip-login')
  },
  /** 发送手机验证码 */
  sendCode(phone: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/send-code', { phone })
  },
  /** 手机号注册 */
  register(phone: string, code: string, password: string, confirmPassword: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/register', {
      phone, code, password, confirm_password: confirmPassword,
    })
  },
  /** 手机号 + 验证码登录 */
  phoneCodeLogin(phone: string, code: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/phone-login', { phone, code })
  },
  /** 手机号 + 密码登录 */
  phonePassLogin(phone: string, password: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/h5/phone-login', { phone, password })
  },
  /** 刷新 Token */
  refresh(refreshToken: string): Promise<UniResponse> {
    return request.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
  },
}
