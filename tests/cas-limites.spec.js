// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic, passResponder } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');

/**
 * Cas limites — la doctrine et le pipeline aux endroits qui comptent :
 * la relance sur planche pauvre, le régime sensible, l'épreuve de l'horoscope
 * (une constatation sans démenti n'entre pas dans la grammaire), et
 * l'enregistrement du corpus + verdicts.
 */

async function chargeImage(page, n = 128) {
  await page.setInputFiles('#file', {
    name: 'fixture.png', mimeType: 'image/png', buffer: pngBuffer(n, n),
  });
}

/** Répond en figures/geste/prose selon le prompt injecté. */
function figuresList(count, withDementi) {
  const zones = ['A1', 'B2', 'C3', 'D4', 'B4', 'C2'];
  return Array.from({ length: count }, (_, i) => {
    const f = { nom: 'constatation ' + (i + 1), zone: zones[i % zones.length],
      configuration: 'masse dense en ' + zones[i % zones.length] + ' + quadrant opposé vide',
      effet: 'l’image bascule' };
    if (withDementi) f.dementi_possible = 'une image équilibrée où la même masse ne fait pas basculer';
    return f;
  });
}

test('planche pauvre : relance automatique puis complétion', async ({ page }) => {
  // Première observation sous le quota (2 figures) ; à la relance (marquée par
  // « Recommence »/« échec de méthode ») on en rend six.
  const responder = ({ content }) => {
    const blob = JSON.stringify(content || '');
    if (blob.includes('Tu es le second regard')) return JSON.stringify({ geste: 'confirme', pourquoi: 'ok' });
    if (blob.includes('Tu reçois une forme')) {
      // « Recommence » n'apparaît que dans la consigne de relance ; « échec de
      // méthode » est déjà dans P_AVEUGLE et ne distingue donc rien.
      const relance = blob.includes('Recommence');
      return JSON.stringify({ figures: figuresList(relance ? 6 : 2, false) });
    }
    return 'prose de synthèse / relevé / carnet.';
  };
  const { calls } = await mockAnthropic(page, { responder });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });
  // La relance a bien été émise au moins une fois…
  const relances = calls.filter(c => JSON.stringify(c.content).includes('Recommence'));
  expect(relances.length).toBeGreaterThanOrEqual(1);
  // …et le pipeline aboutit malgré la pénurie initiale.
  expect(await page.locator('.lec').count()).toBeGreaterThan(0);
  await expect(page.locator('.card.err')).toHaveCount(0);
});

/** Répondeur du régime sensible. `horoscope` insère une constatation sans démenti. */
function sensibleResponder({ horoscope = false } = {}) {
  return ({ content }) => {
    const blob = JSON.stringify(content || '');
    if (blob.includes('grammaire des formes')) {
      return JSON.stringify({
        entrees: [{
          configuration: 'masse dense excentrée + quadrant opposé vide',
          effet: 'chute', pourquoi: 'rien ne retient la masse',
          dementi_possible: 'une image équilibrée sans chute',
          matieres: ['nuage'], vues: 1,
        }],
        retirees: horoscope ? ['le rouge domine → passion'] : [],
      });
    }
    if (blob.includes('Tu es le second regard'))
      return JSON.stringify({ geste: 'affine', pourquoi: 'rapport à resserrer' });
    if (blob.includes('champ visuel')) {
      const list = figuresList(4, true);
      // L'horoscope : une configuration sans démenti imaginable.
      if (horoscope) list.push({ nom: 'le rouge domine', zone: 'C2', configuration: 'le rouge domine', effet: 'passion' });
      return JSON.stringify({ constatations: list });
    }
    return 'prose sensible (relevé / synthèse / texte / carnet).';
  };
}

test('régime sensible : grammaire consolidée et rendue', async ({ page }) => {
  await mockAnthropic(page, { responder: sensibleResponder() });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  // Bascule vers le régime sensible ; les planches couleur se régénèrent.
  await page.click('#regimes button[data-reg="sens"]');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });
  // La carte grammaire existe, ne tombe pas en erreur, et rend au moins une entrée.
  await expect(page.locator('.card.gram')).toBeVisible();
  await expect(page.locator('.card.gram.err')).toHaveCount(0);
  expect(await page.locator('.card.gram .lec').count()).toBeGreaterThanOrEqual(1);
});

test('épreuve de l’horoscope : une constatation sans démenti n’est pas exploitable', async ({ page }) => {
  // Cinq constatations sont rendues, dont une sans démenti (« le rouge domine
  // → passion »). Le code n’en retient que quatre comme rapports exploitables :
  // sans démenti imaginable, le rapport serait vrai de tout, donc écarté.
  await mockAnthropic(page, { responder: sensibleResponder({ horoscope: true }) });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  await page.click('#regimes button[data-reg="sens"]');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');

  await expect(page.locator('.card.gram')).toBeVisible({ timeout: 30000 });

  // Chaque planche sensible rend 5 constatations dont une sans démenti
  // (« le rouge domine → passion ») ; le code n'en retient que 4 par planche.
  // Le nombre de rapports exploitables vaut donc (constatations sens − planches),
  // ce qui prouve que la constatation-horoscope a été écartée.
  const stats = await page.evaluate(() => ({
    planches: state.planches.length,
    sens: state.lectures.filter(L => (L.r || 'fig') === 'sens').length,
  }));
  const sText = (await page.locator('.card.gram .s').textContent()) || '';
  const exploitables = parseInt((sText.match(/\d+/) || ['0'])[0], 10);
  expect(exploitables).toBe(stats.sens - stats.planches);
  expect(exploitables).toBeLessThan(stats.sens); // au moins un rapport écarté
});

test('corpus : la séance s’enregistre et le verdict se persiste', async ({ page }) => {
  await mockAnthropic(page, { responder: passResponder() });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  await chargeImage(page);
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');
  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });

  // La séance est écrite en IndexedDB.
  const nSeances = await page.evaluate(async () => (await corpusTous()).length);
  expect(nSeances).toBe(1);

  // Un clic sur « je la vois » enregistre le verdict.
  await page.locator('.lec .nb.juste').first().click();
  await expect.poll(async () =>
    page.evaluate(async () => {
      const s = (await corpusTous())[0];
      return Object.values(s.verdicts || {}).filter(v => v === 'juste').length;
    }), { timeout: 5000 }
  ).toBeGreaterThanOrEqual(1);
});
