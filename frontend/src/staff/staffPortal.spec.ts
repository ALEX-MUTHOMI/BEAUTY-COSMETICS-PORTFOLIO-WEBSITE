import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import StaffBookingDetail from '../../components/staff/StaffBookingDetail.vue'
import StaffBookingsWorkspace from '../../components/staff/StaffBookingsWorkspace.vue'
import StaffDashboard from '../../components/staff/StaffDashboard.vue'
import StaffGalleryWorkspace from '../../components/staff/StaffGalleryWorkspace.vue'
import StaffPaymentsWorkspace from '../../components/staff/StaffPaymentsWorkspace.vue'
import StaffSettingsSecurity from '../../components/staff/StaffSettingsSecurity.vue'
import {
  canDownloadReceipt,
  canSeePaymentsDesk,
  downloadStaffReceiptPdf,
  getDailySchedule,
  getStaffBookingPayment,
  getStaffMe,
} from './staffPortalApi'
import { containsInternalJargon, friendlyStatus, isReceiptIssued, safeDisplayText } from './staffUxHelpers'

const globalStubs = {
  NuxtLink: {
    props: ['to'],
    template: '<a :href="to"><slot /></a>',
  },
  SheeLogo: {
    template: '<div class="shee-logo-stub">Shee Aesthetics</div>',
  },
  StaffSheeBrand: {
    template: '<div class="shee-logo-stub">Shee Aesthetics</div>',
  },
}

const sampleAppointments = [
  {
    publicBookingId: 'BK-1001',
    time: '09:00',
    client: 'Grace M.',
    service: 'Soft glam makeup',
    bookingStatus: 'held',
    paymentStatus: 'success',
    receiptStatus: 'issued',
    rescheduleStatus: 'none',
  },
  {
    publicBookingId: 'BK-1002',
    time: '11:30',
    client: 'Amina K.',
    service: 'Facial',
    bookingStatus: 'held',
    paymentStatus: 'payment_pending',
    receiptStatus: 'not_issued',
    rescheduleStatus: 'none',
  },
]

describe('staff portal friendly copy and security boundaries', () => {
  it('maps backend states to staff-friendly words without internal jargon', () => {
    expect(friendlyStatus('payment_pending')).toBe('Awaiting payment')
    expect(friendlyStatus('success')).toBe('Payment confirmed')
    expect(friendlyStatus('manual_review')).toBe('Needs attention')
    expect(friendlyStatus('held')).toBe('Awaiting customer payment')
    expect(friendlyStatus('checkout_session_pending')).toBe('Needs attention')
    expect(isReceiptIssued('issued')).toBe(true)
    expect(isReceiptIssued('not_issued')).toBe(false)
    expect(containsInternalJargon('ledger correlation ID')).toBe(true)
    expect(safeDisplayText('ledger correlation ID', 'Hidden')).toBe('Hidden')
  })

  it('gates Payments nav with stub-safe permission rules until Phase B', () => {
    expect(canSeePaymentsDesk(null)).toBe(true)
    expect(canSeePaymentsDesk(['view_staff_payment_summary', 'view_staff_contact_details'])).toBe(true)
    expect(canSeePaymentsDesk(['view_staff_payments_desk'])).toBe(true)
    expect(canSeePaymentsDesk(['view_staff_portal'])).toBe(false)
    expect(canSeePaymentsDesk(['download_staff_receipt', 'view_staff_payment_summary'])).toBe(false)
    expect(canSeePaymentsDesk(['download_staff_receipt', 'view_staff_payments_desk'])).toBe(true)
    expect(canSeePaymentsDesk(['confirm_staff_attendance', 'view_staff_payment_summary'])).toBe(false)
    expect(
      canSeePaymentsDesk(['view_staff_portal', 'view_staff_booking', 'view_staff_payment_summary']),
    ).toBe(false)
  })

  it('requires download_staff_receipt for PDF button gating', () => {
    expect(canDownloadReceipt(null)).toBe(false)
    expect(canDownloadReceipt(['view_staff_payment_summary'])).toBe(false)
    expect(canDownloadReceipt(['download_staff_receipt'])).toBe(true)
  })

  it('renders dashboard, bookings, and payments without raw backend jargon', () => {
    const dashboard = mount(StaffDashboard, {
      props: { appointments: sampleAppointments, capacity: { bookedClients: 2, maxClients: 5, remainingClients: 3 } },
      global: { stubs: globalStubs },
    })
    const bookings = mount(StaffBookingsWorkspace, {
      props: { appointments: sampleAppointments },
      global: { stubs: globalStubs },
    })
    const payments = mount(StaffPaymentsWorkspace, {
      props: { appointments: sampleAppointments },
      global: { stubs: globalStubs },
    })
    const rendered = `${dashboard.text()} ${bookings.text()} ${payments.text()}`

    expect(rendered).toMatch(/\bToday\b/)
    expect(rendered).toContain('Spots left')
    expect(rendered).toContain("Today's payments")
    expect(rendered).toContain("Today’s payments for the selected date")
    expect(rendered).toContain('Awaiting payment')
    expect(rendered).toContain('Payment confirmed')
    expect(rendered).toContain('Visit status')
    expect(rendered).not.toMatch(/checkout session|correlation ID|provider payload/i)
    expect(rendered).not.toMatch(/\bledger\b/i)
    expect(rendered).not.toMatch(/Fulfillment|Day-scoped payment view|Full-package day — up to/i)
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
    const wrapper = mount(StaffBookingDetail, {
      props: { apiBaseUrl: 'https://api.example.com' },
      global: { stubs: globalStubs },
    })

    expect(wrapper.text()).not.toMatch(/checkoutrequest|merchantrequest|ledger/i)
    expect(wrapper.text()).toContain('View receipt PDF')
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

  it('shows receipt PDF CTA on demo detail and gates not-issued receipts', () => {
    const wrapper = mount(StaffBookingDetail, {
      props: { apiBaseUrl: '' },
      global: { stubs: globalStubs },
    })

    expect(wrapper.text()).toContain('View receipt PDF')
    expect(wrapper.find('button.receipt-button').attributes('disabled')).toBeUndefined()
    expect(isReceiptIssued('not_issued')).toBe(false)
    expect(isReceiptIssued('paid')).toBe(true)
  })

  it('renders gallery upload navigation with friendly states and no backend jargon', () => {
    const wrapper = mount(StaffGalleryWorkspace, { global: { stubs: globalStubs } })

    expect(wrapper.text()).toContain('Add photos for the website.')
    expect(wrapper.text()).toContain('JPG, PNG, or WebP')
    expect(wrapper.text()).toContain('Needs warning')
    const uploadButton = wrapper.findAll('button').find((button) => button.text() === 'Upload')
    expect(uploadButton?.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).not.toMatch(/raw payload|checkout ID|receipt token|quarantine|storage key|Checking image/i)
  })

  it('renders settings/security copy without low-level implementation detail', () => {
    const wrapper = mount(StaffSettingsSecurity, { global: { stubs: globalStubs } })

    expect(wrapper.text()).toContain('Appearance')
    expect(wrapper.text()).toContain('Reset password')
    expect(wrapper.text()).toContain('Sign out')
    expect(wrapper.text()).not.toMatch(/csrf|jwt|cookie name|session key|correlation|Google or Apple/i)
  })
})

describe('staff portal API client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

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
            receipt_status: 'not_issued',
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
      receiptStatus: 'not_issued',
      rescheduleStatus: 'manual_review',
    })
    expect(friendlyStatus(appointment?.bookingStatus)).toBe('Booking confirmed')
    expect(friendlyStatus(appointment?.paymentStatus)).toBe('Awaiting payment')
    expect(friendlyStatus(appointment?.rescheduleStatus)).toBe('Needs attention')
  })

  it('normalizes payment summary without exposing provider secrets', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn<() => Promise<unknown>>().mockResolvedValue({
        payment_status: 'paid',
        amount: '4500.00',
        currency: 'KES',
        receipt_status: 'paid',
        paid_at_eat: '2026-06-06T09:01:00+03:00',
        provider_reference: 'redacted',
      }),
    } as unknown as Response)

    const result = await getStaffBookingPayment('https://api.example.com', 'BK-1001', fetcher)
    expect(result.data).toMatchObject({
      paymentStatus: 'paid',
      amount: '4500.00',
      receiptStatus: 'paid',
      providerReference: 'redacted',
    })
    expect(JSON.stringify(result)).not.toMatch(/checkoutrequest|merchantrequest/i)
  })

  it('revokes blob object URLs after staff receipt PDF download', async () => {
    const revokeObjectURL = vi.fn<(url: string) => void>()
    const createObjectURL = vi.fn<(obj: Blob | MediaSource) => string>().mockReturnValue('blob:staff-receipt')
    vi.stubGlobal('URL', { createObjectURL, revokeObjectURL })
    vi.useFakeTimers()

    const click = vi.fn<() => void>()
    const remove = vi.fn<() => void>()
    const appendChild = vi.spyOn(document.body, 'appendChild').mockImplementation((node) => node)
    const createElement = vi.spyOn(document, 'createElement').mockReturnValue({
      href: '',
      target: '',
      rel: '',
      download: '',
      click,
      remove,
    } as unknown as HTMLAnchorElement)

    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      blob: vi.fn<() => Promise<Blob>>().mockResolvedValue(new Blob(['%PDF'], { type: 'application/pdf' })),
    } as unknown as Response)

    const result = await downloadStaffReceiptPdf('https://api.example.com', 'BK-1001', fetcher)
    expect(result.ok).toBe(true)
    expect(result.data?.revoked).toBe(true)
    expect(createObjectURL).toHaveBeenCalled()
    vi.runAllTimers()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:staff-receipt')

    createElement.mockRestore()
    appendChild.mockRestore()
    vi.useRealTimers()
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
