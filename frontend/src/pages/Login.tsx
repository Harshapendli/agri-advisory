import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sprout, Loader2 } from 'lucide-react'
import { loginUser, registerUser } from '../api/client'
import { useStore } from '../store/useStore'

export default function Login() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({ name: '', email: '', password: '', state: '', preferred_language: 'en' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { setToken, setUser } = useStore()
  const nav = useNavigate()

  const handleSubmit = async () => {
    setError(''); setLoading(true)
    try {
      const res = mode === 'login'
        ? await loginUser({ email: form.email, password: form.password })
        : await registerUser(form)
      setToken(res.access_token)
      setUser({ id: res.user_id, name: res.name, preferred_language: res.preferred_language })
      nav('/')
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Something went wrong')
    } finally { setLoading(false) }
  }

  const inp = (key: string, type: string, placeholder: string) => (
    <input type={type} placeholder={placeholder} value={(form as any)[key]}
      onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
      className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-300" />
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-2xl mb-4">
            <Sprout className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">AgriAdvisory</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered farming intelligence</p>
        </div>
        <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
          {(['login', 'register'] as const).map(m => (
            <button key={m} onClick={() => setMode(m)}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all capitalize ${mode === m ? 'bg-white shadow-sm text-gray-800' : 'text-gray-500'}`}>{m}</button>
          ))}
        </div>
        <div className="space-y-3">
          {mode === 'register' && inp('name', 'text', 'Full name')}
          {inp('email', 'email', 'Email address')}
          {inp('password', 'password', 'Password')}
          {mode === 'register' && (
            <>
              <input placeholder="State (e.g. Telangana)" value={form.state}
                onChange={e => setForm(f => ({ ...f, state: e.target.value }))}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-300" />
              <select value={form.preferred_language} onChange={e => setForm(f => ({ ...f, preferred_language: e.target.value }))}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-300">
                <option value="en">English</option><option value="te">తెలుగు</option>
                <option value="hi">हिंदी</option><option value="mr">मराठी</option>
              </select>
            </>
          )}
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <button onClick={handleSubmit} disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </div>
      </div>
    </div>
  )
}
