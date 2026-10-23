import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { Message } from '../types'
import MessageBubble from './MessageBubble'

interface Props {
  messages: Message[]
  isTyping: boolean
  error?: string | null
  onSend: (text: string) => void
}

export default function ChatWindow({ messages, isTyping, error, onSend }: Props) {
  const [text, setText] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ behavior: 'smooth' })
  }, [messages, isTyping])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || isTyping) return
    onSend(trimmed)
    setText('')
  }

  return (
    <div className="flex h-[70vh] flex-col rounded-xl bg-gray-100">
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && !isTyping && (
          <p className="text-center text-sm text-gray-500">Haz una pregunta sobre el material de la asignatura.</p>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isTyping && <p className="text-sm italic text-gray-500">El asistente está escribiendo…</p>}
        {error && (
          <p role="alert" className="rounded bg-red-50 p-2 text-sm text-red-700">
            {error}
          </p>
        )}
        <div ref={endRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 border-t bg-white p-3">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Escribe tu pregunta…"
          maxLength={4000}
          className="flex-1 rounded border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isTyping || !text.trim()}
          className="rounded bg-indigo-600 px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
