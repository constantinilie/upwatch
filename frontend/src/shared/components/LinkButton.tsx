import { Link, type LinkProps } from 'react-router'
import styles from './Button.module.css'

interface LinkButtonProps extends LinkProps {
  variant?: 'primary' | 'secondary'
}

/** A navigation link styled as a button. */
export function LinkButton({ variant = 'primary', className, ...props }: LinkButtonProps) {
  return (
    <Link
      className={[styles.button, styles[variant], className].filter(Boolean).join(' ')}
      {...props}
    />
  )
}
