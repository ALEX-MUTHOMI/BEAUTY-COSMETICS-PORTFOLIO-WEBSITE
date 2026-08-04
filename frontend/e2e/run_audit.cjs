const { chromium } = require('@playwright/test');

const DEVICE_PROFILES = [
  { name: 'Samsung Galaxy S20 (360x800)', width: 360, height: 800, isMobile: true },
  { name: 'iPhone SE (375x667)', width: 375, height: 667, isMobile: true },
  { name: 'iPhone 14 / 15 Pro (393x852)', width: 393, height: 852, isMobile: true },
  { name: 'iPhone 15 Pro Max (430x932)', width: 430, height: 932, isMobile: true },
  { name: 'iPad Air (820x1180)', width: 820, height: 1180, isMobile: false },
  { name: 'iPad Pro (834x1194)', width: 834, height: 1194, isMobile: false },
  { name: 'Laptop (1280x800)', width: 1280, height: 800, isMobile: false },
  { name: 'Desktop HD (1440x900)', width: 1440, height: 900, isMobile: false },
  { name: 'Desktop UltraWide (1920x1080)', width: 1920, height: 1080, isMobile: false }
];

async function runAudit() {
  console.log('=== CHROME DEVICE RESPONSIVE AUDIT RESULTS ===\n');
  const browser = await chromium.launch({ headless: true });
  let totalAnomalies = 0;

  for (const dev of DEVICE_PROFILES) {
    const context = await browser.newContext({
      viewport: { width: dev.width, height: dev.height },
      isMobile: dev.isMobile,
      hasTouch: dev.isMobile,
      deviceScaleFactor: dev.isMobile ? 3 : 1
    });

    const page = await context.newPage();
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 15000 }).catch(() => {});

    // Wait for skeleton loader to clear
    await page.waitForSelector('#behind-the-glow', { timeout: 8000 });

    const audit = await page.evaluate(() => {
      const doc = document.documentElement;
      const scrollWidth = doc.scrollWidth;
      const clientWidth = doc.clientWidth;
      const overflowX = scrollWidth > clientWidth + 1;

      const mirror = document.querySelector('.glow__mirror');
      const mirrorRect = mirror ? mirror.getBoundingClientRect() : null;

      // Helper to check if element or any ancestor clips overflow
      function isClipped(el) {
        let curr = el.parentElement;
        while (curr && curr !== document.body && curr !== document.documentElement) {
          const style = window.getComputedStyle(curr);
          if (style.overflowX === 'hidden' || style.overflowX === 'clip' || style.overflowY === 'hidden' || style.overflowY === 'clip') {
            return true;
          }
          curr = curr.parentElement;
        }
        return false;
      }

      // Find any elements exceeding body width that are NOT clipped by container
      const unclippedOverflowElements = [];
      document.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.right > clientWidth + 2 && !isClipped(el) && el.tagName !== 'HTML' && el.tagName !== 'BODY') {
          unclippedOverflowElements.push({ tag: el.tagName, class: el.className, right: Math.round(r.right) });
        }
      });

      return {
        scrollWidth,
        clientWidth,
        overflowX,
        mirrorRect,
        overflowingElementsCount: unclippedOverflowElements.length,
        overflowingSamples: unclippedOverflowElements.slice(0, 3)
      };
    });

    const isPass = !audit.overflowX && audit.overflowingElementsCount === 0;
    const status = isPass ? '✅ PERFECT PASS (0 Anomalies)' : '❌ ANOMALY DETECTED';
    if (!isPass) totalAnomalies++;

    console.log(`[${dev.name}]`);
    console.log(`  Viewport Width: ${audit.clientWidth}px | Document ScrollWidth: ${audit.scrollWidth}px`);
    console.log(`  Mellis Oval Image Box: width=${Math.round(audit.mirrorRect?.width || 0)}px, height=${Math.round(audit.mirrorRect?.height || 0)}px`);
    console.log(`  Status: ${status}`);
    if (audit.overflowingElementsCount > 0) {
      console.log(`  Unclipped Overflowing Elements (${audit.overflowingElementsCount}):`, JSON.stringify(audit.overflowingSamples));
    }
    console.log('');

    await context.close();
  }

  await browser.close();
  console.log(`=== AUDIT COMPLETED: ${totalAnomalies} ANOMALIES FOUND (${DEVICE_PROFILES.length - totalAnomalies}/${DEVICE_PROFILES.length} DEVICES PASSED) ===`);
}

runAudit().catch(err => console.error(err));
