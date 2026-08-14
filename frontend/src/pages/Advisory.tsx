import { useState } from 'react'
import { MapPin, Navigation } from 'lucide-react'
import SoilInputForm from '../components/SoilInputForm'
import VoiceChat from '../components/VoiceChat'
import { SoilInput } from '../api/client'
import { useStore } from '../store/useStore'
import { t } from '../i18n'

interface SoilContext { soil: SoilInput; crop: string; confidence: number }

const INDIAN_LOCATIONS = [
  // Telangana
  'Hyderabad', 'Warangal', 'Karimnagar', 'Nizamabad', 'Khammam', 'Nalgonda',
  'Adilabad', 'Mahbubnagar', 'Medak', 'Rangareddy', 'Suryapet', 'Siddipet',
  // Andhra Pradesh
  'Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Rajahmundry',
  'Tirupati', 'Kakinada', 'Anantapur', 'Ongole',
  // Karnataka
  'Bangalore', 'Mysore', 'Hubli', 'Dharwad', 'Belgaum', 'Mangalore',
  // Tamil Nadu
  'Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tirupur',
  // Maharashtra
  'Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur',
  // Others
  'Delhi', 'Lucknow', 'Jaipur', 'Bhopal', 'Kolkata', 'Patna', 'Ahmedabad',
]

export default function Advisory() {
  const [soilContext, setSoilContext] = useState<SoilContext | null>(null)
  const { location, setLocation, detectLocation, locationLoading, language } = useStore()
  const [showDropdown, setShowDropdown] = useState(false)
  const [locSearch, setLocSearch] = useState('')

  const handlePredict = (result: any, soil: SoilInput) => {
    setSoilContext({
      soil,
      crop: result.predicted_crop || '',
      confidence: result.confidence || 0
    })
  }

  const filteredLocations = INDIAN_LOCATIONS.filter(l =>
    l.toLowerCase().includes(locSearch.toLowerCase())
  )

  return (
    <div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 md:mb-6 gap-3">
        <h1 className="text-xl md:text-2xl font-bold text-gray-800">{t('adv.title', language)}</h1>
        <div className="relative">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-green-600" />
            <label className="text-sm text-gray-600">{t('adv.location', language)}</label>
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-300 bg-white min-w-[160px] text-left flex items-center justify-between gap-2"
              >
                <span>{location}</span>
                <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </button>
              {showDropdown && (
                <div className="absolute right-0 top-10 bg-white rounded-xl shadow-xl border border-gray-100 w-64 z-50 overflow-hidden">
                  <div className="p-2 border-b border-gray-100 space-y-1.5">
                    <button
                      onClick={() => { detectLocation(); setShowDropdown(false); }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors font-medium"
                    >
                      <Navigation className="w-3.5 h-3.5" />
                      {locationLoading ? 'Detecting...' : 'Use my current location'}
                    </button>
                    <input
                      autoFocus
                      value={locSearch}
                      onChange={e => setLocSearch(e.target.value)}
                      placeholder="Search city..."
                      className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-300"
                    />
                  </div>
                  <div className="max-h-48 overflow-y-auto">
                    {filteredLocations.map(loc => (
                      <button
                        key={loc}
                        onClick={() => { setLocation(loc); setShowDropdown(false); setLocSearch(''); }}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-green-50 transition-colors flex items-center gap-2 ${location === loc ? 'bg-green-50 text-green-700 font-medium' : 'text-gray-700'}`}
                      >
                        <MapPin className="w-3 h-3 text-gray-400" />
                        {loc}
                      </button>
                    ))}
                    {filteredLocations.length === 0 && (
                      <div className="px-4 py-3 text-sm text-gray-400 text-center">
                        No match — type in the box above
                        <button
                          onClick={() => { setLocation(locSearch); setShowDropdown(false); setLocSearch(''); }}
                          className="block mt-1 text-green-600 hover:underline mx-auto"
                        >
                          Use "{locSearch}" anyway
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <SoilInputForm onPredict={handlePredict} />
        <VoiceChat location={location} soilContext={soilContext} />
      </div>
    </div>
  )
}
