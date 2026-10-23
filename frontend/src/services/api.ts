import axios from 'axios'

export const TOKEN_KEY = 'asistenteia.token'
export const USER_KEY = 'asistenteia.user'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 120_000, // la subida de documentos genera embeddings de forma síncrona
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Token expirado o inválido en un endpoint protegido: se limpia la sesión y se vuelve al login.
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const isAuthCall = String(error.config?.url ?? '').startsWith('/auth/')
    if (error.response?.status === 401 && !isAuthCall) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      window.location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export default api

/** Extrae el `detail` de un error de FastAPI (string o lista de validación 422). */
export function getErrorMessage(error: unknown, fallback = 'Ha ocurrido un error'): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) return detail.map((d) => d.msg).join('. ')
    if (!error.response) return 'No se pudo conectar con el servidor'
  }
  return fallback
}
