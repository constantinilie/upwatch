import { useMutation } from '@tanstack/react-query'
import { useAuth } from './useAuth'

/** Cache keys for the auth feature, defined once and reused for invalidation. */
export const authKeys = {
  currentUser: ['auth', 'me'] as const,
}

/** Logs in through AuthProvider, exposing the request state (isPending, error) to the form. */
export function useLogin() {
  const { login } = useAuth()
  return useMutation({ mutationFn: login })
}

/** Creates an account through AuthProvider; on success the new client is already logged in. */
export function useRegister() {
  const { register } = useAuth()
  return useMutation({ mutationFn: register })
}
