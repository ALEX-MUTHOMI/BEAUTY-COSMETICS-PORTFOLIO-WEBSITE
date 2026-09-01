/**
 * Module: clientPagesContent
 * Content structures for client pages.
 */
/** Public FAQ / 404 / 503 / Contact / Legal copy — natural, warm, human Kenyan salon copy. */

export const MELLIS_FLOWER_SRC = '/images/flower.png'

const DASH_AS_PUNCTUATION = /[—–]|\s-\s/
const JARGON =
  /\b(capacity|turnaround|idempotenc|observabilit|shared studio|submit your details|automatically|sanctuary standards|hospital-grade|concierge desk|knowledge base)\b/i

export function assertPlainClientCopy(value: string): boolean {
  if (!value || typeof value !== 'string') return false
  if (DASH_AS_PUNCTUATION.test(value)) return false
  if (JARGON.test(value)) return false
  return true
}

export const NOT_FOUND_PAGE = {
  script: 'Shee',
  eyebrow: '404',
  title: 'Page not found',
  lead: 'We could not find the page you are looking for. Let us get you back on track.',
  faqLink: 'View FAQ',
} as const

export const SERVER_ERROR_PAGE = {
  script: 'Shee',
  eyebrow: 'Notice',
  title: 'Connection interrupted',
  lead: 'Something went wrong while loading this page. Please refresh or message us on WhatsApp.',
  retryButton: 'Try again',
  whatsappButton: 'Message on WhatsApp',
  phoneButton: 'Call studio',
  supportLink: 'Contact & Support',
} as const

export const CUSTOMER_SUPPORT_PAGE = {
  script: 'Shee',
  eyebrow: 'Contact',
  title: 'Get in touch',
  lead: 'Questions about your visit, treatments, or M-Pesa payment? We are here to help.',
  studioTitle: 'Studio location & hours',
  studioAddress: 'Meru Town, Meru County, Kenya',
  packageDays: 'Tuesday and Wednesday: Full packages only',
  treatmentDays: 'Monday, Thursday to Saturday: Single treatments',
  sundayNotice: 'Sunday: Closed',
  email: 'bookings@sheeaesthetics.co.ke',
  phoneDisplay: '+254 712 345 678',
  phoneE164: '+254712345678',
  whatsappE164: '254712345678',
} as const

export interface FaqItem {
  id: string
  category: 'all' | 'booking' | 'packages' | 'visit' | 'changes'
  categoryLabel: string
  q: string
  a: string
}

export const FAQ_PAGE = {
  eyebrow: 'Help',
  title: 'Frequently asked questions',
  lead: 'Common questions about booking, payments, and appointments in Meru Town.',
  asideEyebrow: 'Need something else?',
  asideCopy: 'Call or message us on WhatsApp and we will assist you directly.',
} as const

export const FAQ_CATEGORIES = [
  { id: 'all', label: 'All' },
  { id: 'booking', label: 'Booking & M-Pesa' },
  { id: 'packages', label: 'Packages vs Treatments' },
  { id: 'visit', label: 'Studio & Location' },
  { id: 'changes', label: 'Rescheduling & Help' },
] as const

export const FAQ_ITEMS: FaqItem[] = [
  {
    id: 'faq-booking',
    category: 'booking',
    categoryLabel: 'Booking & M-Pesa',
    q: 'How do I book an appointment?',
    a: 'Select your treatment or package, pick an available date and time slot, and enter your M-Pesa phone number to complete payment.',
  },
  {
    id: 'faq-confirmation',
    category: 'booking',
    categoryLabel: 'Booking & M-Pesa',
    q: 'How do I know my booking is confirmed?',
    a: 'Once your M-Pesa payment is approved, your confirmation screen appears immediately and a PDF receipt is sent to your email.',
  },
  {
    id: 'faq-mpesa',
    category: 'booking',
    categoryLabel: 'Booking & M-Pesa',
    q: 'What if the M-Pesa prompt does not show up?',
    a: 'Make sure your phone is unlocked and has network. Tap Resend Prompt on your screen using the same phone number.',
  },
  {
    id: 'faq-packages-days',
    category: 'packages',
    categoryLabel: 'Packages vs Treatments',
    q: 'Why are full packages only on Tuesdays and Wednesdays?',
    a: 'Full packages include multi-service sessions that take several hours. Reserving Tuesdays and Wednesdays lets us give each client dedicated care without rush.',
  },
  {
    id: 'faq-single-days',
    category: 'packages',
    categoryLabel: 'Packages vs Treatments',
    q: 'What treatments can I book on other days?',
    a: 'On Mondays, Thursdays, Fridays, and Saturdays, you can book individual facials, body massage, waxing, or makeup sessions.',
  },
  {
    id: 'faq-reschedule',
    category: 'changes',
    categoryLabel: 'Rescheduling & Help',
    q: 'Can I reschedule if my plans change?',
    a: 'Yes. Send us a message on WhatsApp or call at least 24 hours before your appointment and we will help you move your slot.',
  },
  {
    id: 'faq-location',
    category: 'visit',
    categoryLabel: 'Studio & Location',
    q: 'Where in Meru Town is the studio?',
    a: 'We are located in Meru Town. Exact building directions and a Google Maps pin are included in your booking confirmation.',
  },
]

export interface PolicySection {
  id: string
  title: string
  points: string[]
}

export const TERMS_SECTIONS: PolicySection[] = [
  {
    id: 'punctuality',
    title: 'Arrival & Punctuality',
    points: [
      'Please arrive 5 to 10 minutes before your appointment start time.',
      'If you are running late, please send us a quick WhatsApp message so we can prepare.',
      'Arrivals later than 15 minutes may require shortening the treatment time so the next guest is not delayed.',
    ],
  },
  {
    id: 'schedule',
    title: 'Booking Schedule & Package Days',
    points: [
      'Full Packages (multi-treatment bundles) are available on Tuesdays and Wednesdays only.',
      'Single treatments (facials, massage, waxing, makeup) are available Monday, Thursday, Friday, and Saturday.',
      'The studio is closed on Sundays.',
    ],
  },
  {
    id: 'payment',
    title: 'M-Pesa Payments & Receipts',
    points: [
      'All appointments are confirmed upon completing M-Pesa payment online.',
      'Unpaid temporary holds are released back to the calendar after 15 minutes.',
      'An official PDF receipt is emailed immediately once payment goes through.',
    ],
  },
  {
    id: 'rescheduling',
    title: 'Reschedules & Cancellations',
    points: [
      'You can reschedule your visit with at least 24 hours advance notice via WhatsApp or phone.',
      'Cancellations made with less than 24 hours notice may forfeit the booking hold.',
      'If Shee Aesthetics needs to reschedule due to an emergency, we will offer you priority rebooking or a full refund.',
    ],
  },
  {
    id: 'hygiene',
    title: 'Health & Studio Etiquette',
    points: [
      'Please inform your practitioner of any skin allergies, pregnancy, or medical sensitivities before treatment begins.',
      'All tools and surfaces are thoroughly disinfected between appointments.',
      'We maintain a quiet, calm space. Please set mobile phones to silent mode during your visit.',
    ],
  },
]

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
    SERVER_ERROR_PAGE.title,
    SERVER_ERROR_PAGE.lead,
    CUSTOMER_SUPPORT_PAGE.title,
    CUSTOMER_SUPPORT_PAGE.lead,
    ...Object.values(BOOKING_STATUS_COPY),
  ]
}

