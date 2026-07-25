// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');

/**
 * Smoke test du banc d'abstraction (banc.html).
 *
 * Contrairement à index.html, banc.html appelle l'API en NON-streamé et sur
 * un endpoint codé en dur : on mocke donc au niveau réseau, avec une réponse
 * JSON complète `{content:[{type:"text",text}]}` (stream:false).
 */

test('le banc parcourt son échelle et rend une courbe', async ({ page }) => {
  const { calls } = await mockAnthropic(page, {
    stream: false,
    responder: () =>
      'Dans ce champ, la masse sombre occupe A3-B5 ; le quart droit est vide. ' +
      'Une diagonale monte de A4 vers C1. Rien ne semble figuratif ici.',
  });
  await page.goto('/banc.html');

  await page.fill('#key', 'test-mock-key');
  await page.setInputFiles('#file', {
    name: 'fixture.png', mimeType: 'image/png', buffer: pngBuffer(160, 160),
  });

  // L'échelle de recul se bâtit côté client ; le bouton s'active alors.
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // Signal de complétion : la courbe SVG est tracée dans #viz.
  await expect(page.locator('#viz svg')).toBeVisible({ timeout: 30000 });
  await expect(page.locator('.banner')).toHaveCount(0);
  await expect(page.locator('#run')).toBeEnabled();

  // Au moins un appel par barreau de l'échelle.
  expect(calls.length).toBeGreaterThanOrEqual(3);
});
