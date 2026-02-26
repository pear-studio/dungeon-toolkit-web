import { useGamedataStore } from '../../stores/gamedataStore'
import { useWizardStore } from '../../stores/wizardStore'

const CLASS_FLAVOR: Record<string, string> = {
  barbarian: '原始力量，战斗中进入狂暴状态。',
  bard: '音乐与故事为武器，兼具法术与技能。',
  cleric: '神明使者，拥有强力治疗与神圣法术。',
  druid: '自然守护者，可变形为野兽。',
  fighter: '全能战士，精通各类武器和战术。',
  monk: '精通气功与武术，速度超凡。',
  paladin: '神圣誓约守护者，结合战士与牧师之能。',
  ranger: '荒野猎手，精通弓箭与追踪。',
  rogue: '暗影潜行，致命偷袭一击。',
  sorcerer: '天生魔法血脉，拥有法术点数。',
  warlock: '与强大存在签订契约，获得奥秘爆发。',
  wizard: '通过学习掌握魔法，法术最丰富。',
}

const ABILITY_ZH: Record<string, string> = {
  strength: '力量', dexterity: '敏捷', constitution: '体质',
  intelligence: '智力', wisdom: '感知', charisma: '魅力',
}

export default function ClassSection() {
  const { data, update } = useWizardStore()
  const { classes, loading } = useGamedataStore()

  const isCustomClass = data.class_slug === 'custom'
  const selectedClass = isCustomClass ? null : classes.find((c) => c.slug === data.class_slug)

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">3</span>
        职业
      </h2>

      <div className="space-y-4">
        <p className="text-xs text-slate-500">职业决定你的战斗风格、特性、技能与生命值成长方向</p>

        {loading ? (
          <div className="grid grid-cols-3 gap-2">
            {Array(12).fill(0).map((_, i) => (
              <div key={i} className="h-20 bg-slate-800 rounded-xl animate-pulse border border-slate-700" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-2">
            {classes.map((cls) => {
              const selected = data.class_slug === cls.slug
              return (
                <button
                  key={cls.slug}
                  onClick={() => update({ class_slug: cls.slug, class_custom_name: '' })}
                  className={`p-3 rounded-xl border-2 text-left transition min-h-[4.5rem]
                    ${selected
                      ? 'border-amber-500 !bg-amber-500/10'
                      : 'border-slate-700 !bg-slate-800 hover:border-slate-600'
                    }`}
                >
                  <div className={`text-sm font-medium leading-tight ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
                    {cls.name}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5 leading-tight">
                    d{cls.hit_die}
                    {cls.is_spellcaster && <span className="ml-1 text-purple-400">·法</span>}
                  </div>
                </button>
              )
            })}

            {/* 自定义职业 */}
            <button
              onClick={() => update({ class_slug: 'custom' })}
              className={`p-3 rounded-xl border-2 text-left transition min-h-[4.5rem]
                ${isCustomClass
                  ? 'border-amber-500 !bg-amber-500/10'
                  : 'border-slate-700 border-dashed !bg-slate-800/50 hover:border-slate-500'
                }`}
            >
              <div className={`text-sm font-medium leading-tight ${isCustomClass ? 'text-amber-400' : 'text-slate-400'}`}>
                自定义
              </div>
            </button>
          </div>
        )}

        {/* 自定义职业输入 */}
        {isCustomClass && (
          <div className="bg-slate-800 border border-amber-500/20 rounded-xl p-4">
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              自定义职业名称 <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={data.class_custom_name}
              onChange={(e) => update({ class_custom_name: e.target.value })}
              placeholder="例：影刃武者、龙血巫师……"
              maxLength={30}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm
                         placeholder-slate-500 focus:outline-none focus:border-amber-500 transition"
            />
          </div>
        )}

        {/* 标准职业详情 */}
        {selectedClass && (
          <div className="bg-slate-800 border border-amber-500/20 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-3">
              <div>
                <h3 className="font-bold text-white">{selectedClass.name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{CLASS_FLAVOR[selectedClass.slug]}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-700/60 rounded-lg p-2.5">
                <div className="text-xs text-slate-400">生命骰</div>
                <div className="text-base font-bold text-amber-400 mt-0.5">d{selectedClass.hit_die}</div>
              </div>
              <div className="bg-slate-700/60 rounded-lg p-2.5">
                <div className="text-xs text-slate-400">主要属性</div>
                <div className="text-sm font-bold text-white mt-0.5">
                  {ABILITY_ZH[selectedClass.primary_ability] ?? selectedClass.primary_ability}
                </div>
              </div>
              <div className="bg-slate-700/60 rounded-lg p-2.5">
                <div className="text-xs text-slate-400">施法</div>
                <div className="text-sm font-bold mt-0.5">
                  {selectedClass.is_spellcaster
                    ? <span className="text-purple-400">✓ 有</span>
                    : <span className="text-slate-500">无</span>}
                </div>
              </div>
            </div>
            {selectedClass.saving_throws?.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-500">豁免骰：</span>
                {selectedClass.saving_throws.map((st) => (
                  <span key={st} className="text-xs px-2 py-0.5 bg-slate-700 text-slate-300 rounded-full">
                    {ABILITY_ZH[st] ?? st}
                  </span>
                ))}
              </div>
            )}
            <p className="text-xs text-slate-500 border-t border-slate-700 pt-3">
              💡 熟练加值在第1级时为 <span className="text-amber-400 font-medium">+2</span>，
              1级生命值为 d{selectedClass.hit_die} 最大值 + 体质调整值（将在确定属性值后计算）
            </p>
          </div>
        )}
      </div>
    </section>
  )
}