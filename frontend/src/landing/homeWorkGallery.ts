/**
 * Homepage “Our work” masonry — prefer staff-published public gallery,
 * fall back to curated static studio shots when the API is empty or offline.
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
    const item = images[i] as ApiImage
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

export async function fetchHomeWorkGallery(
  apiBaseUrl: string,
  fetcher: typeof fetch = fetch,
): Promise<HomeWorkImage[]> {
  const base = trimApiBaseUrl(apiBaseUrl)
  if (!base) return STATIC_HOME_WORK

  try {
    const response = await fetcher(`${base}/api/gallery/public/homepage/`, {
      method: 'GET',
      credentials: 'omit',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return STATIC_HOME_WORK
    const payload = await response.json()
    const mapped = mapPublicGalleryToHomeWork(payload, base)
    return mapped.length > 0 ? mapped : STATIC_HOME_WORK
  } catch {
    return STATIC_HOME_WORK
  }
}
