// The only place that reads import.meta.env; the rest of the app uses `env`.
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
} as const
