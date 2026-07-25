# Tests — harnais Playwright

L'application reste **zéro dépendance** ; seul ce harnais outille les tests.
Il sert les pages en statique et les pilote en Chromium headless, **l'API
Anthropic étant toujours mockée** (aucun appel réseau réel, aucune clé). C'est
le garde-fou que réclame le `CLAUDE.md` avant toute modification de doctrine.

## Lancer

```bash
npm install                       # une fois (n'installe que @playwright/test)
npx playwright install chromium   # une fois, EN LOCAL seulement
npm test                          # = playwright test
```

En session cloud, Chromium est préinstallé (`/opt/pw-browsers/chromium`) et
réutilisé automatiquement ; `npx playwright install` est inutile.

## Ce qui est couvert

| Fichier | Cas |
|---|---|
| `smoke.spec.js` | pipeline figuratif complet ; dialecte JSON hostile absorbé ; clé API manquante → bannière. |
| `cas-limites.spec.js` | relance sur planche pauvre (<4 figures) ; régime sensible + grammaire consolidée ; **épreuve de l'horoscope** (constatation sans démenti écartée) ; corpus + verdict persistés en IndexedDB. |
| `banc.spec.js` | le banc parcourt son échelle et trace la courbe. |

## Les pièces

- `mock-anthropic.js` — interception de `/v1/messages`. Flux **SSE** pour
  `index.html` (le parseur ne consomme que `content_block_delta`/`text_delta`),
  JSON **non-streamé** pour `banc.html` (`stream:false`). `passResponder()` lit
  le prompt injecté et rend la forme attendue **par passe** : figures pour
  l'observation, geste pour le second regard, prose pour relevé/synthèse/texte.
- `make-image.js` — génère un PNG structuré sans dépendance, pour que la
  binarisation en planches produise de vrais contours.

## En ajouter

Un cas hostile se pose en écrivant un `responder` qui renvoie du JSON déformé
(clés étrangères, prose autour, virgules traînantes, synonymes de geste) et en
vérifiant que le pipeline aboutit **sans bannière d'erreur** — la doctrine doit
absorber, jamais casser.
