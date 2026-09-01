/**
 * @module textGuards
 * Provides validation and sanitization for text input.
 */
/**
 * @module textGuards
 * Provides validation and sanitization for text input.
 */
const UNSAFE_BOOK_TOKEN_CHARS = new Set(['<', '>', '"', "'", '`'])

/** Control chars, whitespace, and delimiter injection markers in decoded handoff tokens. */
export function containsUnsafeDecodedToken(value: string): boolean {
  for (const ch of value) {
    if (UNSAFE_BOOK_TOKEN_CHARS.has(ch)) return true
    const code = ch.charCodeAt(0)
    if (code < 0x20 || code === 0x7f) return true
    if (/\s/.test(ch)) return true
  }
  return false
}

/** Replace control characters before displaying API copy. */
export function stripControlCharsForDisplay(value: string): string {
  let out = ''
  for (const ch of value) {
    const code = ch.charCodeAt(0)
    out += code < 0x20 || code === 0x7f ? ' ' : ch
  }
  return out
}
