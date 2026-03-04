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

const AUTH_PATHS = ['/auth/login/', '/auth/register/', '/auth/token/refresh/']

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error.config?.url ?? ''
    const isAuthEndpoint = AUTH_PATHS.some((p) => requestUrl.includes(p))

    if (error.response?.status === 401 && !isAuthEndpoint) {
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
  refresh: (refresh: string) => api.post('/auth/refresh/', { refresh }),
}

export const botApi = {
  list: (params?: { search?: string; status?: string }) =>
    api.get<{ results: Bot[] }>('/bots/', { params }),
  get: (id: string) => api.get<Bot>(`/bots/${id}/`),
  create: (data: Partial<Bot>) => api.post<Bot>('/bots/', data),
  update: (id: string, data: Partial<Bot>) => api.put<Bot>(`/bots/${id}/update/`, data),
  delete: (id: string) => api.delete(`/bots/${id}/delete/`),
}

export default api
