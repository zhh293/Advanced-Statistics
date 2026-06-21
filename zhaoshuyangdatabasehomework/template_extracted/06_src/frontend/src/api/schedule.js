import http from './index'

export const scheduleApi = {
  list:   (params) => http.get('/schedules', { params }),
  getById:(id)     => http.get(`/schedules/${id}`),
  // admin
  create:       (data)     => http.post('/admin/schedules', data),
  updateStatus: (id, data) => http.put(`/admin/schedules/${id}/status`, data),
}
