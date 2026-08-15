import { describe, expect, it, vi } from 'vitest'

import {
  STATIC_HOME_WORK,
  fetchHomeWorkGallery,
  mapPublicGalleryToHomeWork,
  resolvePublicGalleryMediaUrl,
} from './homeWorkGallery'

describe('homeWorkGallery', () => {
  it('ships a static fallback with mixed shapes for masonry', () => {
    expect(STATIC_HOME_WORK.length).toBeGreaterThanOrEqual(8)
    expect(STATIC_HOME_WORK.some((img) => img.shape === 'tall')).toBe(true)
    expect(STATIC_HOME_WORK.some((img) => img.shape === 'wide')).toBe(true)
  })

  it('maps public API variants through the opaque media resolver', () => {
    const mapped = mapPublicGalleryToHomeWork(
      {
        images: [
          {
            public_id: '11111111-1111-4111-8111-111111111111',
            title: 'Soft glam',
            category: { name: 'Makeup' },
            variants: {
              mobile: {
                url: '/media/public/22222222-2222-4222-8222-222222222222.webp',
                width: 640,
                height: 800,
              },
            },
          },
        ],
      },
      'http://localhost:8000',
    )
    expect(mapped).toHaveLength(1)
    expect(mapped[0]?.src).toContain('/media/public/')
    expect(mapped[0]?.alt).toContain('Soft glam')
  })

  it('falls back to static when the API fails', async () => {
    const fetcher = vi.fn<typeof fetch>().mockRejectedValue(new Error('offline'))
    const images = await fetchHomeWorkGallery('http://localhost:8000', fetcher)
    expect(images).toEqual(STATIC_HOME_WORK)
  })

  it('falls back to static when the API times out (abort)', async () => {
    const fetcher = vi.fn<typeof fetch>().mockImplementation((_url, init) => {
      return new Promise((_resolve, reject) => {
        const signal = init?.signal
        if (signal?.aborted) {
          reject(new DOMException('Aborted', 'AbortError'))
          return
        }
        signal?.addEventListener('abort', () => {
          reject(new DOMException('Aborted', 'AbortError'))
        })
      })
    })
    const images = await fetchHomeWorkGallery('http://localhost:8000', fetcher, { timeoutMs: 50 })
    expect(images).toEqual(STATIC_HOME_WORK)
    expect(fetcher).toHaveBeenCalled()
  })

  it('falls back to static when the API returns an empty list', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      json: async () => ({ images: [] }),
    } as Response)
    const images = await fetchHomeWorkGallery('http://localhost:8000', fetcher)
    expect(images).toEqual(STATIC_HOME_WORK)
  })

  it('resolves an opaque public media path against the backend origin', () => {
    expect(
      resolvePublicGalleryMediaUrl(
        '/media/public/11111111-1111-4111-8111-111111111111.webp',
        'http://localhost:8000',
      ),
    ).toBe('http://localhost:8000/media/public/11111111-1111-4111-8111-111111111111.webp')
  })

  it('rejects raw storage paths and non-public URL shapes', () => {
    expect(resolvePublicGalleryMediaUrl('/media/gallery/variants/private/item.webp', 'http://localhost:8000')).toBe('')
    expect(resolvePublicGalleryMediaUrl('https://unexpected.example/object.webp', 'http://localhost:8000')).toBe('')
  })
})
