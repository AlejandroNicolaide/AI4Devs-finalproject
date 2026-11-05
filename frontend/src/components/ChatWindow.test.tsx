import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { Message } from '../types'
import ChatWindow from './ChatWindow'

const messages: Message[] = [
  { id: '1', role: 'user', content: '¿Qué es la mitosis?', created_at: '2026-01-01T00:00:00Z' },
  {
    id: '2',
    role: 'assistant',
    content: 'Es la división celular.',
    created_at: '2026-01-01T00:00:01Z',
    sources: [{ chunk_id: 'c1', document_id: 'd1', filename: 'unidad1.pdf', fragment: 'La mitosis es...' }],
  },
]

function setup(props: Partial<React.ComponentProps<typeof ChatWindow>> = {}) {
  const onSend = vi.fn()
  render(<ChatWindow messages={[]} isTyping={false} onSend={onSend} {...props} />)
  return { onSend, input: screen.getByPlaceholderText('Escribe tu pregunta…'), button: screen.getByRole('button', { name: 'Enviar' }) }
}

describe('ChatWindow', () => {
  it('invita a preguntar cuando no hay mensajes', () => {
    setup()

    expect(screen.getByText('Haz una pregunta sobre el material de la asignatura.')).toBeInTheDocument()
  })

  it('envía la pregunta sin espacios sobrantes y vacía el campo', async () => {
    const { onSend, input, button } = setup()

    await userEvent.type(input, '  ¿Qué es la mitosis?  ')
    await userEvent.click(button)

    expect(onSend).toHaveBeenCalledExactlyOnceWith('¿Qué es la mitosis?')
    expect(input).toHaveValue('')
  })

  it('no permite enviar un mensaje vacío o solo con espacios', async () => {
    const { onSend, input, button } = setup()

    expect(button).toBeDisabled()
    await userEvent.type(input, '   ')
    expect(button).toBeDisabled()
    await userEvent.type(input, '{Enter}')

    expect(onSend).not.toHaveBeenCalled()
  })

  it('muestra "escribiendo…" y bloquea el envío mientras espera la respuesta', async () => {
    const { onSend, input, button } = setup({ isTyping: true })

    expect(screen.getByText('El asistente está escribiendo…')).toBeInTheDocument()
    await userEvent.type(input, 'otra pregunta{Enter}')

    expect(button).toBeDisabled()
    expect(onSend).not.toHaveBeenCalled()
  })

  it('pinta la conversación con la respuesta y sus fuentes', () => {
    setup({ messages })

    expect(screen.getByText('¿Qué es la mitosis?')).toBeInTheDocument()
    expect(screen.getByText('Es la división celular.')).toBeInTheDocument()
    expect(screen.getByText('Fuentes')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /unidad1\.pdf/ })).toBeInTheDocument()
  })

  it('muestra el error como alerta dentro de la conversación', () => {
    setup({ messages, error: 'El modelo de lenguaje no está disponible en este momento' })

    expect(screen.getByRole('alert')).toHaveTextContent('El modelo de lenguaje no está disponible')
  })
})
