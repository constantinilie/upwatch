import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { onSessionExpired } from '@/shared/api/httpClient'
import { tokenStorage } from '@/shared/api/tokenStorage'
import { fetchCurrentUser, login as loginRequest } from './api'
import { AuthContext, type AuthContextValue } from './AuthContext'
import { authKeys } from './queries'
import type { LoginCredentials } from './types'

/** Owns the session: the current client, login and logout. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [hasSession, setHasSession] = useState(() => tokenStorage.getAccess() !== null)

  const { data: user, isPending } = useQuery({
    queryKey: authKeys.currentUser,
    queryFn: ({ signal }) => fetchCurrentUser(signal),
    enabled: hasSession,
    staleTime: 5 * 60 * 1000,
  })

  const logout = useCallback(() => {
    tokenStorage.clear()
    setHasSession(false)
    queryClient.clear()
  }, [queryClient])

  // The refresh token expired during a request: close the session everywhere.
  useEffect(() => onSessionExpired(logout), [logout])

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const tokens = await loginRequest(credentials)
      tokenStorage.setTokens(tokens)
      // Load the client before marking the session as active, so pages never see a session without a user.
      try {
        await queryClient.fetchQuery({
          queryKey: authKeys.currentUser,
          queryFn: ({ signal }) => fetchCurrentUser(signal),
        })
      } catch (error) {
        tokenStorage.clear()
        throw error
      }
      setHasSession(true)
    },
    [queryClient],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user: hasSession ? (user ?? null) : null,
      isLoading: hasSession && isPending,
      login,
      logout,
    }),
    [hasSession, user, isPending, login, logout],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
