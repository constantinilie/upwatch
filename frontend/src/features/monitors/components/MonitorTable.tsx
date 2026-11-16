import { Link } from 'react-router'
import { paths } from '@/shared/config/paths'
import { formatDateTime } from '@/shared/lib/formatDate'
import { MONITOR_TYPE_LABELS } from '../constants'
import type { MonitorSummary } from '../types'
import { MonitorStatusBadge } from './MonitorStatusBadge'
import styles from './MonitorTable.module.css'

/** The monitor list; scrolls horizontally on narrow screens. */
export function MonitorTable({ monitors }: { monitors: MonitorSummary[] }) {
  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Nume</th>
            <th>Tip</th>
            <th>Status</th>
            <th>Ultima verificare</th>
            <th className={styles.numeric}>Incidente</th>
          </tr>
        </thead>
        <tbody>
          {monitors.map((monitor) => (
            <tr key={monitor.id}>
              <td>
                <Link to={paths.monitor(monitor.id)} className={styles.name}>
                  {monitor.name}
                </Link>
                <span className={styles.url}>{monitor.url}</span>
              </td>
              <td>{MONITOR_TYPE_LABELS[monitor.type]}</td>
              <td>
                <MonitorStatusBadge status={monitor.status} />
              </td>
              <td>{formatDateTime(monitor.last_checked_at, 'Niciodată')}</td>
              <td className={styles.numeric}>{monitor.incident_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
