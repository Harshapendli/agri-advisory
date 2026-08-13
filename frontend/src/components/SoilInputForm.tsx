import { useState, useCallback } from 'react'
import { Loader2, FlaskConical, Download } from 'lucide-react'
import { predictCrop, getAdvisory, exportPDF, SoilInput } from '../api/client'
import { useStore } from '../store/useStore'
import { t } from '../i18n'
import ShapCard from './ShapCard'

const defaults: SoilInput = { N: 90, P: 42, K: 43, temperature: 25, humidity: 70, ph: 6.5, rainfall: 200 }
const fields = [
  { key: 'N', label: 'Nitrogen (N)', min: 0, max: 140, unit: 'kg/ha', color: 'bg-blue-500' },
  { key: 'P', label: 'Phosphorus (P)', min: 0, max: 145, unit: 'kg/ha', color: 'bg-purple-500' },
  { key: 'K', label: 'Potassium (K)', min: 0, max: 205, unit: 'kg/ha', color: 'bg-amber-500' },
  { key: 'temperature', label: 'Temperature', min: 8, max: 44, unit: '°C', color: 'bg-red-500' },
  { key: 'humidity', label: 'Humidity', min: 14, max: 100, unit: '%', color: 'bg-cyan-500' },
  { key: 'ph', label: 'Soil pH', min: 3, max: 10, unit: '', color: 'bg-green-500', step: 0.1 },
  { key: 'rainfall', label: 'Rainfall', min: 20, max: 300, unit: 'mm', color: 'bg-sky-500' },
] as const

interface Props { onPredict?: (result: any, soil: SoilInput) => void }

export default function SoilInputForm({ onPredict }: Props) {
  const [soil, setSoil] = useState<SoilInput>(defaults)
  const [result, setResult] = useState<any>(null)
  const [fullAdvisory, setFullAdvisory] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const { language } = useStore()

  const handlePredict = useCallback(async () => {
    setLoading(true)
    try {
      const res = await predictCrop(soil)
      setResult(res)
      onPredict?.(res, soil)

      // Also fetch full advisory for PDF export
      try {
        const advRes = await getAdvisory(
          `Best farming advice for ${res.predicted_crop}`,
          soil, 'Hyderabad', language
        )
        setFullAdvisory(advRes)
      } catch {}
    } catch (e) {
      console.error(e)
    } finally { setLoading(false) }
  }, [soil, onPredict, language])

  const handleExportPDF = async () => {
    if (!result) return
    setExporting(true)
    try {
      const blob = await exportPDF({
        crop: result.predicted_crop,
        confidence: result.confidence,
        location: 'Hyderabad',
        advisory: fullAdvisory?.advisory || {},
        shap_factors: result.shap_factors || [],
        weather: fullAdvisory?.weather || {}
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `AgriAdvisory_${result.predicted_crop}_${new Date().toISOString().slice(0, 10)}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('PDF export failed:', e)
    } finally { setExporting(false) }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 md:p-5">
      <div className="flex items-center gap-2 mb-4">
        <FlaskConical className="w-5 h-5 text-green-600" />
        <h2 className="font-semibold text-gray-800">{t('adv.soilParams', language)}</h2>
      </div>
      <div className="space-y-3">
        {fields.map(f => (
          <div key={f.key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">{f.label}</span>
              <span className="font-medium text-gray-800">{soil[f.key]}{f.unit}</span>
            </div>
            <input type="range" min={f.min} max={f.max} step={(f as any).step || 1}
              value={soil[f.key]}
              onChange={e => setSoil(s => ({ ...s, [f.key]: parseFloat(e.target.value) }))}
              className="w-full h-2 rounded-full appearance-none cursor-pointer accent-green-600"
            />
          </div>
        ))}
      </div>
      <button onClick={handlePredict} disabled={loading}
        className="mt-4 w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-medium py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2">
        {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Predicting...</> : t('adv.getCrop', language)}
      </button>
      {result && !result.error && (
        <div className="mt-4 space-y-3">
          <div className="bg-green-50 rounded-xl p-4 border border-green-100">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-700">{result.predicted_crop}</div>
                <div className="text-sm text-green-600 mt-1">{t('adv.confidence', language)}: {result.confidence}%</div>
              </div>
              <button onClick={handleExportPDF} disabled={exporting}
                className="flex items-center gap-1.5 bg-white border border-green-200 text-green-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-green-50 transition-colors disabled:opacity-50">
                {exporting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                PDF Report
              </button>
            </div>
            {result.alternatives?.length > 0 && (
              <div className="mt-2 flex gap-2 flex-wrap">
                {result.alternatives.map((a: any) => (
                  <span key={a.crop} className="text-xs bg-white border border-green-200 text-green-700 px-2 py-0.5 rounded-full">
                    {a.crop} ({a.confidence}%)
                  </span>
                ))}
              </div>
            )}
          </div>
          {result.shap_factors?.length > 0 && <ShapCard factors={result.shap_factors} />}
        </div>
      )}
    </div>
  )
}
