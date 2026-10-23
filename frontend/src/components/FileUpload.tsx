import { useRef } from 'react'
import { useUploadDocument } from '../hooks/useSubjects'
import { getErrorMessage } from '../services/api'

export default function FileUpload({ subjectId }: { subjectId: string }) {
  const upload = useUploadDocument(subjectId)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleChange(file: File | undefined) {
    if (!file) return
    upload.mutate(file, {
      onSettled: () => {
        if (inputRef.current) inputRef.current.value = ''
      },
    })
  }

  return (
    <div className="rounded-xl border-2 border-dashed border-gray-300 bg-white p-6">
      <label className="block text-sm font-medium">
        Subir material (PDF o TXT)
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          disabled={upload.isPending}
          onChange={(e) => handleChange(e.target.files?.[0])}
          className="mt-2 block w-full text-sm"
        />
      </label>
      {upload.isPending && (
        <p className="mt-3 text-sm text-indigo-600">Procesando documento (extrayendo texto y generando embeddings)…</p>
      )}
      {upload.isSuccess && (
        <p role="status" className="mt-3 rounded bg-green-50 p-2 text-sm text-green-700">
          «{upload.data.filename}» subido correctamente: {upload.data.chunks_created} fragmentos creados.
        </p>
      )}
      {upload.isError && (
        <p role="alert" className="mt-3 rounded bg-red-50 p-2 text-sm text-red-700">
          {getErrorMessage(upload.error, 'No se pudo subir el documento')}
        </p>
      )}
    </div>
  )
}
