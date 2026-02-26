import { create } from 'zustand'

export interface WizardData {
  // 规则集
  ruleset_slug: string
  // Step 1 种族
  race_slug: string
  race_custom_name: string
  subrace_slug: string
  // Step 2 职业
  class_slug: string
  class_custom_name: string
  // Step 3 属性值
  score_method: 'standard' | 'roll' | 'pointbuy'  // 标准数列 / 随机骰 / 购点法
  score_rolls: number[]        // 6个随机骰值（roll方式）
  ability_assignment: {        // 六项属性分配的值（分配给各属性前）
    slot0: number; slot1: number; slot2: number
    slot3: number; slot4: number; slot5: number
  }
  ability_scores: {            // 最终属性值（含种族加成后）
    str: number; dex: number; con: number
    int: number; wis: number; cha: number
  }
  // Step 4 描述
  name: string
  gender: string
  age: string
  alignment: string            // 阵营：如 'lawful-good', 'neutral' 等
  background_slug: string
  personality_traits: string
  ideals: string
  bonds: string
  flaws: string
  appearance: string
}

const DEFAULT_DATA: WizardData = {
  ruleset_slug: 'dnd5e_2014',
  race_slug: '',
  race_custom_name: '',
  subrace_slug: '',
  class_slug: '',
  class_custom_name: '',
  score_method: 'standard',
  score_rolls: [],
  ability_assignment: { slot0: 15, slot1: 14, slot2: 13, slot3: 12, slot4: 10, slot5: 8 },
  // 初始按标准数列顺序分配（STR/DEX/CON/INT/WIS/CHA = 15/14/13/12/10/8）
  ability_scores: { str: 15, dex: 14, con: 13, int: 12, wis: 10, cha: 8 },
  name: '',
  gender: '',
  age: '',
  alignment: '',
  background_slug: '',
  personality_traits: '',
  ideals: '',
  bonds: '',
  flaws: '',
  appearance: '',
}

interface WizardState {
  rulesetConfirmed: boolean
  data: WizardData
  confirmRuleset: () => void
  update: (patch: Partial<WizardData>) => void
  reset: () => void
}

export const useWizardStore = create<WizardState>((set, get) => ({
  rulesetConfirmed: false,
  data: { ...DEFAULT_DATA },

  confirmRuleset: () => set({ rulesetConfirmed: true }),
  update: (patch) => set({ data: { ...get().data, ...patch } }),
  reset: () => set({ rulesetConfirmed: false, data: { ...DEFAULT_DATA } }),
}))