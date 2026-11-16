import { Navigate, Outlet, useLocation } from 'react-router'
import { Spinner } from '@/shared/components/Spinner'
import { paths } from '@/shared/config/paths'
import { useAuth } from '../useAuth'

/** Child routes are shown only to a logged-in client; otherwise redirect to login, remembering the page. */
export function RequireAuth() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <Spinner label="Se verifică sesiunea…" />
  if (!user) return <Navigate to={paths.login} replace state={{ from: location }} />

  return <Outlet />
}
