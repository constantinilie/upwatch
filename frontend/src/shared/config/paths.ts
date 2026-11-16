/** Every client-side URL in one place, so links and redirects cannot drift from the router. */
export const paths = {
  login: '/login',
  register: '/register',
  monitors: '/monitors',
  newMonitor: '/monitors/new',
  monitor: (id: number) => `/monitors/${id}`,
} as const

/** Route patterns that take parameters (used only by the router). */
export const routePatterns = {
  monitor: '/monitors/:id',
} as const
