import DiseaseScanner from '../components/DiseaseScanner'
import { useStore } from '../store/useStore'
import { t } from '../i18n'

export default function Disease() {
  const { language } = useStore()
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl md:text-2xl font-bold text-gray-800 mb-2">{t('dis.title', language)}</h1>
      <p className="text-gray-500 mb-6 text-sm md:text-base">{t('dis.subtitle', language)}</p>
      <DiseaseScanner />
      <div className="mt-6 bg-amber-50 border border-amber-100 rounded-xl p-4">
        <p className="text-sm text-amber-700"><strong>Note:</strong> For best results, take a clear close-up photo of the affected leaf in natural light. The CNN model is trained on the PlantVillage dataset covering 38 disease classes.</p>
      </div>
    </div>
  )
}
