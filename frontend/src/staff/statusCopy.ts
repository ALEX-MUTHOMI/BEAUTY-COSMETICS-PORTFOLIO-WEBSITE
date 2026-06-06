const STATUS_COPY: Record<string, string> = {
  payment_pending: 'Awaiting payment',
  success: 'Payment confirmed',
  paid: 'Payment confirmed',
  failed: 'Payment failed',
  payment_failed: 'Payment failed',
  manual_review: 'Needs attention',
  pending_review: 'Needs attention',
  confirmed: 'Booking confirmed',
  held: 'Awaiting customer payment',
  reschedule_requested: 'Reschedule requested',
  reschedule_held: 'Reschedule in progress',
  completed: 'Service completed',
  late: 'Client running late',
  no_show: 'Client did not attend',
  checked_in: 'Client checked in',
  in_progress: 'In service',
  not_issued: 'Receipt not issued yet',
  issued: 'Receipt ready',
  sent: 'Sent',
  retry_scheduled: 'Retry scheduled',
  failed_final: 'Needs attention',
  full_package: 'Full-package day',
  normal: 'Normal service day',
  closed: 'Closed',
}

const INTERNAL_WORDS = /\b(ledger|checkout session|correlation|provider payload|merchantrequest|checkoutrequest)\b/i

export function friendlyStatus(value?: string): string {
  const normalized = String(value || '').trim().toLowerCase()
  return STATUS_COPY[normalized] || 'Needs attention'
}

export function containsInternalJargon(value: string): boolean {
  return INTERNAL_WORDS.test(value)
}

export function safeDisplayText(value: unknown, fallback = 'Not available'): string {
  const text = String(value || '').replace(/[<>{}`]/g, '').replace(/\s+/g, ' ').trim()
  if (!text || INTERNAL_WORDS.test(text)) {
    return fallback
  }
  return text.slice(0, 120)
}

export function isPublicBookingReference(value: string): boolean {
  return /^[0-9a-f-]{32,36}$/i.test(value) || /^[A-Z0-9-]{6,64}$/i.test(value)
}
