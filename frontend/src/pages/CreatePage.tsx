import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useWizardStore } from '../stores/wizardStore'
import { useCharacterStore } from '../stores/characterStore'
import { useGamedataStore } from '../stores/gamedataStore'
import { characterApi } from '../lib/api'
import { useState } from 'react'
import RulesetSection from '../components/wizard/RulesetSection'
import RaceSection from '../components/wizard/RaceSection'
import ClassSection from '../components/wizard/ClassSection'
import AbilityScoresSection from '../components/wizard/AbilityScoresSection'
import DescribeSection from '../components/wizard/DescribeSection'

// 随机名字库（纯 UI 装饰，不属于游戏数据，允许硬编码）
const RANDOM_NAMES = [
  '艾瑞达', '卡尔文', '莫伊拉', '泰伦斯', '席尔维娅', '加里克',
  '菲利斯', '奥登', '塞拉菲娜', '科雷格', '伊拉芙', '布兰顿',
  '阿特拉', '薇洛薇', '托尔贡', '娜拉西', '埃尔文', '塔尼斯',
]
// D&D 规则常量（不属于数据库内容，允许硬编码）
const STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
const ALIGNMENT_SLUGS = ['lawful-good', 'neutral-good', 'chaotic-good', 'lawful-neutral', 'true-neutral', 'chaotic-neutral', 'lawful-evil', 'neutral-evil', 'chaotic-evil']
const GENDERS = ['男', '女', '保密']

// 种族典型年龄范围（UI 辅助常量，与种族数据库无关，允许硬编码）
const RACE_AGE: Record<string, { min: number; max: number; typical: number }> = {
  human:      { min: 18, max: 80,   typical: 25 },
  elf:        { min: 100, max: 700, typical: 250 },
  dwarf:      { min: 50, max: 350,  typical: 120 },
  halfling:   { min: 20, max: 150,  typical: 40 },
  gnome:      { min: 40, max: 400,  typical: 120 },
  'half-elf': { min: 20, max: 180,  typical: 35 },
  'half-orc': { min: 14, max: 75,   typical: 22 },
  tiefling:   { min: 18, max: 100,  typical: 24 },
  dragonborn: { min: 15, max: 80,   typical: 25 },
}

export function getAgeRange(raceSlug: string) {
  return RACE_AGE[raceSlug] ?? { min: 1, max: 999, typical: 25 }
}

export default function CreatePage() {
  const navigate = useNavigate()
  const { data, update, reset, rulesetConfirmed, confirmRuleset } = useWizardStore()
  const { fetchCharacters } = useCharacterStore()
  const { races, classes, backgrounds, fetchAll, raceName, className: classNameFn } = useGamedataStore()
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // 页面挂载时预加载游戏数据
  useEffect(() => { fetchAll() }, [fetchAll])

  // 随机填充（从已加载的 API 数据中随机选取）
  const handleRandom = () => {
    if (races.length === 0 || classes.length === 0 || backgrounds.length === 0) return
    const race = races[Math.floor(Math.random() * races.length)].slug
    const ageRange = getAgeRange(race)
    const age = Math.floor(Math.random() * (ageRange.max - ageRange.min) * 0.4 + ageRange.min)
    if (!rulesetConfirmed) confirmRuleset()
    const shuffled = [...STANDARD_ARRAY].sort(() => Math.random() - 0.5)
    const keys = ['str', 'dex', 'con', 'int', 'wis', 'cha'] as const
    const scores: Record<string, number> = {}
    keys.forEach((k, i) => { scores[k] = shuffled[i] })
    update({
      name: RANDOM_NAMES[Math.floor(Math.random() * RANDOM_NAMES.length)],
      gender: GENDERS[Math.floor(Math.random() * GENDERS.length)],
      race_slug: race,
      race_custom_name: '',
      subrace_slug: '',
      class_slug: classes[Math.floor(Math.random() * classes.length)].slug,
      class_custom_name: '',
      background_slug: backgrounds[Math.floor(Math.random() * backgrounds.length)].slug,
      alignment: ALIGNMENT_SLUGS[Math.floor(Math.random() * ALIGNMENT_SLUGS.length)],
      age: String(age),
      score_method: 'standard',
      ability_scores: scores as never,
    })
  }

  // 校验
  const raceOk = data.race_slug && (data.race_slug !== 'custom' || data.race_custom_name.trim())
  const classOk = data.class_slug && (data.class_slug !== 'custom' || data.class_custom_name.trim())
  const scoresOk = Object.values(data.ability_scores).every(v => v > 0)
  const canSubmit = data.name.trim() && raceOk && classOk && data.background_slug && scoresOk

  const handleSubmit = async () => {
    if (!canSubmit) return
    setSubmitError('')
    setSubmitting(true)
    try {
      const raceSlug = data.race_slug === 'custom' ? `custom__${data.race_custom_name.trim()}` : data.race_slug
      const classSlug = data.class_slug === 'custom' ? `custom__${data.class_custom_name.trim()}` : data.class_slug
      await characterApi.create({
        name: data.name.trim(),
        gender: data.gender || '保密',
        age: data.age ? parseInt(data.age) : undefined,
        appearance: data.appearance || '',
        race_slug: raceSlug,
        subrace_slug: data.subrace_slug || '',
        class_slug: classSlug,
        background_slug: data.background_slug,
        alignment: data.alignment || '',
        ability_scores: data.ability_scores,
        personality_trait: data.personality_traits || '',
        ideal: data.ideals || '',
        bond: data.bonds || '',
        flaw: data.flaws || '',
      })
      await fetchCharacters()
      reset()
      navigate('/dashboard')
    } catch (e: unknown) {
      const err = e as { response?: { data?: Record<string, unknown> } }
      const detail = err.response?.data
        ? Object.values(err.response.data).flat().join('；')
        : '创建失败，请重试'
      setSubmitError(String(detail))
    } finally {
      setSubmitting(false)
    }
  }

  // 预览栏显示名（从 gamedataStore 查询，不再硬编码）
  const raceDisplayName = data.race_slug === 'custom'
    ? (data.race_custom_name || '自定义种族')
    : raceName(data.race_slug)
  const classDisplayName = data.class_slug === 'custom'
    ? (data.class_custom_name || '自定义职业')
    : classNameFn(data.class_slug)

  // 步骤完成状态
  const step1Done = !!raceOk
  const step2Done = !!classOk
  const step3Done = scoresOk
  const step4Done = !!(data.name.trim() && data.background_slug)
  const steps = [
    { num: 1, label: '种族', done: step1Done },
    { num: 2, label: '职业', done: step2Done },
    { num: 3, label: '属性值', done: step3Done },
    { num: 4, label: '描述', done: step4Done },
  ]

  return (
    <div className="min-h-screen bg-slate-900">
      {/* 顶部导航 */}
      <nav className="border-b border-slate-800 bg-slate-900/95 backdrop-blur sticky top-0 z-20">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
          <button
            onClick={() => { reset(); navigate('/dashboard') }}
            className="text-sm text-slate-400 hover:text-white transition"
          >
            ← 返回大厅
          </button>
          <span className="text-sm font-medium text-slate-300">⚔️ 创建角色</span>
          <button
            onClick={handleRandom}
            title="随机填充"
            className="text-sm px-3 py-1.5 border border-slate-600 hover:border-amber-500/50
                       text-slate-400 hover:text-amber-400 rounded-lg transition flex items-center gap-1.5"
          >
            🎲 随机
          </button>
        </div>

        {/* 悬浮预览栏 */}
        {(data.name || data.race_slug || data.class_slug) && (
          <div className="border-t border-slate-800 bg-slate-900/80">
            <div className="max-w-2xl mx-auto px-4 py-2 flex items-center gap-3 text-sm overflow-x-auto">
              {data.name && <span className="font-semibold text-amber-400 shrink-0">{data.name}</span>}
              {(data.race_slug || data.class_slug) && <span className="text-slate-600 shrink-0">·</span>}
              {data.race_slug && <span className="text-slate-300 shrink-0">{raceDisplayName}</span>}
              {data.class_slug && <span className="text-slate-300 shrink-0">{classDisplayName}</span>}
              {data.age && <span className="text-slate-500 shrink-0">{data.age} 岁</span>}
              {data.gender && <span className="text-slate-500 shrink-0">{data.gender}</span>}
            </div>
          </div>
        )}

        {/* 步骤进度条（规则集确认后显示） */}
        {rulesetConfirmed && (
          <div className="border-t border-slate-800/60 bg-slate-900/60">
            <div className="max-w-2xl mx-auto px-4 py-2 flex items-center gap-1">
              {steps.map((step, idx) => (
                <div key={step.num} className="flex items-center gap-1 flex-1">
                  <div className={`flex items-center gap-1.5 text-xs transition ${step.done ? 'text-amber-400' : 'text-slate-600'}`}>
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0
                      ${step.done ? 'bg-amber-500 text-slate-900' : 'bg-slate-700 text-slate-500'}`}>
                      {step.done ? '✓' : step.num}
                    </span>
                    <span className="hidden sm:inline whitespace-nowrap">{step.label}</span>
                  </div>
                  {idx < steps.length - 1 && (
                    <div className={`flex-1 h-px mx-1 min-w-[8px] ${step.done ? 'bg-amber-500/40' : 'bg-slate-700'}`} />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* 主内容：单页滚动 */}
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-10">
        {/* 规则集选择 */}
        <RulesetSection />

        {/* 规则集确认后，展示 5 步流程（2014版） */}
        {rulesetConfirmed && (
          <>
            {/* 步骤1：角色名字 */}
            <div className="border-t border-slate-800 pt-8">
              <section>
                <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">1</span>
                  角色名字
                </h2>
                <input
                  type="text"
                  value={data.name}
                  onChange={(e) => update({ name: e.target.value })}
                  placeholder="给你的角色起一个名字……"
                  maxLength={40}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white
                             text-base placeholder-slate-500 focus:outline-none focus:border-amber-500 transition"
                />
              </section>
            </div>

            {/* 步骤2：选择种族 */}
            <div className="border-t border-slate-800 pt-8">
              <RaceSection />
            </div>

            {/* 步骤3：选择职业 */}
            <div className="border-t border-slate-800 pt-8">
              <ClassSection />
            </div>

            {/* 步骤4：决定属性值 */}
            <div className="border-t border-slate-800 pt-8">
              <AbilityScoresSection />
            </div>

            {/* 步骤5：描述角色（背景+阵营+外貌） */}
            <div className="border-t border-slate-800 pt-8">
              <DescribeSection />
            </div>

            {/* 错误提示 */}
            {submitError && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                ❌ {submitError}
              </div>
            )}

            {/* 提交按钮 */}
            <div className="pb-16">
              <button
                onClick={handleSubmit}
                disabled={!canSubmit || submitting}
                className="w-full py-3.5 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold
                           rounded-xl text-base transition disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {submitting ? '创建中...' : '🎉 完成创建'}
              </button>
              {!canSubmit && (
                <p className="text-center text-xs text-slate-500 mt-2">
                  请完成种族、职业、属性值分配，并填写角色名和背景
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
