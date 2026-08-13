import { Link, useLocation } from 'react-router-dom'
import { Sprout, MessageSquare, Bug, History, LogOut, ChevronDown } from 'lucide-react'
import { useStore } from '../store/useStore'
import { useState } from 'react'
import { t } from '../i18n'

const langs = [{ code: 'en', label: 'English' }, { code: 'te', label: 'తెలుగు' }, { code: 'hi', label: 'हिंदी' }, { code: 'mr', label: 'मराठी' }]

export default function Navbar() {
  const { user, language, setLanguage, logout } = useStore()
  const { pathname } = useLocation()
  const [showProfile, setShowProfile] = useState(false)

  const navItem = (to: string, icon: React.ReactNode, labelKey: string) => (
    <Link to={to} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${pathname === to ? 'bg-green-700 text-white' : 'text-green-100 hover:bg-green-700/50'}`}>
      {icon}{t(labelKey, language)}
    </Link>
  )
  return (
    <nav className="bg-green-800 text-white shadow-lg relative">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <Sprout className="w-6 h-6 text-green-300" />
            <span>AgriAdvisory</span>
          </Link>
          <div className="hidden md:flex items-center gap-1">
            {navItem('/', <Sprout className="w-4 h-4" />, 'nav.dashboard')}
            {navItem('/advisory', <MessageSquare className="w-4 h-4" />, 'nav.advisory')}
            {navItem('/disease', <Bug className="w-4 h-4" />, 'nav.disease')}
            {navItem('/history', <History className="w-4 h-4" />, 'nav.history')}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <button onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 bg-green-700 hover:bg-green-600 rounded-lg px-3 py-1.5 transition-colors">
              <div className="w-7 h-7 bg-green-500 rounded-full flex items-center justify-center text-sm font-bold">
                {(user?.name || 'F')[0].toUpperCase()}
              </div>
              <span className="text-sm hidden md:block">{user?.name || 'Farmer'}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            {showProfile && (
              <div className="absolute right-0 top-12 bg-white rounded-xl shadow-xl border border-gray-100 w-72 p-4 z-50"
                onMouseLeave={() => setShowProfile(false)}>
                <div className="flex items-center gap-3 mb-3 pb-3 border-b border-gray-100">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-green-700 font-bold text-lg">
                    {(user?.name || 'F')[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800 text-sm">{user?.name || 'Farmer'}</p>
                    <p className="text-xs text-gray-500">{user?.email || ''}</p>
                  </div>
                </div>
                <div className="mb-3">
                  <label className="text-xs font-medium text-gray-500 block mb-1.5">Language / భాష</label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {langs.map(l => (
                      <button key={l.code}
                        onClick={() => { setLanguage(l.code as any); }}
                        className={`text-sm py-1.5 rounded-lg transition-colors ${language === l.code ? 'bg-green-600 text-white font-medium' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                        {l.label}
                      </button>
                    ))}
                  </div>
                </div>
                <button onClick={() => { logout(); setShowProfile(false); }}
                  className="w-full flex items-center justify-center gap-2 text-sm text-red-600 hover:bg-red-50 py-2 rounded-lg transition-colors">
                  <LogOut className="w-4 h-4" /> {t('common.logout', language)}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Mobile nav */}
      <div className="md:hidden flex items-center gap-1 px-4 pb-2 overflow-x-auto">
        {navItem('/', <Sprout className="w-4 h-4" />, 'nav.dashboard')}
        {navItem('/advisory', <MessageSquare className="w-4 h-4" />, 'nav.advisory')}
        {navItem('/disease', <Bug className="w-4 h-4" />, 'nav.disease')}
        {navItem('/history', <History className="w-4 h-4" />, 'nav.history')}
      </div>
    </nav>
  )
}
