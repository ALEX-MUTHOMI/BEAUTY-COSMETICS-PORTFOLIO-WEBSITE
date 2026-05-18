/**
 * Shared Book CTA for header / footer / sticky mobile bar.
 *
 * Prefers the visitor’s last in-progress book path (session handoff), else the
 * day-aware primary href (Nairobi schedule + optional live WhatsApp on Sunday).
 */
import { computed } from 'vue'
import { lastBookHref, SERVICES_BOOK_ENTRY } from '~/src/landing/bookingHandoff'
import { primaryBookHref, primaryBookIsExternal } from '~/src/landing/primaryBookHref'
import { useLandingContact } from './useLandingContact'

/**
 * Provides the main booking CTA logic for the landing page.
 * Prefers the user's last booking step or defaults to the primary booking flow.
 *
 * @returns An object with the booking URL, whether it is external, and contact info.
 */
export function useLandingBookCta() {
  const contact = useLandingContact()

  const bookHref = computed(() => {
    if (import.meta.client) {
      const last = lastBookHref()
      if (last && last !== SERVICES_BOOK_ENTRY) return last
    }
    return primaryBookHref(new Date(), {
      contactIsLive: contact.isLive.value,
      whatsappUrl: contact.whatsappUrl.value,
    })
  })

  const bookIsExternal = computed(() => primaryBookIsExternal(bookHref.value))

  return {
    bookHref,
    bookIsExternal,
    contact,
  }
}
