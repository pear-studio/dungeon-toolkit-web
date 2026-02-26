import { create } from 'zustand'
import api from '../lib/api'

interface UserInfo {
  id: string
  email: string
  username: string
  avatar: string
  date_joined: string
}

interface AuthState {
  user: UserInfo | null
  isAuthenticated: boolean
  isLoading: boolean
  // 登录（支持邮箱或用户名）
  login: (identifier: string, password: string) => Promise<void>
  // 注册
  register: (email: string, username: string, password: string) => Promise<void>
  // 登出
  logout: () => void
  // 从 token 恢复用户信息
  restoreSession: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (identifier, password) => {
    const res = await api.post('/auth/login/', { identifier, password })
    const { access, refresh, user } = res.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    set({ user, isAuthenticated: true, isLoading: false })
  },

  register: async (email, username, password) => {
    const res = await api.post('/auth/register/', { email, username, password })
    const { access, refresh, user } = res.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    set({ user, isAuthenticated: true, isLoading: false })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false, isLoading: false })
  },

  restoreSession: async () => {
    console.log('🔄 开始恢复会话...')
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      console.log('❌ 没有找到 token，设置为未登录状态')
      set({ isLoading: false, isAuthenticated: false, user: null })
      return
    }

    console.log('🔍 找到 token，验证用户信息...')
    
    try {
      const res = await api.get('/auth/me/')
      console.log('✅ 用户验证成功:', res.data)
      set({ user: res.data, isAuthenticated: true, isLoading: false })
    } catch (error) {
      console.log('❌ 用户验证失败:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },
}))

// ⚡ 在模块加载时立即开始恢复会话，不等待 React 渲染周期
// 这样 ProtectedRoute 第一次渲染时，restoreSession 就已经在进行中了
const initSession = async () => {
  try {
    await useAuthStore.getState().restoreSession()
  } catch (error) {
    console.error('💥 初始化会话时出错:', error)
    // 确保即使出错也要设置 isLoading = false
    useAuthStore.setState({ isLoading: false, isAuthenticated: false, user: null })
  }
}

initSession()