import request from '@/utils/request'

export function listLogs(params) {
  return request.get('/api/logs', { params })
}

export function getLog(id) {
  return request.get(`/api/logs/${id}`)
}