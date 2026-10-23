import { Link, useParams } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import { useAuth } from '../hooks/useAuth'
import { useDocuments, useSubject } from '../hooks/useSubjects'
import { getErrorMessage } from '../services/api'

export default function SubjectDetailPage() {
  const { id = '' } = useParams()
  const { user } = useAuth()
  const { data: subject, isLoading, error } = useSubject(id)
  const isOwner = user?.role === 'teacher' && subject?.teacher_id === user.id
  const { data: documents } = useDocuments(id, isOwner)

  if (isLoading) return <p className="text-gray-500">Cargando…</p>
  if (error || !subject) return <p className="text-red-600">{getErrorMessage(error, 'Asignatura no encontrada')}</p>

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Asignaturas
      </Link>
      <div>
        <h1 className="text-2xl font-bold">{subject.name}</h1>
        <p className="mt-1 text-gray-600">{subject.description || 'Sin descripción'}</p>
      </div>

      <Link
        to={`/subjects/${subject.id}/chat`}
        className="inline-block rounded bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700"
      >
        Preguntar al asistente
      </Link>

      {isOwner && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Material de la asignatura</h2>
          <FileUpload subjectId={subject.id} />
          <ul className="divide-y rounded-xl bg-white shadow">
            {documents?.length === 0 && <li className="p-4 text-sm text-gray-500">Aún no hay documentos.</li>}
            {documents?.map((d) => (
              <li key={d.id} className="flex justify-between p-4 text-sm">
                <span>{d.filename}</span>
                <span className="text-gray-500">{new Date(d.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
