import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AxiosError } from 'axios'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../context/AuthContext'
import * as authService from '../services/authService'
import LoginPage from './LoginPage'

vi.mock('../services/authService')

function httpError(status: number, detail: string) {
  return new AxiosError('fail', 'ERR', undefined, undefined, {
    status,
    data: { detail },
  } as never)
}

function renderLogin() {
  render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<p>Pantalla de inicio</p>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>,
  )
}

async function fillAndSubmit(email: string, password: string) {
  await userEvent.type(screen.getByLabelText('Email'), email)
  await userEvent.type(screen.getByLabelText('Contraseña'), password)
  await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.mocked(authService.login).mockReset()
  })

  it('muestra el error del servidor cuando las credenciales son inválidas', async () => {
    vi.mocked(authService.login).mockRejectedValue(httpError(401, 'Credenciales inválidas'))
    renderLogin()

    await fillAndSubmit('ana@test.com', 'incorrecta')

    expect(await screen.findByRole('alert')).toHaveTextContent('Credenciales inválidas')
    expect(screen.queryByText('Pantalla de inicio')).not.toBeInTheDocument()
    expect(localStorage.getItem('asistenteia.token')).toBeNull()
  })

  it('avisa de que no hay conexión si el servidor no responde', async () => {
    vi.mocked(authService.login).mockRejectedValue(new AxiosError('Network Error'))
    renderLogin()

    await fillAndSubmit('ana@test.com', 'Secreta123!')

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con el servidor')
  })

  it('guarda la sesión y redirige al inicio con credenciales válidas', async () => {
    vi.mocked(authService.login).mockResolvedValue('token-jwt')
    vi.mocked(authService.userFromToken).mockReturnValue({ id: 'u1', email: 'ana@test.com', role: 'student' })
    renderLogin()

    await fillAndSubmit('ana@test.com', 'Secreta123!')

    expect(await screen.findByText('Pantalla de inicio')).toBeInTheDocument()
    expect(localStorage.getItem('asistenteia.token')).toBe('token-jwt')
    expect(authService.login).toHaveBeenCalledWith('ana@test.com', 'Secreta123!')
  })

  it('enlaza al registro', () => {
    renderLogin()

    expect(screen.getByRole('link', { name: 'Regístrate' })).toHaveAttribute('href', '/register')
  })
})
