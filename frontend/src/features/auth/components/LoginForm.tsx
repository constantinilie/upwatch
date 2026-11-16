import { useState, type FormEvent } from 'react'
import { toFormErrors } from '@/shared/api/errorMessages'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { TextField } from '@/shared/components/FormField'
import type { LoginCredentials } from '../types'
import styles from './LoginForm.module.css'

const FORM_FIELDS: readonly (keyof LoginCredentials)[] = ['email', 'password']

interface LoginFormProps {
  /** The error of the last submit, if it failed. */
  error?: unknown
  isSubmitting: boolean
  onSubmit: (credentials: LoginCredentials) => void
}

export function LoginForm({ error, isSubmitting, onSubmit }: LoginFormProps) {
  const [credentials, setCredentials] = useState<LoginCredentials>({ email: '', password: '' })
  const { fieldErrors, formError } = toFormErrors(error, FORM_FIELDS)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(credentials)
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {formError && <Alert>{formError}</Alert>}
      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        required
        value={credentials.email}
        error={fieldErrors.email}
        onChange={(event) => setCredentials({ ...credentials, email: event.target.value })}
      />
      <TextField
        label="Parolă"
        type="password"
        autoComplete="current-password"
        required
        value={credentials.password}
        error={fieldErrors.password}
        onChange={(event) => setCredentials({ ...credentials, password: event.target.value })}
      />
      <Button type="submit" isLoading={isSubmitting}>
        Intră în cont
      </Button>
    </form>
  )
}
