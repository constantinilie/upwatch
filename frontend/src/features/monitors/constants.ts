import type { HttpMethod, MonitorStatus, MonitorType } from './types'

export const MONITOR_STATUS_LABELS: Record<MonitorStatus, string> = {
  pending: 'În așteptare',
  up: 'Up',
  down: 'Down',
  paused: 'Pe pauză',
}

export const MONITOR_TYPE_LABELS: Record<MonitorType, string> = {
  http: 'HTTP',
  keyword: 'Keyword',
  ssl: 'Certificat SSL',
}

export const HTTP_METHODS: readonly HttpMethod[] = ['GET', 'HEAD', 'POST']

export const MONITOR_STATUSES = Object.keys(MONITOR_STATUS_LABELS) as MonitorStatus[]
export const MONITOR_TYPES = Object.keys(MONITOR_TYPE_LABELS) as MonitorType[]

/** A status from untrusted text (URL, <select>), or undefined when it is not a known status. */
export function parseMonitorStatus(value: string | null | undefined): MonitorStatus | undefined {
  return MONITOR_STATUSES.find((status) => status === value)
}
