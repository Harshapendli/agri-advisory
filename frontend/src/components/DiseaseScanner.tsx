import { useState, useRef } from 'react'
import { Upload, Camera, Loader2, AlertTriangle, CheckCircle, Leaf } from 'lucide-react'
import { predictDisease } from '../api/client'

export default function DiseaseScanner() {
  const [preview, setPreview] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    setFile(f); setResult(null)
    const reader = new FileReader()
    reader.onload = e => setPreview(e.target?.result as string)
    reader.readAsDataURL(f)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f?.type.startsWith('image/')) handleFile(f)
  }

  const analyse = async () => {
    if (!file) return
    setLoading(true)
    try { setResult(await predictDisease(file)) }
    catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const isHealthy = result?.disease_name?.toLowerCase().includes('healthy')
  const isNotPlant = result?.disease_name?.toLowerCase().includes('not a plant')

  const severityColor = () => {
    if (isHealthy) return 'text-green-600 bg-green-50 border-green-200'
    if (isNotPlant) return 'text-gray-600 bg-gray-50 border-gray-200'
    const conf = result?.confidence ?? 0
    return conf > 80 ? 'text-red-600 bg-red-50 border-red-200' : conf > 60 ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-yellow-600 bg-yellow-50 border-yellow-200'
  }

  const StatusIcon = isHealthy ? Leaf : isNotPlant ? Upload : AlertTriangle

  return (
    <div className="space-y-4">
      <div onDrop={handleDrop} onDragOver={e => e.preventDefault()}
        className="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center hover:border-green-400 transition-colors cursor-pointer bg-gray-50"
        onClick={() => inputRef.current?.click()}>
        {preview ? (
          <img src={preview} alt="Leaf" className="mx-auto max-h-48 rounded-xl object-cover" />
        ) : (
          <div className="space-y-2">
            <Upload className="w-10 h-10 text-gray-400 mx-auto" />
            <p className="text-gray-600 font-medium">Drop a leaf image here</p>
            <p className="text-gray-400 text-sm">or click to browse · JPG, PNG, WebP</p>
          </div>
        )}
        <input ref={inputRef} type="file" accept="image/*" className="hidden"
          onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
      </div>
      {file && (
        <button onClick={analyse} disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-medium py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2">
          {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Analysing with AI Vision...</> : <><Camera className="w-4 h-4" />Analyse Leaf</>}
        </button>
      )}
      {result && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className={`p-4 border ${severityColor()}`}>
            <div className="flex items-center gap-2">
              <StatusIcon className="w-5 h-5" />
              <div>
                <p className="font-semibold text-lg">{result.disease_name}</p>
                <p className="text-sm opacity-80">
                  {isHealthy ? `Confidence: ${result.confidence?.toFixed(1)}% — No disease detected` :
                   isNotPlant ? 'Please upload a leaf image' :
                   `Confidence: ${result.confidence?.toFixed(1)}%`}
                </p>
              </div>
            </div>
          </div>
          <div className="p-4 space-y-4">
            {result.symptoms && <div><p className="text-sm font-medium text-gray-700 mb-1">{isHealthy ? 'Analysis' : 'Symptoms'}</p><p className="text-sm text-gray-600">{result.symptoms}</p></div>}
            {result.immediate_action && (
              <div className={`p-3 rounded-xl text-sm ${isHealthy ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
                <p className="font-medium mb-1">{isHealthy ? '✅ Status' : '⚡ Immediate Action'}</p>
                <p>{result.immediate_action}</p>
              </div>
            )}
            {result.treatments?.length > 0 && (
              <div><p className="text-sm font-medium text-gray-700 mb-2">Treatment</p>
                <div className="space-y-1">{result.treatments.map((t: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" /><span>{t.pesticide} — {t.application}</span></div>
                ))}</div>
              </div>
            )}
            {result.prevention_tips?.length > 0 && (
              <div><p className="text-sm font-medium text-gray-700 mb-2">{isHealthy ? 'Maintenance Tips' : 'Prevention Tips'}</p>
                <ul className="space-y-1">{result.prevention_tips.map((tip: string, i: number) => <li key={i} className="text-sm text-gray-600 flex gap-2"><span className="text-green-500">•</span>{tip}</li>)}</ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
