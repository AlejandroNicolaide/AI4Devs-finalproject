import { Link } from 'react-router-dom'
import { useConversations, useDeleteConversation } from '../hooks/useChat'
import { useSubjects } from '../hooks/useSubjects'
import { getErrorMessage } from '../services/api'

export default function HistoryPage() {
  const { data: conversations, isLoading, error } = useConversations()
  const { data: subjects } = useSubjects()
  const remove = useDeleteConversation()

  const subjectName = (id: string) => subjects?.find((s) => s.id === id)?.name ?? 'Asignatura'

  function handleDelete(id: string) {
    if (window.confirm('¿Eliminar esta conversación? Se borrarán todos sus mensajes y no se puede deshacer.')) {
      remove.mutate(id)
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Historial de conversaciones</h1>
      {isLoading && <p className="text-gray-500">Cargando…</p>}
      {error && <p className="text-red-600">{getErrorMessage(error)}</p>}
      {remove.isError && <p className="text-red-600">{getErrorMessage(remove.error)}</p>}
      {conversations?.length === 0 && <p className="text-gray-500">No tienes conversaciones.</p>}

      <ul className="space-y-3">
        {conversations?.map((c) => (
          <li key={c.id} className="flex items-center justify-between rounded-xl bg-white p-4 shadow">
            <div>
              <p className="font-medium">{subjectName(c.subject_id)}</p>
              <p className="text-sm text-gray-500">{new Date(c.created_at).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <Link
                to={`/subjects/${c.subject_id}/chat?conversation=${c.id}`}
                className="rounded bg-indigo-600 px-3 py-1 text-sm text-white hover:bg-indigo-700"
              >
                Continuar
              </Link>
              <button
                onClick={() => handleDelete(c.id)}
                disabled={remove.isPending}
                className="rounded border border-red-300 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
              >
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
