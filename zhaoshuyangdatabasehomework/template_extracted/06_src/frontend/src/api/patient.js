import http from './index'

export const patientApi = {
  createProfile: (data)   => http.post('/patients/profile', data),
  getProfile:    ()       => http.get('/patients/profile'),
  updateProfile: (data)   => http.put('/patients/profile', data),
  getRecords:    (params) => http.get('/patients/records', { params }),
}
