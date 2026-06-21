import http from './index'

export const adminApi = {
  statistics:       (params) => http.get('/admin/statistics', { params }),
  updateUserStatus: (id, data) => http.put(`/admin/users/${id}/status`, data),
}
