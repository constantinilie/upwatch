import { createContext } from 'react'
import type { CurrentUser, LoginCredentials } from './types'

export interface AuthContextValue {
  /** The logged-in client, or null when nobody is logged in. */
  user: CurrentUser | null
  /** True while an existing session (the token in localStorage) is being checked. */
  isLoading: boolean
  /** Gets the tokens, then loads the client; rejects with an ApiError on wrong credentials. */
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
