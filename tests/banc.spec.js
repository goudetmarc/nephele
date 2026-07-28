// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');
const { cosine, levRatio } = require('./similarity');

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

test('mesure : l’esquive ne compte pas « est »/« pas », mais compte les locutions', async ({ page }) => {
  await page.goto('/banc.html');
  const r = await page.evaluate(() => {
    // Prose sans esquive, mais riche en « est » et « pas ».
    const neutre = "L'image est sombre, la masse est dense et rien ne bascule pas vers le bas.";
    // Vraie esquive : locutions + mots simples.
    const esquive = "Il est difficile de déterminer ; cela semble ambigu et pourrait varier.";
    return { neutre: mesure(neutre).brut.esq, esquive: mesure(esquive).brut.esq };
  });
  // Aucune esquive comptée sur la prose neutre (le bug « est »/« pas » est fermé).
  expect(r.neutre).toBe(0);
  // La vraie esquive est bien détectée (locution « il est difficile » + semble/ambigu/pourrait).
  expect(r.esquive).toBeGreaterThanOrEqual(4);
});

test('mesure : les lexiques couvrent les angles morts (chameau, coins composés, jargon)', async ({ page }) => {
  await page.goto('/banc.html');
  const r = await page.evaluate(() => ({
    // « chameau » — l'exemple canonique de la doctrine — doit compter en figuration.
    chameau: mesure("On dirait un chameau et une péninsule.").brut.concret,
    // Les coins composés que la doctrine écrit doivent compter en ancrage.
    coin: mesure("La masse occupe le bas-gauche, le haut-droite reste vide.").brut.pos,
    // Les mots creux ajoutés doivent compter en jargon.
    jargon: mesure("Un rendu chatoyant, spectaculaire, flamboyant.").brut.creux,
  }));
  expect(r.chameau).toBeGreaterThanOrEqual(2);   // chameau + péninsule
  expect(r.coin).toBeGreaterThanOrEqual(2);      // bas-gauche + haut-droite
  expect(r.jargon).toBeGreaterThanOrEqual(3);    // chatoyant + spectaculaire + flamboyant
});

test('mesure : stable sous paraphrase (la dérive du juge reste bornée)', async ({ page }) => {
  await page.goto('/banc.html');
  // Deux paraphrases proches : même contenu, mots creux identiques, syntaxe
  // différente. Le banc ne doit pas noter le jargon très différemment.
  const a = 'Un rendu chatoyant et spectaculaire, vraiment flamboyant.';
  const b = 'Un rendu chatoyant, spectaculaire et aussi flamboyant.';
  // On confirme d'abord que ce sont bien des paraphrases (similarité élevée).
  expect(cosine(a, b)).toBeGreaterThan(0.6);
  expect(levRatio(a, b)).toBeGreaterThan(0.6);

  const m = await page.evaluate(([x, y]) => ({
    ja: mesure(x).brut.creux, jb: mesure(y).brut.creux,
  }), [a, b]);
  // Jargon compté identiquement malgré la reformulation : le juge ne dérive pas.
  expect(Math.abs(m.ja - m.jb)).toBeLessThanOrEqual(1);
});
