import { friendlyStatus, safeDisplayText } from './statusCopy'

export interface StaffSessionProfile {
  displayName: string
  permissions: string[]
  role?: string | null
}

export interface StaffAppointment {
  publicBookingId: string
  time: string
  client: string
  service: string
  bookingStatus: string
  fulfillmentStatus?: string
  paymentStatus: string
  receiptStatus: string
  rescheduleStatus: string
  amount?: string
  currency?: string
  bookingReference?: string
  assignedStaffDisplayName?: string
  receiptNumber?: string
}

export interface StaffSchedule {
  localDate: string
  dayType: string
  capacity: {
    bookedClients: number
    maxClients: number
    remainingClients: number
  }
  appointments: StaffAppointment[]
}

export interface StaffGallerySubcategory {
  publicId: string
  name: string
  slug: string
  sensitivityDefault: string
  requiresWarningDefault: boolean
}

export interface StaffGalleryCategory {
  publicId: string
  name: string
  slug: string
  isSensitiveDefault: boolean
  subcategories: StaffGallerySubcategory[]
}

export interface StaffApiResult<T> {
  ok: boolean
  status: number
  data?: T
  sessionExpired?: boolean
  message?: string
}

/**
 * Payments desk nav (UX only — backend still enforces authz).
 * Requires `view_staff_payments_desk`. Legacy fallback: `view_staff_payment_summary`
 * only when no Phase B role codenames are present on the session.
 */
export function canSeePaymentsDesk(permissions: string[] | null | undefined): boolean {
  if (permissions == null) return true
  const permissionSet = new Set(permissions)
  if (permissionSet.has('view_staff_payments_desk')) return true
  const phaseBMarkers = [
    'download_staff_receipt',
    'confirm_staff_attendance',
    'assign_staff_booking',
    'view_staff_payments_desk',
  ]
  if (phaseBMarkers.some((code) => permissionSet.has(code))) return false
  // Beautician-only grants (portal + booking + summary) must not open the PDF desk.
  if (
    permissionSet.has('view_staff_payment_summary') &&
    !permissionSet.has('view_staff_contact_details') &&
    !permissionSet.has('manage_staff_booking_notes')
  ) {
    return false
  }
  return permissionSet.has('view_staff_payment_summary')
}

/** Receipt PDF download — requires `download_staff_receipt` (owner). */
export function canDownloadReceipt(permissions: string[] | null | undefined): boolean {
  if (permissions == null) return false
  return new Set(permissions).has('download_staff_receipt')
}

export function canConfirmAttendance(permissions: string[] | null | undefined): boolean {
  if (permissions == null) return false
  return new Set(permissions).has('confirm_staff_attendance')
}

export function canAssignStaff(permissions: string[] | null | undefined): boolean {
  if (permissions == null) return false
  return new Set(permissions).has('assign_staff_booking')
}


type Fetcher = typeof fetch

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '')
}

function apiBase(apiBaseUrl: string): string {
  try {
    const parsed = new URL(apiBaseUrl)
    if (['web', 'backend', 'django'].includes(parsed.hostname)) {
      return ''
    }
  } catch {
    return ''
  }
  return trimTrailingSlash(apiBaseUrl)
}

async function safeJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return {}
  }
}

async function staffFetch<T>(apiBaseUrl: string, path: string, fetcher: Fetcher = fetch): Promise<StaffApiResult<T>> {
  try {
    const response = await fetcher(`${apiBase(apiBaseUrl)}${path}`, {
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })
    const data = await safeJson(response)
    return {
      ok: response.ok,
      status: response.status,
      data: response.ok ? (data as T) : undefined,
      sessionExpired: response.status === 401 || response.status === 403,
      message: response.ok ? undefined : 'Please sign in again to continue.',
    }
  } catch {
    return {
      ok: false,
      status: 0,
      sessionExpired: true,
      message: 'Please sign in again to continue.',
    }
  }
}

export async function getStaffMe(apiBaseUrl: string, fetcher?: Fetcher): Promise<StaffApiResult<StaffSessionProfile>> {
  const result = await staffFetch<{ display_name?: string; permissions?: string[]; role?: string | null }>(
    apiBaseUrl,
    '/api/staff/auth/me/',
    fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  return {
    ...result,
    data: {
      displayName: safeDisplayText(result.data.display_name, 'Staff'),
      permissions: Array.isArray(result.data.permissions) ? result.data.permissions : [],
      role: result.data.role ?? null,
    },
  }
}

export async function getStaffGalleryCategories(
  apiBaseUrl: string,
  fetcher?: Fetcher,
): Promise<StaffApiResult<{ categories: StaffGalleryCategory[] }>> {
  const result = await staffFetch<{ categories?: Record<string, unknown>[] }>(
    apiBaseUrl,
    '/api/staff/gallery/categories/',
    fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  return {
    ...result,
    data: {
      categories: (result.data.categories || []).map((category) => ({
        publicId: safeDisplayText(category.public_id),
        name: safeDisplayText(category.name),
        slug: safeDisplayText(category.slug),
        isSensitiveDefault: Boolean(category.is_sensitive_default),
        subcategories: Array.isArray(category.subcategories)
          ? category.subcategories.map((subcategory) => {
              const item = subcategory as Record<string, unknown>
              return {
                publicId: safeDisplayText(item.public_id),
                name: safeDisplayText(item.name),
                slug: safeDisplayText(item.slug),
                sensitivityDefault: safeDisplayText(item.sensitivity_default, 'normal'),
                requiresWarningDefault: Boolean(item.requires_warning_default),
              }
            })
          : [],
      })),
    },
  }
}

export async function postStaffGalleryImage(
  apiBaseUrl: string,
  formData: FormData,
  csrfToken: string,
  fetcher: Fetcher = fetch,
): Promise<StaffApiResult<{ image: { publicId: string; status: string; title: string; category: string } }>> {
  const response = await fetcher(`${apiBase(apiBaseUrl)}/api/staff/gallery/images/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
    body: formData,
  })
  const data = await safeJson(response)
  if (!response.ok || typeof data !== 'object' || data === null || !('image' in data)) {
    return {
      ok: false,
      status: response.status,
      message:
        response.status === 409
          ? 'This image is already in the gallery.'
          : 'Could not use this image. Choose a clear JPG, PNG, or WebP and try again.',
    }
  }
  const image = (data as { image: Record<string, unknown> }).image
  return {
    ok: true,
    status: response.status,
    data: {
      image: {
        publicId: safeDisplayText(image.public_id),
        status: safeDisplayText(image.status, 'checking'),
        title: safeDisplayText(image.title),
        category: safeDisplayText(image.category),
      },
    },
  }
}

export async function getDailySchedule(
  apiBaseUrl: string,
  date: string,
  options: { status?: string; bookingType?: string; assignedTo?: string; fetcher?: Fetcher } = {},
): Promise<StaffApiResult<StaffSchedule>> {
  const params = new URLSearchParams({ date })
  if (options.status) params.set('status', options.status)
  if (options.bookingType) params.set('booking_type', options.bookingType)
  if (options.assignedTo) params.set('assigned_to', options.assignedTo)
  const result = await staffFetch<Record<string, unknown>>(
    apiBaseUrl,
    `/api/staff/bookings/schedule/?${params.toString()}`,
    options.fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  const appointments = Array.isArray(result.data.appointments) ? result.data.appointments : []
  return {
    ...result,
    data: {
      localDate: safeDisplayText(result.data.local_date),
      dayType: friendlyStatus(String(result.data.day_type || 'normal')),
      capacity: {
        bookedClients: Number((result.data.capacity as Record<string, unknown> | undefined)?.booked_clients || 0),
        maxClients: Number((result.data.capacity as Record<string, unknown> | undefined)?.max_clients || 0),
        remainingClients: Number((result.data.capacity as Record<string, unknown> | undefined)?.remaining_clients || 0),
      },
      appointments: appointments.map((row) => mapAppointmentRow(row as Record<string, unknown>)),
    },
  }
}

function mapAppointmentRow(item: Record<string, unknown>): StaffAppointment {
  return {
    publicBookingId: safeDisplayText(item.public_booking_id || item.booking_reference),
    time: safeDisplayText(item.start_time_eat),
    client: safeDisplayText(item.customer_display_name_safe, 'Client'),
    service: safeDisplayText(item.service_summary, 'Selected service'),
    bookingStatus: String(item.booking_status || 'confirmed'),
    fulfillmentStatus: String(item.fulfillment_status || 'not_started'),
    paymentStatus: String(item.payment_status || 'payment_pending'),
    receiptStatus: String(item.receipt_status || 'not_issued'),
    rescheduleStatus: String(item.reschedule_status || 'none'),
    amount: item.amount ? safeDisplayText(item.amount) : undefined,
    currency: item.currency ? safeDisplayText(item.currency) : undefined,
    bookingReference: safeDisplayText(item.booking_reference || item.public_booking_id),
    assignedStaffDisplayName: item.assigned_staff_display_name
      ? safeDisplayText(item.assigned_staff_display_name)
      : undefined,
  }
}

export async function searchStaffBookings(
  apiBaseUrl: string,
  q: string,
  fetcher?: Fetcher,
): Promise<StaffApiResult<{ query: string; count: number; appointments: StaffAppointment[] }>> {
  const trimmed = q.trim()
  if (trimmed.length < 3) {
    return {
      ok: false,
      status: 400,
      message: 'Enter at least 3 characters to search.',
    }
  }
  const params = new URLSearchParams({ q: trimmed })
  const result = await staffFetch<Record<string, unknown>>(
    apiBaseUrl,
    `/api/staff/bookings/search/?${params.toString()}`,
    fetcher,
  )
  if (!result.ok || !result.data) {
    return {
      ...result,
      data: undefined,
      message: result.message || 'Search could not run.',
    }
  }
  const appointments = Array.isArray(result.data.appointments) ? result.data.appointments : []
  return {
    ...result,
    data: {
      query: safeDisplayText(result.data.query, trimmed),
      count: Number(result.data.count || appointments.length),
      appointments: appointments.map((row) => mapAppointmentRow(row as Record<string, unknown>)),
    },
  }
}

export interface StaffBookingDetailData {
  publicBookingId: string
  localDate: string
  time: string
  endTime: string
  client: string
  service: string
  bookingStatus: string
  fulfillmentStatus: string
  paymentStatus: string
  receiptStatus: string
  amount: string
  currency: string
  resource: string
  bookingReference: string
  assignedStaffId?: string | number | null
  assignedStaffDisplayName?: string
}

export interface StaffPaymentSummary {
  paymentStatus: string
  amount: string
  currency: string
  receiptStatus: string
  paidAtEat: string
  providerReference: string
}

export async function getStaffBookingDetail(
  apiBaseUrl: string,
  publicBookingId: string,
  fetcher?: Fetcher,
): Promise<StaffApiResult<StaffBookingDetailData>> {
  const result = await staffFetch<Record<string, unknown>>(
    apiBaseUrl,
    `/api/staff/bookings/${encodeURIComponent(publicBookingId)}/`,
    fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  return {
    ...result,
    data: {
      publicBookingId: safeDisplayText(result.data.public_booking_id || publicBookingId),
      localDate: safeDisplayText(result.data.local_date),
      time: safeDisplayText(result.data.start_time_eat),
      endTime: safeDisplayText(result.data.end_time_eat),
      client: safeDisplayText(result.data.customer_display_name_safe, 'Client'),
      service: safeDisplayText(result.data.service_summary, 'Selected service'),
      bookingStatus: String(result.data.booking_status || 'confirmed'),
      fulfillmentStatus: String(result.data.fulfillment_status || 'not_started'),
      paymentStatus: String(result.data.payment_status || 'payment_pending'),
      receiptStatus: String(result.data.receipt_status || 'not_issued'),
      amount: safeDisplayText(result.data.amount),
      currency: safeDisplayText(result.data.currency, 'KES'),
      resource: safeDisplayText(result.data.resource),
      bookingReference: safeDisplayText(result.data.booking_reference || result.data.public_booking_id || publicBookingId),
      assignedStaffId:
        result.data.assigned_staff_id == null ? null : String(result.data.assigned_staff_id),
      assignedStaffDisplayName: result.data.assigned_staff_display_name
        ? safeDisplayText(result.data.assigned_staff_display_name)
        : undefined,
    },
  }
}

export async function getStaffBookingPayment(
  apiBaseUrl: string,
  publicBookingId: string,
  fetcher?: Fetcher,
): Promise<StaffApiResult<StaffPaymentSummary>> {
  const result = await staffFetch<Record<string, unknown>>(
    apiBaseUrl,
    `/api/staff/bookings/${encodeURIComponent(publicBookingId)}/payment/`,
    fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  return {
    ...result,
    data: {
      paymentStatus: String(result.data.payment_status || 'payment_pending'),
      amount: safeDisplayText(result.data.amount),
      currency: safeDisplayText(result.data.currency, 'KES'),
      receiptStatus: String(result.data.receipt_status || 'not_issued'),
      paidAtEat: safeDisplayText(result.data.paid_at_eat, ''),
      providerReference: safeDisplayText(result.data.provider_reference, 'unavailable'),
    },
  }
}

export async function downloadStaffReceiptPdf(
  apiBaseUrl: string,
  publicBookingId: string,
  fetcher: Fetcher = fetch,
): Promise<StaffApiResult<{ revoked: boolean }>> {
  const response = await fetcher(
    `${apiBase(apiBaseUrl)}/api/staff/bookings/${encodeURIComponent(publicBookingId)}/receipt.pdf`,
    {
      credentials: 'include',
      headers: { Accept: 'application/pdf' },
    },
  )
  if (!response.ok) {
    return {
      ok: false,
      status: response.status,
      sessionExpired: response.status === 401 || response.status === 403,
      message:
        response.status === 404
          ? 'Receipt is not available yet.'
          : 'Receipt could not be opened. Please try again.',
    }
  }
  const blob = await response.blob()
  const objectUrl = URL.createObjectURL(blob)
  let revoked = false
  try {
    const anchor = document.createElement('a')
    anchor.href = objectUrl
    anchor.target = '_blank'
    anchor.rel = 'noopener'
    anchor.download = `receipt-${publicBookingId}.pdf`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
  } finally {
    // Always revoke after trigger so blob URLs do not accumulate in memory.
    window.setTimeout(() => {
      URL.revokeObjectURL(objectUrl)
    }, 0)
    revoked = true
  }
  return { ok: true, status: response.status, data: { revoked } }
}

export async function postStaffContactAccess(
  apiBaseUrl: string,
  publicBookingId: string,
  reason: string,
  csrfToken: string,
  fetcher: Fetcher = fetch,
): Promise<StaffApiResult<{ email: string; phone: string; client: string }>> {
  const response = await fetcher(`${apiBase(apiBaseUrl)}/api/staff/bookings/${encodeURIComponent(publicBookingId)}/contact-access/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
    body: JSON.stringify({ reason }),
  })
  const data = await safeJson(response)
  if (!response.ok || typeof data !== 'object' || data === null) {
    return {
      ok: false,
      status: response.status,
      sessionExpired: response.status === 401 || response.status === 403,
      message: 'Contact details could not be revealed. Confirm your password and try again.',
    }
  }
  const payload = data as Record<string, unknown>
  return {
    ok: true,
    status: response.status,
    data: {
      email: safeDisplayText(payload.email),
      phone: safeDisplayText(payload.phone),
      client: safeDisplayText(payload.customer_display_name_safe, 'Client'),
    },
  }
}

export async function postStaffFulfillment(
  apiBaseUrl: string,
  publicBookingId: string,
  fulfillmentStatus: string,
  csrfToken: string,
  fetcher: Fetcher = fetch,
): Promise<StaffApiResult<StaffAppointment>> {
  const response = await fetcher(
    `${apiBase(apiBaseUrl)}/api/staff/bookings/${encodeURIComponent(publicBookingId)}/fulfillment/`,
    {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        Accept: 'application/json',
      },
      body: JSON.stringify({ fulfillment_status: fulfillmentStatus }),
    },
  )
  const data = await safeJson(response)
  if (!response.ok || typeof data !== 'object' || data === null) {
    return {
      ok: false,
      status: response.status,
      sessionExpired: response.status === 401 || response.status === 403,
      message: 'Fulfillment could not be updated.',
    }
  }
  return { ok: true, status: response.status, data: mapAppointmentRow(data as Record<string, unknown>) }
}

export async function postStaffAssign(
  apiBaseUrl: string,
  publicBookingId: string,
  assignedStaffId: string | number | null,
  csrfToken: string,
  fetcher: Fetcher = fetch,
): Promise<StaffApiResult<StaffAppointment>> {
  const response = await fetcher(
    `${apiBase(apiBaseUrl)}/api/staff/bookings/${encodeURIComponent(publicBookingId)}/assign/`,
    {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        Accept: 'application/json',
      },
      body: JSON.stringify({ assigned_staff_id: assignedStaffId }),
    },
  )
  const data = await safeJson(response)
  if (!response.ok || typeof data !== 'object' || data === null) {
    return {
      ok: false,
      status: response.status,
      sessionExpired: response.status === 401 || response.status === 403,
      message: 'Assignment could not be updated.',
    }
  }
  return { ok: true, status: response.status, data: mapAppointmentRow(data as Record<string, unknown>) }
}

export async function getAssignableBeauticians(
  apiBaseUrl: string,
  fetcher?: Fetcher,
): Promise<StaffApiResult<{ beauticians: { id: string; email: string; displayName: string; role: string }[] }>> {
  const result = await staffFetch<{ beauticians?: Record<string, unknown>[] }>(
    apiBaseUrl,
    '/api/staff/bookings/assignable/',
    fetcher,
  )
  if (!result.ok || !result.data) {
    return { ...result, data: undefined }
  }
  return {
    ...result,
    data: {
      beauticians: (result.data.beauticians || []).map((row) => ({
        id: String(row.id),
        email: safeDisplayText(row.email),
        displayName: safeDisplayText(row.display_name, 'Beautician'),
        role: safeDisplayText(row.role, 'beautician'),
      })),
    },
  }
}

export async function postStaffLogout(apiBaseUrl: string, csrfToken: string, fetcher: Fetcher = fetch) {
  return fetcher(`${apiBase(apiBaseUrl)}/api/staff/auth/logout/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
  })
}

export async function postStaffReauth(apiBaseUrl: string, password: string, csrfToken: string, fetcher: Fetcher = fetch) {
  return fetcher(`${apiBase(apiBaseUrl)}/api/staff/auth/reauth/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
    body: JSON.stringify({ password }),
  })
}
