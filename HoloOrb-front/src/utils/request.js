import axios from 'axios'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import router from '@/router'

function stringifyValues(value) {
  if (value === null || value === undefined) return value
  if (Array.isArray(value)) return value.map(stringifyValues)
  if (typeof value === 'object' && !(value instanceof FormData)) {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, stringifyValues(item)])
    )
  }
  return String(value)
}

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

service.interceptors.request.use(
  (config) => {
    const appStore = useAppStore()
    const userStore = useUserStore()

    appStore.setLoading(true)

    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    if (config.data && !(config.data instanceof FormData)) {
      config.data = stringifyValues(config.data)
    }
    if (config.params) {
      config.params = stringifyValues(config.params)
    }

    return config
  },
  (error) => {
    const appStore = useAppStore()
    appStore.setLoading(false)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) {
        return res.data
      }
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      }
      return Promise.reject(new Error(res.message || 'Request failed'))
    }

    return res
  },
  (error) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    const status = error?.response?.status
    const errMsg = error?.response?.data?.msg || error?.response?.data?.message || ''
    if (status === 401 || (status === 422 && /token|subject/i.test(errMsg))) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
    }

    const msg = error?.response?.data?.msg || error?.response?.data?.message || error.message || '网络异常'
    console.error('[Axios Error]', msg)
    return Promise.reject(error)
  }
)

export default service