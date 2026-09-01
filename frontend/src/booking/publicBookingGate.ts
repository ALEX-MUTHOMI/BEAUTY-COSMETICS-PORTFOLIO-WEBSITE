/**
 * Public booking kill switch. Unset / anything other than true is fail-closed.
 */
export function isPublicBookingEnabled(flag: unknown): boolean {
  return flag === true || flag === 'true'
}
