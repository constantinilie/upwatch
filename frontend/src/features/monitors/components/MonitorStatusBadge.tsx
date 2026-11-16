import { MONITOR_STATUS_LABELS } from '../constants'
import type { MonitorStatus } from '../types'
import styles from './MonitorStatusBadge.module.css'

/** A colored label for a monitor status. */
export function MonitorStatusBadge({ status }: { status: MonitorStatus }) {
  return (
    <span className={`${styles.badge} ${styles[status]}`}>{MONITOR_STATUS_LABELS[status]}</span>
  )
}
