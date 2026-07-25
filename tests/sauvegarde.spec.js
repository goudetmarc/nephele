// @ts-check
const { test, expect } = require('@playwright/test');
const { mockAnthropic, passResponder } = require('./mock-anthropic');
const { pngBuffer } = require('./make-image');

/**
 * Sauvegarde durable du corpus (File System Access), sans backend.
 *
 * Le vrai sélecteur de dossier ne peut pas s'ouvrir en headless ; on injecte
 * un handle de dossier factice (en mémoire) et on vérifie que bkpEcrire()
 * y recopie bien l'archive du corpus. C'est le chemin d'écriture qui compte.
 */
test('le corpus se recopie dans le dossier lié', async ({ page }) => {
  await mockAnthropic(page, { responder: passResponder() });
  await page.goto('/index.html');
  await page.fill('#key', 'test-mock-key');
  await page.setInputFiles('#file', {
    name: 'fixture.png', mimeType: 'image/png', buffer: pngBuffer(128, 128),
  });
  await expect(page.locator('#run')).toBeEnabled({ timeout: 10000 });
  await page.click('#run');
  await expect(page.locator('.card.synth .prose')).toContainText(/\S/, { timeout: 30000 });

  const res = await page.evaluate(async () => {
    const files = {};
    const fakeHandle = {
      name: 'dossier-test',
      async queryPermission() { return 'granted'; },
      async requestPermission() { return 'granted'; },
      async getFileHandle(nom) {
        return { async createWritable() {
          return { async write(c) { files[nom] = c; }, async close() {} };
        } };
      },
    };
    const ok = await bkpEcrire(fakeHandle, false);
    return { ok, noms: Object.keys(files), corpus: files['nephele-corpus.json'] };
  });

  expect(res.ok).toBe(true);
  expect(res.noms).toContain('nephele-corpus.json');
  const archive = JSON.parse(res.corpus);
  // La séance qu'on vient de jouer est bien dans l'archive écrite sur disque.
  expect(archive.seances.length).toBe(1);
  expect(archive.seances[0].lectures.length).toBeGreaterThan(0);
});

test('sans dossier lié, la sauvegarde ne casse rien', async ({ page }) => {
  await page.goto('/index.html');
  // bkpAuto() ne doit rien tenter tant qu'aucun dossier n'est lié.
  const ok = await page.evaluate(async () => {
    await bkpAuto();               // ne doit pas lever
    return (await bkpEcrire(null)) === false;  // pas de handle → false
  });
  expect(ok).toBe(true);
});
