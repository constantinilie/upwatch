import { Alert } from '@/shared/components/Alert'
import { LinkButton } from '@/shared/components/LinkButton'
import { paths } from '@/shared/config/paths'

export function NotFoundPage() {
  return (
    <>
      <Alert tone="info">Pagina nu există.</Alert>
      <p>
        <LinkButton to={paths.monitors} variant="secondary">
          Mergi la monitoare
        </LinkButton>
      </p>
    </>
  )
}
