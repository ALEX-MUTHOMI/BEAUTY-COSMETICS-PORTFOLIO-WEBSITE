/** Calendar date in Africa/Nairobi (desk business TZ), YYYY-MM-DD. */
export function staffLocalDateIso(now: Date = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Africa/Nairobi',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now)
}
