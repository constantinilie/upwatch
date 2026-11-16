import { useNavigate } from 'react-router'
import { useAuth } from '@/features/auth'
import { Card } from '@/shared/components/Card'
import { PageHeader } from '@/shared/components/PageHeader'
import { paths } from '@/shared/config/paths'
import { MonitorForm } from '../components/MonitorForm'
import { useCreateMonitor } from '../queries'
import type { MonitorInput } from '../types'

export function MonitorCreatePage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const createMonitor = useCreateMonitor()

  function handleSubmit(input: MonitorInput) {
    createMonitor.mutate(input, {
      onSuccess: (monitor) => navigate(paths.monitor(monitor.id)),
    })
  }

  return (
    <>
      <PageHeader
        title="Monitor nou"
        description="Adaugă un site pe care UpWatch să îl verifice."
      />
      <Card>
        <MonitorForm
          minIntervalSec={user?.plan?.min_check_interval_sec}
          error={createMonitor.error}
          isSubmitting={createMonitor.isPending}
          submitLabel="Adaugă monitor"
          onSubmit={handleSubmit}
          onCancel={() => navigate(paths.monitors)}
        />
      </Card>
    </>
  )
}
