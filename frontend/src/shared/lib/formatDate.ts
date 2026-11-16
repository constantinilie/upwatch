const dateTimeFormat = new Intl.DateTimeFormat('ro-RO', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function formatDateTime(value: string | null, fallback = '—') {
  return value ? dateTimeFormat.format(new Date(value)) : fallback
}
