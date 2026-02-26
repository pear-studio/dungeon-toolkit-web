import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

// 占位角色卡片
const PlaceholderCard = () => (
  <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 flex flex-col items-center
                  justify-center text-slate-500 hover:border-amber-500/50 hover:text-amber-500/70
                  transition cursor-pointer group">
    <div className="text-4xl mb-3 group-hover:scale-110 transition">✨</div>
    <p className="font-medium">创建新角色</p>
    <p className="text-sm mt-1 text-slate-600">开始你的冒险</p>
  </div>
)

// 功能卡片
interface FeatureCardProps {
  icon: string
  title: string
  desc: string
  badge?: string
}
const FeatureCard = ({ icon, title, desc, badge }: FeatureCardProps) => (
  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 hover:border-slate-600 transition">
    <div className="flex items-start gap-3">
      <div className="text-2xl">{icon}</div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-white">{title}</h3>
          {badge && (
            <span className="text-xs px-2 py-0.5 bg-amber-500/20 text-amber-400 rounded-full">{badge}</span>
          )}
        </div>
        <p className="text-sm text-slate-400 mt-1">{desc}</p>
      </div>
    </div>
  </div>
)

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* 顶部导航 */}
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚔️</span>
            <span className="text-lg font-bold text-amber-400">DNDChar</span>
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
                你的冒险者大厅已准备就绪。创建或管理你的 D&D 角色吧。
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-900
                               font-semibold rounded-lg transition text-sm cursor-pointer">
              ✨ 创建新角色
            </button>
            <button className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-white
                               font-medium rounded-lg transition text-sm cursor-pointer">
              📖 规则手册
            </button>
          </div>
        </div>

        {/* 我的角色区域 */}
        <section className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">我的角色</h2>
            <span className="text-sm text-slate-500">0 / 20 个角色位</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <PlaceholderCard />
          </div>
        </section>

        {/* 功能预告 */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-4">
            即将推出
            <span className="ml-2 text-sm font-normal text-slate-500">开发中...</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <FeatureCard
              icon="🧙‍♂️"
              title="向导式角色创建"
              desc="8步引导，从种族到背景故事，轻松创建你的第一个角色"
              badge="开发中"
            />
            <FeatureCard
              icon="🎨"
              title="AI 角色立绘"
              desc="描述你的角色，AI 为你生成专属立绘"
              badge="即将上线"
            />
            <FeatureCard
              icon="📜"
              title="角色小故事"
              desc="AI 根据背景信息自动生成角色的故事片段"
              badge="即将上线"
            />
            <FeatureCard
              icon="📚"
              title="中文规则手册"
              desc="内置完整中文 5e 规则库，支持目录导航和搜索"
              badge="开发中"
            />
          </div>
        </section>
      </main>

      {/* 底部版本信息 */}
      <footer className="border-t border-slate-800 mt-16 py-6 text-center text-sm text-slate-600">
        DNDChar v0.1.0 · 开源项目 · 使用 React + Django 构建
      </footer>
    </div>
  )
}
