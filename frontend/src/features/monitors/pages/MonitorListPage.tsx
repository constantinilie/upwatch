import { useSearchParams } from 'react-router'
import { useAuth } from '@/features/auth'
import { getErrorMessage } from '@/shared/api/errorMessages'
import { Alert } from '@/shared/components/Alert'
import { LinkButton } from '@/shared/components/LinkButton'
import { paths } from '@/shared/config/paths'
import { PageHeader } from '@/shared/components/PageHeader'
import { Spinner } from '@/shared/components/Spinner'
import { useDebouncedValue } from '@/shared/hooks/useDebouncedValue'
import { MonitorFilterBar } from '../components/MonitorFilterBar'
import { MonitorTable } from '../components/MonitorTable'
import { parseMonitorStatus } from '../constants'
import { useMonitors } from '../queries'

export function MonitorListPage() {
  const { user } = useAuth()
  // Filters live in the URL, so a filtered page can be reloaded or shared as a link.
  const [searchParams, setSearchParams] = useSearchParams()
  const search = searchParams.get('search') ?? ''
  const debouncedSearch = useDebouncedValue(search.trim())
  const status = parseMonitorStatus(searchParams.get('status'))

  const {
    data: monitors,
    isPending,
    isError,
    error,
    isFetching,
  } = useMonitors({
    status,
    search: debouncedSearch || undefined,
  })

  function setFilter(name: 'status' | 'search', value: string | undefined) {
    // replace: typing in the search box must not add one browser history entry per key
    setSearchParams(
      (params) => {
        if (value) params.set(name, value)
        else params.delete(name)
        return params
      },
      { replace: true },
    )
  }

  // Plan usage is meaningful only for the full, unfiltered list.
  const plan = user?.plan
  const usage =
    plan && monitors && !status && !debouncedSearch
      ? `${monitors.length} din ${plan.max_monitors} monitoare · plan ${plan.name}`
      : plan && `Plan ${plan.name}`

  return (
    <>
      <PageHeader
        title="Monitoarele mele"
        description={usage}
        actions={<LinkButton to={paths.newMonitor}>Adaugă monitor</LinkButton>}
      />

      <MonitorFilterBar
        status={status}
        search={search}
        onStatusChange={(next) => setFilter('status', next)}
        onSearchChange={(next) => setFilter('search', next)}
      />

      {isPending ? (
        <Spinner />
      ) : isError ? (
        <Alert>{getErrorMessage(error)}</Alert>
      ) : monitors.length === 0 ? (
        <Alert tone="info">Nu ai niciun monitor care să corespundă filtrelor.</Alert>
      ) : (
        <div aria-busy={isFetching}>
          <MonitorTable monitors={monitors} />
        </div>
      )}
    </>
  )
}
