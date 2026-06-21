import http from './index'

export const prescriptionApi = {
  create:  (data) => http.post('/prescriptions', data),
  getById: (id)   => http.get(`/prescriptions/${id}`),
}
