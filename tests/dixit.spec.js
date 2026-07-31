// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');

/**
 * Régime projectif — dixit.html.
 *
 * L'outil montre l'œuvre entière et la soumet à trois postures indépendantes
 * (le naïf, le chercheur, le connaisseur), puis tisse les trois. Pas de
 * planches, pas de second regard, pas de grammaire : une prose par voix,
 * streamée comme dans l'app. On mocke l'API en SSE et on renvoie une prose
 * distincte selon la posture, repérée dans le prompt système.
 */

/** Rend une prose différente selon la posture injectée dans le système. */
function proseParPosture({ system }) {
  // La passe aveugle : système = SOCLE_SENSIBLE (aucun marqueur de posture).
  if (/sans le réduire à ce qu'il représente/.test(system))
    return "Le poids bascule à gauche, A3-B5 ; le quart droit reste vide et rien ne le retient. Le rythme se rompt en C4.";
  // Le naïf « à nu » : nourri du substrat (marqueur unique de l'amorce).
  if (/UN SOL T'EST DONNÉ/.test(system))
    return "Ce basculement à gauche m'oppresse avant que je sache quoi que ce soit ; le vide de droite me donne le vertige.";
  if (/TU ES LE NAÏF/.test(system))
    return "Je recule d'un pas. Ce rouge en bas me serre la gorge, il me revient une cuisine d'enfance.";
  if (/TU ES LE CHERCHEUR/.test(system))
    return "Le vide en haut à droite n'est pas innocent : on a retiré quelque chose là, et ça pèse.";
  if (/TU ES LE CONNAISSEUR/.test(system))
    return "La touche divisée et ce traitement de la lumière évoquent le post-impressionnisme ; l'intention semble décorative.";
  if (/Tu tisses\./.test(system) || /trois lectures/.test(system))
    return "Le même coin sombre devient chez l'un un souvenir, chez l'autre un manque, chez le dernier un parti pris de facture. Tous trois, pourtant, buttent sur ce bas de toile.";
  return "…";
}

async function chargeImage(page) {
  await page.setInputFiles('#file', {
    name: 'oeuvre.png', mimeType: 'image/png', buffer: pngBuffer(200, 160),
  });
}

test('dixit : trois regards indépendants + un tissage, quatre appels', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: proseParPosture });
  await page.goto('/dixit.html');

  await page.fill('#key', 'test-mock-key');
  await chargeImage(page);

  // L'image se prépare côté client (canvas) ; le bouton s'active ensuite.
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // Quatre voix rendues : les trois postures, dans l'ordre, plus le tissage.
  const voix = page.locator('.voix');
  await expect(voix).toHaveCount(4, { timeout: 30000 });
  await expect(page.locator('.voix.naif .prose')).toContainText('cuisine');
  await expect(page.locator('.voix.chercheur .prose')).toContainText('retiré quelque chose');
  await expect(page.locator('.voix.connaisseur .prose')).toContainText('post-impressionnisme');
  await expect(page.locator('.voix.tissage .prose')).toContainText('buttent sur ce bas');

  // Le naïf est présenté en premier (il ne doit pas être teinté par le savant).
  const first = voix.first();
  await expect(first).toHaveClass(/naif/);

  // Aucune panne, aucun regard perdu.
  await expect(page.locator('.banner')).toHaveCount(0);
  await expect(page.locator('.voix.fail')).toHaveCount(0);

  // Exactement quatre appels : 3 postures + tissage.
  expect(calls.length).toBe(4);
  await expect(page.locator('#run')).toBeEnabled();
});

test('dixit : sans tissage, trois appels et trois voix', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: proseParPosture });
  await page.goto('/dixit.html');

  await page.fill('#key', 'test-mock-key');
  await page.uncheck('#doTissage');
  await chargeImage(page);

  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  await expect(page.locator('.voix')).toHaveCount(3, { timeout: 30000 });
  await expect(page.locator('.voix.tissage')).toHaveCount(0);
  await expect(page.locator('.banner')).toHaveCount(0);
  expect(calls.length).toBe(3);
});

test('dixit : la passe aveugle nourrit le naïf, deux naïfs en comparatif', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: proseParPosture });
  await page.goto('/dixit.html');

  await page.fill('#key', 'test-mock-key');
  await page.check('#doAveugle');
  await chargeImage(page);

  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // Six voix : le regard nu, deux naïfs, chercheur, connaisseur, tissage.
  await expect(page.locator('.voix')).toHaveCount(6, { timeout: 30000 });

  // Le regard nu montre la silhouette binarisée et un relevé de forces sans nom.
  await expect(page.locator('.voix.nu')).toHaveCount(1);
  await expect(page.locator('.voix.nu .board')).toBeVisible();
  await expect(page.locator('.voix.nu .prose')).toContainText('bascule à gauche');

  // Le comparatif tient les deux naïfs côte à côte, distincts.
  const duo = page.locator('.compare .voix.naif');
  await expect(duo).toHaveCount(2);
  await expect(duo.nth(0)).toContainText('aveugle');            // en-tête
  await expect(duo.nth(0).locator('.prose')).toContainText('cuisine');
  await expect(duo.nth(1)).toContainText('à nu');               // en-tête
  await expect(duo.nth(1).locator('.prose')).toContainText('avant que je sache');

  await expect(page.locator('.voix.tissage')).toHaveCount(1);
  await expect(page.locator('.voix.fail')).toHaveCount(0);
  await expect(page.locator('.banner')).toHaveCount(0);

  // Six appels : aveugle + 2 naïfs + chercheur + connaisseur + tissage.
  expect(calls.length).toBe(6);
});

test('dixit : la table lumineuse trace la grille, les plans et les marqueurs', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: ({ system }) => {
    if (/TU ES LE NAÏF/.test(system)) return "Le rouge à gauche m'appelle. La masse tient en A3-E5, et un point en C3 me fixe.";
    if (/TU ES LE CHERCHEUR/.test(system)) return "Quelque chose se cache en bas, vers D4.";
    if (/TU ES LE CONNAISSEUR/.test(system)) return "Le bleu en haut, en B2, situe l'intention.";
    return "…";
  }});
  await page.goto('/dixit.html');

  await page.fill('#key', 'test-mock-key');
  await page.uncheck('#doTissage');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  // La table et ses deux plans (couleur + niveaux), plus les contrôles.
  await expect(page.locator('.table .planes img.pc')).toBeVisible({ timeout: 30000 });
  await expect(page.locator('.table .planes img.pl')).toHaveCount(1);
  await expect(page.locator('.tctrls .opL')).toHaveCount(1);

  // La matrice A–E × 1–5 : 8 lignes internes + 10 étiquettes.
  await expect(page.locator('.ov .grid line')).toHaveCount(8);
  await expect(page.locator('.ov .grid .glabel')).toHaveCount(10);

  // On attend la fin (trois voix) puis on compte les marqueurs tracés.
  await expect(page.locator('.voix')).toHaveCount(3, { timeout: 30000 });
  const nMk = await page.locator('.ov .markers g.mk').count();
  expect(nMk).toBeGreaterThanOrEqual(3);           // croix, zones, couleurs, bandes
  await expect(page.locator('.tlegend .chip')).toHaveCount(3); // une par voix

  await expect(page.locator('.voix.fail')).toHaveCount(0);
  await expect(page.locator('.banner')).toHaveCount(0);
  expect(calls.length).toBe(3);
});

test('dixit : sans clé, un bandeau le dit et rien n’est appelé', async ({ page }) => {
  const { calls } = await mockAnthropic(page, { responder: proseParPosture });
  await page.goto('/dixit.html');

  // On force l'image sans clé, puis on tente de lancer par le code (le bouton
  // reste désactivé sans clé — on vérifie le garde-fou du run()).
  await chargeImage(page);
  await page.evaluate(() => run());

  await expect(page.locator('.banner')).toContainText('clé API');
  expect(calls.length).toBe(0);
});
