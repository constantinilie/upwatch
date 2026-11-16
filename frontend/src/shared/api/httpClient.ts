import { env } from '@/shared/config/env'
import { ApiError } from './ApiError'
import { tokenStorage } from './tokenStorage'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

type QueryParams = Record<string, string | undefined>

interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  query?: QueryParams
  /** Cancels the request (React Query passes one, so leaving a page aborts its pending calls). */
  signal?: AbortSignal
  /** false for public endpoints (login, register, refresh), which must not send a token. */
  auth?: boolean
}

/** Options a caller may pass; method and body are set by the `api` helpers. */
export type CallOptions = Omit<RequestOptions, 'method' | 'body'>

type SessionExpiredListener = () => void

const sessionExpiredListeners = new Set<SessionExpiredListener>()

/** Notifies when the session can no longer be renewed (refresh token expired). Returns the unsubscribe function. */
export function onSessionExpired(listener: SessionExpiredListener) {
  sessionExpiredListeners.add(listener)
  return () => {
    sessionExpiredListeners.delete(listener)
  }
}

/** A call to the UpWatch API: adds the JWT and retries once after a successful token refresh. */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true } = options
  let response = await send(path, options)

  if (response.status === 401 && auth && (await refreshAccessToken())) {
    response = await send(path, options)
  }
  if (response.status === 401 && auth) {
    expireSession()
  }
  return parse<T>(response)
}

export const api = {
  get: <T>(path: string, options?: CallOptions) => request<T>(path, options),
  post: <T>(path: string, body: unknown, options?: CallOptions) =>
    request<T>(path, { ...options, method: 'POST', body }),
  put: <T>(path: string, body: unknown, options?: CallOptions) =>
    request<T>(path, { ...options, method: 'PUT', body }),
}

async function send(
  path: string,
  { method = 'GET', body, query, signal, auth = true }: RequestOptions,
) {
  const headers = new Headers({ Accept: 'application/json' })
  if (body !== undefined) headers.set('Content-Type', 'application/json')

  const accessToken = tokenStorage.getAccess()
  if (auth && accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  try {
    return await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    })
  } catch (error) {
    // An aborted request is not a failure: let React Query see the original AbortError.
    if (signal?.aborted) throw error
    throw ApiError.network()
  }
}

function buildUrl(path: string, query: QueryParams | undefined) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value) params.set(key, value)
  }
  const search = params.toString()
  return `${env.apiBaseUrl}${path}${search ? `?${search}` : ''}`
}

async function parse<T>(response: Response): Promise<T> {
  const isJson = response.headers.get('Content-Type')?.includes('application/json')
  const data: unknown = isJson ? await response.json() : null

  if (!response.ok) {
    throw new ApiError(response.status, data as Record<string, unknown> | null)
  }
  return data as T
}

// Several requests can get a 401 at the same time; they all wait for the same refresh.
let refreshInFlight: Promise<boolean> | null = null

function refreshAccessToken(): Promise<boolean> {
  const refresh = tokenStorage.getRefresh()
  if (!refresh) return Promise.resolve(false)

  refreshInFlight ??= send('/auth/token/refresh/', {
    method: 'POST',
    body: { refresh },
    auth: false,
  })
    .then(async (response) => {
      if (!response.ok) return false
      const { access } = (await response.json()) as { access: string }
      tokenStorage.setAccess(access)
      return true
    })
    .catch(() => false)
    .finally(() => {
      refreshInFlight = null
    })

  return refreshInFlight
}

function expireSession() {
  tokenStorage.clear()
  sessionExpiredListeners.forEach((listener) => listener())
}
