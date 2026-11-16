import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createMonitor, fetchMonitor, fetchMonitors } from './api'
import type { MonitorFilters } from './types'

/** Cache keys for monitors, defined once and reused for invalidation. */
export const monitorKeys = {
  all: ['monitors'] as const,
  list: (filters: MonitorFilters) => [...monitorKeys.all, 'list', filters] as const,
  detail: (id: number) => [...monitorKeys.all, 'detail', id] as const,
}

export function useMonitors(filters: MonitorFilters) {
  return useQuery({
    queryKey: monitorKeys.list(filters),
    queryFn: ({ signal }) => fetchMonitors(filters, signal),
    // Keep showing the previous results while a new filter loads, instead of a spinner.
    placeholderData: keepPreviousData,
  })
}

export function useMonitor(id: number) {
  return useQuery({
    queryKey: monitorKeys.detail(id),
    queryFn: ({ signal }) => fetchMonitor(id, signal),
  })
}

export function useCreateMonitor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createMonitor,
    // Lists and counters change after a create, so every monitor query is refetched.
    onSuccess: () => queryClient.invalidateQueries({ queryKey: monitorKeys.all }),
  })
}
