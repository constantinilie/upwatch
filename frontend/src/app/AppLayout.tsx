import { NavLink, Outlet } from 'react-router'
import { useAuth } from '@/features/auth'
import { Button } from '@/shared/components/Button'
import { paths } from '@/shared/config/paths'
import styles from './AppLayout.module.css'

/** The frame of every page for a logged-in client: top bar + the current route. */
export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <div className={styles.inner}>
          <NavLink to={paths.monitors} className={styles.brand}>
            UpWatch
          </NavLink>
          <nav className={styles.nav} aria-label="Navigare principală">
            <NavLink to={paths.monitors} end className={navLinkClass}>
              Monitoare
            </NavLink>
          </nav>
          <div className={styles.account}>
            <span className={styles.email}>{user?.email}</span>
            <Button variant="secondary" onClick={logout}>
              Ieșire
            </Button>
          </div>
        </div>
      </header>
      <main className={styles.inner}>
        <Outlet />
      </main>
    </div>
  )
}

function navLinkClass({ isActive }: { isActive: boolean }) {
  return isActive ? `${styles.link} ${styles.active}` : styles.link
}
