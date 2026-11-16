import type { ReactNode } from 'react'
import styles from './Card.module.css'

export function Card({ children }: { children: ReactNode }) {
  return <section className={styles.card}>{children}</section>
}
