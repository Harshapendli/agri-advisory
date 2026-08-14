import { create } from 'zustand'

interface User { id: string; name: string; email?: string; preferred_language: string }

interface Store {
  user: User | null
  token: string | null
  language: 'en' | 'te' | 'hi' | 'mr'
  location: string
  locationLoading: boolean
  setUser: (u: User | null) => void
  setToken: (t: string | null) => void
  setLanguage: (l: 'en' | 'te' | 'hi' | 'mr') => void
  setLocation: (loc: string) => void
  detectLocation: () => void
  logout: () => void
}

// Load persisted user on init
const savedUser = localStorage.getItem('agri_user')
const parsedUser = savedUser ? JSON.parse(savedUser) : null

export const useStore = create<Store>((set) => ({
  user: parsedUser,
  token: localStorage.getItem('agri_token'),
  language: (localStorage.getItem('agri_lang') as any) || 'en',
  location: localStorage.getItem('agri_location') || 'Hyderabad',
  locationLoading: false,
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
  setLocation: (location) => {
    localStorage.setItem('agri_location', location)
    set({ location })
  },
  detectLocation: () => {
    if (!navigator.geolocation) return
    set({ locationLoading: true })
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords
          // Reverse geocode using OpenWeatherMap (free, no extra API key needed)
          const res = await fetch(
            `https://api.openweathermap.org/geo/1.0/reverse?lat=${latitude}&lon=${longitude}&limit=1&appid=ff5b2b3d4aedd9a54c05cbf072d8a5bc`
          )
          const data = await res.json()
          if (data?.[0]?.name) {
            const city = data[0].name
            localStorage.setItem('agri_location', city)
            set({ location: city, locationLoading: false })
          } else {
            set({ locationLoading: false })
          }
        } catch {
          set({ locationLoading: false })
        }
      },
      () => { set({ locationLoading: false }) },
      { timeout: 10000 }
    )
  },
  logout: () => {
    localStorage.removeItem('agri_token')
    localStorage.removeItem('agri_user')
    localStorage.removeItem('agri_lang')
    localStorage.removeItem('agri_location')
    set({ user: null, token: null, language: 'en', location: 'Hyderabad' })
  }
}))
