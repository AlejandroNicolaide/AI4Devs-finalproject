import { createContext, useCallback, useMemo, useState, type ReactNode } from 'react'
import { TOKEN_KEY, USER_KEY } from '../services/api'
import * as authService from '../services/authService'
import type { Role, User } from '../types'

interface AuthContextValue {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string, role: Role) => Promise<void>
  logout: () => void
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null)

function loadSession(): { token: string | null; user: User | null } {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const user = localStorage.getItem(USER_KEY)
    if (token && user) return { token, user: JSON.parse(user) as User }
  } catch {
    // almacenamiento no disponible o JSON corrupto: sesión vacía
  }
  return { token: null, user: null }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState(loadSession)

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setSession({ token: null, user: null })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const token = await authService.login(email, password)
    const user = authService.userFromToken(token, email)
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    setSession({ token, user })
  }, [])

  const register = useCallback(
    async (name: string, email: string, password: string, role: Role) => {
      await authService.register({ name, email, password, role })
      await login(email, password)
    },
    [login],
  )

  const value = useMemo<AuthContextValue>(
    () => ({ ...session, isAuthenticated: !!session.token, login, register, logout }),
    [session, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
