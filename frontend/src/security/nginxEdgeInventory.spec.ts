import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

describe('frontend-edge nginx inventory', () => {
  const conf = readFileSync(join(__dirname, '../../docker/nginx-edge.conf'), 'utf8')

  it('keeps admin off the public hostname', () => {
    expect(conf).toMatch(/location \^~ \/admin/)
    expect(conf).toContain('return 404')
  })

  it('proxies same-origin API and public gallery handles only', () => {
    expect(conf).toMatch(/location \/api\//)
    expect(conf).toMatch(/location \^~ \/media\/public\//)
    expect(conf).toMatch(/location \/media\//)
  })

  it('does not SPA-fallback scanner bait or the private media prefix', () => {
    expect(conf).toMatch(/wp-admin/)
    expect(conf).toMatch(/graphql/)
    expect(conf).toMatch(/\\.env/)
    const mediaPrefix = /location \/media\/ \{\s*return 404;/
    expect(conf).toMatch(mediaPrefix)
  })
})
