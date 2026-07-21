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

/** Curated static fallback — mixed crops for a Pinterest-like fill. */
export const STATIC_HOME_WORK: HomeWorkImage[] = [
  { id: 'static-1', src: '/images/gallery-1.jpg', alt: 'Shee client work', width: 800, height: 1000, shape: 'tall' },
  { id: 'static-2', src: '/images/gallery-2.jpg', alt: 'Shee studio result', width: 900, height: 700, shape: 'wide' },
  { id: 'static-3', src: '/images/showcase-facial.jpg', alt: 'Facial finish at Shee', width: 640, height: 800, shape: 'tall' },
  { id: 'static-4', src: '/images/gallery-3.jpg', alt: 'Makeup look by Shee', width: 800, height: 800, shape: 'square' },
  { id: 'static-5', src: '/images/showcase-makeup.jpg', alt: 'Soft glam makeup', width: 640, height: 800, shape: 'tall' },
  { id: 'static-6', src: '/images/gallery-4.jpg', alt: 'Spa treatment detail', width: 900, height: 700, shape: 'wide' },
  { id: 'static-7', src: '/images/showcase-massage.jpg', alt: 'Massage in studio', width: 640, height: 800, shape: 'tall' },
  { id: 'static-8', src: '/images/gallery-5.jpg', alt: 'Client glow after visit', width: 800, height: 800, shape: 'square' },
  { id: 'static-9', src: '/images/gallery-6.jpg', alt: 'Shee aesthetics work', width: 900, height: 700, shape: 'wide' },
  { id: 'static-10', src: '/images/showcase-waxing.jpg', alt: 'Clean wax finish', width: 640, height: 800, shape: 'tall' },
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
