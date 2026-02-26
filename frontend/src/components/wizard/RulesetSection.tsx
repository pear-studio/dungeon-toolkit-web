import { useWizardStore } from '../../stores/wizardStore'

const RULESETS = [
  { slug: 'dnd5e_2014', name: 'D&D 5e（2014 版）', desc: '经典版本，市面上绝大多数桌游内容使用此版本规则。', icon: '📜', available: true },
  { slug: 'dnd5e_2024', name: 'D&D 5e（2024 版）', desc: '修订版，优化了部分规则和职业特性，与旧版大部分兼容。', icon: '✨', available: false },
]

export default function RulesetSection() {
  const { data, update, rulesetConfirmed, confirmRuleset } = useWizardStore()

  return (
    <section>
      <h2 className="text-base font-semibold text-slate-300 mb-3 flex items-center gap-2">
        📜 规则集
        {rulesetConfirmed && (
          <button
            onClick={() => update({ ruleset_slug: data.ruleset_slug })}
            className="ml-auto text-xs text-slate-500 hover:text-amber-400 transition"
            title="切换规则集"
          >
            {/* 已锁定后允许点击修改 */}
          </button>
        )}
      </h2>
      <div className="space-y-2">
        {RULESETS.map((rs) => {
          const selected = data.ruleset_slug === rs.slug
          return (
            <button
              key={rs.slug}
              disabled={!rs.available || rulesetConfirmed}
              onClick={() => rs.available && !rulesetConfirmed && update({ ruleset_slug: rs.slug })}
              className={`w-full text-left p-4 rounded-xl border-2 transition
                ${!rs.available
                  ? 'border-slate-700 !bg-slate-800/40 opacity-40 cursor-not-allowed'
                  : rulesetConfirmed && selected
                    ? 'border-amber-500 !bg-amber-500/10 cursor-default'
                    : rulesetConfirmed
                      ? 'border-slate-700 !bg-slate-800/40 opacity-30 cursor-not-allowed'
                      : selected
                        ? 'border-amber-500 !bg-amber-500/10 cursor-pointer'
                        : 'border-slate-700 !bg-slate-800 hover:border-slate-500 cursor-pointer'
                }`}
            >
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold text-sm ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
                      {rs.name}
                    </span>
                    {!rs.available && <span className="text-xs px-1.5 py-0.5 bg-slate-700 text-slate-400 rounded">即将推出</span>}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">{rs.desc}</p>
                </div>
                {selected && <span className="text-amber-400">✓</span>}
              </div>
            </button>
          )
        })}
      </div>

      {/* 确认按钮：未确认时显示 */}
      {!rulesetConfirmed && (
        <button
          onClick={confirmRuleset}
          disabled={!data.ruleset_slug}
          className="mt-4 w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold
                     rounded-xl text-sm transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          使用此规则集，开始创建 →
        </button>
      )}

      {/* 已确认后显示切换入口 */}
      {rulesetConfirmed && (
        <div className="mt-2 flex justify-end">
          <button
            onClick={() => {
              // 重置规则集确认状态，允许重新选择
              useWizardStore.setState({ rulesetConfirmed: false })
            }}
            className="text-xs text-slate-500 hover:text-amber-400 transition underline underline-offset-2"
          >
            更换规则集
          </button>
        </div>
      )}
    </section>
  )
}