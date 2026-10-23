import { useState } from 'react'
import type { Message, Source } from '../types'

function SourceChip({ source }: { source: Source }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="text-xs">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="rounded-full border border-indigo-200 bg-indigo-50 px-2 py-1 text-indigo-700 hover:bg-indigo-100"
      >
        📄 {source.filename}
      </button>
      {/* El fragmento siempre está en el DOM; se muestra recortado y se expande al pulsar */}
      <p className={`mt-1 max-w-md text-gray-600 ${open ? '' : 'line-clamp-2'}`}>{source.fragment}</p>
    </div>
  )
}

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        data-role={message.role}
        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
          isUser ? 'bg-indigo-600 text-white' : 'bg-white text-gray-900 shadow'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2 border-t pt-2">
            <p className="text-xs font-semibold text-gray-500">Fuentes</p>
            {message.sources.map((s) => (
              <SourceChip key={s.chunk_id} source={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
