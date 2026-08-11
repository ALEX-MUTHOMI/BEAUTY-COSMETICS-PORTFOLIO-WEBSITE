/**
 * Client FAQ Architecture — Categorized questions beauty salon clients actually want answered.
 * Provides data structures and category filtering for the interactive FAQ page.
 */

export interface ClientFaqItem {
  id: string
  category: 'packages' | 'payment' | 'location' | 'manage' | 'prep'
  categoryLabel: string
  question: string
  answer: string
}

export interface FaqCategoryOption {
  id: 'all' | 'packages' | 'payment' | 'location' | 'manage' | 'prep'
  label: string
}

export const FAQ_CATEGORIES: FaqCategoryOption[] = [
  { id: 'all', label: 'All Questions' },
  { id: 'packages', label: 'Packages & Days' },
  { id: 'payment', label: 'M-Pesa & Payment' },
  { id: 'location', label: 'Studio & Visit' },
  { id: 'manage', label: 'Reschedules & Receipts' },
  { id: 'prep', label: 'Prep & Arrival' },
]

export const CLIENT_FAQ_ITEMS: ClientFaqItem[] = [
  {
    id: 'faq-days',
    category: 'packages',
    categoryLabel: 'Packages & Days',
    question: 'When can I book full packages vs. single treatments?',
    answer:
      'Full spa packages (facial + waxing + massage + makeup) are offered on Tuesdays and Wednesdays only so we can reserve dedicated multi-hour studio blocks. Single treatments (individual facials, massage, waxing, or makeup) are available Monday and Thursday through Saturday.',
  },
  {
    id: 'faq-mpesa',
    category: 'payment',
    categoryLabel: 'M-Pesa & Payment',
    question: 'How does M-Pesa payment work and when is my slot locked?',
    answer:
      'When you choose a date and time, entering your M-Pesa phone number sends an STK prompt directly to your phone. Simply enter your PIN on your phone to complete payment. Your slot is locked instantly and your official PDF receipt is generated.',
  },
  {
    id: 'faq-location',
    category: 'location',
    categoryLabel: 'Studio & Visit',
    question: 'Where is Shee Aesthetics located in Meru Town?',
    answer:
      'We are located in Meru Town, Meru County, Kenya. Our studio provides a private, relaxing spa environment. You will receive precise direction pins and contact details in your instant booking confirmation.',
  },
  {
    id: 'faq-reschedule',
    category: 'manage',
    categoryLabel: 'Reschedules & Receipts',
    question: 'Can I change my appointment date or resend my receipt?',
    answer:
      'Yes. You can look up your booking at any time using your phone number or reference ID on the booking status page to view details, request a schedule shift, or download your PDF receipt.',
  },
  {
    id: 'faq-prep',
    category: 'prep',
    categoryLabel: 'Prep & Arrival',
    question: 'How early should I arrive and how do I prepare for my facial or makeup?',
    answer:
      'We recommend arriving 5 to 10 minutes before your scheduled start time. For facial treatments, no special prep is required. For event makeup sessions, arriving with clean, hydrated skin helps ensure a seamless long-lasting finish.',
  },
  {
    id: 'faq-account',
    category: 'payment',
    categoryLabel: 'M-Pesa & Payment',
    question: 'Do I need to create a password or account to book?',
    answer:
      'No account or password is required. You can book directly with your name, email, and phone number in less than 60 seconds.',
  },
]

export function filterFaqItems(
  items: ClientFaqItem[],
  selectedCategory: FaqCategoryOption['id'],
): ClientFaqItem[] {
  if (selectedCategory === 'all') return items
  return items.filter((item) => item.category === selectedCategory)
}

export function validateClientFaqItems(items: ClientFaqItem[]): boolean {
  if (!Array.isArray(items) || items.length === 0) return false
  return items.every(
    (item) =>
      typeof item.id === 'string' &&
      typeof item.question === 'string' &&
      item.question.length > 10 &&
      typeof item.answer === 'string' &&
      item.answer.length > 20,
  )
}
