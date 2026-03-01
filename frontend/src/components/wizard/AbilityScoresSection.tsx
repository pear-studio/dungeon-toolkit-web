import { useState } from 'react'
import { useWizardStore } from '../../stores/wizardStore'

// 六项属性定义
const ABILITIES = [
  { key: 'str', label: '力量', en: 'STR', desc: '运动·近战攻击', color: 'text-red-400' },
  { key: 'dex', label: '敏捷', en: 'DEX', desc: '反射·远程攻击·AC', color: 'text-green-400' },
  { key: 'con', label: '体质', en: 'CON', desc: '生命值·耐力', color: 'text-orange-400' },
  { key: 'int', label: '智力', en: 'INT', desc: '知识·法术（法师）', color: 'text-blue-400' },
  { key: 'wis', label: '感知', en: 'WIS', desc: '察觉·直觉·法术（牧师）', color: 'text-cyan-400' },
  { key: 'cha', label: '魅力', en: 'CHA', desc: '说服·施压·法术（术士）', color: 'text-pink-400' },
] as const

type AbilityKey = typeof ABILITIES[number]['key']

// 标准数列
const STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

// 购点法：值 → 花费
const POINT_COST: Record<number, number> = { 8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9 }
const POINT_BUY_TOTAL = 27

// 属性调整值
function getMod(val: number): number {
  return Math.floor((val - 10) / 2)
}
function fmtMod(mod: number): string {
  return mod >= 0 ? `+${mod}` : String(mod)
}

// 种族属性加成数据（2014版）
const RACE_BONUSES: Record<string, Partial<Record<AbilityKey, number>>> = {
  human:       { str: 1, dex: 1, con: 1, int: 1, wis: 1, cha: 1 },
  elf:         { dex: 2 },
  'high-elf':  { dex: 2, int: 1 },
  'wood-elf':  { dex: 2, wis: 1 },
  dwarf:       { con: 2 },
  'hill-dwarf':  { con: 2, wis: 1 },
  'mountain-dwarf': { con: 2, str: 2 },
  halfling:    { dex: 2 },
  'lightfoot-halfling': { dex: 2, cha: 1 },
  'stout-halfling':     { dex: 2, con: 1 },
  gnome:       { int: 2 },
  'rock-gnome':  { int: 2, con: 1 },
  'forest-gnome': { int: 2, dex: 1 },
  'half-elf':  { cha: 2 },
  'half-orc':  { str: 2, con: 1 },
  tiefling:    { int: 1, cha: 2 },
  dragonborn:  { str: 2, cha: 1 },
}

function getRaceBonuses(raceSlug: string, subraceSlug: string): Partial<Record<AbilityKey, number>> {
  if (subraceSlug && RACE_BONUSES[subraceSlug]) return RACE_BONUSES[subraceSlug]
  if (RACE_BONUSES[raceSlug]) return RACE_BONUSES[raceSlug]
  return {}
}

export default function AbilityScoresSection() {
  const { data, update } = useWizardStore()
  const [dragSlot, setDragSlot] = useState<number | null>(null)
  const [dragTarget, setDragTarget] = useState<AbilityKey | null>(null)

  const method = data.score_method
  // 对于 standard / roll 方式，采用「分配槽位 → 属性」的选择逻辑
  // ability_scores 存最终值（含种族加成），score_rolls 存骰点结果

  const baseValues: number[] = method === 'standard'
    ? STANDARD_ARRAY
    : method === 'roll'
    ? (data.score_rolls.length === 6 ? data.score_rolls : STANDARD_ARRAY)
    : []

  // 对于 pointbuy，直接编辑 ability_scores 中的值
  const raceBonuses = getRaceBonuses(data.race_slug, data.subrace_slug)

  // 计算购点总花费
  const pbUsed = method === 'pointbuy'
    ? ABILITIES.reduce((sum, ab) => {
        const base = data.ability_scores[ab.key] - (raceBonuses[ab.key] ?? 0)
        return sum + (POINT_COST[base] ?? 0)
      }, 0)
    : 0

  // 对于 standard/roll：记录哪个槽位已分配给哪个属性
  // 使用 ability_scores 倒推：base = score - raceBonus
  const slotAssignment: Record<AbilityKey, number | null> = {
    str: null, dex: null, con: null, int: null, wis: null, cha: null,
  }
  const usedSlots = new Set<number>()

  if (method !== 'pointbuy' && baseValues.length === 6) {
    // 对每个属性，找到 base 值在 baseValues 中的槽位
    for (const ab of ABILITIES) {
      const base = data.ability_scores[ab.key] - (raceBonuses[ab.key] ?? 0)
      // 找第一个未使用的匹配槽位
      for (let i = 0; i < baseValues.length; i++) {
        if (!usedSlots.has(i) && baseValues[i] === base) {
          slotAssignment[ab.key] = i
          usedSlots.add(i)
          break
        }
      }
    }
  }

  const unassignedSlots = baseValues.map((_, i) => i).filter((i) => !usedSlots.has(i))

  // 分配值到属性
  const assignSlotToAbility = (slotIdx: number, abilityKey: AbilityKey) => {
    const val = baseValues[slotIdx]
    // 找出原本占据该属性的槽位
    const prevSlotIdx = slotAssignment[abilityKey]
    // 找出原本占据该槽位的属性
    const prevAbility = ABILITIES.find(ab => slotAssignment[ab.key] === slotIdx)?.key ?? null

    const newScores = { ...data.ability_scores }
    // 新值
    newScores[abilityKey] = val + (raceBonuses[abilityKey] ?? 0)
    // 如果原来有属性占用此槽，把那个属性改为原属性的槽值
    if (prevAbility && prevAbility !== abilityKey) {
      if (prevSlotIdx !== null) {
        newScores[prevAbility] = baseValues[prevSlotIdx] + (raceBonuses[prevAbility] ?? 0)
      } else {
        // 原属性没有分配，恢复为最低值+种族加成
        newScores[prevAbility] = 8 + (raceBonuses[prevAbility] ?? 0)
      }
    }
    update({ ability_scores: newScores })
  }

  // 购点法：调整单个属性值
  const pbAdjust = (key: AbilityKey, delta: number) => {
    const current = data.ability_scores[key]
    const base = current - (raceBonuses[key] ?? 0)
    const newBase = base + delta
    if (newBase < 8 || newBase > 15) return
    const newCost = POINT_COST[newBase] ?? 0
    const oldCost = POINT_COST[base] ?? 0
    const remaining = pbUsed - oldCost + newCost
    if (remaining > POINT_BUY_TOTAL) return
    update({ ability_scores: { ...data.ability_scores, [key]: newBase + (raceBonuses[key] ?? 0) } })
  }

  // 随机骰点
  const rollDice = () => {
    const rolls: number[] = []
    for (let i = 0; i < 6; i++) {
      const dice = Array.from({ length: 4 }, () => Math.floor(Math.random() * 6) + 1)
      dice.sort((a, b) => a - b)
      rolls.push(dice.slice(1).reduce((a, b) => a + b, 0))
    }
    rolls.sort((a, b) => b - a)
    // 重置分配
    const newScores = { ...data.ability_scores }
    update({ score_rolls: rolls, ability_scores: newScores })
  }

  // 切换方式时重置属性值
  const switchMethod = (m: 'standard' | 'roll' | 'pointbuy') => {
    const newScores = { str: 8, dex: 8, con: 8, int: 8, wis: 8, cha: 8 } as Record<AbilityKey, number>
    // 加上种族加成
    for (const ab of ABILITIES) {
      newScores[ab.key] += (raceBonuses[ab.key] ?? 0)
    }
    if (m === 'standard') {
      // 默认按属性顺序分配标准数列
      ABILITIES.forEach((ab, i) => {
        newScores[ab.key] = STANDARD_ARRAY[i] + (raceBonuses[ab.key] ?? 0)
      })
    }
    update({ score_method: m, ability_scores: newScores, score_rolls: [] })
  }

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">4</span>
        决定属性值
      </h2>

      {/* 种族加成提示 */}
      {Object.keys(raceBonuses).length > 0 && (
        <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-xs text-blue-300 flex flex-wrap gap-x-3 gap-y-1">
          <span className="text-blue-400 font-medium">种族加成：</span>
          {ABILITIES.filter(ab => (raceBonuses[ab.key] ?? 0) > 0).map(ab => (
            <span key={ab.key}>{ab.label} +{raceBonuses[ab.key]}</span>
          ))}
        </div>
      )}

      {/* 方式选择 */}
      <div className="grid grid-cols-3 gap-2 mb-5">
        {[
          { key: 'standard' as const, label: '标准数列', desc: '15·14·13·12·10·8' },
          { key: 'roll' as const,     label: '随机骰点', desc: '4d6取最高3骰' },
          { key: 'pointbuy' as const, label: '购点法',   desc: `共 ${POINT_BUY_TOTAL} 点` },
        ].map(({ key, label, desc }) => (
          <button
            key={key}
            onClick={() => switchMethod(key)}
            className={`p-3 rounded-xl border-2 text-center transition
              ${method === key
                ? 'border-amber-500 !bg-amber-500/10'
                : 'border-slate-700 !bg-slate-800 hover:border-slate-600'
              }`}
          >
            <div className={`text-sm font-medium ${method === key ? 'text-amber-400' : 'text-slate-200'}`}>{label}</div>
            <div className="text-xs text-slate-500 mt-0.5">{desc}</div>
          </button>
        ))}
      </div>

      {/* ── 标准数列 / 随机骰点：分配槽位 ── */}
      {(method === 'standard' || method === 'roll') && (
        <div className="space-y-4">
          {method === 'roll' && (
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-400">
                {data.score_rolls.length === 6
                  ? <span className="text-slate-300 font-medium">骰点结果：{data.score_rolls.join(' / ')}</span>
                  : '点击"重新骰点"生成六项数值'}
              </div>
              <button
                onClick={rollDice}
                className="px-3 py-1.5 text-xs bg-amber-500/20 border border-amber-500/40 text-amber-400
                           hover:bg-amber-500/30 rounded-lg transition"
              >
                🎲 重新骰点
              </button>
            </div>
          )}

          {(method === 'standard' || data.score_rolls.length === 6) && (
            <>
              <p className="text-xs text-slate-500">
                将下方数值分配到各属性（点击数值，再点击属性）
              </p>

              {/* 可用数值槽 */}
              <div className="flex flex-wrap gap-2 p-3 bg-slate-800/60 border border-slate-700 rounded-xl min-h-[3rem]">
                {unassignedSlots.length === 0
                  ? <span className="text-xs text-slate-600 self-center">✓ 所有数值已分配</span>
                  : unassignedSlots.map((i) => (
                    <button
                      key={i}
                      onClick={() => setDragSlot(dragSlot === i ? null : i)}
                       className={`w-12 h-10 rounded-lg text-sm font-bold border-2 transition
                        ${dragSlot === i
                          ? 'border-amber-500 !bg-amber-500/20 text-amber-400 scale-110'
                          : 'border-slate-500 !bg-slate-600 text-slate-100 hover:border-amber-500/50 hover:!bg-slate-500'
                        }`}
                    >
                      {baseValues[i]}
                    </button>
                  ))
                }
              </div>

              {/* 属性分配表格 */}
              <div className="grid grid-cols-2 gap-2">
                {ABILITIES.map((ab) => {
                  const slotIdx = slotAssignment[ab.key]
                  const base = slotIdx !== null ? baseValues[slotIdx] : null
                  const bonus = raceBonuses[ab.key] ?? 0
                  const total = base !== null ? base + bonus : null
                  const mod = total !== null ? getMod(total) : null
                  const isTarget = dragTarget === ab.key

                  return (
                    <button
                      key={ab.key}
                      onClick={() => {
                        if (dragSlot !== null) {
                          assignSlotToAbility(dragSlot, ab.key)
                          setDragSlot(null)
                        } else if (slotIdx !== null) {
                          // 点击已分配的属性 → 取消分配（放回池）
                          const newScores = { ...data.ability_scores }
                          newScores[ab.key] = 8 + bonus
                          update({ ability_scores: newScores })
                        }
                      }}
                      onMouseEnter={() => setDragTarget(ab.key)}
                      onMouseLeave={() => setDragTarget(null)}
                      className={`p-3 rounded-xl border-2 text-left transition
                        ${slotIdx !== null
                          ? 'border-amber-500/60 !bg-slate-800'
                          : dragSlot !== null
                          ? 'border-slate-500 !bg-slate-800 hover:border-amber-400 hover:!bg-amber-500/10 cursor-pointer'
                          : 'border-slate-700 !bg-slate-800 cursor-default'
                        }
                        ${isTarget && dragSlot !== null ? 'border-amber-400 !bg-amber-500/15 scale-[1.02]' : ''}
                      `}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className={`text-xs font-bold ${ab.color}`}>{ab.en}</span>
                          <span className="text-xs text-slate-400 ml-1.5">{ab.label}</span>
                          {bonus > 0 && (
                            <span className="ml-1 text-xs text-blue-400">+{bonus}</span>
                          )}
                        </div>
                        <div className="text-right">
                          {total !== null ? (
                            <div className="flex items-baseline gap-1">
                              <span className="text-lg font-bold text-slate-100">{total}</span>
                              <span className={`text-xs font-medium ${mod! >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                ({fmtMod(mod!)})
                              </span>
                            </div>
                          ) : (
                            <span className="text-sm text-slate-500">
                              {dragSlot !== null ? '← 点击分配' : '未分配'}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">{ab.desc}</div>
                    </button>
                  )
                })}
              </div>
            </>
          )}
        </div>
      )}

      {/* ── 购点法 ── */}
      {method === 'pointbuy' && (
        <div className="space-y-4">
          {/* 剩余点数 */}
          <div className="flex items-center justify-between p-3 bg-slate-800 border border-slate-700 rounded-xl">
            <span className="text-sm text-slate-400">可用点数</span>
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full transition-all"
                  style={{ width: `${Math.min((pbUsed / POINT_BUY_TOTAL) * 100, 100)}%` }}
                />
              </div>
              <span className={`text-sm font-bold ${pbUsed > POINT_BUY_TOTAL ? 'text-red-400' : 'text-amber-400'}`}>
                {POINT_BUY_TOTAL - pbUsed} / {POINT_BUY_TOTAL}
              </span>
            </div>
          </div>

          {/* 属性调节器 */}
          <div className="space-y-2">
            <p className="text-xs text-slate-500">每项属性基础值范围 8~15（种族加成另计）</p>
            {ABILITIES.map((ab) => {
              const bonus = raceBonuses[ab.key] ?? 0
              const total = data.ability_scores[ab.key]
              const base = total - bonus
              const mod = getMod(total)
              const cost = POINT_COST[base] ?? 0
              const canIncrease = base < 15 && (pbUsed - cost + (POINT_COST[base + 1] ?? 0)) <= POINT_BUY_TOTAL
              const canDecrease = base > 8

              return (
                <div key={ab.key} className="flex items-center gap-3 p-3 bg-slate-800 border border-slate-700 rounded-xl">
                  <div className="w-20 shrink-0">
                    <span className={`text-xs font-bold ${ab.color}`}>{ab.en}</span>
                    <span className="text-xs text-slate-400 ml-1.5 block leading-none mt-0.5">{ab.label}</span>
                  </div>
                  <div className="flex-1 text-xs text-slate-500">{ab.desc}</div>
                  {bonus > 0 && (
                    <span className="text-xs text-blue-400 shrink-0">+{bonus}</span>
                  )}
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => pbAdjust(ab.key, -1)}
                      disabled={!canDecrease}
                      className="w-7 h-7 rounded-lg bg-slate-700 border border-slate-600 text-slate-300
                                 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed
                                 text-sm font-bold transition flex items-center justify-center"
                    >−</button>
                    <div className="w-16 text-center">
                      <span className="text-lg font-bold text-slate-100">{total}</span>
                      <span className={`text-xs ml-1 ${mod >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ({fmtMod(mod)})
                      </span>
                    </div>
                    <button
                      onClick={() => pbAdjust(ab.key, 1)}
                      disabled={!canIncrease}
                      className="w-7 h-7 rounded-lg bg-slate-700 border border-slate-600 text-slate-300
                                 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed
                                 text-sm font-bold transition flex items-center justify-center"
                    >+</button>
                  </div>
                  <div className="text-xs text-slate-500 w-12 text-right shrink-0">{cost}点</div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 属性总览 */}
      {method !== 'pointbuy' && (method === 'standard' || data.score_rolls.length === 6) && (
        <div className="mt-4 p-3 bg-slate-800/60 border border-slate-700 rounded-xl">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>属性总览</span>
            <span>总和: {ABILITIES.reduce((s, ab) => s + (data.ability_scores[ab.key] ?? 0), 0)}</span>
          </div>
          <div className="grid grid-cols-6 gap-1">
            {ABILITIES.map((ab) => {
              const val = data.ability_scores[ab.key]
              const mod = getMod(val)
              return (
                <div key={ab.key} className="text-center">
                  <div className={`text-xs font-bold ${ab.color}`}>{ab.en}</div>
                  <div className="text-base font-bold text-slate-100">{val || '—'}</div>
                  <div className={`text-xs ${mod >= 0 ? 'text-green-400' : 'text-red-400'}`}>{val ? fmtMod(mod) : ''}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
