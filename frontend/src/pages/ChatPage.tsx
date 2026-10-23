import { useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import ChatWindow from '../components/ChatWindow'
import { useConversationMessages, useSendMessage } from '../hooks/useChat'
import { useSubject } from '../hooks/useSubjects'
import { getErrorMessage } from '../services/api'
import type { Message, Source } from '../types'

export default function ChatPage() {
  const { id: subjectId = '' } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const conversationId = searchParams.get('conversation') ?? undefined

  const { data: subject } = useSubject(subjectId)
  const { data: history } = useConversationMessages(conversationId)
  const send = useSendMessage()

  // La API de historial no devuelve fuentes: se conservan las de la última respuesta de esta sesión.
  const [live, setLive] = useState<{ conversationId: string; sources: Source[] } | null>(null)
  const [pendingText, setPendingText] = useState<string | null>(null)

  const messages: Message[] = [...(history ?? [])]
  if (live && live.conversationId === conversationId && messages.length > 0) {
    const last = messages[messages.length - 1]
    if (last.role === 'assistant') messages[messages.length - 1] = { ...last, sources: live.sources }
  }
  if (pendingText) {
    messages.push({ id: 'pending', role: 'user', content: pendingText, created_at: '' })
  }

  function handleSend(text: string) {
    setPendingText(text)
    send.mutate(
      { subjectId, message: text, conversationId },
      {
        onSuccess: (res) => {
          setLive({ conversationId: res.conversation_id, sources: res.sources })
          setPendingText(null)
          if (res.conversation_id !== conversationId) {
            navigate(`/subjects/${subjectId}/chat?conversation=${res.conversation_id}`, { replace: true })
          }
        },
        onError: () => setPendingText(null),
      },
    )
  }

  return (
    <div className="space-y-4">
      <Link to={`/subjects/${subjectId}`} className="text-sm text-indigo-600 hover:underline">
        ← {subject?.name ?? 'Asignatura'}
      </Link>
      <h1 className="text-xl font-bold">Chat · {subject?.name}</h1>
      <ChatWindow
        messages={messages}
        isTyping={send.isPending}
        error={send.isError ? getErrorMessage(send.error, 'No se pudo obtener la respuesta') : null}
        onSend={handleSend}
      />
    </div>
  )
}
