import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Factor { feature: string; feature_label: string; value: number; shap_importance: number; direction: string }
interface Props { factors: Factor[] }

export default function ShapCard({ factors }: Props) {
  if (!factors || factors.length === 0 || !factors[0]?.shap_importance) {
    return (
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Why this crop? (SHAP Explanation)</h3>
        <p className="text-xs text-gray-500">SHAP explanation not available for this prediction.</p>
      </div>
    )
  }
  const data = factors.map(f => ({ name: f.feature_label, importance: parseFloat((f.shap_importance ?? 0).toFixed(3)), direction: f.direction, value: f.value }))
  return (
    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Why this crop? (SHAP Explanation)</h3>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20 }}>
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
          <Tooltip formatter={(v: any, n: any, p: any) => [`${v} (value: ${p.payload.value})`, 'SHAP']} />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((d, i) => <Cell key={i} fill={d.direction === 'positive' ? '#16a34a' : '#dc2626'} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-1">Green = factor favors this crop · Red = factor against</p>
    </div>
  )
}
