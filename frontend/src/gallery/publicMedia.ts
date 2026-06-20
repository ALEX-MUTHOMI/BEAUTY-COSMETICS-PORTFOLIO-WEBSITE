const PUBLIC_MEDIA_PREFIX = '/media/public/'

export function resolvePublicGalleryMediaUrl(value: string, apiBaseUrl: string): string {
  const candidate = String(value || '')
  if (!candidate.startsWith(PUBLIC_MEDIA_PREFIX)) {
    return ''
  }

  try {
    const apiOrigin = new URL(apiBaseUrl).origin
    return new URL(candidate, apiOrigin).toString()
  } catch {
    return ''
  }
}
