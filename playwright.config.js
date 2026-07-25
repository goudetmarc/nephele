// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Harnais de test de Nephélé.
 *
 * L'application est une page HTML sans build : on la sert statiquement
 * (python3 -m http.server) et on la pilote en Chromium headless, l'API
 * Anthropic étant systématiquement mockée par interception de requête
 * (voir tests/mock-anthropic.js). Aucun appel réseau réel, aucune clé.
 *
 * Chromium est préinstallé dans l'environnement (PLAYWRIGHT_BROWSERS_PATH) ;
 * on pointe dessus explicitement pour ne rien télécharger.
 */

const PORT = process.env.PORT || 8099;
const chromiumPath = '/opt/pw-browsers/chromium';
const fs = require('fs');
const hasPreinstalled = fs.existsSync(chromiumPath);

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Réutilise le Chromium préinstallé de l'environnement cloud ;
        // en local, Playwright retombe sur son propre binaire.
        launchOptions: hasPreinstalled ? { executablePath: chromiumPath } : {},
      },
    },
  ],
  webServer: {
    command: `python3 -m http.server ${PORT}`,
    url: `http://127.0.0.1:${PORT}/index.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});
