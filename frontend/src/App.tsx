import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/ProtectedRoute'
import RobotPlazaPage from './pages/robots/RobotPlazaPage'
import RobotDetailPage from './pages/robots/RobotDetailPage'
import MyRobotsPage from './pages/robots/MyRobotsPage'
import ProfilePage from './pages/ProfilePage'

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
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/robots" element={<RobotPlazaPage />} />
        <Route path="/robots/:id" element={<RobotDetailPage />} />

        <Route
          path="/robots/my"
          element={
            <ProtectedRoute>
              <MyRobotsPage />
            </ProtectedRoute>
          }
        />

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
    </BrowserRouter>
  )
}

export default App