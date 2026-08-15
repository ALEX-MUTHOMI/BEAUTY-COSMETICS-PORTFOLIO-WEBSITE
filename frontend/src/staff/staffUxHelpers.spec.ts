import { describe, expect, it } from 'vitest'
import {
  clientStaffPasswordHint,
  dayCapacityBanner,
  firstNameFromDisplay,
  firstNameFromEmail,
  friendlyStatus,
  isPublicBookingReference,
  isReceiptIssued,
  mapStaffPasswordApiMessage,
  normalizePasswordHintInput,
  readStoredGreetName,
  receiptChipStatus,
  safeDisplayText,
  staffLocalDateIso,
  welcomeHeadline,
  writeStoredGreetName,
} from './staffUxHelpers'

describe('staffUxHelpers', () => {
  describe('staffLocalDateIso', () => {
    it('formats a date to YYYY-MM-DD in Africa/Nairobi timezone', () => {
      const d = new Date('2026-08-17T10:00:00Z')
      expect(staffLocalDateIso(d)).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('staff greetings', () => {
    it('extracts first name from display name or email', () => {
      expect(firstNameFromDisplay('Shee Wambui')).toBe('Shee')
      expect(firstNameFromEmail('shee.admin@sheeaesthetics.co.ke')).toBe('Shee')
    })

    it('generates welcome headline reacting to typed email', () => {
      expect(welcomeHeadline('Shee', 'jane@sheeaesthetics.co.ke')).toBe('Welcome back, Jane')
      expect(welcomeHeadline('Shee', '')).toBe('Welcome back, Shee')
      expect(welcomeHeadline('', '')).toBe('Welcome back')
    })

    it('reads and writes to storage safely', () => {
      const store: Record<string, string> = {}
      const mockStorage = {
        getItem: (k: string) => store[k] ?? null,
        setItem: (k: string, v: string) => { store[k] = v },
      } as Storage

      writeStoredGreetName('Faith', mockStorage)
      expect(readStoredGreetName(mockStorage)).toBe('Faith')
    })
  })

  describe('staffPasswordHints', () => {
    it('normalizes password hint input', () => {
      expect(normalizePasswordHintInput('P@ss-word123')).toBe('pssword123')
    })

    it('enforces minimum length and common password patterns', () => {
      expect(clientStaffPasswordHint('short')).toBe('Use at least 15 characters.')
      expect(clientStaffPasswordHint('password1234567890')).toBe('That password is too common.')
      expect(clientStaffPasswordHint('SuperSecureUniquePassphrase2026!')).toBeNull()
    })

    it('flags email fragments in password', () => {
      expect(clientStaffPasswordHint('sheeAdminLongSecret123!', { email: 'shee@beauty.ke' })).toBe(
        'Don’t use your name or email in the password.',
      )
    })

    it('maps server error messages to staff-friendly copy', () => {
      expect(mapStaffPasswordApiMessage('password too short, must have 15 characters')).toBe(
        'Use at least 15 characters.',
      )
      expect(mapStaffPasswordApiMessage('Token invalid or expired token_hash')).toBe(
        'This reset link is invalid or expired.',
      )
    })
  })

  describe('statusCopy & desensitization', () => {
    it('provides friendly desk status labels', () => {
      expect(friendlyStatus('payment_pending')).toBe('Awaiting payment')
      expect(friendlyStatus('paid')).toBe('Payment confirmed')
      expect(friendlyStatus('unknown_status')).toBe('Needs attention')
    })

    it('formats day capacity banners accurately', () => {
      expect(dayCapacityBanner('closed', 0)).toContain('Closed today')
      expect(dayCapacityBanner('full_package', 3)).toContain('Full-package day — up to 3 clients')
      expect(dayCapacityBanner('normal', 5)).toContain('Service day — up to 5 clients')
    })

    it('normalizes receipt statuses', () => {
      expect(receiptChipStatus('paid')).toBe('issued')
      expect(receiptChipStatus('not_issued')).toBe('not_issued')
      expect(isReceiptIssued('paid')).toBe(true)
      expect(isReceiptIssued('not_issued')).toBe(false)
    })

    it('scrubs internal backend jargon from customer-facing display', () => {
      expect(safeDisplayText('Booking confirmed for facial')).toBe('Booking confirmed for facial')
      expect(safeDisplayText('Internal ledger correlation failure')).toBe('Not available')
    })

    it('identifies valid public booking reference tokens', () => {
      expect(isPublicBookingReference('11111111-1111-4111-8111-111111111111')).toBe(true)
      expect(isPublicBookingReference('SHEE-2026-X9')).toBe(true)
      expect(isPublicBookingReference('a')).toBe(false)
    })
  })
})
