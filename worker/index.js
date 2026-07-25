/**
 * Passerelle Nephélé — Cloudflare Worker.
 *
 * But unique : garder la clé Anthropic CÔTÉ SERVEUR. Aujourd'hui l'app la met
 * dans le navigateur (lisible par quiconque ouvre la page). Ici, le navigateur
 * ne détient plus qu'un JETON D'ACCÈS à la passerelle ; c'est le Worker qui
 * ajoute la vraie clé et parle à Anthropic.
 *
 * Le Worker est un proxy mince : il ne bufferise pas, il fait passer le flux
 * SSE tel quel (streaming) et les erreurs telles quelles. Il n'ouvre pas un
 * proxy public : sans le bon jeton, il refuse (sinon n'importe qui brûlerait
 * ta clé).
 *
 * Secrets attendus (posés par `wrangler secret put`, jamais en clair) :
 *   ANTHROPIC_API_KEY  — la vraie clé Anthropic
 *   ACCESS_TOKEN       — le jeton que l'app enverra (dans le champ « clé »)
 *
 * Wiring côté app : mettre le champ « Endpoint » sur l'URL du Worker, et le
 * champ « clé » sur la valeur d'ACCESS_TOKEN. Aucune autre modification.
 */

const ANTHROPIC = "https://api.anthropic.com";
const ALLOW_HEADERS =
  "content-type, x-api-key, authorization, anthropic-version, anthropic-dangerous-direct-browser-access";

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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Préflight CORS.
    if (request.method === "OPTIONS")
      return new Response(null, { status: 204, headers: cors() });

    // Seules les routes de l'API Messages / Models passent.
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

    let resp;
    try {
      resp = await fetch(cible, {
        method: request.method,
        headers,
        body: request.method === "POST" ? request.body : undefined,
        // laisse passer le corps en flux quand il y en a un
        ...(request.method === "POST" ? { duplex: "half" } : {}),
      });
    } catch (e) {
      return erreur(502, "upstream", "Anthropic injoignable : " + (e && e.message));
    }

    // Renvoie la réponse telle quelle (flux SSE compris) + en-têtes CORS.
    const out = new Headers(resp.headers);
    for (const [k, v] of Object.entries(cors())) out.set(k, v);
    return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: out });
  },
};
