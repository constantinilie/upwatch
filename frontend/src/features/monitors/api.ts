import { api } from '@/shared/api/httpClient'
import type { Monitor, MonitorFilters, MonitorInput, MonitorSummary } from './types'

/** The client's monitors, optionally filtered by status and a name / URL search. */
export function fetchMonitors(filters: MonitorFilters, signal?: AbortSignal) {
  return api.get<MonitorSummary[]>('/monitors/', {
    query: { status: filters.status, search: filters.search },
    signal,
  })
}

/** One of the client's monitors; 404 also when it belongs to another client. */
export function fetchMonitor(id: number, signal?: AbortSignal) {
  return api.get<MonitorSummary>(`/monitors/${id}/`, { signal })
}

/** Creates a monitor; plan limits are checked by the API (400 with field errors). */
export function createMonitor(input: MonitorInput) {
  return api.post<Monitor>('/monitors/', input)
}
