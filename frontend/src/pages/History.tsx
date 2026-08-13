import { useQuery } from '@tanstack/react-query'
import { getHistory } from '../api/client'
import { Loader2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import { t } from '../i18n'

export default function History() {
  const { language } = useStore()
  const { data, isLoading } = useQuery({ queryKey: ['history'], queryFn: getHistory })
  return (
    <div>
      <h1 className="text-xl md:text-2xl font-bold text-gray-800 mb-6">{t('hist.title', language)}</h1>
      {isLoading ? <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-green-600" /></div> :
        data?.length === 0 ? <div className="text-center py-12 text-gray-500">{t('hist.empty', language)}</div> :
          <div className="space-y-3">
            {data?.map((a: any) => (
              <div key={a.id} className="bg-white rounded-xl border border-gray-100 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:shadow-sm transition-shadow">
                <div>
                  <p className="font-medium text-gray-800 text-sm">{a.query}</p>
                  <div className="flex items-center gap-3 mt-1 flex-wrap">
                    {a.recommended_crop && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{a.recommended_crop}</span>}
                    {a.confidence && <span className="text-xs text-gray-500">{a.confidence}% confidence</span>}
                    <span className="text-xs text-gray-400">{new Date(a.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full uppercase self-start sm:self-auto">{a.language}</span>
              </div>
            ))}
          </div>
      }
    </div>
  )
}
