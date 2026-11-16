import { useRouteError } from 'react-router'
import { Alert } from '@/shared/components/Alert'
import { LinkButton } from '@/shared/components/LinkButton'
import { paths } from '@/shared/config/paths'

/** Shown when a page throws while rendering, instead of the router's default error screen. */
export function RouteErrorPage() {
  const error = useRouteError()
  if (import.meta.env.DEV) console.error(error)

  return (
    <main style={{ padding: 'var(--space-6)' }}>
      <Alert>A apărut o eroare neașteptată. Reîncarcă pagina sau încearcă mai târziu.</Alert>
      <p>
        <LinkButton to={paths.monitors} variant="secondary">
          Mergi la monitoare
        </LinkButton>
      </p>
    </main>
  )
}
