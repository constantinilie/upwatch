import { useParams } from 'react-router'
import { ApiError } from '@/shared/api/ApiError'
import { getErrorMessage } from '@/shared/api/errorMessages'
import { Alert } from '@/shared/components/Alert'
import { Card } from '@/shared/components/Card'
import { LinkButton } from '@/shared/components/LinkButton'
import { PageHeader } from '@/shared/components/PageHeader'
import { Spinner } from '@/shared/components/Spinner'
import { paths } from '@/shared/config/paths'
import { formatDateTime } from '@/shared/lib/formatDate'
import { MonitorStatusBadge } from '../components/MonitorStatusBadge'
import { MONITOR_TYPE_LABELS } from '../constants'
import { useMonitor } from '../queries'
import styles from './MonitorDetailPage.module.css'

const NOT_FOUND_MESSAGE = 'Monitorul nu există sau nu îți aparține.'

export function MonitorDetailPage() {
  const id = Number(useParams().id)

  // A malformed id (e.g. /monitors/abc) is answered here, without asking the API.
  if (!Number.isInteger(id) || id <= 0) return <MonitorLoadError message={NOT_FOUND_MESSAGE} />
  return <MonitorDetails id={id} />
}

function MonitorDetails({ id }: { id: number }) {
  const { data: monitor, isPending, isError, error } = useMonitor(id)

  if (isPending) return <Spinner />
  if (isError) {
    const notFound = error instanceof ApiError && error.status === 404
    return <MonitorLoadError message={notFound ? NOT_FOUND_MESSAGE : getErrorMessage(error)} />
  }

  return (
    <>
      <PageHeader
        title={monitor.name}
        description={monitor.url}
        actions={
          <LinkButton to={paths.monitors} variant="secondary">
            Înapoi
          </LinkButton>
        }
      />
      <Card>
        <dl className={styles.details}>
          <dt>Status</dt>
          <dd>
            <MonitorStatusBadge status={monitor.status} />
          </dd>
          <dt>Tip</dt>
          <dd>{MONITOR_TYPE_LABELS[monitor.type]}</dd>
          <dt>Pe pauză</dt>
          <dd>{monitor.is_paused ? 'Da' : 'Nu'}</dd>
          <dt>Ultima verificare</dt>
          <dd>{formatDateTime(monitor.last_checked_at, 'Niciodată')}</dd>
          <dt>Incidente</dt>
          <dd>{monitor.incident_count}</dd>
        </dl>
      </Card>
    </>
  )
}

function MonitorLoadError({ message }: { message: string }) {
  return (
    <>
      <Alert>{message}</Alert>
      <p>
        <LinkButton to={paths.monitors} variant="secondary">
          Înapoi la monitoare
        </LinkButton>
      </p>
    </>
  )
}
