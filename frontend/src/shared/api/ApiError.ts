/** Body of an error response from Django REST Framework. */
type ErrorBody = Record<string, unknown> | null

export type FieldErrors = Record<string, string>

const NETWORK_ERROR_MESSAGE =
  'Nu s-a putut contacta serverul. Verifică conexiunea și încearcă din nou.'

/** A failed API call: keeps the HTTP status and the response body. Status 0 means no response at all. */
export class ApiError extends Error {
  readonly status: number
  readonly body: ErrorBody

  constructor(status: number, body: ErrorBody, message?: string) {
    super(message ?? ApiError.messageFrom(body) ?? `Cererea a eșuat (HTTP ${status}).`)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }

  /** The server could not be reached (offline, DNS, CORS, server down). */
  static network() {
    return new ApiError(0, null, NETWORK_ERROR_MESSAGE)
  }

  get isNetworkError() {
    return this.status === 0
  }

  /** 4xx: the request itself is wrong, so retrying it will not help. */
  get isClientError() {
    return this.status >= 400 && this.status < 500
  }

  /** Errors per field ({"url": ["..."]} → {url: "..."}), without `detail` and `non_field_errors`. */
  get fieldErrors(): FieldErrors {
    const errors: FieldErrors = {}
    for (const [field, value] of Object.entries(this.body ?? {})) {
      if (field === 'detail' || field === 'non_field_errors' || field === 'code') continue
      const message = firstMessage(value)
      if (message) errors[field] = message
    }
    return errors
  }

  private static messageFrom(body: ErrorBody): string | undefined {
    return firstMessage(body?.detail) ?? firstMessage(body?.non_field_errors)
  }
}

function firstMessage(value: unknown): string | undefined {
  if (typeof value === 'string') return value
  if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
  return undefined
}
