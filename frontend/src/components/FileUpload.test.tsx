import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AxiosError } from 'axios'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as subjectService from '../services/subjectService'
import FileUpload from './FileUpload'

vi.mock('../services/subjectService')

function renderUpload() {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <FileUpload subjectId="subject-1" />
    </QueryClientProvider>,
  )
  return screen.getByLabelText(/Subir material/) as HTMLInputElement
}

describe('FileUpload', () => {
  beforeEach(() => {
    vi.mocked(subjectService.uploadDocument).mockReset()
  })

  it('solo ofrece PDF y TXT en el selector de archivos', () => {
    const input = renderUpload()

    expect(input.accept).toContain('.pdf')
    expect(input.accept).toContain('.txt')
    expect(input.accept).not.toContain('.exe')
  })

  it('sube el archivo y muestra cuántos fragmentos se crearon', async () => {
    vi.mocked(subjectService.uploadDocument).mockResolvedValue({ id: 'd1', filename: 'unidad1.txt', chunks_created: 7 })
    const input = renderUpload()
    const file = new File(['La mitosis...'], 'unidad1.txt', { type: 'text/plain' })

    await userEvent.upload(input, file)

    expect(await screen.findByRole('status')).toHaveTextContent('«unidad1.txt» subido correctamente: 7 fragmentos creados.')
    expect(subjectService.uploadDocument).toHaveBeenCalledWith('subject-1', file)
  })

  it('muestra el rechazo del servidor para un formato no soportado', async () => {
    vi.mocked(subjectService.uploadDocument).mockRejectedValue(
      new AxiosError('fail', 'ERR', undefined, undefined, {
        status: 415,
        data: { detail: 'Formato no soportado. Formatos aceptados: PDF, TXT' },
      } as never),
    )
    const input = renderUpload()

    await userEvent.upload(input, new File(['MZ'], 'virus.exe'), { applyAccept: false })

    expect(await screen.findByRole('alert')).toHaveTextContent('Formato no soportado. Formatos aceptados: PDF, TXT')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})
