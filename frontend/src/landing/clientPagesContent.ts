/** Public FAQ / 404 / booking status copy — short, plain, no dash punctuation. */

export const MELLIS_FLOWER_SRC = '/images/flower.png'

const DASH_AS_PUNCTUATION = /[—–]|\s-\s/
const JARGON =
  /\b(capacity|turnaround|idempotenc|observabilit|shared studio|submit your details|automatically)\b/i

export function assertPlainClientCopy(value: string): boolean {
  if (!value || typeof value !== 'string') return false
  if (DASH_AS_PUNCTUATION.test(value)) return false
  if (JARGON.test(value)) return false
  return true
}

export const FAQ_PAGE = {
  eyebrow: 'Help',
  title: 'Questions',
  lead: 'Booking and payment, answered simply.',
  asideEyebrow: 'Still need help?',
  asideCopy: 'Message or call us from the header.',
} as const

export const FAQ_ITEMS = [
  {
    id: 'faq-booking',
    q: 'How do I book?',
    a: 'Pick a package or treatment, choose a time, then pay with M-Pesa to confirm.',
  },
  {
    id: 'faq-confirmation',
    q: 'Where is my confirmation?',
    a: 'You see it after payment. Keep the page open until it says you are booked.',
  },
  {
    id: 'faq-mpesa',
    q: 'Missed the M-Pesa prompt?',
    a: 'Tap Resend on your confirmation page, then approve on your phone.',
  },
  {
    id: 'faq-limited',
    q: 'Why limited spots?',
    a: 'Each day has limited space. When it fills, that day closes online.',
  },
  {
    id: 'faq-change',
    q: 'Can I change my visit?',
    a: 'Message or call us and we will help you change it.',
  },
  {
    id: 'faq-contact',
    q: 'How do I reach you?',
    a: 'WhatsApp or call from the header, or email bookings@sheeaesthetics.co.ke.',
  },
] as const

export const NOT_FOUND_PAGE = {
  script: 'Shee',
  eyebrow: '404',
  title: 'Page not found',
  lead: 'This page is not here. Head home or book a visit.',
  faqLink: 'Need help? FAQ',
} as const

export const BOOKING_STATUS_COPY = {
  confirmationEyebrow: 'Booking confirmation',
  statusEyebrow: 'Booking status',
  confirmingHeadline: 'Confirming your booking',
  loadingHeadline: 'Loading your booking',
  confirmedConfirmationHeadline: 'You are booked',
  confirmedStatusHeadline: 'Booking confirmed',
  paymentFailedHeadline: 'Payment not completed',
  paymentPendingHeadline: 'Complete M-Pesa payment',
  heldHeadline: 'Finish payment to confirm',
  updateHeadline: 'Booking update',
  confirmingLead: 'Checking your payment now.',
  loadingLead: 'Loading your booking now.',
  confirmedLead: 'Thank you. We have your booking. A receipt email is on the way.',
  paymentFailedLead: 'No charge went through. Resend the M-Pesa prompt with the same phone.',
  paymentPendingLead: 'Approve the M-Pesa prompt on your phone. This page updates on its own.',
  updateLead: 'We are tracking your booking. You can leave and return later.',
  polling: 'Checking for payment updates',
  emptyReference: 'Pending',
  retryLabel: 'M-Pesa phone (same number as at booking)',
  retryButton: 'Resend M-Pesa prompt',
  retryingButton: 'Sending',
} as const

export function collectClientPageCopy(): string[] {
  return [
    FAQ_PAGE.eyebrow,
    FAQ_PAGE.title,
    FAQ_PAGE.lead,
    FAQ_PAGE.asideEyebrow,
    FAQ_PAGE.asideCopy,
    ...FAQ_ITEMS.flatMap((item) => [item.q, item.a]),
    NOT_FOUND_PAGE.script,
    NOT_FOUND_PAGE.eyebrow,
    NOT_FOUND_PAGE.title,
    NOT_FOUND_PAGE.lead,
    NOT_FOUND_PAGE.faqLink,
    ...Object.values(BOOKING_STATUS_COPY),
  ]
}
