import { friendlyStatus, safeDisplayText } from './statusCopy'

export interface StaffSessionProfile {
  displayName: string
  permissions: string[]
}

export interface StaffAppointment {
  publicBookingId: string
  time: string
  client: string
  service: string
  bookingStatus: string
  paymentStatus: string
  rescheduleStatus: string
  amount?: string
  currency?: string
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
}

export async function getStaffMe(apiBaseUrl: string, fetcher?: Fetcher): Promise<StaffApiResult<StaffSessionProfile>> {
  const result = await staffFetch<{ display_name?: string; permissions?: string[] }>(
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
  fetcher?: Fetcher,
): Promise<StaffApiResult<StaffSchedule>> {
  const result = await staffFetch<Record<string, unknown>>(
    apiBaseUrl,
    `/api/staff/bookings/schedule/?date=${encodeURIComponent(date)}`,
    fetcher,
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
      appointments: appointments.map((row) => {
        const item = row as Record<string, unknown>
        return {
          publicBookingId: safeDisplayText(item.public_booking_id || item.booking_reference),
          time: safeDisplayText(item.start_time_eat),
          client: safeDisplayText(item.customer_display_name_safe, 'Client'),
          service: safeDisplayText(item.service_summary, 'Selected service'),
          bookingStatus: friendlyStatus(String(item.booking_status || 'confirmed')),
          paymentStatus: friendlyStatus(String(item.payment_status || 'payment_pending')),
          rescheduleStatus: friendlyStatus(String(item.reschedule_status || 'none')),
          amount: item.amount ? safeDisplayText(item.amount) : undefined,
          currency: item.currency ? safeDisplayText(item.currency) : undefined,
        }
      }),
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
