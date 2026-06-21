import http from './index'

export const doctorApi = {
  list:   (params) => http.get('/doctors', { params }),
  me:     ()       => http.get('/doctors/me'),
  getById:(id)     => http.get(`/doctors/${id}`),
}
