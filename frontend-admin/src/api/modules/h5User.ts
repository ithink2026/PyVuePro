import request from '../request'

export const h5UserApi = {
  getList(params?: { username?: string }) {
    return request.get('/api/v1/h5-users', { params })
  },
  toggleStatus(id: number, isActive: boolean) {
    return request.put(`/api/v1/h5-users/${id}/toggle-status`, { is_active: isActive })
  },
  resetPassword(id: number) {
    return request.post(`/api/v1/h5-users/${id}/reset-password`)
  },
}
