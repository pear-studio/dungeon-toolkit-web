import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截：自动带上 JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 时清除 token 并跳转登录
// 注意：登录/注册接口本身返回 401 时不应跳转，只有"已登录但 token 失效"才跳转
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

export interface Character {
  id: string
  name: string
  gender: string
  age: number | null
  appearance: string
  backstory: string
  ruleset_slug: string
  race_slug: string
  subrace_slug: string | null
  class_slug: string
  background_slug: string
  alignment: string
  level: number
  experience_points: number
  ability_scores: Record<string, number>
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  personality_trait: string
  ideal: string
  bond: string
  flaw: string
  is_public: boolean
  share_token: string
  created_at: string
  updated_at: string
}

export interface Race {
  id: string
  slug: string
  name: string
  has_subraces: boolean
  subraces?: { id: string; slug: string; name: string }[]
  traits: Record<string, unknown>
}

export interface CharClass {
  id: string
  slug: string
  name: string
  is_spellcaster: boolean
  hit_die: number
  primary_ability: string
  saving_throws: string[]
}

export interface Background {
  id: string
  slug: string
  name: string
  skill_proficiencies: string[]
  feature_name: string
  feature_description: string
}

// ── API 方法 ──────────────────────────────────────────────

// 角色
export const characterApi = {
  list: () => api.get<Character[]>('/characters/'),
  get: (id: string) => api.get<Character>(`/characters/${id}/`),
  create: (data: Partial<Character>) => api.post<Character>('/characters/', data),
  update: (id: string, data: Partial<Character>) => api.patch<Character>(`/characters/${id}/`, data),
  delete: (id: string) => api.delete(`/characters/${id}/`),
  toggleShare: (id: string) => api.post<Character>(`/characters/${id}/toggle_share/`),
}

// DRF 分页响应包装
export interface PagedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 游戏数据
export const gamedataApi = {
  races: () => api.get<PagedResponse<Race>>('/gamedata/races/'),
  race: (slug: string) => api.get<Race>(`/gamedata/races/${slug}/`),
  classes: () => api.get<PagedResponse<CharClass>>('/gamedata/classes/'),
  backgrounds: () => api.get<PagedResponse<Background>>('/gamedata/backgrounds/'),
}

export default api