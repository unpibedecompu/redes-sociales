const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 700, height: 900 });
  const file = path.resolve(__dirname, 'Geoffrey_Hinton.html').replace(/\\/g, '/');
  await page.goto('file:///' + file);
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: path.join(__dirname, 'fullpage.png'), fullPage: true });
  await browser.close();
  console.log('done');
})();
