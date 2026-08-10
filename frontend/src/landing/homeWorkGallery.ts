/**
 * Homepage “Our work” masonry — prefer staff-published public gallery,
 * fall back to curated static studio shots when the API is empty or offline.
 *
 * Resilience: SSR must never hang waiting on Django. We abort after ~2.5s
 * and render STATIC_HOME_WORK so nginx edge does not 504 the marketing site.
 */
import { trimApiBaseUrl, safeApiText } from '../booking/bookingApi'
import { resolvePublicGalleryMediaUrl } from '../gallery/publicMedia'

export type HomeWorkImage = {
  id: string
  src: string
  alt: string
  width: number
  height: number
  /** Masonry rhythm hint — tall / square / wide */
  shape: 'tall' | 'square' | 'wide'
}

const SHAPES: HomeWorkImage['shape'][] = ['tall', 'wide', 'square', 'tall', 'square', 'wide', 'tall', 'wide']

/** Default SSR timeout — keep under edge proxy budgets (often ~10–60s). */
export const HOME_WORK_GALLERY_TIMEOUT_MS = 2500

/** Curated static fallback — realistic Kenyan-facing spa/beauty frames (not client PII). */
export const STATIC_HOME_WORK: HomeWorkImage[] = [
  {
    id: 'static-1',
    src: '/images/work-1.jpg',
    alt: 'Makeup glow — joyful client with a natural afro at Shee',
    width: 1000,
    height: 1500,
    shape: 'tall',
  },
  {
    id: 'static-2',
    src: '/images/work-2.jpg',
    alt: 'African-print beauty look styled for a Shee client',
    width: 1000,
    height: 1500,
    shape: 'tall',
  },
  {
    id: 'static-3',
    src: '/images/work-3.jpg',
    alt: 'Warm oil back massage for deep relaxation at Shee',
    width: 1000,
    height: 1500,
    shape: 'tall',
  },
  {
    id: 'static-4',
    src: '/images/work-4.jpg',
    alt: 'Natural glow — close-up beauty portrait at Shee',
    width: 1000,
    height: 1000,
    shape: 'square',
  },
  {
    id: 'static-5',
    src: '/images/work-5.jpg',
    alt: 'Overhead facial massage in the Shee treatment room',
    width: 1000,
    height: 667,
    shape: 'wide',
  },
  {
    id: 'static-6',
    src: '/images/work-6.jpg',
    alt: 'Candlelit facial massage — calm spa moment at Shee',
    width: 1000,
    height: 1500,
    shape: 'tall',
  },
  {
    id: 'static-7',
    src: '/images/work-7.jpg',
    alt: 'Joyful client glow — natural hair and beaded earrings at Shee',
    width: 1200,
    height: 900,
    shape: 'wide',
  },
  {
    id: 'static-8',
    src: '/images/work-8.jpg',
    alt: 'Natural afro glow — confident client energy at Shee',
    width: 1200,
    height: 1804,
    shape: 'tall',
  },
]

type ApiVariant = {
  url?: unknown
  width?: unknown
  height?: unknown
}

type ApiImage = {
  public_id?: unknown
  title?: unknown
  category?: { name?: unknown }
  variants?: Record<string, ApiVariant>
}

function pickVariant(variants: Record<string, ApiVariant> | undefined): ApiVariant | null {
  if (!variants || typeof variants !== 'object') return null
  return variants.mobile || variants.hero || variants.desktop || Object.values(variants)[0] || null
}

function shapeForIndex(index: number): HomeWorkImage['shape'] {
  return SHAPES[index % SHAPES.length]!
}

export function mapPublicGalleryToHomeWork(
  payload: unknown,
  apiBaseUrl: string,
): HomeWorkImage[] {
  const images = (payload as { images?: unknown })?.images
  if (!Array.isArray(images) || images.length === 0) return []

  const mapped: HomeWorkImage[] = []
  for (let i = 0; i < images.length; i++) {
    const item = images[i] as ApiImage & { category?: { slug?: string; name?: string } }
    const categorySlug = String(item.category?.slug || '').toLowerCase()
    const rawTitle = String(item.title || '')
    if (categorySlug.startsWith('api-acceptance') || rawTitle.toLowerCase().includes('acceptance')) {
      continue
    }

    const variant = pickVariant(item.variants)
    const rawUrl = String(variant?.url || '')
    const src = resolvePublicGalleryMediaUrl(rawUrl, apiBaseUrl)
    if (!src) continue

    const category = safeApiText(item.category?.name, 64)
    const title = safeApiText(item.title, 80)
    const alt = title || (category ? `${category} by Shee` : 'Shee client work')
    const width = Number(variant?.width) || 800
    const height = Number(variant?.height) || 1000

    mapped.push({
      id: safeApiText(item.public_id, 64) || `api-${i}`,
      src,
      alt,
      width,
      height,
      shape: shapeForIndex(i),
    })
  }
  return mapped
}

/**
 * Fetch public homepage gallery images.
 * @param apiBaseUrl Trusted API origin (empty → static fallback immediately)
 * @param options.timeoutMs Abort budget (clamped 500–8000ms)
 */
export async function fetchHomeWorkGallery(
  apiBaseUrl: string,
  fetcher: typeof fetch = fetch,
  options?: { timeoutMs?: number },
): Promise<HomeWorkImage[]> {
  const base = trimApiBaseUrl(apiBaseUrl)
  const timeoutMs = Math.min(
    Math.max(options?.timeoutMs ?? HOME_WORK_GALLERY_TIMEOUT_MS, 500),
    8000,
  )
  if (!base) return STATIC_HOME_WORK

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetcher(`${base}/api/gallery/public/homepage/`, {
      method: 'GET',
      credentials: 'omit',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    })
    if (!response.ok) return STATIC_HOME_WORK
    const payload = await response.json()
    const mapped = mapPublicGalleryToHomeWork(payload, base)
    return mapped.length > 0 ? mapped : STATIC_HOME_WORK
  } catch {
    // AbortError, network failure, or JSON parse — marketing page stays up.
    return STATIC_HOME_WORK
  } finally {
    clearTimeout(timer)
  }
}
