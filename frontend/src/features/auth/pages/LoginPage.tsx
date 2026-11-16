import { Link, Navigate, useLocation, useNavigate, type Location } from 'react-router'
import { paths } from '@/shared/config/paths'
import { AuthPageLayout } from '../components/AuthPageLayout'
import { LoginForm } from '../components/LoginForm'
import { useLogin } from '../queries'
import type { LoginCredentials } from '../types'
import { useAuth } from '../useAuth'

export function LoginPage() {
  const { user } = useAuth()
  const login = useLogin()
  const navigate = useNavigate()
  const location = useLocation()
  // RequireAuth stores the page the client tried to open, so we can send them back after login.
  const from = (location.state as { from?: Location } | null)?.from?.pathname ?? paths.monitors

  if (user) return <Navigate to={from} replace />

  function handleLogin(credentials: LoginCredentials) {
    login.mutate(credentials, { onSuccess: () => navigate(from, { replace: true }) })
  }

  return (
    <AuthPageLayout
      subtitle="Intră în contul tău ca să îți vezi monitoarele."
      footer={
        <>
          Nu ai cont? <Link to={paths.register}>Creează unul gratuit</Link>
        </>
      }
    >
      <LoginForm error={login.error} isSubmitting={login.isPending} onSubmit={handleLogin} />
    </AuthPageLayout>
  )
}
