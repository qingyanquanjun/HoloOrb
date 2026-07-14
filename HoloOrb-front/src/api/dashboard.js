import request from '@/utils/request'

export function getOverview() {
  return request.get('/api/dashboard/overview')
}

export function getCpuMemoryTrend(params) {
  return request.get('/api/dashboard/cpu-memory', { params })
}

export function getTrafficTrend(params) {
  return request.get('/api/dashboard/traffic', { params })
}

export function getDevicesByType() {
  return request.get('/api/dashboard/devices-by-type')
}

export function getRecentAlarms(params) {
  return request.get('/api/dashboard/recent-alarms', { params })
}