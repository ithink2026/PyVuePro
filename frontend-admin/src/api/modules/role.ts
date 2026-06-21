import request from '../request'

export const roleApi = {
  getList(params?: { name?: string }) {
    return request.get('/api/v1/roles', { params })
  },
  getAssignableMenus() {
    return request.get('/api/v1/menus/assignable')
  },
  create(data: any) {
    return request.post('/api/v1/roles', data)
  },
  update(id: number, data: any) {
    return request.put(`/api/v1/roles/${id}`, data)
  },
  remove(id: number) {
    return request.delete(`/api/v1/roles/${id}`)
  },
}