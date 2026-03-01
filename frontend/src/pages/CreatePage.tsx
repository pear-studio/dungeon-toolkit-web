import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
/* eslint-disable react-refresh/only-export-components */
import { useWizardStore, selectTotalLevel } from '../stores/wizardStore'
import { useCharacterStore } from '../stores/characterStore'
import { useGamedataStore } from '../stores/gamedataStore'
import { characterApi } from '../lib/api'
import { useState } from 'react'
import RulesetSection from '../components/wizard/RulesetSection'
import RaceSection from '../components/wizard/RaceSection'
import ClassSection from '../components/wizard/ClassSection'
import AbilityScoresSection from '../components/wizard/AbilityScoresSection'
import DescribeSection from '../components/wizard/DescribeSection'
import CharacterPreview from '../components/wizard/CharacterPreview'

const RANDOM_NAMES = [
  '艾瑞达', '卡尔文', '莫伊拉', '泰伦斯', '席尔维娅', '加里克',
  '菲利斯', '奥登', '塞拉菲娜', '科雷格', '伊拉芙', '布兰顿',
  '阿特拉', '薇洛薇', '托尔贡', '娜拉西', '埃尔文', '塔尼斯',
]

const STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
const ALIGNMENT_SLUGS = ['lawful-good', 'neutral-good', 'chaotic-good', 'lawful-neutral', 'true-neutral', 'chaotic-neutral', 'lawful-evil', 'neutral-evil', 'chaotic-evil']
const GENDERS = ['男', '女', '保密']

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
  const totalLevel = useWizardStore(selectTotalLevel)

  useEffect(() => { fetchAll() }, [fetchAll])

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
      classes: [{ class_slug: classes[Math.floor(Math.random() * classes.length)].slug, level: 1 }],
      class_custom_name: '',
      background_slug: backgrounds[Math.floor(Math.random() * backgrounds.length)].slug,
      alignment: ALIGNMENT_SLUGS[Math.floor(Math.random() * ALIGNMENT_SLUGS.length)],
      age: String(age),
      ability_scores: scores as never,
    })
  }

  const race = races.find(r => r.slug === data.race_slug)
  const needsSubrace = race?.has_subraces && race.subraces && race.subraces.length > 0
  const subraceSelected = !needsSubrace || data.subrace_slug

  const primaryClass = data.classes[0]
  const classOk = primaryClass?.class_slug && (primaryClass.class_slug !== 'custom' || data.class_custom_name.trim())
  const scoresOk = Object.values(data.ability_scores).every(v => v > 0)
  const canSubmit = data.name.trim() && data.race_slug && subraceSelected && classOk && data.background_slug && scoresOk

  const handleSubmit = async () => {
    if (!canSubmit) return
    setSubmitError('')
    setSubmitting(true)
    try {
      const raceSlug = data.race_slug === 'custom' ? `custom__${data.race_custom_name.trim()}` : data.race_slug
      const classSlug = primaryClass.class_slug === 'custom' ? `custom__${data.class_custom_name.trim()}` : primaryClass.class_slug
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

  const raceDisplayName = data.race_slug === 'custom'
    ? (data.race_custom_name || '自定义种族')
    : raceName(data.race_slug)

  const classDisplayName = primaryClass?.class_slug
    ? (primaryClass.class_slug === 'custom'
        ? (data.class_custom_name || '自定义职业')
        : classNameFn(primaryClass.class_slug))
    : ''

  const classLevelDisplay = classDisplayName ? `${classDisplayName} ${totalLevel}级` : ''

  const step1Done = !!data.race_slug && subraceSelected
  const step2Done = !!classOk
  const step3Done = scoresOk
  const step4Done = !!(data.name.trim() && data.background_slug)

  const steps = [
    { num: 1, label: '种族', done: step1Done },
    { num: 2, label: '职业', done: step2Done },
    { num: 3, label: '属性值', done: step3Done },
    { num: 4, label: '描述', done: step4Done },
    { num: 5, label: '预览', done: true },
  ]

  return (
    <div className="min-h-screen bg-slate-900">
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

        {(data.name || data.race_slug || primaryClass?.class_slug) && (
          <div className="border-t border-slate-800 bg-slate-900/80">
            <div className="max-w-2xl mx-auto px-4 py-2 flex items-center gap-3 text-sm overflow-x-auto">
              {data.name && <span className="font-semibold text-amber-400 shrink-0">{data.name}</span>}
              {(data.race_slug || primaryClass?.class_slug) && <span className="text-slate-600 shrink-0">·</span>}
              {data.race_slug && <span className="text-slate-300 shrink-0">{raceDisplayName}</span>}
              {primaryClass?.class_slug && <span className="text-slate-300 shrink-0">{classLevelDisplay}</span>}
              {data.age && <span className="text-slate-500 shrink-0">{data.age} 岁</span>}
              {data.gender && <span className="text-slate-500 shrink-0">{data.gender}</span>}
            </div>
          </div>
        )}

        {rulesetConfirmed && (
          <div className="border-t border-slate-800/60 bg-slate-900/60">
            <div className="max-w-2xl mx-auto px-4 py-2 flex items-center gap-1 overflow-x-auto">
              {steps.map((step, idx) => (
                <div key={step.num} className="flex items-center gap-1 flex-1 min-w-0">
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

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-10">
        <RulesetSection />

        {rulesetConfirmed && (
          <>
            <div className="border-t border-slate-800 pt-8">
              <RaceSection />
            </div>

            <div className="border-t border-slate-800 pt-8">
              <ClassSection />
            </div>

            <div className="border-t border-slate-800 pt-8">
              <AbilityScoresSection />
            </div>

            <div className="border-t border-slate-800 pt-8">
              <DescribeSection />
            </div>

            <div className="border-t border-slate-800 pt-8">
              <CharacterPreview />
            </div>

            {submitError && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                ❌ {submitError}
              </div>
            )}

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
