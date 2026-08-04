import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

/*
 * Vitest mounts Vue SFCs under src/ without Nuxt auto-imports.
 * Nuxt runtime config / routing must be injected from pages/ and middleware/
 * (see StaffLoginPanel + StaffContactRevealModal apiBaseUrl props).
 *
 * Regression: CI run 29117806683 failed when StaffContactRevealModal called
 * bare useRuntimeConfig() which threw ReferenceError under Vue Test Utils.
 */
const FORBIDDEN_NUXT_AUTO_IMPORTS = [
  'useRuntimeConfig',
  'useHead',
  'useRoute',
  'useRouter',
  'navigateTo',
  'definePageMeta',
  'useCookie',
  'useNuxtApp',
  'useSeoMeta',
] as const

const srcRoot = join(process.cwd(), 'src')

function listVueFiles(dir: string): string[] {
  const entries = readdirSync(dir)
  const files: string[] = []
  for (const entry of entries) {
    const absolute = join(dir, entry)
    const stats = statSync(absolute)
    if (stats.isDirectory()) {
      files.push(...listVueFiles(absolute))
      continue
    }
    if (entry.endsWith('.vue')) files.push(absolute)
  }
  return files
}

describe('Nuxt boundary for unit-tested src components', () => {
  it('keeps Nuxt auto-imports out of src Vue SFCs so Vitest mounts stay fail-closed', () => {
    const violations: string[] = []

    for (const file of listVueFiles(srcRoot)) {
      const source = readFileSync(file, 'utf8')
      const relative = file.slice(srcRoot.length + 1).replace(/\\/g, '/')
      for (const name of FORBIDDEN_NUXT_AUTO_IMPORTS) {
        const callPattern = new RegExp(`\\b${name}\\s*\\(`)
        if (callPattern.test(source)) {
          violations.push(`${relative}: ${name}(...) — inject from pages/ instead`)
        }
      }
    }

    expect(violations).toEqual([])
  })
})
