export type MonitorStatus = 'pending' | 'up' | 'down' | 'paused'
export type MonitorType = 'http' | 'keyword' | 'ssl'
export type HttpMethod = 'GET' | 'HEAD' | 'POST'

/** Response of GET /monitors/ and GET /monitors/<id>/ (MonitorSummary in the API). */
export interface MonitorSummary {
  id: number
  name: string
  url: string
  type: MonitorType
  status: MonitorStatus
  is_paused: boolean
  last_checked_at: string | null
  incident_count: number
}

/** Body of POST /monitors/ and PUT /monitors/<id>/. */
export interface MonitorInput {
  name: string
  url: string
  monitor_type: MonitorType
  keyword: string
  http_method: HttpMethod
  interval_sec: number
}

/** Response of POST / PUT: the full monitor, including its configuration. */
export interface Monitor extends MonitorInput {
  id: number
  expected_status_code: number
  timeout_sec: number
  is_active: boolean
  status: MonitorStatus
  incident_count: number
  last_checked_at: string | null
  created_at: string
  updated_at: string
}

/** List filters; they live in the URL (see MonitorListPage). */
export interface MonitorFilters {
  status?: MonitorStatus
  search?: string
}
