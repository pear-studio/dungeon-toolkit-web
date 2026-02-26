import { useEffect } from 'react'
import { useGamedataStore } from '../stores/gamedataStore'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useCharacterStore } from '../stores/characterStore'
import CharacterCard from '../components/CharacterCard'

// 空状态：点击即进入创建向导
function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <button
      onClick={onCreate}
      className="border-2 border-dashed border-slate-600 rounded-xl p-10 flex flex-col
                 items-center justify-center text-slate-500 hover:border-amber-500/50
                 hover:text-amber-500/70 transition cursor-pointer group w-full"
    >
      <div className="text-5xl mb-3 group-hover:scale-110 transition">✨</div>
      <p className="font-semibold text-base">创建你的第一个角色</p>
      <p className="text-sm mt-1 text-slate-600">开始你的冒险</p>
    </button>
  )
}

// 骨架屏加载状态
function SkeletonCard() {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 bg-slate-700 rounded-xl" />
        <div className="flex-1 space-y-2 pt-1">
          <div className="h-4 bg-slate-700 rounded w-2/3" />
          <div className="h-3 bg-slate-700 rounded w-1/2" />
          <div className="h-5 bg-slate-700 rounded w-12 mt-2" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const { fetchAll: fetchGamedata } = useGamedataStore()
  const { characters, loading, error, fetchCharacters, deleteCharacter, toggleShare } =
    useCharacterStore()

  useEffect(() => {
    fetchCharacters()
    fetchGamedata()
  }, [fetchCharacters, fetchGamedata])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const goToWizard = () => navigate('/create')

  return (
    <div className="min-h-screen bg-slate-900">
      {/* 顶部导航 */}
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚔️</span>
            <span className="text-lg font-bold text-amber-400">Dungeon Toolkit</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400 hidden sm:block">
              🧙 {user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-400 hover:text-white transition px-3 py-1.5
                         border border-slate-700 hover:border-slate-500 rounded-lg"
            >
              退出
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-10">
        {/* 欢迎横幅 */}
        <div className="mb-10 bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-slate-800
                        border border-amber-500/20 rounded-2xl p-8">
          <div className="flex items-center gap-4">
            <div className="text-5xl">🏰</div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                欢迎回来，<span className="text-amber-400">{user?.username}</span>！
              </h1>
              <p className="text-slate-400 mt-1">
                你的冒险者大厅已准备就绪。创建角色，踏上传奇旅程。
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={goToWizard}
              className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-900
                         font-semibold rounded-lg transition text-sm cursor-pointer"
            >
              ✨ 创建新角色
            </button>
          </div>
        </div>

        {/* 角色列表 */}
        <section>
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-white">我的角色</h2>
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-500">
                {loading ? '加载中...' : `${characters.length} / 20 个角色位`}
              </span>
              {characters.length > 0 && (
                <button
                  onClick={goToWizard}
                  className="text-sm text-amber-400 hover:text-amber-300 transition
                             border border-amber-500/30 hover:border-amber-500/60
                             px-3 py-1 rounded-lg"
                >
                  + 新建
                </button>
              )}
            </div>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl
                            text-red-400 text-sm flex items-center gap-2">
              <span>⚠️</span>
              <span>{error}</span>
              <button
                onClick={fetchCharacters}
                className="ml-auto underline hover:no-underline"
              >
                重试
              </button>
            </div>
          )}

          {/* 骨架屏 */}
          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
            </div>
          )}

          {/* 空状态 */}
          {!loading && !error && characters.length === 0 && (
            <EmptyState onCreate={goToWizard} />
          )}

          {/* 角色卡片网格 */}
          {!loading && characters.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {characters.map((char) => (
                <CharacterCard
                  key={char.id}
                  character={char}
                  onDelete={deleteCharacter}
                  onToggleShare={toggleShare}
                />
              ))}
              {/* 末尾加新建卡 */}
              {characters.length < 20 && (
                <button
                  onClick={goToWizard}
                  className="border-2 border-dashed border-slate-700 rounded-xl p-5
                             flex flex-col items-center justify-center text-slate-600
                             hover:border-amber-500/40 hover:text-amber-500/60
                             transition cursor-pointer group min-h-[120px]"
                >
                  <div className="text-3xl mb-2 group-hover:scale-110 transition">＋</div>
                  <p className="text-sm font-medium">创建新角色</p>
                </button>
              )}
            </div>
          )}
        </section>
      </main>

      {/* 底部版本信息 */}
      <footer className="border-t border-slate-800 mt-16 py-6 text-center text-sm text-slate-600">
        Dungeon Toolkit v0.1.0 · 使用 React + Django 构建
      </footer>
    </div>
  )
}