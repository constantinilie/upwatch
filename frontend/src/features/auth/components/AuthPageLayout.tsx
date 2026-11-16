import type { ReactNode } from 'react'
import { Card } from '@/shared/components/Card'
import styles from './AuthPageLayout.module.css'

interface AuthPageLayoutProps {
  subtitle: string
  children: ReactNode
  /** Shown under the card, e.g. the link between login and sign-up. */
  footer?: ReactNode
}

/** The centered card shared by the public auth pages (login, sign-up). */
export function AuthPageLayout({ subtitle, children, footer }: AuthPageLayoutProps) {
  return (
    <main className={styles.page}>
      <div className={styles.content}>
        <Card>
          <h1 className={styles.title}>UpWatch</h1>
          <p className={styles.subtitle}>{subtitle}</p>
          {children}
        </Card>
        {footer && <p className={styles.footer}>{footer}</p>}
      </div>
    </main>
  )
}
