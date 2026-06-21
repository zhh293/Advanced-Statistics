import http from './index'

export const appointmentApi = {
  create:   (data)         => http.post('/appointments', data),
  list:     (params)       => http.get('/appointments', { params }),
  today:    (params)       => http.get('/appointments/today', { params }),
  getById:  (id)           => http.get(`/appointments/${id}`),
  cancel:   (id, data)     => http.put(`/appointments/${id}/cancel`, data),
}
