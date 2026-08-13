import { create } from 'zustand'

interface User { id: string; name: string; email?: string; preferred_language: string }

interface Store {
  user: User | null
  token: string | null
  language: 'en' | 'te' | 'hi' | 'mr'
  setUser: (u: User | null) => void
  setToken: (t: string | null) => void
  setLanguage: (l: 'en' | 'te' | 'hi' | 'mr') => void
  logout: () => void
}

// Load persisted user on init
const savedUser = localStorage.getItem('agri_user')
const parsedUser = savedUser ? JSON.parse(savedUser) : null

export const useStore = create<Store>((set) => ({
  user: parsedUser,
  token: localStorage.getItem('agri_token'),
  language: (localStorage.getItem('agri_lang') as any) || 'en',
  setUser: (user) => {
    if (user) localStorage.setItem('agri_user', JSON.stringify(user))
    else localStorage.removeItem('agri_user')
    set({ user })
  },
  setToken: (token) => {
    if (token) localStorage.setItem('agri_token', token)
    else localStorage.removeItem('agri_token')
    set({ token })
  },
  setLanguage: (language) => {
    localStorage.setItem('agri_lang', language)
    set({ language })
  },
  logout: () => {
    localStorage.removeItem('agri_token')
    localStorage.removeItem('agri_user')
    localStorage.removeItem('agri_lang')
    set({ user: null, token: null, language: 'en' })
  }
}))
