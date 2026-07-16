import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffDashboard from './StaffDashboard.vue'
import StaffLoginPanel from './StaffLoginPanel.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffReschedulesWorkspace from './StaffReschedulesWorkspace.vue'
import StaffSettingsSecurity from './StaffSettingsSecurity.vue'
import { staffLocalDateIso } from './staffLocalDate'
import { clientStaffPasswordHint, mapStaffPasswordApiMessage } from './staffPasswordHints'
import { dayCapacityBanner } from './statusCopy'

vi.mock('./staffAuth', async () => {
  const actual = await vi.importActual<typeof import('./staffAuth')>('./staffAuth')
  return {
    ...actual,
    fetchStaffOAuthProviders: vi.fn<() => Promise<{ google: boolean; apple: boolean }>>().mockResolvedValue({
      google: false,
      apple: false,
    }),
  }
})

vi.mock('./staffPortalApi', async () => {
  const actual = await vi.importActual<typeof import('./staffPortalApi')>('./staffPortalApi')
  return {
    ...actual,
    getStaffMe: vi
      .fn<() => Promise<{ ok: boolean; data: { permissions: string[] } }>>()
      .mockResolvedValue({ ok: true, data: { permissions: ['bookings.view_staff_payments_desk'] } }),
    getDailySchedule: vi.fn<() => Promise<{ ok: boolean; data: Record<string, unknown> }>>().mockResolvedValue({
      ok: true,
      data: {
        dayType: 'Full-package day',
        capacity: { bookedClients: 0, maxClients: 3, remainingClients: 3 },
        appointments: [],
      },
    }),
    getStaffRescheduleQueue: vi.fn<() => Promise<{ ok: boolean; data: Record<string, unknown> }>>().mockResolvedValue({
      ok: true,
      data: {
        count: 1,
        appointments: [
          {
            publicBookingId: '11111111-1111-4111-8111-111111111111',
            time: '10:00',
            client: 'Amina K.',
            service: 'Soft glam',
            bookingStatus: 'confirmed',
            fulfillmentStatus: 'not_started',
            paymentStatus: 'paid',
            receiptStatus: 'issued',
            rescheduleStatus: 'none',
            bookingReference: '11111111-1111-4111-8111-111111111111',
          },
        ],
      },
    }),
    postStaffLogout: vi.fn<() => Promise<{ ok: boolean }>>().mockResolvedValue({ ok: true }),
  }
})

vi.mock('../booking/bookingCsrf', () => ({
  ensureBookingCsrfToken: vi.fn<() => Promise<string>>().mockResolvedValue('csrf-token'),
}))

const globalStubs = {
  NuxtLink: { template: '<a><slot /></a>', props: ['to'] },
  StaffSheeBrand: { template: '<div class="brand-stub" />' },
  StaffThemeToggle: { template: '<button type="button" class="theme-stub">Theme</button>' },
  StaffStatusChip: { template: '<span class="chip-stub" />', props: ['status'] },
}

describe('staff desk UX contracts', () => {
  it('dayCapacityBanner still maps policy labels for secondary surfaces', () => {
    expect(dayCapacityBanner('Full-package day', 3)).toBe('Full-package day — up to 3 clients.')
    expect(dayCapacityBanner('Service day', 5)).toBe('Service day — up to 5 clients.')
    expect(dayCapacityBanner('Closed', 0)).toBe('Closed today — no client bookings.')
  })

  it('staffLocalDateIso returns YYYY-MM-DD in Nairobi', () => {
    expect(staffLocalDateIso(new Date('2026-07-14T21:00:00Z'))).toBe('2026-07-15')
    expect(staffLocalDateIso(new Date('2026-07-14T10:00:00Z'))).toBe('2026-07-14')
  })

  it('password hints stay plain-language', () => {
    expect(clientStaffPasswordHint('short')).toBe('Use at least 15 characters.')
    expect(clientStaffPasswordHint('password1234567')).toBe('That password is too common.')
    expect(clientStaffPasswordHint('aminaspecialphrase1', { email: 'amina@example.com' })).toBe(
      'Don’t use your name or email in the password.',
    )
    expect(clientStaffPasswordHint('Nairobi salon passphrase secure 2026', { confirm: 'other' })).toBe(
      'Passwords don’t match.',
    )
    expect(mapStaffPasswordApiMessage('Staff password must be at least 15 characters.')).toBe(
      'Use at least 15 characters.',
    )
    expect(mapStaffPasswordApiMessage('traceback HMAC challenge')).toBe(
      'We could not update the password. Please try again.',
    )
  })

  it('dashboard shows spots left only — no full-package banner or paid/awaiting cards', async () => {
    const wrapper = mount(StaffDashboard, {
      props: { apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })
    await wrapper.vm.$nextTick()
    await Promise.resolve()
    await Promise.resolve()
    expect(wrapper.text()).toMatch(/Spots left/)
    expect(wrapper.text()).toMatch(/3/)
    expect(wrapper.text()).toMatch(/0 booked · 3 today/)
    expect(wrapper.text()).not.toMatch(/Full-package day — up to/i)
    expect(wrapper.text()).not.toMatch(/BOOKED TODAY|AWAITING|Payment confirmed/i)
    expect(wrapper.text()).not.toMatch(/keep each visit unhurried/i)
  })

  it('login has proper providers, eye toggle, and no ops oauth hint', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: { apiBaseUrl: 'https://api.example.com', csrfToken: 'csrf' },
      global: { stubs: globalStubs },
    })
    expect(wrapper.text()).toMatch(/Welcome back/)
    expect(wrapper.text()).toContain('Continue with Google')
    expect(wrapper.text()).toContain('Continue with Apple')
    expect(wrapper.text()).not.toMatch(/ops connects them|Use email for now\./i)
    expect(wrapper.find('.staff-login__oauth-hint').exists()).toBe(false)
    expect(wrapper.find('.staff-login__eye').exists()).toBe(true)
    expect(wrapper.find('.staff-login__text-btn').exists()).toBe(false)
    expect(wrapper.find('.staff-login__provider-icon--google svg').exists()).toBe(true)
    expect(wrapper.find('.staff-login__provider-icon--apple svg').exists()).toBe(true)
  })

  it('shell uses bottom tabs only — no hamburger drawer', () => {
    const wrapper = mount(StaffPortalShell, {
      props: { title: 'Bookings', apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })
    expect(wrapper.find('.staff-shell__menu-btn').exists()).toBe(false)
    expect(wrapper.find('.staff-shell__drawer').exists()).toBe(false)
    expect(wrapper.find('.staff-shell__bottom').exists()).toBe(true)
    expect(wrapper.text()).toContain('Gallery')
    expect(wrapper.text()).toContain('Settings')
    expect(wrapper.text()).toContain('Sign out')
    expect(wrapper.text()).toContain('Reschedules')
  })

  it('settings only offers appearance, reset password, and sign out', () => {
    const wrapper = mount(StaffSettingsSecurity, {
      props: { apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })
    expect(wrapper.text()).toContain('Appearance')
    expect(wrapper.text()).toContain('Reset password')
    expect(wrapper.text()).toContain('Sign out')
    expect(wrapper.text()).not.toMatch(/session|Google or Apple|passphrase|theme preference/i)
  })

  it('reschedule workspace loads queue and links into booking detail', async () => {
    const wrapper = mount(StaffReschedulesWorkspace, {
      props: { apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })
    await wrapper.vm.$nextTick()
    await Promise.resolve()
    await Promise.resolve()
    expect(wrapper.text()).toContain('Amina K.')
    expect(wrapper.text()).toContain('Open reschedule')
    expect(wrapper.text()).not.toMatch(/BK-1003|demo cards/i)
  })
})
