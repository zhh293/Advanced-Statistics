import http from './index'

export const medicalRecordApi = {
  create:  (data)     => http.post('/medical-records', data),
  getById: (id)       => http.get(`/medical-records/${id}`),
  update:  (id, data) => http.put(`/medical-records/${id}`, data),
}
