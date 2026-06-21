import http from './index'

export const medicineApi = {
  list:    (params)     => http.get('/medicines', { params }),
  getById: (id)         => http.get(`/medicines/${id}`),
  // admin
  create:      (data)     => http.post('/admin/medicines', data),
  updateStock: (id, data) => http.put(`/admin/medicines/${id}/stock`, data),
}
