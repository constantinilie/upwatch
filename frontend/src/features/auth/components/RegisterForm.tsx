import { useState, type FormEvent } from 'react'
import { toFormErrors } from '@/shared/api/errorMessages'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { TextField } from '@/shared/components/FormField'
import type { RegisterInput } from '../types'
import styles from './RegisterForm.module.css'

const EMPTY_FORM: RegisterInput = { email: '', password: '', first_name: '', last_name: '' }

// The inputs this form renders; API errors on any other field are shown above the form.
const FORM_FIELDS = Object.keys(EMPTY_FORM)

const PASSWORD_MISMATCH_MESSAGE = 'Parolele nu coincid.'

interface RegisterFormProps {
  /** The error of the last submit, if it failed. */
  error?: unknown
  isSubmitting: boolean
  onSubmit: (input: RegisterInput) => void
}

export function RegisterForm({ error, isSubmitting, onSubmit }: RegisterFormProps) {
  const [values, setValues] = useState(EMPTY_FORM)
  const [passwordConfirmation, setPasswordConfirmation] = useState('')
  // The confirmation is checked only in the browser: the API never receives it.
  const [hasPasswordMismatch, setHasPasswordMismatch] = useState(false)
  const { fieldErrors, formError } = toFormErrors(error, FORM_FIELDS)

  function update<K extends keyof RegisterInput>(field: K, value: RegisterInput[K]) {
    setValues((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const isMismatch = values.password !== passwordConfirmation
    setHasPasswordMismatch(isMismatch)
    if (!isMismatch) onSubmit(values)
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {formError && <Alert>{formError}</Alert>}

      <div className={styles.row}>
        <TextField
          label="Prenume"
          autoComplete="given-name"
          value={values.first_name}
          error={fieldErrors.first_name}
          onChange={(event) => update('first_name', event.target.value)}
        />
        <TextField
          label="Nume"
          autoComplete="family-name"
          value={values.last_name}
          error={fieldErrors.last_name}
          onChange={(event) => update('last_name', event.target.value)}
        />
      </div>
      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        required
        value={values.email}
        error={fieldErrors.email}
        onChange={(event) => update('email', event.target.value)}
      />
      <TextField
        label="Parolă"
        type="password"
        autoComplete="new-password"
        required
        hint="Minim 8 caractere; nu doar cifre și nu asemănătoare cu emailul."
        value={values.password}
        error={fieldErrors.password}
        onChange={(event) => update('password', event.target.value)}
      />
      <TextField
        label="Confirmă parola"
        type="password"
        autoComplete="new-password"
        required
        value={passwordConfirmation}
        error={hasPasswordMismatch ? PASSWORD_MISMATCH_MESSAGE : undefined}
        onChange={(event) => {
          setPasswordConfirmation(event.target.value)
          setHasPasswordMismatch(false)
        }}
      />

      <Button type="submit" isLoading={isSubmitting}>
        Creează cont
      </Button>
    </form>
  )
}
