const ACCESS_KEY = 'upwatch.access'
const REFRESH_KEY = 'upwatch.refresh'

export interface Tokens {
  access: string
  refresh: string
}

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),

  setAccess(access: string) {
    localStorage.setItem(ACCESS_KEY, access)
  },

  setTokens({ access, refresh }: Tokens) {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },

  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}
