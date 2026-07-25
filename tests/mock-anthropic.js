// @ts-check
/**
 * Mock de l'API Anthropic pour les tests Playwright.
 *
 * Nephélé appelle `POST {base}/v1/messages` en streaming SSE et ne consomme
 * que les événements `content_block_delta` / `text_delta` (cf. ask() dans
 * index.html) ; `message_start`, `content_block_start` et `message_stop`
 * sont ignorés par le parseur, un événement `error` fait lever ask().
 *
 * On intercepte donc la requête et on renvoie un flux SSE minimal mais
 * fidèle : le texte voulu, découpé en quelques deltas pour exercer le
 * réassemblage incrémental. Le texte renvoyé est choisi par `responder`
 * en fonction de la requête (système + contenu), ce qui permet de rendre
 * une forme JSON adaptée à chaque passe.
 */

/** Encode un texte en flux SSE de deltas texte, comme le vrai endpoint. */
function sseFromText(text, { chunks = 3 } = {}) {
  const parts = [];
  const size = Math.max(1, Math.ceil(text.length / chunks));
  for (let i = 0; i < text.length; i += size) parts.push(text.slice(i, i + size));
  let body = 'event: message_start\ndata: {"type":"message_start"}\n\n';
  body += 'event: content_block_start\ndata: {"type":"content_block_start","index":0}\n\n';
  for (const p of parts) {
    const ev = { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: p } };
    body += 'event: content_block_delta\ndata: ' + JSON.stringify(ev) + '\n\n';
  }
  body += 'event: message_stop\ndata: {"type":"message_stop"}\n\n';
  body += 'data: [DONE]\n\n';
  return body;
}

/**
 * Installe l'interception sur une page Playwright.
 *
 * @param {import('@playwright/test').Page} page
 * @param {object} opts
 * @param {(req: {system: string, content: any, raw: object}) => string} opts.responder
 *        Reçoit la requête décodée, renvoie le TEXTE que le modèle doit produire.
 * @param {() => void} [opts.onCall] appelé à chaque requête interceptée (compteur).
 * @param {object[]} [opts.models] liste renvoyée par /v1/models (défaut : un modèle).
 * @param {boolean} [opts.stream] true (défaut) = flux SSE comme index.html ;
 *        false = corps JSON non-streamé `{content:[{type:"text",text}]}` comme banc.html.
 */
async function mockAnthropic(page, { responder, onCall, models, stream = true } = {}) {
  const calls = [];

  // Liste des modèles — certaines UI la chargent avant de pouvoir lancer.
  await page.route('**/v1/models*', async (route) => {
    const data = models || [
      { id: 'claude-opus-5', display_name: 'Claude Opus 5', type: 'model' },
      { id: 'claude-sonnet-5', display_name: 'Claude Sonnet 5', type: 'model' },
      { id: 'claude-haiku-4-5', display_name: 'Claude Haiku 4.5', type: 'model' },
    ];
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data, has_more: false, first_id: null, last_id: null }),
    });
  });

  await page.route('**/v1/messages', async (route) => {
    const req = route.request();
    let raw = {};
    try { raw = JSON.parse(req.postData() || '{}'); } catch (_) {}
    const system = typeof raw.system === 'string' ? raw.system : '';
    const userMsg = (raw.messages && raw.messages[0]) || {};
    const content = userMsg.content;
    const info = { system, content, raw };
    calls.push(info);
    if (onCall) onCall(info);

    const text = String(responder ? responder(info) : '{}');
    if (stream) {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        headers: { 'cache-control': 'no-cache' },
        body: sseFromText(text),
      });
    } else {
      // Forme de banc.html : réponse JSON complète, non streamée.
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'msg_mock', type: 'message', role: 'assistant',
          content: [{ type: 'text', text }],
          model: raw.model || 'mock', stop_reason: 'end_turn',
        }),
      });
    }
  });

  return { calls };
}

/**
 * Répondeur fidèle aux passes de Nephélé : il lit le prompt injecté dans la
 * requête et renvoie la forme attendue par le normaliseur de chaque passe.
 * - observation (P_AVEUGLE / P_SENSIBLE)      → JSON de figures (≥4, pas de relance)
 * - second regard (P_SECOND / …_SENSIBLE)     → JSON de geste
 * - grammaire (P_GRAMMAIRE)                    → {entrees:[…]}
 * - relevé / synthèse / texte / carnet         → prose brute
 */
function passResponder({ figures = 5 } = {}) {
  const zones = ['A1', 'B2', 'C3', 'D4', 'B4', 'C2', 'A3', 'D1'];
  const figuresJSON = () => JSON.stringify({
    seuil: 'B2',
    figures: Array.from({ length: figures }, (_, i) => ({
      nom: 'figure ' + (i + 1),
      zone: zones[i % zones.length],
      par_ou: 'pars de la pointe en ' + zones[i % zones.length] + ', descends le bord',
      parties: [{ partie: 'le dos', ou: zones[i % zones.length] }],
      tenue: 0.7,
      ecart: 0.5,
    })),
  });
  const gesteJSON = () => JSON.stringify({
    geste: 'affine',
    pourquoi: 'presque juste, orientation à corriger',
    nom: 'figure affinée',
    zone: 'B2',
    par_ou: 'pars du creux en B2 et remonte',
  });
  const grammaireJSON = () => JSON.stringify({ entrees: [] });

  return ({ content }) => {
    const blob = JSON.stringify(content || '');
    // Le second regard doit être testé AVANT la synthèse : la synthèse cite
    // « passée par un second regard », mais seul le prompt du second regard
    // s'ouvre par « Tu es le second regard ».
    if (blob.includes('Tu es le second regard')) return gesteJSON();
    if (blob.includes("Tu re\\u00e7ois une forme") || blob.includes('Tu reçois une forme')) return figuresJSON();
    if (blob.includes('champ visuel')) return figuresJSON();
    if (blob.includes('grammaire des formes')) return grammaireJSON();
    if (blob.includes('Relève la géométrie') || blob.includes('Rel\\u00e8ve la g\\u00e9om\\u00e9trie'))
      return 'Cadre orthogonal, horizon bas au tiers, une diagonale montante de A4 vers C1.';
    if (blob.includes('figures proposées') || blob.includes('figures propos\\u00e9es'))
      return 'À voir en premier : la figure 1 en A1 tient le contour. Deux lectures se partagent B2.';
    if (blob.includes('texte court') || blob.includes('Écris un texte'))
      return 'Un bord, puis rien, puis un autre bord qui répond.';
    if (blob.includes('carnet de méthode') || blob.includes('carnet de m\\u00e9thode'))
      return 'Descendre d’échelle avant de nommer. Chercher la tête en premier.';
    // Défaut prudent : une forme qui satisfait figures ET geste à la fois.
    return JSON.stringify({ figures: JSON.parse(figuresJSON()).figures, geste: 'confirme', pourquoi: 'ok' });
  };
}

module.exports = { mockAnthropic, sseFromText, passResponder };
