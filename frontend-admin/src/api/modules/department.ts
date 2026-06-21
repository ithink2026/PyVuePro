import request from '../request'

export const departmentApi = {
  getTree() {
    return request.get('/api/v1/departments/tree')
  },
  create(data: any) {
    return request.post('/api/v1/departments', data)
  },
  update(id: number, data: any) {
    return request.put(`/api/v1/departments/${id}`, data)
  },
  remove(id: number) {
    return request.delete(`/api/v1/departments/${id}`)
  },
}