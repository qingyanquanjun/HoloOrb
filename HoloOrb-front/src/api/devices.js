import request from '@/utils/request'

export function listDevices(params) {
  return request.get('/api/devices', { params })
}

export function getDevice(id) {
  return request.get(`/api/devices/${id}`)
}

export function createDevice(data) {
  return request.post('/api/devices', data)
}

export function updateDevice(id, data) {
  return request.put(`/api/devices/${id}`, data)
}

export function deleteDevice(id) {
  return request.delete(`/api/devices/${id}`)
}

export function updateDeviceStatus(id, data) {
  return request.patch(`/api/devices/${id}/status`, data)
}

export function getDeviceSummary() {
  return request.get('/api/devices/summary/counts')
}

export function listAreas() {
  return request.get('/api/devices/areas')
}