import http from './index'

export const departmentApi = {
  list:      ()   => http.get('/departments'),
  getById:   (id) => http.get(`/departments/${id}`),
  // admin
  create:    (data)     => http.post('/admin/departments', data),
  update:    (id, data) => http.put(`/admin/departments/${id}`, data),
}
