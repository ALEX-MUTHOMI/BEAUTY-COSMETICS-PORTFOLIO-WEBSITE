import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffBookingDetail from './StaffBookingDetail.vue'
import StaffBookingsWorkspace from './StaffBookingsWorkspace.vue'
import StaffDashboard from './StaffDashboard.vue'
import StaffGalleryWorkspace from './StaffGalleryWorkspace.vue'
import StaffPaymentsWorkspace from './StaffPaymentsWorkspace.vue'
import StaffSettingsSecurity from './StaffSettingsSecurity.vue'
import { getDailySchedule, getStaffMe } from './staffPortalApi'
import { containsInternalJargon, friendlyStatus, safeDisplayText } from './statusCopy'

const globalStubs = {
  NuxtLink: {
    props: ['to'],
    template: '<a :href="to"><slot /></a>',
  },
}

describe('staff portal friendly copy and security boundaries', () => {
  it('maps backend states to staff-friendly words without internal jargon', () => {
    expect(friendlyStatus('payment_pending')).toBe('Awaiting payment')
    expect(friendlyStatus('success')).toBe('Payment confirmed')
    expect(friendlyStatus('manual_review')).toBe('Needs attention')
    expect(friendlyStatus('held')).toBe('Awaiting customer payment')
    expect(friendlyStatus('checkout_session_pending')).toBe('Needs attention')
    expect(containsInternalJargon('ledger correlation ID')).toBe(true)
    expect(safeDisplayText('ledger correlation ID', 'Hidden')).toBe('Hidden')
  })

  it('renders dashboard, bookings, and payments without raw backend jargon', () => {
    const dashboard = mount(StaffDashboard, { global: { stubs: globalStubs } })
    const bookings = mount(StaffBookingsWorkspace, {
      props: {
        appointments: [
          {
            publicBookingId: 'BK-1001',
            time: '09:00',
            client: 'Grace M.',
            service: 'Soft glam makeup',
            bookingStatus: 'held',
            paymentStatus: 'success',
            rescheduleStatus: 'none',
          },
        ],
      },
      global: { stubs: globalStubs },
    })
    const payments = mount(StaffPaymentsWorkspace, { global: { stubs: globalStubs } })
    const rendered = `${dashboard.text()} ${bookings.text()} ${payments.text()}`

    expect(rendered).toContain('Today at a glance')
    expect(rendered).toContain('Awaiting payment')
    expect(rendered).toContain('Payment confirmed')
    expect(rendered).not.toMatch(/ledger|checkout session|correlation ID|provider payload/i)
  })

  it('renders skeleton and safe retry states for slow or failed staff data requests', () => {
    const bookingsLoading = mount(StaffBookingsWorkspace, { props: { loading: true }, global: { stubs: globalStubs } })
    const paymentsError = mount(StaffPaymentsWorkspace, {
      props: { errorMessage: 'Please check your connection and try again.' },
      global: { stubs: globalStubs },
    })

    expect(bookingsLoading.findAll('.skeleton-row')).toHaveLength(4)
    expect(paymentsError.text()).toContain('Payments could not load.')
    expect(paymentsError.text()).toContain('Try again')
    expect(paymentsError.text()).not.toMatch(/traceback|exception|provider payload/i)
  })

  it('requires a re-auth modal before contact reveal and prevents duplicate completion clicks', async () => {
    // apiBaseUrl is injected like pages/staff/bookings/[publicId].vue — no Nuxt auto-imports in src/.
    const wrapper = mount(StaffBookingDetail, {
      props: { apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })

    expect(wrapper.text()).not.toMatch(/checkoutrequest|merchantrequest|ledger/i)
    const revealButton = wrapper.findAll('button').find((button) => button.text().includes('Reveal customer contact'))
    expect(revealButton).toBeDefined()
    await revealButton?.trigger('click')
    expect(wrapper.text()).toContain("Confirm it's you")
    const completion = wrapper.findAll('button').find((button) => button.text().includes('Mark service completed'))
    expect(completion?.attributes('disabled')).toBeUndefined()
    await completion?.trigger('click')
    expect(wrapper.text()).toContain('Service completed')
    const completed = wrapper.findAll('button').find((button) => button.text().includes('Service completed'))
    expect(completed?.attributes('disabled')).toBeDefined()
  })

  it('renders gallery upload navigation with friendly states and no backend jargon', () => {
    const wrapper = mount(StaffGalleryWorkspace, { global: { stubs: globalStubs } })

    expect(wrapper.text()).toContain('Checking image')
    expect(wrapper.text()).toContain('Choose JPG, PNG, or WebP')
    expect(wrapper.text()).toContain('Sensitive waxing image')
    const uploadButton = wrapper.findAll('button').find((button) => button.text().includes('Upload'))
    expect(uploadButton?.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).not.toMatch(/raw payload|checkout ID|receipt token|quarantine|storage key/i)
  })

  it('renders settings/security copy without low-level implementation detail', () => {
    const wrapper = mount(StaffSettingsSecurity, { global: { stubs: globalStubs } })

    expect(wrapper.text()).toContain('Provider sign-in')
    expect(wrapper.text()).toContain('not connected yet')
    expect(wrapper.text()).not.toMatch(/csrf|jwt|cookie name|session key|correlation/i)
  })
})

describe('staff portal API client', () => {
  it('uses cookie credentials and hides Docker-only upstream hosts', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn<() => Promise<unknown>>().mockResolvedValue({
        display_name: 'Staff <Admin>',
        permissions: ['bookings:view'],
      }),
    } as unknown as Response)

    const result = await getStaffMe('http://web:8000', fetcher)

    expect(fetcher).toHaveBeenCalledWith(
      '/api/staff/auth/me/',
      expect.objectContaining({ credentials: 'include' }),
    )
    expect(result.data?.displayName).toBe('Staff Admin')
  })

  it('normalizes schedule responses into safe public booking rows', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn<() => Promise<unknown>>().mockResolvedValue({
        local_date: '2026-06-06',
        day_type: 'full_package',
        capacity: { booked_clients: 4, max_clients: 6, remaining_clients: 2 },
        appointments: [
          {
            public_booking_id: 'BK-1001',
            start_time_eat: '09:00',
            customer_display_name_safe: 'Grace M.',
            service_summary: 'Soft glam',
            booking_status: 'confirmed',
            payment_status: 'payment_pending',
            reschedule_status: 'manual_review',
          },
        ],
      }),
    } as unknown as Response)

    const result = await getDailySchedule('https://api.example.com', '2026-06-06', { fetcher })

    expect(result.data?.dayType).toBe('Full-package day')
    const appointment = result.data?.appointments[0]
    expect(appointment).toBeDefined()
    expect(appointment).toMatchObject({
      publicBookingId: 'BK-1001',
      bookingStatus: 'confirmed',
      paymentStatus: 'payment_pending',
      rescheduleStatus: 'manual_review',
    })
    expect(friendlyStatus(appointment?.bookingStatus)).toBe('Booking confirmed')
    expect(friendlyStatus(appointment?.paymentStatus)).toBe('Awaiting payment')
    expect(friendlyStatus(appointment?.rescheduleStatus)).toBe('Needs attention')
  })

  it('marks 401/403 as session-expired without exposing backend error bodies', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 403,
      json: vi.fn<() => Promise<unknown>>().mockResolvedValue({ detail: 'raw backend auth detail' }),
    } as unknown as Response)

    const result = await getStaffMe('https://api.example.com', fetcher)

    expect(result.sessionExpired).toBe(true)
    expect(result.message).toBe('Please sign in again to continue.')
    expect(JSON.stringify(result)).not.toContain('raw backend auth detail')
  })
})
