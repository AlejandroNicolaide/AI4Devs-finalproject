import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useCreateSubject, useSubjects } from '../hooks/useSubjects'
import { getErrorMessage } from '../services/api'

export default function SubjectsPage() {
  const { user } = useAuth()
  const { data: subjects, isLoading, error } = useSubjects()
  const createSubject = useCreateSubject()

  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  function handleCreate(e: FormEvent) {
    e.preventDefault()
    createSubject.mutate(
      { name, description: description || undefined },
      {
        onSuccess: () => {
          setName('')
          setDescription('')
          setShowForm(false)
        },
      },
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Asignaturas</h1>
        {user?.role === 'teacher' && (
          <button
            onClick={() => setShowForm((v) => !v)}
            className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Crear asignatura
          </button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="mb-6 space-y-3 rounded-xl bg-white p-4 shadow">
          {createSubject.isError && (
            <p role="alert" className="rounded bg-red-50 p-2 text-sm text-red-700">
              {getErrorMessage(createSubject.error)}
            </p>
          )}
          <input
            required
            placeholder="Nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          <textarea
            placeholder="Descripción (opcional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          <button
            type="submit"
            disabled={createSubject.isPending}
            className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {createSubject.isPending ? 'Guardando…' : 'Guardar'}
          </button>
        </form>
      )}

      {isLoading && <p className="text-gray-500">Cargando asignaturas…</p>}
      {error && <p className="text-red-600">{getErrorMessage(error)}</p>}
      {subjects?.length === 0 && <p className="text-gray-500">Todavía no hay asignaturas.</p>}

      <ul className="grid gap-4 sm:grid-cols-2">
        {subjects?.map((s) => (
          <li key={s.id}>
            <Link
              to={`/subjects/${s.id}`}
              className="block rounded-xl bg-white p-5 shadow transition hover:shadow-md"
            >
              <h2 className="font-semibold text-indigo-700">{s.name}</h2>
              <p className="mt-1 text-sm text-gray-600">{s.description || 'Sin descripción'}</p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
