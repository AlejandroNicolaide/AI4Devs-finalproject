import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded px-3 py-1 text-sm font-medium ${isActive ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:text-indigo-600'}`

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="border-b bg-white">
      <nav className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
        <Link to="/" className="text-lg font-bold text-indigo-600">
          AsistenteIA
        </Link>
        <NavLink to="/" end className={linkClass}>
          Asignaturas
        </NavLink>
        <NavLink to="/conversations" className={linkClass}>
          Historial
        </NavLink>
        <div className="ml-auto flex items-center gap-3 text-sm text-gray-600">
          <span>
            {user?.email} · {user?.role === 'teacher' ? 'Docente' : 'Estudiante'}
          </span>
          <button onClick={handleLogout} className="rounded border px-3 py-1 hover:bg-gray-100">
            Salir
          </button>
        </div>
      </nav>
    </header>
  )
}

export default function Layout() {
  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </>
  )
}
