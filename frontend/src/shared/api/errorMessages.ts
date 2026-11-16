import { ApiError, type FieldErrors } from './ApiError'

const UNEXPECTED_ERROR_MESSAGE = 'A apărut o eroare neașteptată. Încearcă din nou.'

/** A message that is safe to show to the user for any thrown value. */
export function getErrorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : UNEXPECTED_ERROR_MESSAGE
}

export interface FormErrors {
  /** Shown under the matching fields. */
  fieldErrors: FieldErrors
  /** Shown above the form: a general error, or a field error the form has no input for. */
  formError?: string
}

/**
 * Splits a failed submit into field errors and one form-level message.
 *
 * `formFields` lists the inputs the form renders; an error on any other field (e.g. a server-side
 * rule on a field the form does not show) is moved to `formError`, so it is never silently lost.
 */
export function toFormErrors(error: unknown, formFields?: readonly string[]): FormErrors {
  if (error == null) return { fieldErrors: {} }
  if (!(error instanceof ApiError)) return { fieldErrors: {}, formError: getErrorMessage(error) }

  const fieldErrors: FieldErrors = {}
  const otherMessages: string[] = []
  for (const [field, message] of Object.entries(error.fieldErrors)) {
    if (!formFields || formFields.includes(field)) fieldErrors[field] = message
    else otherMessages.push(message)
  }

  const hasFieldErrors = Object.keys(fieldErrors).length > 0
  return {
    fieldErrors,
    formError: otherMessages[0] ?? (hasFieldErrors ? undefined : error.message),
  }
}
