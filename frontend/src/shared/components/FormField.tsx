import { useId, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes } from 'react'
import styles from './FormField.module.css'

interface FieldShellProps {
  id: string
  label: string
  error?: string
  hint?: string
  children: ReactNode
}

function FieldShell({ id, label, error, hint, children }: FieldShellProps) {
  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
      </label>
      {children}
      {error ? (
        <p id={`${id}-error`} className={styles.error} role="alert">
          {error}
        </p>
      ) : (
        hint && (
          <p id={`${id}-hint`} className={styles.hint}>
            {hint}
          </p>
        )
      )}
    </div>
  )
}

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  hint?: string
}

export function TextField({ label, error, hint, id, ...props }: TextFieldProps) {
  const generatedId = useId()
  const fieldId = id ?? generatedId

  return (
    <FieldShell id={fieldId} label={label} error={error} hint={hint}>
      <input
        id={fieldId}
        className={styles.control}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy(fieldId, error, hint)}
        {...props}
      />
    </FieldShell>
  )
}

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string
  options: ReadonlyArray<{ value: string; label: string }>
  error?: string
  hint?: string
}

export function SelectField({ label, options, error, hint, id, ...props }: SelectFieldProps) {
  const generatedId = useId()
  const fieldId = id ?? generatedId

  return (
    <FieldShell id={fieldId} label={label} error={error} hint={hint}>
      <select
        id={fieldId}
        className={styles.control}
        aria-invalid={Boolean(error)}
        aria-describedby={describedBy(fieldId, error, hint)}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </FieldShell>
  )
}

function describedBy(id: string, error?: string, hint?: string) {
  if (error) return `${id}-error`
  if (hint) return `${id}-hint`
  return undefined
}
