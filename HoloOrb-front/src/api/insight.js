import request from '@/utils/request'

export function chat(data) {
  return request({
    url: '/api/insight/chat',
    method: 'post',
    data
  })
}