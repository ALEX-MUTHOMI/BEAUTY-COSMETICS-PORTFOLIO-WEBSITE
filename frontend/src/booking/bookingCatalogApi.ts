/**
 * Module: bookingCatalogApi
 * Catalog and service list retrieval API.
 */
import { slugifyCatalogName } from '@/landing/bookingCatalog'
import { GENERIC_BOOKING_API_ERROR, isUuid, publicBookingGet, safeApiText } from './bookingApi'

export interface CatalogService {
  publicId: string
  name: string
  category: string
  durationMinutes: number
  price: string
  currency: string
}

export interface CatalogPackage {
  publicId: string
  name: string
  description: string
  durationMinutes: number
  price: string
  currency: string
}

function parseServiceRow(value: unknown): CatalogService | null {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>
  const publicId = String(row.public_id ?? '')
  if (!isUuid(publicId)) return null
  const durationMinutes = Number(row.duration_minutes)
  if (!Number.isFinite(durationMinutes) || durationMinutes <= 0) return null
  return {
    publicId,
    name: safeApiText(row.name),
    category: safeApiText(row.category),
    durationMinutes,
    price: safeApiText(row.price, 32),
    currency: safeApiText(row.currency, 8) || 'KES',
  }
}

function parsePackageRow(value: unknown): CatalogPackage | null {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>
  const publicId = String(row.public_id ?? '')
  if (!isUuid(publicId)) return null
  const durationMinutes = Number(row.duration_minutes)
  if (!Number.isFinite(durationMinutes) || durationMinutes <= 0) return null
  return {
    publicId,
    name: safeApiText(row.name),
    description: safeApiText(row.description, 240),
    durationMinutes,
    price: safeApiText(row.price, 32),
    currency: safeApiText(row.currency, 8) || 'KES',
  }
}

function parseServicesPayload(payload: unknown): CatalogService[] | null {
  if (!payload || typeof payload !== 'object') return null
  const list = (payload as { services?: unknown }).services
  if (!Array.isArray(list)) return null
  const parsed = list.map(parseServiceRow).filter((row): row is CatalogService => row !== null)
  return parsed.length === list.length ? parsed : null
}

function parsePackagesPayload(payload: unknown): CatalogPackage[] | null {
  if (!payload || typeof payload !== 'object') return null
  const list = (payload as { packages?: unknown }).packages
  if (!Array.isArray(list)) return null
  const parsed = list.map(parsePackageRow).filter((row): row is CatalogPackage => row !== null)
  return parsed.length === list.length ? parsed : null
}

export async function fetchCatalogServices(
  apiBaseUrl: string,
): Promise<{ data: CatalogService[] } | { error: string }> {
  const result = await publicBookingGet(
    apiBaseUrl,
    '/api/bookings/catalog/services/',
    {},
    parseServicesPayload,
  )
  if ('error' in result) return { error: result.error }
  if (result.data.length === 0) return { error: GENERIC_BOOKING_API_ERROR }
  return result
}

export async function fetchCatalogPackages(
  apiBaseUrl: string,
): Promise<{ data: CatalogPackage[] } | { error: string }> {
  const result = await publicBookingGet(
    apiBaseUrl,
    '/api/bookings/catalog/packages/',
    {},
    parsePackagesPayload,
  )
  if ('error' in result) return { error: result.error }
  if (result.data.length === 0) return { error: GENERIC_BOOKING_API_ERROR }
  return result
}

export function findPackageByPlanSlug(
  packages: CatalogPackage[],
  planSlug: string,
): CatalogPackage | null {
  return (
    packages.find((pkg) => slugifyCatalogName(pkg.name) === planSlug) ?? null
  )
}

