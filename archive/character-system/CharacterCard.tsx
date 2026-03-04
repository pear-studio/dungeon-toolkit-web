import { useState } from 'react'
import type { Character } from '../lib/api'
import { useGamedataStore } from '../stores/gamedataStore'

// 职业图标（纯 UI 装饰，允许硬编码）
const CLASS_ICONS: Record<string, string> = {
  barbarian: '⚔️', bard: '🎵', cleric: '✝️', druid: '🌿',
  fighter: '🛡️', monk: '👊', paladin: '⚜️', ranger: '🏹',
  rogue: '🗡️', sorcerer: '🔮', warlock: '👁️', wizard: '📚',
}

interface CharacterCardProps {
  character: Character
  onDelete: (id: string) => void
  onToggleShare: (id: string) => void
}

export default function CharacterCard({ character, onDelete, onToggleShare }: CharacterCardProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const { raceName, className: classNameFn } = useGamedataStore()

  const icon = CLASS_ICONS[character.class_slug] ?? '🧙'
  const raceName_ = raceName(character.race_slug)
  const className_ = classNameFn(character.class_slug)

  const handleDelete = async () => {
    if (!confirm(`确定要删除角色「${character.name}」吗？此操作无法撤销。`)) return
    setDeleting(true)
    await onDelete(character.id)
  }

  return (
    <div className="relative bg-slate-800 border border-slate-700 rounded-xl p-5
                    hover:border-amber-500/40 transition group">
      {/* 更多菜单按钮 */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="absolute top-3 right-3 w-7 h-7 flex items-center justify-center
                   text-slate-500 hover:text-white rounded-lg hover:bg-slate-700 transition text-lg"
      >
        ⋯
      </button>
      {menuOpen && (
        <div
          className="absolute top-10 right-3 z-20 bg-slate-700 border border-slate-600
                     rounded-lg shadow-xl py-1 min-w-[130px]"
          onBlur={() => setMenuOpen(false)}
        >
          <button
            onClick={() => { onToggleShare(character.id); setMenuOpen(false) }}
            className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-600 hover:text-white transition"
          >
            {character.is_public ? '🔒 取消分享' : '🔗 公开分享'}
          </button>
          <hr className="border-slate-600 my-1" />
          <button
            onClick={() => { handleDelete(); setMenuOpen(false) }}
            disabled={deleting}
            className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-slate-600 hover:text-red-300 transition disabled:opacity-50"
          >
            🗑️ 删除角色
          </button>
        </div>
      )}

      {/* 关闭菜单的背景遮罩 */}
      {menuOpen && (
        <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
      )}

      {/* 角色主体 */}
      <div className="flex items-start gap-4">
        {/* 头像区 */}
        <div className="w-14 h-14 rounded-xl bg-slate-700/80 border border-slate-600
                        flex items-center justify-center text-3xl flex-shrink-0">
          {icon}
        </div>
        {/* 信息区 */}
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-white truncate pr-6">{character.name}</h3>
          <p className="text-sm text-slate-400 mt-0.5">
            {raceName_} · {className_}
          </p>
          <div className="mt-2 flex items-center gap-3">
            <span className="text-xs bg-amber-500/15 text-amber-400 px-2 py-0.5 rounded-full">
              Lv.{character.level}
            </span>
            {character.is_public && (
              <span className="text-xs bg-green-500/15 text-green-400 px-2 py-0.5 rounded-full">
                🔗 已分享
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 属性值缩略 */}
      {character.ability_scores && Object.keys(character.ability_scores).length > 0 && (
        <div className="mt-4 grid grid-cols-6 gap-1 border-t border-slate-700 pt-4">
          {(['str', 'dex', 'con', 'int', 'wis', 'cha'] as const).map((attr) => {
            const val = character.ability_scores[attr] ?? '—'
            const mod = typeof val === 'number' ? Math.floor((val - 10) / 2) : null
            return (
              <div key={attr} className="text-center">
                <div className="text-xs text-slate-400 uppercase">{attr}</div>
                <div className="text-sm font-bold text-white">{val}</div>
                {mod !== null && (
                  <div className="text-xs text-slate-400">
                    {mod >= 0 ? `+${mod}` : mod}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
