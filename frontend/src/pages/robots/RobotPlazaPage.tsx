import { useState, useEffect } from 'react'
import { Search, Filter } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'
import { INPUT, ALERT, LAYOUT } from '../../lib/constants'
import { cn } from '../../lib/utils'
import Header from '../../components/Header'
import RobotCard from '../../components/RobotCard'
import RobotCardSkeleton from '../../components/RobotCardSkeleton'
import EmptyState from '../../components/EmptyState'

export default function RobotPlazaPage() {
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadBots()
  }, [search, statusFilter])

  const loadBots = async () => {
    setLoading(true)
    try {
      const params: { search?: string; status?: string } = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await botApi.list(params)
      setBots(res.data.results)
      setError('')
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className={cn(LAYOUT.container, LAYOUT.section)}>
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden="true" />
            <input
              type="text"
              placeholder="搜索机器人..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={cn(INPUT.base, "pl-10")}
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden="true" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg pl-10 pr-8 py-2 text-gray-900 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            >
              <option value="">全部状态</option>
              <option value="online">在线</option>
              <option value="offline">离线</option>
            </select>
          </div>
        </div>

        {error && (
          <div className={cn(ALERT.error, "mb-4")} role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <RobotCardSkeleton count={6} layout="grid" />
        ) : bots.length === 0 ? (
          <EmptyState title="暂无机器人" />
        ) : (
          <div className={LAYOUT.grid3}>
            {bots.map((bot) => (
              <RobotCard key={bot.id} bot={bot} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}