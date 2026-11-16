import { useContext } from 'react'
import { AuthContext } from './AuthContext'

/** The current session; throws outside <AuthProvider> so a missing provider fails loudly. */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside <AuthProvider>.')
  }
  return context
}
