import { api } from '@/shared/api/httpClient'
import type { Tokens } from '@/shared/api/tokenStorage'
import type { CurrentUser, LoginCredentials } from './types'

/** Exchanges email + password for a JWT pair (public endpoint, no token sent). */
export function login(credentials: LoginCredentials) {
  return api.post<Tokens>('/auth/token/', credentials, { auth: false })
}

/** The logged-in client and their active plan. */
export function fetchCurrentUser(signal?: AbortSignal) {
  return api.get<CurrentUser>('/auth/me/', { signal })
}
