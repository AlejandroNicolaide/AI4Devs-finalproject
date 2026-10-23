import api from './api'
import type { Role, User } from '../types'

interface RegisterData {
  name: string
  email: string
  password: string
  role: Role
}

export async function register(data: RegisterData): Promise<User> {
  const res = await api.post<User>('/auth/register', data)
  return res.data
}

export async function login(email: string, password: string): Promise<string> {
  const res = await api.post<{ access_token: string }>('/auth/login', { email, password })
  return res.data.access_token
}

/** Extrae id y role del payload del JWT (sub, role). No valida la firma: eso lo hace el backend. */
export function userFromToken(token: string, email: string): User {
  const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
  return { id: payload.sub, email, role: payload.role }
}
