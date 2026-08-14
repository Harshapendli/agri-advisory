import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { MessageSquare, Bug, History, Sprout, CloudSun, Droplets, Wind, Thermometer, MapPin, Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import { t } from '../i18n'

export default function Dashboard() {
  const { user, language, location, locationLoading, detectLocation } = useStore()
  const nav = useNavigate()
  const [weather, setWeather] = useState<any>(null)

  // Auto-detect location on first load
  useEffect(() => {
    detectLocation()
  }, [])

  // Fetch weather whenever location changes
  useEffect(() => {
    if (!location) return
    setWeather(null)
    fetch(`https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(location)}&appid=ff5b2b3d4aedd9a54c05cbf072d8a5bc&units=metric`)
      .then(r => r.json())
      .then(data => { if (data.main) setWeather(data) })
      .catch(() => {})
  }, [location])

  const cards = [
    { icon: <MessageSquare className="w-7 h-7 md:w-8 md:h-8 text-green-600" />, title: t('dash.getAdvisory', language), desc: 'AI-powered crop and farming recommendations', action: () => nav('/advisory'), bg: 'bg-green-50', border: 'border-green-100' },
    { icon: <Bug className="w-7 h-7 md:w-8 md:h-8 text-red-600" />, title: t('dash.diseaseScanner', language), desc: 'Upload leaf image for disease detection', action: () => nav('/disease'), bg: 'bg-red-50', border: 'border-red-100' },
    { icon: <History className="w-7 h-7 md:w-8 md:h-8 text-blue-600" />, title: t('dash.advisoryHistory', language), desc: 'View past recommendations', action: () => nav('/history'), bg: 'bg-blue-50', border: 'border-blue-100' },
  ]

  const currentMonth = new Date().getMonth() + 1
  const season = currentMonth >= 6 && currentMonth <= 10 ? 'Kharif' : currentMonth >= 11 || currentMonth <= 3 ? 'Rabi' : 'Zaid'
  const seasonCrops: Record<string, string> = {
    Kharif: 'Rice, Cotton, Maize, Groundnut, Soybean',
    Rabi: 'Wheat, Chickpea, Mustard, Barley, Lentil',
    Zaid: 'Watermelon, Muskmelon, Cucumber, Vegetables'
  }

  return (
    <div>
      <div className="mb-6 md:mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Sprout className="w-7 h-7 md:w-8 md:h-8 text-green-600" />
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800">{t('dash.welcome', language)}, {user?.name || 'Farmer'}!</h1>
        </div>
        <p className="text-gray-500 text-sm md:text-base">{t('dash.subtitle', language)}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5 mb-5 md:mb-6">
        {weather ? (
          <div className="bg-gradient-to-br from-sky-500 to-blue-600 rounded-2xl p-4 md:p-5 text-white">
            <div className="flex items-center gap-2 mb-3">
              <CloudSun className="w-5 h-5" />
              <h2 className="font-semibold text-sm md:text-base">{t('dash.weather', language)} — {location}</h2>
              {locationLoading && <Loader2 className="w-3 h-3 animate-spin opacity-70" />}
              <button onClick={detectLocation} className="ml-auto bg-white/20 hover:bg-white/30 rounded-lg px-2 py-1 text-xs flex items-center gap-1 transition-colors" title="Detect my location">
                <MapPin className="w-3 h-3" />
                <span className="hidden sm:inline">Sync</span>
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2 md:gap-3">
              <div className="bg-white/15 rounded-xl p-2.5 md:p-3">
                <Thermometer className="w-4 h-4 mb-1 opacity-80" />
                <div className="text-xl md:text-2xl font-bold">{Math.round(weather.main.temp)}°C</div>
                <div className="text-[10px] md:text-xs opacity-80">{t('common.feelsLike', language)} {Math.round(weather.main.feels_like)}°C</div>
              </div>
              <div className="bg-white/15 rounded-xl p-2.5 md:p-3">
                <Droplets className="w-4 h-4 mb-1 opacity-80" />
                <div className="text-xl md:text-2xl font-bold">{weather.main.humidity}%</div>
                <div className="text-[10px] md:text-xs opacity-80">{t('common.humidity', language)}</div>
              </div>
              <div className="bg-white/15 rounded-xl p-2.5 md:p-3">
                <Wind className="w-4 h-4 mb-1 opacity-80" />
                <div className="text-xl md:text-2xl font-bold">{Math.round(weather.wind.speed)} km/h</div>
                <div className="text-[10px] md:text-xs opacity-80">{t('common.wind', language)}</div>
              </div>
              <div className="bg-white/15 rounded-xl p-2.5 md:p-3">
                <CloudSun className="w-4 h-4 mb-1 opacity-80" />
                <div className="text-base md:text-lg font-bold capitalize">{weather.weather[0].description}</div>
                <div className="text-[10px] md:text-xs opacity-80">{t('common.conditions', language)}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-sky-500 to-blue-600 rounded-2xl p-4 md:p-5 text-white flex items-center justify-center min-h-[200px]">
            <div className="text-center">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 opacity-70" />
              <p className="text-sm opacity-80">Loading weather for {location}...</p>
            </div>
          </div>
        )}
        <div className="bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl p-4 md:p-5 text-white">
          <div className="flex items-center gap-2 mb-3">
            <Sprout className="w-5 h-5" />
            <h2 className="font-semibold text-sm md:text-base">{t('dash.season', language)} — {season}</h2>
          </div>
          <p className="text-white/90 text-sm mb-3">{t('dash.recommended', language)} {season}:</p>
          <div className="flex flex-wrap gap-2">
            {seasonCrops[season].split(', ').map(crop => (
              <span key={crop} className="bg-white/20 px-3 py-1 rounded-full text-xs md:text-sm font-medium">{crop}</span>
            ))}
          </div>
          <p className="text-white/70 text-xs mt-3">
            {season === 'Kharif' ? '🌧️ Monsoon season — ideal for rain-fed crops' :
             season === 'Rabi' ? '❄️ Winter season — irrigated crops thrive' :
             '☀️ Summer season — short-duration crops'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-5 mb-6 md:mb-8">
        {cards.map((c, i) => (
          <button key={i} onClick={c.action}
            className={`${c.bg} border ${c.border} rounded-2xl p-5 md:p-6 text-left hover:shadow-md transition-all hover:-translate-y-0.5`}>
            <div className="mb-2 md:mb-3">{c.icon}</div>
            <h2 className="font-semibold text-gray-800 mb-1">{c.title}</h2>
            <p className="text-sm text-gray-500">{c.desc}</p>
          </button>
        ))}
      </div>
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl p-5 md:p-6 text-white">
        <h2 className="text-lg font-semibold mb-2">{t('dash.quickStart', language)}</h2>
        <p className="text-green-100 text-sm mb-4">Enter your soil parameters and get an instant crop recommendation powered by XGBoost ML + Knowledge Graph + OpenAI GPT.</p>
        <button onClick={() => nav('/advisory')} className="bg-white text-green-700 font-medium px-4 py-2 rounded-xl hover:bg-green-50 transition-colors text-sm">
          {t('dash.startAdvisory', language)}
        </button>
      </div>
    </div>
  )
}
