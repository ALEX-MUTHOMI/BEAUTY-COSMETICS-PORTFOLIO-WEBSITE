/** Mirrors SiteLoader timing contract — keep in sync with components/SiteLoader.vue */
export function loaderSafetyTimeoutMs(minDuration: number): number {
  return minDuration + 1200
}
