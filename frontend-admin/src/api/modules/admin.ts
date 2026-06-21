import request from '../request'

export const adminApi = {
  getUserInfo() {
    return request.get('/api/v1/admin/info')
  },
  changePassword(data: { old_password: string; new_password: string }) {
    return request.post('/api/v1/admin/change-password', data)
  },
  getWsConfig() {
    return request.get('/api/v1/admin/ws-config')
  },
  toggleWs(enabled: boolean) {
    return request.post('/api/v1/admin/ws-toggle', { enabled })
  },
  getH5Status() {
    return request.get('/api/v1/admin/h5-status')
  },
  getH5Config() {
    return request.get('/api/v1/admin/h5-config')
  },
  toggleH5(enabled: boolean) {
    return request.post('/api/v1/admin/h5-config', { enabled })
  },
  getOnlineConfig() {
    return request.get('/api/v1/admin/online-config')
  },
  toggleOnline(enabled: boolean) {
    return request.post('/api/v1/admin/online-config', { enabled })
  },
  getH5LoginConfig() {
    return request.get('/api/v1/admin/h5-login-config')
  },
  toggleH5LoginMode(mode: 'ip' | 'phone') {
    return request.post('/api/v1/admin/h5-login-config', { mode })
  },
}