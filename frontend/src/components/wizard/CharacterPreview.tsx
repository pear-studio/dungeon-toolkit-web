import { useMemo } from 'react'
import { useWizardStore, selectTotalLevel } from '../../stores/wizardStore'
import { useGamedataStore } from '../../stores/gamedataStore'

const ABILITY_ZH: Record<string, string> = {
  str: '力量', dex: '敏捷', con: '体质',
  int: '智力', wis: '感知', cha: '魅力',
}

const SKILL_ZH: Record<string, string> = {
  acrobatics: '杂技', 'animal handling': '动物处理', 'animal-handling': '动物处理',
  arcana: '奥秘', athletics: '运动', deception: '欺诈', history: '历史',
  insight: '洞察', intimidation: '恐吓', investigation: '调查', medicine: '医疗',
  nature: '自然', perception: '察觉', performance: '表演', persuasion: '说服',
  religion: '宗教', 'sleight of hand': '巧手', 'sleight-of-hand': '巧手',
  stealth: '隐匿', survival: '生存',
}

const ALIGNMENT_ZH: Record<string, string> = {
  'lawful-good': '守序善良', 'neutral-good': '中立善良', 'chaotic-good': '混乱善良',
  'lawful-neutral': '守序中立', 'true-neutral': '绝对中立', 'chaotic-neutral': '混乱中立',
  'lawful-evil': '守序邪恶', 'neutral-evil': '中立邪恶', 'chaotic-evil': '混乱邪恶',
}

function skillZh(slug: string): string {
  return SKILL_ZH[slug] || slug
}

export default function CharacterPreview() {
  const { data } = useWizardStore()
  const { races, classes, backgrounds } = useGamedataStore()
  const totalLevel = useWizardStore(selectTotalLevel)

  const race = useMemo(() => races.find(r => r.slug === data.race_slug), [races, data.race_slug])
  const subrace = useMemo(() => {
    if (!race?.subraces) return null
    return race.subraces.find(s => s.slug === data.subrace_slug)
  }, [race, data.subrace_slug])

  const classEntries = useMemo(() => {
    return data.classes
      .filter(c => c.class_slug)
      .map(c => ({
        entry: c,
        cls: classes.find(cls => cls.slug === c.class_slug)
      }))
      .filter(c => c.cls)
  }, [data.classes, classes])

  const background = useMemo(() =>
    backgrounds.find(b => b.slug === data.background_slug),
    [backgrounds, data.background_slug]
  )

  const allSkills = useMemo(() => {
    const backgroundSkills = background?.skill_proficiencies || []
    const chosenSkills = data.chosen_skills || []
    return [...new Set([...backgroundSkills, ...chosenSkills])]
  }, [background, data.chosen_skills])

  const proficiencyBonus = Math.ceil(totalLevel / 4) + 1

  const abilityModifiers = useMemo(() => {
    const modifiers: Record<string, number> = {}
    for (const [key, value] of Object.entries(data.ability_scores)) {
      modifiers[key] = Math.floor((value - 10) / 2)
    }
    return modifiers
  }, [data.ability_scores])

  const estimatedHP = useMemo(() => {
    if (classEntries.length === 0) return 0
    const con = abilityModifiers.con || 0
    let hp = 0
    classEntries.forEach(({ entry, cls }) => {
      if (cls) {
        hp += cls.hit_die + con
        hp += (entry.level - 1) * (Math.ceil(cls.hit_die / 2) + 1 + con)
      }
    })
    return hp
  }, [classEntries, abilityModifiers])

  const classDisplay = classEntries.map(({ entry, cls }) =>
    cls ? `${cls.name} ${entry.level}级` : ''
  ).filter(Boolean).join(' / ')

  const missingFields: string[] = []
  if (!data.name) missingFields.push('角色名')
  if (!data.race_slug) missingFields.push('种族')
  if (!data.classes[0]?.class_slug) missingFields.push('职业')
  if (!data.background_slug) missingFields.push('背景')

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">6</span>
        角色卡预览
      </h2>

      {missingFields.length > 0 && (
        <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <p className="text-sm text-yellow-400">
            ⚠️ 以下信息尚未填写：{missingFields.join('、')}
          </p>
        </div>
      )}

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-6">
        {/* 基本信息 */}
        <div>
          <h3 className="text-sm font-medium text-amber-400 mb-2">基本信息</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-slate-400">角色名：<span className="text-white">{data.name || '—'}</span></div>
            <div className="text-slate-400">种族：<span className="text-white">{race?.name || '—'}{subrace ? `(${subrace.name})` : ''}</span></div>
            <div className="text-slate-400">职业：<span className="text-white">{classDisplay || '—'}</span></div>
            <div className="text-slate-400">阵营：<span className="text-white">{ALIGNMENT_ZH[data.alignment] || '—'}</span></div>
            <div className="text-slate-400">年龄：<span className="text-white">{data.age || '—'} 岁</span></div>
            <div className="text-slate-400">性别：<span className="text-white">{data.gender || '—'}</span></div>
          </div>
        </div>

        {/* 属性值 */}
        <div>
          <h3 className="text-sm font-medium text-amber-400 mb-2">属性值</h3>
          <div className="grid grid-cols-6 gap-2">
            {(['str', 'dex', 'con', 'int', 'wis', 'cha'] as const).map(ability => {
              const value = data.ability_scores[ability] || 0
              const mod = abilityModifiers[ability] || 0
              const sign = mod >= 0 ? '+' : ''
              return (
                <div key={ability} className="bg-slate-700 rounded-lg p-2 text-center">
                  <div className="text-xs text-slate-500">{ABILITY_ZH[ability]}</div>
                  <div className="text-lg font-bold text-white">{value}</div>
                  <div className="text-xs text-amber-400">{sign}{mod}</div>
                </div>
              )
            })}
          </div>
        </div>

        {/* 战斗数据 */}
        <div>
          <h3 className="text-sm font-medium text-amber-400 mb-2">战斗数据</h3>
          <div className="flex gap-6 text-sm">
            <div className="text-slate-400">熟练加值：<span className="text-white">+{proficiencyBonus}</span></div>
            <div className="text-slate-400">预估 HP：<span className="text-white">{estimatedHP || '—'}</span></div>
          </div>
        </div>

        {/* 技能熟练 */}
        <div>
          <h3 className="text-sm font-medium text-amber-400 mb-2">技能熟练</h3>
          <div className="flex flex-wrap gap-1">
            {allSkills.length > 0 ? allSkills.map(skill => (
              <span key={skill} className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded">
                {skillZh(skill)}
              </span>
            )) : (
              <span className="text-slate-500 text-sm">—</span>
            )}
          </div>
        </div>

        {/* 背景 */}
        {background && (
          <div>
            <h3 className="text-sm font-medium text-amber-400 mb-2">背景</h3>
            <div className="space-y-1 text-sm">
              <div className="text-slate-400">背景：<span className="text-white">{background.name}</span></div>
              {background.feature_name && background.feature_name !== '背景特性' && (
                <div className="text-slate-400">特性：<span className="text-white">{background.feature_name}</span></div>
              )}
              {background.feature_description && (
                <div className="text-xs text-slate-500 line-clamp-2">{background.feature_description}</div>
              )}
            </div>
          </div>
        )}

        {/* 初始装备 */}
        {background?.starting_equipment && background.starting_equipment.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-amber-400 mb-2">初始装备</h3>
            <div className="text-sm text-slate-300">
              {background.starting_equipment.join('、')}
            </div>
          </div>
        )}

        {/* 职业特性 */}
        <div>
          <h3 className="text-sm font-medium text-amber-400 mb-2">职业特性</h3>
          <div className="flex flex-wrap gap-1">
            {classEntries.map(({ entry, cls }, idx) => {
              if (!cls?.level_features) return null
              const features: string[] = []
              for (let l = 1; l <= entry.level; l++) {
                const levelFeatures = cls.level_features[String(l)]
                if (levelFeatures) {
                  levelFeatures.forEach((f: { name: string }) => features.push(`${l}级 - ${f.name}`))
                }
              }
              return features.length > 0 ? (
                <div key={idx} className="mb-2">
                  <div className="text-xs text-slate-500 mb-1">{cls.name}</div>
                  <div className="flex flex-wrap gap-1">
                    {features.map((f, fidx) => (
                      <span key={fidx} className="text-xs px-2 py-0.5 bg-slate-700 text-slate-400 rounded">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null
            })}
          </div>
          {classEntries.length === 0 && (
            <span className="text-slate-500 text-sm">—</span>
          )}
        </div>
      </div>
    </section>
  )
}
