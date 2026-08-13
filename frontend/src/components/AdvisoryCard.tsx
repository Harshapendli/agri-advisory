import { CloudSun, Sprout, Droplets, AlertTriangle, Building2, Leaf, Bug, Calendar, TrendingUp } from 'lucide-react'

interface Props { result: any; compact?: boolean }

export default function AdvisoryCard({ result, compact }: Props) {
  const a = result?.advisory || {}
  if (!a.recommendation) return null

  if (compact) return (
    <div className="bg-green-50 border border-green-100 rounded-xl p-3 text-sm space-y-2">
      <p className="text-green-800 font-medium">{a.crop_advice}</p>
      {a.weather_advisory && <p className="text-gray-600 text-xs">{a.weather_advisory}</p>}
      {a.pest_control && <p className="text-gray-600 text-xs"><strong>Pest control:</strong> {a.pest_control}</p>}
    </div>
  )

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="bg-gradient-to-r from-green-600 to-green-700 px-5 py-4">
        <h3 className="text-white font-semibold text-lg">🌾 Agricultural Advisory</h3>
        <p className="text-green-100 text-sm mt-1">{a.recommendation}</p>
      </div>
      <div className="p-5 space-y-4">
        {a.crop_advice && (
          <Section icon={<Sprout className="w-5 h-5 text-green-600" />} title="Crop Advice">
            <p className="text-sm text-gray-600">{a.crop_advice}</p>
          </Section>
        )}
        {a.fertilizer_plan?.length > 0 && (
          <Section icon={<Leaf className="w-5 h-5 text-amber-600" />} title="Fertilizer Plan">
            <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="bg-amber-50">
              <th className="text-left p-2 text-amber-700">Fertilizer</th>
              <th className="p-2 text-amber-700">Dose</th>
              <th className="p-2 text-amber-700">Timing</th>
              <th className="p-2 text-amber-700">Method</th>
            </tr></thead><tbody>
              {a.fertilizer_plan.map((f: any, i: number) => (
                <tr key={i} className="border-t border-gray-100">
                  <td className="p-2 font-medium text-gray-700">{f.fertilizer}</td>
                  <td className="p-2 text-center text-gray-600">{f.dose}</td>
                  <td className="p-2 text-center text-gray-600">{f.timing}</td>
                  <td className="p-2 text-center text-gray-600">{f.method || '-'}</td>
                </tr>
              ))}
            </tbody></table></div>
          </Section>
        )}
        {a.fertilizer_schedule?.length > 0 && (
          <Section icon={<Calendar className="w-5 h-5 text-purple-600" />} title="Fertilizer Schedule">
            <div className="space-y-1.5">
              {a.fertilizer_schedule.map((s: any, i: number) => (
                <div key={i} className="flex items-center gap-2 text-xs bg-purple-50 p-2 rounded-lg">
                  <span className="font-medium text-purple-700 min-w-[100px]">{s.stage}</span>
                  <span className="text-gray-600">{s.fertilizer} — {s.dose} — {s.timing}</span>
                </div>
              ))}
            </div>
          </Section>
        )}
        {(a.irrigation_advice || a.irrigation_planning) && (
          <Section icon={<Droplets className="w-5 h-5 text-blue-500" />} title="Irrigation Planning">
            {a.irrigation_planning ? (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-blue-50 p-2 rounded-lg"><span className="font-medium text-blue-700">Method:</span> <span className="text-gray-600">{a.irrigation_planning.method}</span></div>
                <div className="bg-blue-50 p-2 rounded-lg"><span className="font-medium text-blue-700">Frequency:</span> <span className="text-gray-600">{a.irrigation_planning.frequency}</span></div>
                <div className="bg-blue-50 p-2 rounded-lg"><span className="font-medium text-blue-700">Quantity:</span> <span className="text-gray-600">{a.irrigation_planning.quantity}</span></div>
                <div className="bg-blue-50 p-2 rounded-lg"><span className="font-medium text-blue-700">Best time:</span> <span className="text-gray-600">{a.irrigation_planning.best_time}</span></div>
                {a.irrigation_planning.tips && <div className="col-span-2 bg-blue-50 p-2 rounded-lg"><span className="font-medium text-blue-700">💡 Tip:</span> <span className="text-gray-600">{a.irrigation_planning.tips}</span></div>}
              </div>
            ) : <p className="text-sm text-gray-600">{a.irrigation_advice}</p>}
          </Section>
        )}
        {a.disease_risk?.length > 0 && (
          <Section icon={<AlertTriangle className="w-5 h-5 text-red-500" />} title="Disease Risks">
            <div className="space-y-1.5">{a.disease_risk.map((d: any, i: number) => (
              <div key={i} className={`flex flex-col gap-1 text-xs p-2.5 rounded-lg ${d.risk_level === 'high' ? 'bg-red-50 border border-red-100' : d.risk_level === 'medium' ? 'bg-amber-50 border border-amber-100' : 'bg-gray-50 border border-gray-100'}`}>
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${d.risk_level === 'high' ? 'text-red-700' : d.risk_level === 'medium' ? 'text-amber-700' : 'text-gray-600'}`}>{d.disease}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${d.risk_level === 'high' ? 'bg-red-200 text-red-800' : d.risk_level === 'medium' ? 'bg-amber-200 text-amber-800' : 'bg-gray-200 text-gray-600'}`}>{d.risk_level}</span>
                </div>
                <span className="text-gray-600">{d.prevention}</span>
              </div>
            ))}</div>
          </Section>
        )}
        {a.pest_control && (
          <Section icon={<Bug className="w-5 h-5 text-orange-600" />} title="Pest Control">
            <p className="text-sm text-gray-600">{a.pest_control}</p>
          </Section>
        )}
        {a.weather_advisory && (
          <Section icon={<CloudSun className="w-5 h-5 text-sky-500" />} title="Weather Advisory">
            <p className="text-sm text-gray-600">{a.weather_advisory}</p>
          </Section>
        )}
        {a.government_schemes?.length > 0 && (
          <Section icon={<Building2 className="w-5 h-5 text-indigo-600" />} title="Government Schemes">
            <div className="space-y-2">
              {a.government_schemes.map((s: any, i: number) => (
                <div key={i} className="bg-indigo-50 border border-indigo-100 rounded-lg p-3">
                  <p className="font-semibold text-indigo-800 text-sm">{typeof s === 'string' ? s : s.scheme}</p>
                  {typeof s !== 'string' && <>
                    <p className="text-xs text-indigo-700 mt-1">✅ {s.benefit}</p>
                    <p className="text-xs text-gray-600 mt-0.5">👤 Eligibility: {s.eligibility}</p>
                    <p className="text-xs text-gray-600 mt-0.5">📝 How to apply: {s.how_to_apply}</p>
                  </>}
                </div>
              ))}
            </div>
          </Section>
        )}
        {a.seasonal_tips && (
          <Section icon={<TrendingUp className="w-5 h-5 text-teal-600" />} title="Seasonal Tips">
            <p className="text-sm text-gray-600">{a.seasonal_tips}</p>
          </Section>
        )}
        {a.market_outlook && (
          <p className="text-xs text-gray-500 bg-gray-50 rounded-lg p-2">📊 {a.market_outlook}</p>
        )}
        {result.sources?.length > 0 && <p className="text-xs text-gray-400 border-t pt-3">Sources: {result.sources.join(' · ')}</p>}
      </div>
    </div>
  )
}

function Section({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">{icon}<p className="text-sm font-semibold text-gray-700">{title}</p></div>
      {children}
    </div>
  )
}
