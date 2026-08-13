import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL: API_URL })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('agri_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('agri_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export interface SoilInput {
  N: number; P: number; K: number
  temperature: number; humidity: number; ph: number; rainfall: number
}

export const predictCrop = (soil: SoilInput) => api.post('/predict/crop', soil).then(r => r.data)

export const getAdvisory = (query: string, soil: SoilInput | null, location: string, language: string) =>
  api.post('/advisory', { query, soil, location, language }).then(r => r.data)

export interface ChatMessage { role: 'user' | 'ai'; text: string }

export const chatAdvisory = (query: string, location: string, language: string, history: ChatMessage[] = []) =>
  api.post('/advisory/chat', { query, location, language, history }).then(r => r.data)

export const predictDisease = (file: File) => {
  const fd = new FormData(); fd.append('file', file)
  return api.post('/disease/predict', fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}

export const transcribeAudio = (blob: Blob) => {
  const fd = new FormData(); fd.append('file', blob, 'recording.webm')
  return api.post('/voice/transcribe', fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}

export const textToSpeech = (text: string, lang: string): Promise<Blob> =>
  api.post('/voice/speak', { text, lang }, { responseType: 'blob' }).then(r => r.data)

export const loginUser = (data: { email?: string; phone?: string; password: string }) =>
  api.post('/auth/login', data).then(r => r.data)

export const registerUser = (data: any) => api.post('/auth/register', data).then(r => r.data)

export const getHistory = () => api.get('/advisory/history').then(r => r.data)

export const exportPDF = (data: any): Promise<Blob> =>
  api.post('/advisory/export-pdf', data, { responseType: 'blob' }).then(r => r.data)
