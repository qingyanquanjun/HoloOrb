import request from '@/utils/request'

export function listAlerts(params) {
  return request.get('/api/alerts', { params })
}

export function getAlert(id) {
  return request.get(`/api/alerts/${id}`)
}

export function createAlert(data) {
  return request.post('/api/alerts', data)
}

export function updateAlertStatus(id, data) {
  return request.patch(`/api/alerts/${id}/status`, data)
}

export function ackAlert(id, data) {
  return request.patch(`/api/alerts/${id}/ack`, data)
}

export function resolveAlert(id, data) {
  return request.patch(`/api/alerts/${id}/resolve`, data)
}

export function deleteAlert(id) {
  return request.delete(`/api/alerts/${id}`)
}

export function batchAckAlerts(data) {
  return request.patch('/api/alerts/batch/ack', data)
}

export function batchResolveAlerts(data) {
  return request.patch('/api/alerts/batch/resolve', data)
}

export function batchDeleteAlerts(data) {
  return request.delete('/api/alerts/batch', { data })
}

export function getAlertSummary() {
  return request.get('/api/alerts/summary/counts')
}