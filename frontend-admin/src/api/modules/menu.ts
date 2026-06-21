import request from '../request'

export const menuApi = {
  getTree() {
    return request.get('/api/v1/menus/tree')
  },
  getSidebar() {
    return request.get('/api/v1/menus/sidebar')
  },
  getAssignable() {
    return request.get('/api/v1/menus/assignable')
  },
  create(data: any) {
    return request.post('/api/v1/menus', data)
  },
  update(id: number, data: any) {
    return request.put(`/api/v1/menus/${id}`, data)
  },
  remove(id: number) {
    return request.delete(`/api/v1/menus/${id}`)
  },
}