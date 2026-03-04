import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProtectedRoute from './components/ProtectedRoute'
import RobotPlazaPage from './pages/robots/RobotPlazaPage'
import RobotDetailPage from './pages/robots/RobotDetailPage'
import MyRobotsPage from './pages/robots/MyRobotsPage'
import RobotFormPage from './pages/robots/RobotFormPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  const isLoading = useAuthStore((s) => s.isLoading)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-spin">⚙️</div>
          <p className="text-slate-400">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

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
          path="/robots/my/bind"
          element={
            <ProtectedRoute>
              <RobotFormPage />
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

        <Route path="/" element={<Navigate to="/robots" replace />} />
        <Route path="*" element={<Navigate to="/robots" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
