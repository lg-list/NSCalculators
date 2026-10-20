const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const output = __dirname;
  const observations = [];
  try {
    for (const width of [1366, 390]) {
      const context = await browser.newContext({ viewport: { width, height: width === 1366 ? 1200 : 844 } });
      await context.route('**/*', route => {
        const url = new URL(route.request().url());
        return url.hostname !== 'nscalculators.com' || url.pathname.startsWith('/cdn-cgi/') ? route.abort() : route.continue();
      });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const response = await page.goto('https://nscalculators.com/area-calculator/', { waitUntil: 'networkidle' });
      assert.equal(response.status(), 200);
      assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'), 'https://nscalculators.com/area-calculator/');
      await page.locator('#geo_shape').selectOption('rectangle');
      await page.locator('#geo_input_unit').selectOption('ft');
      await page.locator('#geo_output_unit').selectOption('sqft');
      await page.locator('#geo_length').fill('12');
      await page.locator('#geo_width').fill('14');
      await page.locator('#geo_add_section').click();
      assert.match(await page.locator('#geo_total_value').innerText(), /168/);
      await page.locator('#geo_length').fill('8');
      await page.locator('#geo_width').fill('8');
      await page.locator('#geo_add_section').click();
      assert.match(await page.locator('#geo_total_value').innerText(), /^232 .* across 2 sections$/);
      assert.equal(await page.locator('#geo_total_list li').count(), 2);
      await page.locator('#geo_output_unit').selectOption('sqm');
      assert.match(await page.locator('#geo_total_value').innerText(), /^21\.55350528 /);
      await page.locator('#geo_output_unit').selectOption('sqft');
      const totalText = await page.locator('#geo_total_value').innerText();
      assert.match(totalText, /^232 /);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      if (width === 1366) await page.evaluate(() => window.scrollTo(0, 0));
      else await page.locator('#geo_total_panel').scrollIntoViewIfNeeded();
      const screenshot = width === 1366 ? 'area-demo-desktop.png' : 'area-demo-mobile.png';
      await page.screenshot({ path: path.join(output, screenshot) });
      await page.locator('#geo_total_list [data-geo-remove="1"]').click();
      assert.match(await page.locator('#geo_total_value').innerText(), /^168 /);
      await page.locator('#geo_clear_sections').click();
      assert.equal(await page.locator('#geo_total_panel').isVisible(), false);
      await page.locator('#geo_input_unit').selectOption('in');
      await page.locator('#geo_length').fill('4');
      await page.locator('#geo_width').fill('4');
      const exactTileResult = await page.locator('#result').innerText();
      assert.match(exactTileResult, /0\.111111/);
      observations.push({ width, totalText, screenshot, inputSections: [[12, 14], [8, 8]], squareFeet: 232,
        squareMeters: 21.55350528, exactFourInchSquare: { squareFeet: 16 / 144, resultText: exactTileResult } });
      assert.deepEqual(errors, []);
      await context.close();
    }
    const result = { source: 'Live NS Calculators UI, Playwright', sourceUrl: 'https://nscalculators.com/area-calculator/',
      capturedAt: new Date().toISOString(), externalMessagesSent: 0, observations };
    fs.writeFileSync(path.join(output, 'demo-checks.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
