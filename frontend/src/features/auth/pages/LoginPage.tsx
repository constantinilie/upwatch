import { Navigate, useLocation, useNavigate, type Location } from 'react-router'
import { Card } from '@/shared/components/Card'
import { paths } from '@/shared/config/paths'
import { LoginForm } from '../components/LoginForm'
import { useLogin } from '../queries'
import type { LoginCredentials } from '../types'
import { useAuth } from '../useAuth'
import styles from './LoginPage.module.css'

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
    <main className={styles.page}>
      <Card>
        <h1 className={styles.title}>UpWatch</h1>
        <p className={styles.subtitle}>Intră în contul tău ca să îți vezi monitoarele.</p>
        <LoginForm error={login.error} isSubmitting={login.isPending} onSubmit={handleLogin} />
      </Card>
    </main>
  )
}
