import request from '@/utils/request'

export function listMetrics(params) {
  return request.get('/api/metrics', { params })
}

export function getLatestMetrics() {
  return request.get('/api/metrics/latest/all')
}

export function getDeviceLatestMetric(deviceId) {
  return request.get(`/api/metrics/${deviceId}/latest`)
}

export function getDeviceTrend(deviceId, params) {
  return request.get(`/api/metrics/${deviceId}/trend`, { params })
}

export function createMetric(data) {
  return request.post('/api/metrics', data)
}

export function batchCreateMetrics(data) {
  return request.post('/api/metrics/batch', data)
}