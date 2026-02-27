import { useMemo } from 'react'
import { useGamedataStore } from '../../stores/gamedataStore'
import { useWizardStore, selectTotalLevel } from '../../stores/wizardStore'

const SKILL_ZH: Record<string, string> = {
  acrobatics: '杂技', animal: '动物处理', arcana: '奥秘',
  athletics: '运动', deception: '欺诈', history: '历史',
  insight: '洞察', intimidation: '恐吓', investigation: '调查',
  medicine: '医疗', nature: '自然', perception: '察觉',
  performance: '表演', persuasion: '说服', religion: '宗教',
  sleight: '巧手', stealth: '隐匿', survival: '生存',
}

const ABILITY_ZH: Record<string, string> = {
  strength: '力量', dexterity: '敏捷', constitution: '体质',
  intelligence: '智力', wisdom: '感知', charisma: '魅力',
}

const ABILITY_SHORT: Record<string, string> = {
  str: '力量', dex: '敏捷', con: '体质',
  int: '智力', wis: '感知', cha: '魅力',
}

const PREREQUISITE_ABILITY: Record<string, string> = {
  paladin: 'cha', ranger: 'wis', monk: 'wis', bard: 'cha',
  sorcerer: 'cha', warlock: 'cha', druid: 'wis', cleric: 'wis',
}

export default function ClassSection() {
  const { data, addClass, removeClass, updateClass, setChosenSkills } = useWizardStore()
  const { classes, backgrounds } = useGamedataStore()
  const totalLevel = selectTotalLevel(useWizardStore())

  const currentClass = data.classes[0]?.class_slug
  const selectedClass = currentClass ? classes.find(c => c.slug === currentClass) : null

  const background = useMemo(() => {
    return backgrounds.find(b => b.slug === data.background_slug)
  }, [backgrounds, data.background_slug])

  const backgroundSkills = background?.skill_proficiencies || []

  const skillChoicesCount = selectedClass?.skill_choices_count || 2

  const availableSkills = useMemo(() => {
    if (!selectedClass?.skill_choices) return []
    return selectedClass.skill_choices.map((s: string) => ({
      slug: s,
      name: SKILL_ZH[s] || s,
      isFromBackground: backgroundSkills.includes(s),
    }))
  }, [selectedClass, backgroundSkills])

  const handleSkillToggle = (skillSlug: string) => {
    const current = data.chosen_skills || []
    const isSelected = current.includes(skillSlug)
    const isFromBackground = backgroundSkills.includes(skillSlug)

    if (isFromBackground) return

    if (isSelected) {
      setChosenSkills(current.filter(s => s !== skillSlug))
    } else if (current.length < skillChoicesCount) {
      setChosenSkills([...current, skillSlug])
    }
  }

  const canAddClass = totalLevel < 20 && data.classes.length < 3

  const handleLevelChange = (index: number, newLevel: number) => {
    const clampedLevel = Math.max(1, Math.min(20, newLevel))
    const currentClassEntry = data.classes[index]
    const otherClasses = data.classes.filter((_, i) => i !== index)
    const otherLevels = otherClasses.reduce((sum, c) => sum + c.level, 0)
    const maxForThis = Math.min(20 - otherLevels, clampedLevel)

    updateClass(index, { ...currentClassEntry, level: clampedLevel > maxForThis ? maxForThis : clampedLevel })
  }

  const getClassFeatures = (classSlug: string, level: number) => {
    const cls = classes.find(c => c.slug === classSlug)
    if (!cls?.level_features) return []

    const features: Array<{ level: number; name: string; description: string }> = []
    for (let l = 1; l <= level; l++) {
      const levelKey = String(l)
      if (cls.level_features[levelKey]) {
        cls.level_features[levelKey].forEach((f: { name: string; description: string }) => {
          features.push({ level: l, ...f })
        })
      }
    }
    return features
  }

  const allFeatures = useMemo(() => {
    return data.classes
      .filter(c => c.class_slug)
      .map(c => {
        const cls = classes.find(x => x.slug === c.class_slug)
        return {
          className: cls?.name || c.class_slug,
          features: getClassFeatures(c.class_slug, c.level),
        }
      })
  }, [data.classes, classes])

  const totalSelectedSkills = (data.chosen_skills?.length || 0) + backgroundSkills.length

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">3</span>
        职业与等级
      </h2>

      <div className="space-y-4">
        <p className="text-xs text-slate-500">
          选择职业决定你的战斗风格、特性、技能与生命值成长方向。可添加兼职职业，但总等级不超过20级
        </p>

        <div className="space-y-3">
          {data.classes.map((classEntry, index) => (
            <div key={index} className={`bg-slate-800 border rounded-xl p-4 ${index === 0 ? 'border-amber-500/30' : 'border-slate-700'}`}>
              <div className="flex items-center gap-3 mb-3">
                {index === 0 && <span className="text-xs font-medium text-amber-400">主职业</span>}
                <select
                  value={classEntry.class_slug}
                  onChange={(e) => updateClass(index, { ...classEntry, class_slug: e.target.value })}
                  className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm
                             focus:outline-none focus:border-amber-500"
                >
                  <option value="">选择职业...</option>
                  {classes.map(cls => (
                    <option key={cls.slug} value={cls.slug}>{cls.name}</option>
                  ))}
                </select>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleLevelChange(index, classEntry.level - 1)}
                    className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-slate-600 text-white flex items-center justify-center"
                  >
                    -
                  </button>
                  <span className="text-white font-medium w-12 text-center">
                    {classEntry.level}级
                  </span>
                  <button
                    onClick={() => handleLevelChange(index, classEntry.level + 1)}
                    disabled={totalLevel >= 20}
                    className="w-8 h-8 rounded-lg bg-slate-700 hover:bg-slate-600 text-white flex items-center justify-center disabled:opacity-50"
                  >
                    +
                  </button>
                </div>

                {index > 0 && (
                  <button
                    onClick={() => removeClass(index)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    删除
                  </button>
                )}
              </div>

              {classEntry.class_slug && (
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span>总等级: {totalLevel}/20</span>
                  {PREREQUISITE_ABILITY[classEntry.class_slug] && (
                    <span className="text-yellow-500">
                      需要{ABILITY_SHORT[PREREQUISITE_ABILITY[classEntry.class_slug]]}≥13可兼职
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}

          {canAddClass && (
            <button
              onClick={addClass}
              className="w-full py-2 border-2 border-dashed border-slate-700 rounded-xl text-slate-500 hover:border-amber-500/50 hover:text-amber-400 text-sm transition"
            >
              + 添加兼职职业
            </button>
          )}
        </div>

        {selectedClass && (
          <div className="bg-slate-800 border border-amber-500/20 rounded-xl p-5 space-y-4">
            <div>
              <h3 className="font-bold text-white">{selectedClass.name}</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                生命骰 d{selectedClass.hit_die} · 主要属性: {ABILITY_ZH[selectedClass.primary_ability] || selectedClass.primary_ability}
                {selectedClass.is_spellcaster && ' · 可施法'}
              </p>
            </div>

            {availableSkills.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-300">选择技能熟练 ({totalSelectedSkills}/{skillChoicesCount + backgroundSkills.length})</span>
                  <span className="text-xs text-slate-500">
                    职业选择 {skillChoicesCount} 项，背景包含 {backgroundSkills.length} 项
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {availableSkills.map(skill => {
                    const isSelected = (data.chosen_skills || []).includes(skill.slug)
                    const isDisabled = !isSelected && (data.chosen_skills?.length || 0) >= skillChoicesCount && !skill.isFromBackground
                    return (
                      <button
                        key={skill.slug}
                        onClick={() => handleSkillToggle(skill.slug)}
                        disabled={isDisabled}
                        className={`px-3 py-1.5 rounded-full text-xs transition
                          ${skill.isFromBackground
                            ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                            : isSelected
                              ? 'bg-amber-500/20 text-amber-400 border border-amber-500'
                              : isDisabled
                                ? 'bg-slate-700 text-slate-600 cursor-not-allowed'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                          }`}
                      >
                        {skill.name}
                        {skill.isFromBackground && ' (背景已有)'}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {allFeatures.length > 0 && (
              <div>
                <span className="text-sm text-slate-300 block mb-2">职业特性</span>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {allFeatures.map((classGroup, idx) => (
                    <div key={idx}>
                      <div className="text-xs text-amber-400 mb-1">{classGroup.className}</div>
                      <div className="flex flex-wrap gap-1">
                        {classGroup.features.map((f, fidx) => (
                          <span
                            key={fidx}
                            className={`text-xs px-2 py-0.5 rounded ${
                              [4, 8, 12, 16, 19].includes(f.level)
                                ? 'bg-purple-500/20 text-purple-400 border border-purple-500/50'
                                : 'bg-slate-700 text-slate-400'
                            }`}
                          >
                            {f.level}级 - {f.name}
                            {[4, 8, 12, 16, 19].includes(f.level) && ' ⭐属性提升'}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
