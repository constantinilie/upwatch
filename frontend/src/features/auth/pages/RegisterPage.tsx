import { Link, Navigate, useNavigate } from 'react-router'
import { paths } from '@/shared/config/paths'
import { AuthPageLayout } from '../components/AuthPageLayout'
import { RegisterForm } from '../components/RegisterForm'
import { useRegister } from '../queries'
import type { RegisterInput } from '../types'
import { useAuth } from '../useAuth'

export function RegisterPage() {
  const { user } = useAuth()
  const register = useRegister()
  const navigate = useNavigate()

  if (user) return <Navigate to={paths.monitors} replace />

  function handleRegister(input: RegisterInput) {
    register.mutate(input, { onSuccess: () => navigate(paths.monitors, { replace: true }) })
  }

  return (
    <AuthPageLayout
      subtitle="Creează un cont gratuit și începe să îți monitorizezi site-urile."
      footer={
        <>
          Ai deja cont? <Link to={paths.login}>Intră în cont</Link>
        </>
      }
    >
      <RegisterForm
        error={register.error}
        isSubmitting={register.isPending}
        onSubmit={handleRegister}
      />
    </AuthPageLayout>
  )
}
