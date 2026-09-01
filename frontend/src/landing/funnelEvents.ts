/**
 * @module funnelEvents
 * Analytics tracking for funnel progression.
 */
/**
 * Minimal client funnel hooks for book→pay conversion measurement.
 * No PII — event names + optional string tags only.
 */
export type FunnelEventName =
  | 'cta_book_click'
  | 'slot_selected'
  | 'checkout_continue'
  | 'stk_sent'
  | 'wa_click'
  | 'gallery_open'
  | 'book_again_click'
  | 'welcome_back_dismiss'

export function trackFunnelEvent(
  name: FunnelEventName,
  detail?: Record<string, string | number | boolean | undefined>,
): void {
  if (!import.meta.client) return
  try {
    const payload = { name, t: Date.now(), ...detail }
    window.dispatchEvent(new CustomEvent('shee-funnel', { detail: payload }))
    if (typeof console !== 'undefined' && console.debug) {
      console.debug('[shee-funnel]', payload)
    }
  } catch {
    /* ignore */
  }
}
