import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const UNSAFE = new Set(['post', 'put', 'patch', 'delete'])

function readCookie(name: string): string | null {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'))
  return m ? decodeURIComponent(m[1]) : null
}

export const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  withCredentials: true,
})

http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (config.method && UNSAFE.has(config.method)) {
    const csrf = readCookie('csrf_token')
    if (csrf) config.headers.set('X-CSRF-Token', csrf)
  }
  return config
})

// Single-flight refresh: many parallel 401s share one /auth/refresh call.
let refreshing: Promise<boolean> | null = null
let onAuthLost: (() => void) | null = null

export function setAuthLostHandler(fn: () => void) {
  onAuthLost = fn
}

async function tryRefresh(): Promise<boolean> {
  if (!refreshing) {
    refreshing = http
      .post('/auth/refresh')
      .then(() => true)
      .catch(() => false)
      .finally(() => {
        refreshing = null
      })
  }
  return refreshing
}

http.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined
    const url = original?.url || ''
    const isAuthCall = url.includes('/auth/refresh') || url.includes('/auth/otp') || url.includes('/auth/logout')

    if (error.response?.status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true
      if (await tryRefresh()) return http(original)
      onAuthLost?.()
    }
    return Promise.reject(error)
  },
)
