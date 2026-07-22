const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const relPath = process.argv[2];
  if (!relPath) { console.error('Usage: node render_slides.js <path/to/file.html>'); process.exit(1); }

  const htmlPath = path.resolve(process.cwd(), relPath);
  if (!fs.existsSync(htmlPath)) { console.error('File not found:', htmlPath); process.exit(1); }

  const outDir = path.dirname(htmlPath);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 600, height: 800 });
  await page.goto('file://' + htmlPath);
  await page.waitForLoadState('networkidle');

  // Count slides
  const total = await page.evaluate(() => window.slides ? window.slides.length : document.querySelectorAll('.ig-item').length);
  console.log(`Rendering ${total} slides…`);

  for (let i = 0; i < total; i++) {
    await page.evaluate((idx) => window.goTo(idx), i);
    await page.waitForTimeout(400);
    const frame = await page.$('.ig-frame');
    const num = String(i + 1).padStart(2, '0');
    const outPath = path.join(outDir, `slide_${num}.png`);
    await frame.screenshot({ path: outPath });
    console.log(`  saved slide_${num}.png`);
  }

  await browser.close();
  console.log(`Done. ${total} slides saved to ${outDir}`);
}

main().catch(e => { console.error(e); process.exit(1); });
