import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import ProtectedRoute from './components/ProtectedRoute'

const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const RobotPlazaPage = lazy(() => import('./pages/robots/RobotPlazaPage'))
const RobotDetailPage = lazy(() => import('./pages/robots/RobotDetailPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))

function RouteFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="text-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  )
}

function App() {
  const isLoading = useAuthStore((s) => s.isLoading)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route path="/robots" element={<RobotPlazaPage />} />
          <Route path="/robots/:id" element={<RobotDetailPage />} />

          <Route path="/robots/my" element={<Navigate to="/profile" replace />} />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          {/* 重定向 */}
          <Route path="/robots/my/bind" element={<Navigate to="/profile" replace />} />
          <Route path="/dashboard" element={<Navigate to="/robots" replace />} />
          <Route path="/" element={<Navigate to="/robots" replace />} />
          <Route path="*" element={<Navigate to="/robots" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App