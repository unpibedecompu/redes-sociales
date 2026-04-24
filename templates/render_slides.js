const { chromium } = require('playwright');
const path = require('path');

const htmlArg = process.argv[2];
if (!htmlArg) {
  console.error('Usage: node templates/render_slides.js <path/to/file.html>');
  process.exit(1);
}

const HTML_FILE = path.resolve(process.cwd(), htmlArg);
const OUT_DIR   = path.dirname(HTML_FILE);

(async () => {
  const browser = await chromium.launch();
  const page    = await browser.newPage();

  // Large viewport so no slide gets clipped during rendering
  await page.setViewportSize({ width: 1920, height: 1920 });

  await page.goto('file:///' + HTML_FILE.replace(/\\/g, '/'));
  await page.waitForLoadState('networkidle');

  const slides = await page.locator('.sl').all();
  console.log(`Found ${slides.length} slides`);

  for (let i = 0; i < slides.length; i++) {
    const num  = String(i + 1).padStart(2, '0');
    const file = path.join(OUT_DIR, `slide_${num}.png`);
    await slides[i].screenshot({ path: file });
    console.log(`Saved slide_${num}.png`);
  }

  await browser.close();
  console.log('Done.');
})();
