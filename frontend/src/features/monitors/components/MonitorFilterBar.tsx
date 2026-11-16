import { SelectField, TextField } from '@/shared/components/FormField'
import { MONITOR_STATUS_LABELS, MONITOR_STATUSES, parseMonitorStatus } from '../constants'
import type { MonitorStatus } from '../types'
import styles from './MonitorFilterBar.module.css'

const STATUS_OPTIONS = [
  { value: '', label: 'Toate' },
  ...MONITOR_STATUSES.map((status) => ({ value: status, label: MONITOR_STATUS_LABELS[status] })),
]

interface MonitorFilterBarProps {
  status: MonitorStatus | undefined
  search: string
  onStatusChange: (status: MonitorStatus | undefined) => void
  onSearchChange: (search: string) => void
}

/** Search and status filter above the monitor list; the page owns the values. */
export function MonitorFilterBar({
  status,
  search,
  onStatusChange,
  onSearchChange,
}: MonitorFilterBarProps) {
  return (
    <div className={styles.bar}>
      <TextField
        label="Caută"
        type="search"
        placeholder="Nume sau URL"
        value={search}
        onChange={(event) => onSearchChange(event.target.value)}
      />
      <SelectField
        label="Status"
        options={STATUS_OPTIONS}
        value={status ?? ''}
        onChange={(event) => onStatusChange(parseMonitorStatus(event.target.value))}
      />
    </div>
  )
}
