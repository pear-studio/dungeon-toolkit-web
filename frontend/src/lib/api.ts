import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const AUTH_PATHS = ['/auth/login/', '/auth/register/', '/auth/refresh/']
const REFRESH_PATH = '/auth/refresh/'
let isRefreshing = false
let refreshPromise: Promise<string> | null = null

interface RetryableRequestConfig {
  _retry?: boolean
  headers?: Record<string, string>
  url?: string
}

async function refreshAccessToken(): Promise<string> {
  if (refreshPromise) {
    return refreshPromise
  }

  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) {
    throw new Error('No refresh token available')
  }

  isRefreshing = true
  refreshPromise = api
    .post<{ access: string }>(REFRESH_PATH, { refresh })
    .then((res) => {
      const nextAccess = res.data.access
      localStorage.setItem('access_token', nextAccess)
      return nextAccess
    })
    .finally(() => {
      isRefreshing = false
      refreshPromise = null
    })

  return refreshPromise
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = (error.config ?? {}) as RetryableRequestConfig
    const requestUrl = originalRequest.url ?? ''
    const isAuthEndpoint = AUTH_PATHS.some((p) => requestUrl.includes(p))
    const isUnauthorized = error.response?.status === 401

    if (isUnauthorized && !isAuthEndpoint && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const nextAccess = isRefreshing ? await refreshPromise! : await refreshAccessToken()
        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${nextAccess}`,
        }
        return api(originalRequest)
      } catch {
        // Refresh failed, fallback to logout flow.
      }
    }

    if (isUnauthorized && !isAuthEndpoint) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── 类型定义 ──────────────────────────────────────────────

export interface Bot {
  id: string
  bot_id: string
  nickname: string
  master: string
  master_qq: string
  version: string
  description: string
  is_public: boolean
  status: 'online' | 'offline' | 'unknown'
  last_seen: string | null
  created_at: string
  api_key?: string
  updated_at: string
}

export interface LoginData {
  identifier: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
}

export interface AuthResponse {
  user: {
    id: string
    email: string
    username: string
  }
  access: string
  refresh: string
}

// ── API 方法 ──────────────────────────────────────────────

export const authApi = {
  login: (data: LoginData) => api.post<AuthResponse>('/auth/login/', data),
  register: (data: RegisterData) => api.post<AuthResponse>('/auth/register/', data),
  me: () => api.get('/auth/me/'),
  refresh: (refresh: string) => api.post(REFRESH_PATH, { refresh }),
}

export const botApi = {
  list: (params?: { search?: string; status?: string }) =>
    api.get<{ results: Bot[] }>('/bots/', { params }),
  listMy: () => api.get<{ results: Bot[] }>('/bots/my/'),
  get: (id: string) => api.get<Bot>(`/bots/${id}/`),
  bind: (botId: string) => api.post<{ message: string }>('/bots/bind/', { bot_id: botId }),
  regenerateKey: (id: string) => api.post<{ api_key: string }>(`/bots/${id}/regenerate-key/`),
  delete: (id: string) => api.delete(`/bots/${id}/delete/`),
}

export default api
