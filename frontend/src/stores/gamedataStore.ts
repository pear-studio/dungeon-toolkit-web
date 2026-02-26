/**
 * gamedataStore —— 缓存从后端加载的游戏数据（种族、职业、背景）
 *
 * 规范：
 * - 所有种族/职业/背景的展示名、选项列表，必须来自此 store（即后端 API）
 * - 禁止在组件或页面中以硬编码数组/对象充当这些列表的 fallback
 * - 若 API 失败，保持空数组并通过 error 字段暴露错误，由 UI 展示错误状态
 */
import { create } from 'zustand'
import { gamedataApi, type Race, type CharClass, type Background } from '../lib/api'

interface GamedataState {
  races: Race[]
  classes: CharClass[]
  backgrounds: Background[]
  loading: boolean
  error: string | null
  loaded: boolean   // 是否已经成功加载过一次
  fetchAll: () => Promise<void>
  /** 根据 slug 查种族中文名，找不到返回 slug 本身 */
  raceName: (slug: string) => string
  /** 根据 slug 查职业中文名，找不到返回 slug 本身 */
  className: (slug: string) => string
  /** 根据 slug 查背景中文名，找不到返回 slug 本身 */
  backgroundName: (slug: string) => string
}

export const useGamedataStore = create<GamedataState>((set, get) => ({
  races: [],
  classes: [],
  backgrounds: [],
  loading: false,
  error: null,
  loaded: false,

  fetchAll: async () => {
    // 已加载过则跳过（除非需要强制刷新）
    if (get().loaded) return
    set({ loading: true, error: null })
    try {
      const [racesRes, classesRes, bgsRes] = await Promise.all([
        gamedataApi.races(),
        gamedataApi.classes(),
        gamedataApi.backgrounds(),
      ])
      set({
        races: racesRes.data.results,
        classes: classesRes.data.results,
        backgrounds: bgsRes.data.results,
        loading: false,
        loaded: true,
      })
    } catch (e: unknown) {
      const msg = (e as { message?: string })?.message ?? '加载游戏数据失败'
      set({ loading: false, error: msg })
    }
  },

  raceName: (slug) => {
    if (!slug) return ''
    if (slug.startsWith('custom__')) return slug.replace('custom__', '')
    return get().races.find((r) => r.slug === slug)?.name ?? slug
  },

  className: (slug) => {
    if (!slug) return ''
    if (slug.startsWith('custom__')) return slug.replace('custom__', '')
    return get().classes.find((c) => c.slug === slug)?.name ?? slug
  },

  backgroundName: (slug) => {
    if (!slug) return ''
    return get().backgrounds.find((b) => b.slug === slug)?.name ?? slug
  },
}))
