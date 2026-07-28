/**
 * Passerelle Nephélé — Cloudflare Worker.
 *
 * But unique : garder la clé Anthropic CÔTÉ SERVEUR. Le navigateur ne détient
 * plus qu'un JETON D'ACCÈS ; c'est le Worker qui ajoute la vraie clé et parle à
 * Anthropic, en laissant passer le flux SSE tel quel (streaming, pas de buffer).
 *
 * Robustesse (objectif : appels vers une inférence potentiellement lente/lourde)
 *   - Retry avec backoff exponentiel sur 502/503/504 et sur erreur réseau.
 *   - Le corps POST est BUFFERISÉ avant la boucle, pour pouvoir être renvoyé
 *     tel quel à chaque tentative.
 *   - On ne réessaie JAMAIS une fois le flux commencé : un code 5xx arrive avant
 *     tout octet de réponse, donc réessayer là est sûr ; une fois le corps
 *     streamé, on le laisse passer sans le rejouer (pas de double génération).
 *
 * Secrets attendus (via `wrangler secret put`, jamais en clair) :
 *   ANTHROPIC_API_KEY  — la vraie clé Anthropic
 *   ACCESS_TOKEN       — le jeton que l'app enverra (dans le champ « clé »)
 */

const ANTHROPIC = "https://api.anthropic.com";
const ALLOW_HEADERS =
  "content-type, x-api-key, authorization, anthropic-version, anthropic-dangerous-direct-browser-access";
const RETRYABLE = new Set([502, 503, 504]);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function cors(extra = {}) {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": ALLOW_HEADERS,
    "access-control-max-age": "86400",
    ...extra,
  };
}

function erreur(status, type, message) {
  return new Response(JSON.stringify({ error: { type, message } }), {
    status,
    headers: cors({ "content-type": "application/json" }),
  });
}

/**
 * Appelle l'amont avec retry + backoff exponentiel. Réessaie sur 502/503/504 et
 * sur erreur réseau, jamais au-delà de `attempts`. `sleepFn` est injectable pour
 * les tests.
 */
export async function proxyWithRetry(fetchImpl, target, init, opts = {}) {
  const { attempts = 3, base = 250, sleepFn = sleep } = opts;
  let derniereErreur;
  for (let i = 0; i < attempts; i++) {
    let resp;
    try {
      resp = await fetchImpl(target, init);
    } catch (e) {
      derniereErreur = e;
      if (i < attempts - 1) {
        await sleepFn(base * 2 ** i);
        continue;
      }
      throw e;
    }
    if (RETRYABLE.has(resp.status) && i < attempts - 1) {
      await sleepFn(base * 2 ** i);
      continue;
    }
    return resp; // succès, ou échec non-réessayable, ou dernière tentative
  }
  throw derniereErreur;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS")
      return new Response(null, { status: 204, headers: cors() });

    if (!/^\/v1\/(messages|models)\b/.test(url.pathname))
      return erreur(404, "not_found", "route non proxifiée");

    // Jeton d'accès à la passerelle — PAS la clé Anthropic.
    const token =
      request.headers.get("x-api-key") ||
      (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
    if (!env.ACCESS_TOKEN)
      return erreur(500, "config", "ACCESS_TOKEN non configuré sur la passerelle");
    if (token !== env.ACCESS_TOKEN)
      return erreur(403, "forbidden", "jeton d'accès invalide");
    if (!env.ANTHROPIC_API_KEY)
      return erreur(500, "config", "ANTHROPIC_API_KEY non configuré sur la passerelle");

    // Réécrit la requête vers Anthropic avec la vraie clé.
    const cible = ANTHROPIC + url.pathname + url.search;
    const headers = new Headers(request.headers);
    headers.set("x-api-key", env.ANTHROPIC_API_KEY);
    headers.set("anthropic-version", request.headers.get("anthropic-version") || "2023-06-01");
    headers.delete("authorization");
    headers.delete("host");

    // Bufferise le corps POST une fois, pour pouvoir le rejouer à chaque essai.
    const body = request.method === "POST" ? await request.arrayBuffer() : undefined;
    const init = { method: request.method, headers, body };

    let resp;
    try {
      resp = await proxyWithRetry(fetch, cible, init);
    } catch (e) {
      return erreur(502, "upstream", "Anthropic injoignable après plusieurs essais : " + (e && e.message));
    }

    // Renvoie la réponse telle quelle (flux SSE compris) + en-têtes CORS.
    const out = new Headers(resp.headers);
    for (const [k, v] of Object.entries(cors())) out.set(k, v);
    return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: out });
  },
};
