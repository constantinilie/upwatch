import { useState, type FormEvent } from 'react'
import { toFormErrors } from '@/shared/api/errorMessages'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { SelectField, TextField } from '@/shared/components/FormField'
import { HTTP_METHODS, MONITOR_TYPE_LABELS, MONITOR_TYPES } from '../constants'
import type { HttpMethod, MonitorInput, MonitorType } from '../types'
import styles from './MonitorForm.module.css'

const TYPE_OPTIONS = MONITOR_TYPES.map((type) => ({
  value: type,
  label: MONITOR_TYPE_LABELS[type],
}))
const METHOD_OPTIONS = HTTP_METHODS.map((method) => ({ value: method, label: method }))

const EMPTY_MONITOR: MonitorInput = {
  name: '',
  url: '',
  monitor_type: 'http',
  keyword: '',
  http_method: 'GET',
  interval_sec: 300,
}

// The inputs this form renders; API errors on any other field are shown above the form.
const FORM_FIELDS = Object.keys(EMPTY_MONITOR)

interface MonitorFormProps {
  initialValues?: MonitorInput
  /** The minimum interval of the client's plan (shown as a hint; the API enforces the rule). */
  minIntervalSec?: number
  /** The error of the last submit, if it failed. */
  error?: unknown
  isSubmitting: boolean
  submitLabel: string
  onSubmit: (input: MonitorInput) => void
  onCancel: () => void
}

/** Create / edit form for a monitor; the page decides what happens on submit. */
export function MonitorForm({
  initialValues = EMPTY_MONITOR,
  minIntervalSec,
  error,
  isSubmitting,
  submitLabel,
  onSubmit,
  onCancel,
}: MonitorFormProps) {
  const [values, setValues] = useState(initialValues)
  const { fieldErrors, formError } = toFormErrors(error, FORM_FIELDS)

  function update<K extends keyof MonitorInput>(field: K, value: MonitorInput[K]) {
    setValues((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit(values)
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {formError && <Alert>{formError}</Alert>}

      <TextField
        label="Nume"
        required
        value={values.name}
        error={fieldErrors.name}
        onChange={(event) => update('name', event.target.value)}
      />
      <TextField
        label="URL"
        type="url"
        required
        placeholder="https://exemplu.ro"
        value={values.url}
        error={fieldErrors.url}
        onChange={(event) => update('url', event.target.value)}
      />

      <div className={styles.row}>
        <SelectField
          label="Tip monitor"
          options={TYPE_OPTIONS}
          value={values.monitor_type}
          error={fieldErrors.monitor_type}
          onChange={(event) => update('monitor_type', event.target.value as MonitorType)}
        />
        <SelectField
          label="Metodă HTTP"
          options={METHOD_OPTIONS}
          value={values.http_method}
          error={fieldErrors.http_method}
          onChange={(event) => update('http_method', event.target.value as HttpMethod)}
        />
      </div>

      {values.monitor_type === 'keyword' && (
        <TextField
          label="Keyword"
          required
          hint="Textul care trebuie să apară în pagină."
          value={values.keyword}
          error={fieldErrors.keyword}
          onChange={(event) => update('keyword', event.target.value)}
        />
      )}

      <TextField
        label="Interval verificare (secunde)"
        type="number"
        min={minIntervalSec}
        hint={minIntervalSec ? `Planul tău permite minim ${minIntervalSec} de secunde.` : undefined}
        value={values.interval_sec}
        error={fieldErrors.interval_sec}
        onChange={(event) => update('interval_sec', event.target.valueAsNumber)}
      />

      <div className={styles.actions}>
        <Button type="submit" isLoading={isSubmitting}>
          {submitLabel}
        </Button>
        <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>
          Renunță
        </Button>
      </div>
    </form>
  )
}
