/**
 * Sync production-safe marketing images into frontend/docker/images-prod.
 * Excludes underscore candidate folders and scratch `_*.jpg` files.
 *
 * Usage: node scripts/sync-prod-images.mjs
 */
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(fileURLToPath(new URL('.', import.meta.url)), '..')
const src = join(root, 'public', 'images')
const dest = join(root, 'docker', 'images-prod')

function isProdSafeName(name) {
  if (name.startsWith('_') || name.startsWith('.')) return false
  if (name.includes('..')) return false
  return true
}

function walkCopy(fromDir, toDir) {
  mkdirSync(toDir, { recursive: true })
  for (const name of readdirSync(fromDir)) {
    if (!isProdSafeName(name)) continue
    const from = join(fromDir, name)
    const to = join(toDir, name)
    const st = statSync(from)
    if (st.isDirectory()) {
      // Skip any nested underscore dirs by name rule above; never copy _cand*
      walkCopy(from, to)
    } else if (st.isFile()) {
      cpSync(from, to)
    }
  }
}

if (!existsSync(src)) {
  console.error('missing', src)
  process.exit(1)
}

rmSync(dest, { recursive: true, force: true })
walkCopy(src, dest)
const count = readdirSync(dest).length
console.log(`synced ${count} top-level entries → ${dest}`)
