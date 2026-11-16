import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { onSessionExpired } from '@/shared/api/httpClient'
import { tokenStorage, type Tokens } from '@/shared/api/tokenStorage'
import { fetchCurrentUser, login as loginRequest, register as registerRequest } from './api'
import { AuthContext, type AuthContextValue } from './AuthContext'
import { authKeys } from './queries'
import type { LoginCredentials, RegisterInput } from './types'

/** Owns the session: the current client, login, sign-up and logout. */
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

  /** Stores the tokens of a fresh login / sign-up and loads the client they belong to. */
  const startSession = useCallback(
    async (tokens: Tokens) => {
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

  const login = useCallback(
    async (credentials: LoginCredentials) => startSession(await loginRequest(credentials)),
    [startSession],
  )

  const register = useCallback(
    async (input: RegisterInput) => startSession(await registerRequest(input)),
    [startSession],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user: hasSession ? (user ?? null) : null,
      isLoading: hasSession && isPending,
      login,
      register,
      logout,
    }),
    [hasSession, user, isPending, login, register, logout],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
