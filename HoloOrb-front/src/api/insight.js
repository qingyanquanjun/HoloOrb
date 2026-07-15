import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

export function chat(data) {
  return request({
    url: '/api/insight/chat',
    method: 'post',
    data: { ...data, stream: false }
  })
}

/**
 * 流式聊天 - 通过 SSE 接收 AI 的逐字回复
 * @param {Object} data - { message, history }
 * @param {Function} onChunk - 每收到一个文本块时回调 (text: string) => void
 * @param {AbortSignal} signal - 可选，用于取消请求
 * @returns {Promise<string>} 完整的回复文本
 */
export async function chatStream(data, onChunk, signal) {
  const userStore = useUserStore()
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''

  const response = await fetch(`${baseURL}/api/insight/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userStore.token}`
    },
    body: JSON.stringify({ ...data, stream: true }),
    signal
  })

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    throw new Error(errData.message || `请求失败 (${response.status})`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let fullContent = ''
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim()
        if (data === '[DONE]') {
          return fullContent
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.error) {
            throw new Error(parsed.error)
          }
          if (parsed.content) {
            fullContent += parsed.content
            onChunk(parsed.content)
          }
        } catch (e) {
          if (e.message && e.message !== 'Unexpected end of JSON input') {
            throw e
          }
        }
      }
    }
  }

  return fullContent
}

export function saveReport(data) {
  return request({
    url: '/api/insight/save-report',
    method: 'post',
    data
  })
}