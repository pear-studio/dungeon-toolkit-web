import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface WizardClassEntry {
  class_slug: string
  level: number
}

export interface WizardData {
  _v: number
  ruleset_slug: string
  race_slug: string
  race_custom_name: string
  subrace_slug: string
  classes: WizardClassEntry[]
  class_custom_name: string
  chosen_skills: string[]
  ability_method: string
  score_method: string
  score_rolls: number[]
  ability_scores: Record<string, number>
  background_slug: string
  name: string
  gender: string
  age: string
  alignment: string
  personality_traits: string
  ideals: string
  bonds: string
  flaws: string
  appearance: string
}

const DEFAULT_DATA: WizardData = {
  _v: 2,
  ruleset_slug: 'dnd5e_2014',
  race_slug: '',
  race_custom_name: '',
  subrace_slug: '',
  classes: [{ class_slug: '', level: 1 }],
  class_custom_name: '',
  chosen_skills: [],
  ability_method: 'standard',
  score_method: 'standard',
  score_rolls: [],
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

function migrateFromV1(data: Record<string, unknown>): WizardData {
  const oldClassSlug = data.class_slug as string | undefined
  if (oldClassSlug && typeof oldClassSlug === 'string' && oldClassSlug.trim()) {
    return {
      ...DEFAULT_DATA,
      ...data,
      _v: 2,
      classes: [{ class_slug: oldClassSlug, level: 1 }],
      score_method: (data.score_method as string) || 'standard',
      score_rolls: (data.score_rolls as number[]) || [],
    } as WizardData
  }
  return {
    ...DEFAULT_DATA,
    ...data,
    _v: 2,
    score_method: (data.score_method as string) || 'standard',
    score_rolls: (data.score_rolls as number[]) || [],
  } as WizardData
}

function migrateData(data: unknown): WizardData {
  if (!data || typeof data !== 'object') {
    return DEFAULT_DATA
  }
  const record = data as Record<string, unknown>
  const version = record._v as number | undefined
  if (!version || version < 2) {
    return migrateFromV1(record)
  }
  return data as WizardData
}

interface WizardState {
  rulesetConfirmed: boolean
  data: WizardData
  confirmRuleset: () => void
  update: (patch: Partial<WizardData>) => void
  addClass: () => void
  removeClass: (index: number) => void
  updateClass: (index: number, entry: WizardClassEntry) => void
  setChosenSkills: (skills: string[]) => void
  reset: () => void
}

export const useWizardStore = create<WizardState>()(
  persist(
    (set, get) => ({
      rulesetConfirmed: false,
      data: { ...DEFAULT_DATA },

      confirmRuleset: () => set({ rulesetConfirmed: true }),

      update: (patch) => set({ data: { ...get().data, ...patch } }),

      addClass: () => {
        const { classes } = get().data
        if (classes.length < 3) {
          set({
            data: {
              ...get().data,
              classes: [...classes, { class_slug: '', level: 1 }],
            },
          })
        }
      },

      removeClass: (index) => {
        const { classes } = get().data
        if (classes.length > 1 && index > 0) {
          const newClasses = classes.filter((_, i) => i !== index)
          set({ data: { ...get().data, classes: newClasses } })
        }
      },

      updateClass: (index, entry) => {
        const { classes } = get().data
        const newClasses = [...classes]
        newClasses[index] = entry
        set({ data: { ...get().data, classes: newClasses } })
      },

      setChosenSkills: (skills) => {
        set({ data: { ...get().data, chosen_skills: skills } })
      },

      reset: () => set({ rulesetConfirmed: false, data: { ...DEFAULT_DATA } }),
    }),
    {
      name: 'wizard-storage',
      partialize: (state) => ({ rulesetConfirmed: state.rulesetConfirmed, data: state.data }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          const migrated = migrateData(state.data)
          state.data = migrated
        }
      },
    }
  )
)

export const selectTotalLevel = (state: WizardState): number => {
  return state.data.classes.reduce((sum, cls) => sum + cls.level, 0)
}

export const selectMainClass = (state: WizardState): string => {
  return state.data.classes[0]?.class_slug || ''
}
