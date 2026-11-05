import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import type { Message } from '../types'
import MessageBubble from './MessageBubble'

const source = (n: number) => ({
  chunk_id: `chunk-${n}`,
  document_id: 'doc-1',
  filename: `unidad${n}.pdf`,
  fragment: `Fragmento citado número ${n}`,
})

const assistant = (sources?: Message['sources']): Message => ({
  id: 'm1',
  role: 'assistant',
  content: 'La mitosis tiene cuatro fases.',
  created_at: '2026-01-01T00:00:00Z',
  sources,
})

describe('MessageBubble', () => {
  it('muestra el contenido del mensaje', () => {
    render(<MessageBubble message={assistant()} />)

    expect(screen.getByText('La mitosis tiene cuatro fases.')).toBeInTheDocument()
  })

  it('lista todas las fuentes citadas como chips con el nombre del documento', () => {
    render(<MessageBubble message={assistant([source(1), source(2)])} />)

    expect(screen.getByText('Fuentes')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /unidad1\.pdf/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /unidad2\.pdf/ })).toBeInTheDocument()
  })

  it('funciona con una sola fuente', () => {
    render(<MessageBubble message={assistant([source(1)])} />)

    expect(screen.getAllByRole('button')).toHaveLength(1)
  })

  it('expande y contrae el fragmento al pulsar el chip', async () => {
    render(<MessageBubble message={assistant([source(1)])} />)
    const chip = screen.getByRole('button', { name: /unidad1\.pdf/ })
    const fragment = screen.getByText('Fragmento citado número 1')

    expect(chip).toHaveAttribute('aria-expanded', 'false')
    expect(fragment).toHaveClass('line-clamp-2')

    await userEvent.click(chip)
    expect(chip).toHaveAttribute('aria-expanded', 'true')
    expect(fragment).not.toHaveClass('line-clamp-2')

    await userEvent.click(chip)
    expect(chip).toHaveAttribute('aria-expanded', 'false')
  })

  it('no muestra el bloque Fuentes si el asistente no citó nada', () => {
    render(<MessageBubble message={assistant([])} />)

    expect(screen.queryByText('Fuentes')).not.toBeInTheDocument()
  })

  it('no muestra fuentes en los mensajes del estudiante', () => {
    const message: Message = { ...assistant([source(1)]), role: 'user' }
    render(<MessageBubble message={message} />)

    expect(screen.queryByText('Fuentes')).not.toBeInTheDocument()
  })
})
