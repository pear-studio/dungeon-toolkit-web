import { create } from 'zustand'
import { characterApi, type Character } from '../lib/api'

interface CharacterState {
  characters: Character[]
  loading: boolean
  error: string | null

  fetchCharacters: () => Promise<void>
  deleteCharacter: (id: string) => Promise<void>
  toggleShare: (id: string) => Promise<void>
}

export const useCharacterStore = create<CharacterState>((set, get) => ({
  characters: [],
  loading: false,
  error: null,

  fetchCharacters: async () => {
    set({ loading: true, error: null })
    try {
      const res = await characterApi.list()
      set({ characters: res.data, loading: false })
    } catch {
      set({ error: '加载角色失败', loading: false })
    }
  },

  deleteCharacter: async (id: string) => {
    await characterApi.delete(id)
    set({ characters: get().characters.filter((c) => c.id !== id) })
  },

  toggleShare: async (id: string) => {
    const res = await characterApi.toggleShare(id)
    set({
      characters: get().characters.map((c) => (c.id === id ? res.data : c)),
    })
  },
}))
