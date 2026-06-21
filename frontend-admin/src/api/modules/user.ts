import request from '../request'

export const userApi = {
  getList(params?: { username?: string }) {
    return request.get('/api/v1/users', { params })
  },
  create(data: any) {
    return request.post('/api/v1/users', data)
  },
  update(id: number, data: any) {
    return request.put(`/api/v1/users/${id}`, data)
  },
  remove(id: number) {
    return request.delete(`/api/v1/users/${id}`)
  },
  resetPassword(id: number) {
    return request.post(`/api/v1/users/${id}/reset-password`)
  },
}