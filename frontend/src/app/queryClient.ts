import { QueryClient } from '@tanstack/react-query'
import { ApiError } from '@/shared/api/ApiError'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,
      // 4xx errors (404, 403, validation) will not go away on retry; only network / 5xx errors are retried.
      retry: (failureCount, error) =>
        !(error instanceof ApiError && error.isClientError) && failureCount < 2,
    },
  },
})
