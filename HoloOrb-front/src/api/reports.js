import request from '@/utils/request'

export function listReports(params) {
  return request.get('/api/reports', { params })
}

export function getReport(id) {
  return request.get(`/api/reports/${id}`)
}

export function createReport(data) {
  return request.post('/api/reports', data)
}

export function updateReport(id, data) {
  return request.patch(`/api/reports/${id}`, data)
}

export function deleteReport(id) {
  return request.delete(`/api/reports/${id}`)
}