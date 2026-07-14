import request from '@/utils/request'

export function listUsers(params) {
  return request.get('/api/users', { params })
}

export function getUser(id) {
  return request.get(`/api/users/${id}`)
}

export function createUser(data) {
  return request.post('/api/users', data)
}

export function updateUser(id, data) {
  return request.put(`/api/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/api/users/${id}`)
}

export function resetPassword(id, data) {
  return request.patch(`/api/users/${id}/password`, data)
}

export function updateUserStatus(id, data) {
  return request.patch(`/api/users/${id}/status`, data)
}

export function login(data) {
  return request.post('/api/auth/login', data)
}

export function register(data) {
  return request.post('/api/auth/register', data)
}

export function getCurrentUser() {
  return request.get('/api/auth/me')
}

export function changePassword(data) {
  return request.patch('/api/auth/me/password', data)
}