import type { ReactNode } from 'react'
import styles from './Alert.module.css'

interface AlertProps {
  tone?: 'error' | 'info'
  children: ReactNode
}

export function Alert({ tone = 'error', children }: AlertProps) {
  return (
    <div className={`${styles.alert} ${styles[tone]}`} role={tone === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  )
}
