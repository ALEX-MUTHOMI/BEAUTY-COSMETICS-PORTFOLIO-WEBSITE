import { describe, expect, it } from 'vitest'

import { resolvePublicGalleryMediaUrl } from './publicMedia'

describe('resolvePublicGalleryMediaUrl', () => {
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
