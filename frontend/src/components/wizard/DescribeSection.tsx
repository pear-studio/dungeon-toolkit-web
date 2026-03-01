import { useState } from 'react'
import { useGamedataStore } from '../../stores/gamedataStore'
import { useWizardStore } from '../../stores/wizardStore'

const SKILL_ZH: Record<string, string> = {
  acrobatics: '杂技',
  animal_handling: '驯兽', 'animal-handling': '驯兽',
  arcana: '奥秘', athletics: '运动',
  deception: '欺骗', history: '历史', insight: '洞察', intimidation: '威吓',
  investigation: '调查', medicine: '医疗', nature: '自然', perception: '察觉',
  performance: '表演', persuasion: '说服', religion: '宗教',
  sleight_of_hand: '手法', 'sleight-of-hand': '手法',
  stealth: '潜行', survival: '生存',
}

/** 将技能 slug（连字符或下划线）统一查中文名，查不到则原样返回 */
const skillZh = (s: string) => SKILL_ZH[s] ?? SKILL_ZH[s.replace(/-/g, '_')] ?? s

// 阵营数据（3×3方格）
const ALIGNMENTS = [
  { key: 'lawful-good',    label: '守序善良', abbr: 'LG', desc: '正义执法者，可靠的道德典范', color: 'text-blue-300' },
  { key: 'neutral-good',  label: '中立善良', abbr: 'NG', desc: '行善而不受规则约束的好人', color: 'text-green-300' },
  { key: 'chaotic-good',  label: '混乱善良', abbr: 'CG', desc: '以良心而非规则指引行动', color: 'text-emerald-300' },
  { key: 'lawful-neutral', label: '守序中立', abbr: 'LN', desc: '遵循秩序，不偏善恶', color: 'text-blue-400' },
  { key: 'true-neutral',  label: '绝对中立', abbr: 'N',  desc: '相信力量的平衡', color: 'text-slate-300' },
  { key: 'chaotic-neutral', label: '混乱中立', abbr: 'CN', desc: '追求自由，不受任何约束', color: 'text-orange-300' },
  { key: 'lawful-evil',   label: '守序邪恶', abbr: 'LE', desc: '通过法规与等级实现目的', color: 'text-red-400' },
  { key: 'neutral-evil',  label: '中立邪恶', abbr: 'NE', desc: '纯粹追求自身利益', color: 'text-red-300' },
  { key: 'chaotic-evil',  label: '混乱邪恶', abbr: 'CE', desc: '暴力与混乱的化身', color: 'text-red-500' },
]

export default function DescribeSection() {
  const { data, update } = useWizardStore()
  const { backgrounds, loading: bgLoading } = useGamedataStore()
  const [showPersonality, setShowPersonality] = useState(false)

  const selectedBg = backgrounds.find((b) => b.slug === data.background_slug)
  const selectedAlignment = ALIGNMENTS.find((a) => a.key === data.alignment)

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">5</span>
        描述你的角色
      </h2>

      <div className="space-y-6">

        {/* ── 角色名 ── */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            角色名 <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={data.name}
            onChange={(e) => update({ name: e.target.value })}
            placeholder="为你的角色起一个名字……"
            maxLength={40}
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white text-base
                       placeholder-slate-600 focus:outline-none focus:border-amber-500 transition"
          />
        </div>

        {/* ── 背景 ── */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-1">
            背景 <span className="text-red-400">*</span>
          </h3>
          <p className="text-xs text-slate-500 mb-3">
            背景代表冒险前的生活经历，赋予技能熟练、工具熟练和背景特性
          </p>

          {bgLoading ? (
            <div className="grid grid-cols-2 gap-2">
              {Array(6).fill(0).map((_, i) => (
                <div key={i} className="h-14 bg-slate-800 rounded-xl animate-pulse border border-slate-700" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {backgrounds.map((bg) => {
                const selected = data.background_slug === bg.slug
                return (
                  <button
                    key={bg.slug}
                    onClick={() => update({ background_slug: bg.slug })}
                    className={`p-3 rounded-xl border-2 text-left transition
                      ${selected
                        ? 'border-amber-500 !bg-amber-500/10'
                        : 'border-slate-700 !bg-slate-800 hover:border-slate-600'
                      }`}
                  >
                    <div className={`text-sm font-medium ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
                      {bg.name}
                    </div>
                    {bg.skill_proficiencies?.length > 0 && (
                      <div className="text-xs text-slate-500 mt-0.5 leading-tight">
                        {bg.skill_proficiencies.map((s) => skillZh(s)).join('、')}
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          )}

          {/* 选中背景详情 */}
          {selectedBg && (
            <div className="mt-3 bg-slate-800 border border-amber-500/20 rounded-xl p-4 space-y-2">
              <div className="font-semibold text-white text-sm">{selectedBg.name}</div>
              {selectedBg.skill_proficiencies?.length > 0 && (
                <div className="text-xs text-slate-400">
                  <span className="text-slate-500">技能熟练：</span>
                  {selectedBg.skill_proficiencies.map((s) => skillZh(s)).join('、')}
                </div>
              )}
              {selectedBg.feature_name && (
                <div className="text-xs">
                  <span className="text-slate-500">特性：</span>
                  <span className="text-amber-400/80">{selectedBg.feature_name}</span>
                </div>
              )}
              {selectedBg.feature_description && (
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                  {selectedBg.feature_description}
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── 阵营 ── */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-1">阵营</h3>
          <p className="text-xs text-slate-500 mb-3">
            阵营代表角色的道德倾向，指引其做出决定。可选择或跳过。
          </p>
          <div className="grid grid-cols-3 gap-2">
            {ALIGNMENTS.map((al) => {
              const selected = data.alignment === al.key
              return (
                <button
                  key={al.key}
                  onClick={() => update({ alignment: selected ? '' : al.key })}
                  title={al.desc}
                  className={`p-2.5 rounded-xl border-2 text-center transition
                    ${selected
                      ? 'border-amber-500 !bg-amber-500/10'
                      : 'border-slate-700 !bg-slate-800 hover:border-slate-600'
                    }`}
                >
                  <div className={`text-sm font-bold ${selected ? 'text-amber-400' : al.color}`}>
                    {al.abbr}
                  </div>
                  <div className={`text-xs leading-tight mt-0.5 ${selected ? 'text-amber-400/80' : 'text-slate-400'}`}>
                    {al.label}
                  </div>
                </button>
              )
            })}
          </div>
          {selectedAlignment && (
            <p className="mt-2 text-xs text-slate-500 text-center">{selectedAlignment.desc}</p>
          )}
        </div>

        {/* ── 外貌描述（可选） ── */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            外貌描述
            <span className="ml-2 text-xs text-slate-500 font-normal">（可选）</span>
          </label>
          <textarea
            value={data.appearance}
            onChange={(e) => update({ appearance: e.target.value })}
            placeholder="描述你角色的外貌特征……"
            rows={2}
            maxLength={200}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm
                       placeholder-slate-500 focus:outline-none focus:border-amber-500 transition resize-none"
          />
        </div>

        {/* ── 个性细节（折叠） ── */}
        <div>
          <button
            onClick={() => setShowPersonality(!showPersonality)}
            className="w-full flex items-center justify-between p-3 bg-slate-800/60 border border-slate-700
                       rounded-xl text-sm text-slate-400 hover:text-white hover:border-slate-600 transition"
          >
            <span>📖 个性细节（理想·牵绊·缺点）</span>
            <span className="text-xs">{showPersonality ? '▲ 收起' : '▼ 展开'}</span>
          </button>

          {showPersonality && (
            <div className="mt-2 space-y-3">
              {[
                { key: 'personality_traits' as const, label: '个人特征', placeholder: '你的角色有哪些独特的行为习惯或口头禅……' },
                { key: 'ideals' as const, label: '理想', placeholder: '你的角色相信什么，或者为何而战……' },
                { key: 'bonds' as const, label: '牵绊', placeholder: '哪些人、地点或事物对你的角色最重要……' },
                { key: 'flaws' as const, label: '缺点', placeholder: '你的角色有哪些弱点、恐惧或不当行为……' },
              ].map(({ key, label, placeholder }) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-slate-400 mb-1">{label}</label>
                  <textarea
                    value={data[key]}
                    onChange={(e) => update({ [key]: e.target.value })}
                    placeholder={placeholder}
                    rows={2}
                    maxLength={200}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm
                               placeholder-slate-500 focus:outline-none focus:border-amber-500 transition resize-none"
                  />
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </section>
  )
}
