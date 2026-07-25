// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic, passResponder } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');

/**
 * Smoke test de l'outil principal (index.html).
 *
 * L'API Anthropic est mockée : aucun appel réseau réel, aucune clé valide.
 * On vérifie que la tuyauterie tient de bout en bout — planches générées
 * côté client, pipeline lancé, figures rendues, synthèse produite, aucune
 * bannière d'erreur — et que la doctrine absorbe les dialectes JSON hostiles.
 */

async function chargeImage(page) {
  await page.setInputFiles('#file', {
    name: 'fixture.png', mimeType: 'image/png', buffer: pngBuffer(128, 128),
  });
}

test('pipeline figuratif complet, API mockée', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: passResponder() });
  await page.goto('/index.html');

  await page.fill('#key', 'test-mock-key');
  await chargeImage(page);

  // Les planches se génèrent côté client (canvas) ; le bouton s'active alors.
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  // Au moins une planche a été bâtie.
  await expect(page.locator('#platePrev').locator('img,canvas')).not.toHaveCount(0);

  await page.click('#run');

  // Signal de succès : la synthèse porte du texte.
  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });
  // Des figures ont été rendues.
  expect(await page.locator('.lec').count()).toBeGreaterThan(0);
  // Aucune bannière d'erreur, aucune carte en échec.
  await expect(page.locator('.banner')).toHaveCount(0);
  await expect(page.locator('.card.err')).toHaveCount(0);
  // Le bouton est rendu (run terminé) et l'interruption masquée.
  await expect(page.locator('#run')).toBeEnabled();
  await expect(page.locator('#halt')).toBeHidden();

  // Le pipeline a bien enchaîné ses passes (relevé + observations + second
  // regard + synthèse + texte + carnet ≈ une quinzaine d'appels).
  expect(calls.length).toBeGreaterThanOrEqual(10);
});

test('dialecte JSON hostile absorbé (clé anglaise, prose, virgules traînantes)', async ({ page }) => {
  // L'observation renvoie ses figures sous un nom anglais, noyées dans de la
  // prose, avec une virgule traînante ; le second regard renvoie un synonyme.
  const hostile = ({ content }) => {
    const blob = JSON.stringify(content || '');
    if (blob.includes('Tu es le second regard'))
      return 'Alors : {"action":"tient", "why":"elle tient le contour",}';
    if (blob.includes('Tu reçois une forme') || blob.includes('champ visuel'))
      return 'Voici ce que je vois.\n```json\n{"readings":[' +
        '{"name":"un chien","area":"A1"},{"name":"une tête","area":"B2"},' +
        '{"name":"une aile","area":"C3"},{"name":"un pont","area":"D4"},' +
        '{"name":"un cri","area":"B4"},]}\n```\nVoilà.';
    return 'Texte de synthèse, relevé ou carnet — peu importe ici.';
  };
  await mockAnthropic(page, { responder: hostile });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // Malgré le JSON déformé, le pipeline aboutit et rend des figures.
  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });
  expect(await page.locator('.lec').count()).toBeGreaterThan(0);
  await expect(page.locator('.banner')).toHaveCount(0);
});

test('clé API manquante : bannière, pas de plantage', async ({ page }) => {
  await mockAnthropic(page, { responder: passResponder() });
  await page.goto('/index.html');
  // Pas de clé.
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // run() s'arrête proprement sur une bannière explicite.
  await expect(page.locator('.banner')).toContainText(/cl[ée]/i, { timeout: 5000 });
});
