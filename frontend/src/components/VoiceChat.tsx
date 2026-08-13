import { useState, useRef, useCallback, useEffect } from 'react'
import { Mic, MicOff, Volume2, Send, MapPin, Sprout } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { transcribeAudio, textToSpeech, chatAdvisory, ChatMessage, SoilInput } from '../api/client'
import { useStore } from '../store/useStore'

interface Message { role: 'user' | 'ai'; text: string; location?: string; sources?: string[] }
interface Props { location?: string; soilContext?: { soil: SoilInput; crop: string; confidence: number } | null }

export default function VoiceChat({ location = 'Hyderabad', soilContext }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', text: 'నమస్కారం! Hello! I am your AI agricultural advisor. Ask me anything about crops, diseases, fertilizers or farming practices for any region in India. 🌾' }
  ])
  const [recording, setRecording] = useState(false)
  const [loading, setLoading] = useState(false)
  const [textInput, setTextInput] = useState('')
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const chatEndRef = useRef<HTMLDivElement | null>(null)
  const { language } = useStore()

  // When soil prediction changes, inject context into chat
  useEffect(() => {
    if (soilContext && soilContext.crop) {
      setMessages(m => [...m, {
        role: 'ai',
        text: `🧪 I see you just predicted **${soilContext.crop}** (${soilContext.confidence}% confidence) from your soil analysis.\n\nYour soil readings: N=${soilContext.soil.N}, P=${soilContext.soil.P}, K=${soilContext.soil.K}, pH=${soilContext.soil.ph}, Temperature=${soilContext.soil.temperature}°C, Humidity=${soilContext.soil.humidity}%, Rainfall=${soilContext.soil.rainfall}mm.\n\nAsk me anything about this crop — fertilizer plans, irrigation, disease risks, or market prices!`
      }])
      scrollToBottom()
    }
  }, [soilContext?.crop, soilContext?.confidence])

  const scrollToBottom = () => {
    setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
  }

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    chunksRef.current = []
    mr.ondataavailable = e => chunksRef.current.push(e.data)
    mr.onstop = async () => {
      stream.getTracks().forEach(t => t.stop())
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
      await processAudio(blob)
    }
    mr.start()
    mediaRef.current = mr
    setRecording(true)
  }, [])

  const stopRecording = useCallback(() => {
    mediaRef.current?.stop()
    setRecording(false)
  }, [])

  const processAudio = async (blob: Blob) => {
    setLoading(true)
    try {
      const { text } = await transcribeAudio(blob)
      if (text) await sendQuery(text)
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }

  const sendQuery = async (query: string) => {
    setMessages(m => [...m, { role: 'user', text: query }])
    setLoading(true)
    scrollToBottom()
    try {
      // Build chat history from recent messages (include soil context)
      const history: ChatMessage[] = messages
        .filter(m => m.role === 'user' || m.role === 'ai')
        .slice(-6)
        .map(m => ({ role: m.role, text: m.text }))

      // If we have soil context, prepend it so the LLM knows about the prediction
      let enrichedQuery = query
      if (soilContext && soilContext.crop) {
        enrichedQuery = `[Context: Farmer's soil analysis predicted ${soilContext.crop} with ${soilContext.confidence}% confidence. Soil: N=${soilContext.soil.N}, P=${soilContext.soil.P}, K=${soilContext.soil.K}, pH=${soilContext.soil.ph}, Temp=${soilContext.soil.temperature}°C, Humidity=${soilContext.soil.humidity}%, Rainfall=${soilContext.soil.rainfall}mm]\n\n${query}`
      }

      const result = await chatAdvisory(enrichedQuery, location, language, history)
      const answer = result.answer || 'Sorry, I could not generate a response. Please try again.'
      const detectedLocation = result.location || location

      setMessages(m => [...m, {
        role: 'ai',
        text: answer,
        location: detectedLocation,
        sources: result.sources
      }])

      // Try text-to-speech for the response
      try {
        const audioBlob = await textToSpeech(answer.substring(0, 300), language)
        const url = URL.createObjectURL(audioBlob)
        new Audio(url).play()
      } catch {}
    } catch (e) {
      setMessages(m => [...m, { role: 'ai', text: 'Sorry, could not fetch advisory. Please try again.' }])
    } finally {
      setLoading(false)
      scrollToBottom()
    }
  }

  const handleSend = async () => {
    if (!textInput.trim()) return
    const q = textInput.trim(); setTextInput('')
    await sendQuery(q)
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col h-[600px]">
      <div className="p-4 border-b border-gray-100 flex items-center gap-2">
        <Volume2 className="w-5 h-5 text-green-600" />
        <h2 className="font-semibold text-gray-800">Voice Advisory Chat</h2>
        {soilContext?.crop && (
          <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full flex items-center gap-1">
            <Sprout className="w-3 h-3" />
            {soilContext.crop}
          </span>
        )}
        <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{language.toUpperCase()}</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] space-y-1`}>
              <div className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-green-600 text-white rounded-br-sm'
                  : 'bg-gray-100 text-gray-800 rounded-bl-sm'
              }`}>
                {m.role === 'ai' ? (
                  <div className="prose prose-sm prose-gray max-w-none
                    [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1
                    [&_li]:my-0.5 [&_strong]:text-gray-900
                    [&_h1]:text-base [&_h1]:font-semibold [&_h1]:my-2
                    [&_h2]:text-sm [&_h2]:font-semibold [&_h2]:my-2
                    [&_h3]:text-sm [&_h3]:font-medium [&_h3]:my-1
                    [&_code]:bg-gray-200 [&_code]:px-1 [&_code]:rounded [&_code]:text-xs">
                    <ReactMarkdown>{m.text}</ReactMarkdown>
                  </div>
                ) : (
                  <span>{m.text}</span>
                )}
              </div>
              {/* Show detected location badge for AI responses */}
              {m.role === 'ai' && m.location && (
                <div className="flex items-center gap-1 px-2">
                  <MapPin className="w-3 h-3 text-green-500" />
                  <span className="text-[10px] text-green-600 font-medium">{m.location}</span>
                  {m.sources && m.sources.length > 0 && (
                    <span className="text-[10px] text-gray-400 ml-2">
                      via {m.sources.join(', ')}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => <div key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <div className="p-4 border-t border-gray-100 flex gap-2">
        <input value={textInput} onChange={e => setTextInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Type your farming question... (e.g. best crop for Warangal?)"
          className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-300" />
        <button onClick={handleSend} disabled={loading || !textInput.trim()}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-200 text-white p-2.5 rounded-xl transition-colors">
          <Send className="w-4 h-4" />
        </button>
        <button onMouseDown={startRecording} onMouseUp={stopRecording} onTouchStart={startRecording} onTouchEnd={stopRecording}
          className={`p-2.5 rounded-xl transition-all ${recording ? 'bg-red-500 text-white scale-110 animate-pulse' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>
          {recording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>
      </div>
    </div>
  )
}
