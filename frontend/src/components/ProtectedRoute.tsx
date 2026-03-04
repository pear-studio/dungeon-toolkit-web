import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Loader, Shield } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

/**
 * 受保护的路由：未登录时跳转到 /login
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <Loader className="w-12 h-12 text-amber-400 mx-auto mb-4 animate-spin" aria-hidden="true" />
          <p className="text-slate-300">加载中...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
