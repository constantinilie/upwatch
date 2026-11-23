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

/** Deletes a monitor (soft delete on the server: its incident history is kept); 204 without body. */
export function deleteMonitor(id: number) {
  return api.delete(`/monitors/${id}/`)
}
