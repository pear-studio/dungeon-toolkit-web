import { useGamedataStore } from '../../stores/gamedataStore'
import { useWizardStore } from '../../stores/wizardStore'
import { getAgeRange } from '../../pages/CreatePage'


const RACE_AGE_DESC: Record<string, string> = {
  human:      '人类通常在 18 岁成年，寿命约 80 年',
  elf:        '精灵约 100 岁成年，可活 700 年以上',
  dwarf:      '矮人约 50 岁成年，寿命可达 350 年',
  halfling:   '半身人约 20 岁成年，寿命约 150 年',
  gnome:      '侏儒约 40 岁成年，寿命可达 400 年',
  'half-elf': '半精灵约 20 岁成年，寿命约 180 年',
  'half-orc': '半兽人约 14 岁成年，寿命约 75 年',
  tiefling:   '魔裔与人类寿命相仿，约 80~100 年',
  dragonborn: '龙裔约 15 岁成年，寿命约 80 年',
}


const GENDERS = [
  { value: '男', label: '男' },
  { value: '女', label: '女' },
  { value: '保密', label: '保密' },
]

export default function RaceSection() {
  const { data, update } = useWizardStore()
  const { races, loading } = useGamedataStore()

  const isCustomRace = data.race_slug === 'custom'
  const selectedRace = isCustomRace ? null : races.find((r) => r.slug === data.race_slug)
  const ageRange = getAgeRange(data.race_slug)
  const ageVal = parseInt(data.age) || ageRange.typical

  const handleRaceSelect = (slug: string) => {
    const range = getAgeRange(slug)
    update({ race_slug: slug, race_custom_name: '', subrace_slug: '', age: String(range.typical) })
  }

  const handleSlider = (val: number) => update({ age: String(val) })

  const handleAgeInput = (raw: string) => {
    if (raw === '') { update({ age: '' }); return }
    const n = parseInt(raw)
    if (!isNaN(n) && n >= 1) update({ age: String(n) })
  }


  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-900 text-xs font-bold flex items-center justify-center">2</span>
        种族
      </h2>

      {loading ? (
        <div className="grid grid-cols-3 gap-2">
          {Array(9).fill(0).map((_, i) => (
            <div key={i} className="h-20 bg-slate-800 rounded-xl animate-pulse border border-slate-700" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {/* 种族网格 */}
          <div className="grid grid-cols-3 gap-2">
            {races.map((race) => {
              const selected = data.race_slug === race.slug
              return (
                <button
                  key={race.slug}
                  onClick={() => handleRaceSelect(race.slug)}
                  className={`p-3 rounded-xl border-2 text-left transition min-h-[4.5rem]
                    ${selected
                      ? 'border-amber-500 !bg-amber-500/10'
                      : 'border-slate-700 !bg-slate-800 hover:border-slate-600'
                    }`}
                >
                  <div className={`text-sm font-medium leading-tight ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
                    {race.name}
                  </div>
                  {race.has_subraces && (
                    <div className="text-xs text-slate-400 mt-0.5 leading-tight">有亚种族</div>
                  )}
                </button>
              )
            })}

            {/* 自定义种族 */}
            <button
              onClick={() => update({ race_slug: 'custom', subrace_slug: '', age: '25' })}
              className={`p-3 rounded-xl border-2 text-left transition min-h-[4.5rem]
                ${isCustomRace
                  ? 'border-amber-500 !bg-amber-500/10'
                  : 'border-slate-700 border-dashed !bg-slate-800/50 hover:border-slate-500'
                }`}
            >
              <div className={`text-sm font-medium leading-tight ${isCustomRace ? 'text-amber-400' : 'text-slate-400'}`}>
                自定义
              </div>
            </button>
          </div>

          {/* 自定义种族输入 */}
          {isCustomRace && (
            <div className="bg-slate-800 border border-amber-500/20 rounded-xl p-4">
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                自定义种族名称 <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={data.race_custom_name}
                onChange={(e) => update({ race_custom_name: e.target.value })}
                placeholder="例：半龙人、天使血裔……"
                maxLength={30}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm
                           placeholder-slate-500 focus:outline-none focus:border-amber-500 transition"
              />
            </div>
          )}

          {/* 选中标准种族后：亚种族 + 年龄 + 性别 */}
          {(selectedRace || isCustomRace) && (
            <div className="bg-slate-800 border border-amber-500/20 rounded-xl p-5 space-y-5">
              {/* 亚种族 */}
              {selectedRace?.has_subraces && selectedRace.subraces && selectedRace.subraces.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    亚种族 <span className="text-red-400">* 必选</span>
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {selectedRace.subraces.map((sub) => (
                      <button
                        key={sub.slug}
                        onClick={() => update({ subrace_slug: sub.slug })}
                        className={`px-3 py-1.5 rounded-lg text-sm border transition
                          ${data.subrace_slug === sub.slug
                            ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                            : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                          }`}
                      >
                        {sub.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* 性别 */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  性别
                </label>
                <div className="flex gap-2">
                  {GENDERS.map((g) => (
                    <button
                      key={g.value}
                      type="button"
                      onClick={() => update({ gender: g.value })}
                      className={`flex-1 py-2 rounded-lg text-sm border transition
                        ${data.gender === g.value
                          ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                          : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                        }`}
                    >
                      {g.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 年龄 */}
              {!isCustomRace && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-slate-300">年龄</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={data.age}
                        onChange={(e) => handleAgeInput(e.target.value)}
                        min={1}
                        className="w-20 px-2 py-1 bg-slate-700 border border-slate-600 rounded-lg
                                   text-white text-sm text-center focus:outline-none focus:border-amber-500 transition
                                   [color-scheme:dark] [&::-webkit-inner-spin-button]:opacity-0"
                      />
                      <span className="text-sm text-slate-400">岁</span>
                    </div>
                  </div>
                  <input
                    type="range"
                    min={ageRange.min}
                    max={ageRange.max}
                    value={Math.min(Math.max(ageVal, ageRange.min), ageRange.max)}
                    onChange={(e) => handleSlider(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer
                               [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                               [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                               [&::-webkit-slider-thumb]:bg-amber-500 [&::-webkit-slider-thumb]:cursor-pointer
                               [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4
                               [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-amber-500
                               [&::-moz-range-thumb]:border-0"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>{ageRange.min}</span>
                    <span className="text-slate-400 text-center px-2">
                      {selectedRace ? (RACE_AGE_DESC[selectedRace.slug] ?? '') : ''}
                    </span>
                    <span>{ageRange.max}</span>
                  </div>
                </div>
              )}

              {/* 自定义种族的年龄输入 */}
              {isCustomRace && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">年龄</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={data.age}
                      onChange={(e) => handleAgeInput(e.target.value)}
                      min={1}
                      placeholder="例：25"
                      className="w-28 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg
                                 text-white text-sm text-center focus:outline-none focus:border-amber-500 transition
                                 [color-scheme:dark]"
                    />
                    <span className="text-sm text-slate-400">岁</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  )
}