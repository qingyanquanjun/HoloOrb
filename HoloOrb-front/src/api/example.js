import request from '@/utils/request'

/**
 * 健康检查
 */
export function healthCheck() {
  return request.get('/api/health')
}

/**
 * 示例 GET 接口
 * @param {string} name
 */
export function sayHello(name = 'World') {
  return request.get('/api/hello', { params: { name } })
}

/**
 * 示例 POST 接口
 * @param {object} data
 */
export function echoData(data) {
  return request.post('/api/echo', data)
}
