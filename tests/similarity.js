// @ts-check
/**
 * Mesures de similarité textuelle, sans dépendance.
 *
 * Le banc mesure la dérive du VRAI modèle sur de VRAIES images (banc.html) ;
 * ces tests-ci pilotent un mock déterministe. La similarité sert donc ici à
 * deux choses concrètes et vérifiables :
 *   1. borner la dérive de la sortie NORMALISÉE face à des réponses déformées
 *      (le normaliseur doit rendre quelque chose de « proche » de la forme
 *      canonique malgré un JSON cassé) ;
 *   2. vérifier la stabilité des mesures du banc face à des paraphrases.
 *
 * On ne peut pas charger d'embeddings locaux dans l'environnement de test :
 * on s'en tient donc à Levenshtein (caractères) et à un cosinus sac-de-mots
 * (tokens), tous deux exacts et gratuits.
 */

/** Distance d'édition de Levenshtein (caractères). */
function levenshtein(a, b) {
  a = String(a); b = String(b);
  const m = a.length, n = b.length;
  if (!m) return n;
  if (!n) return m;
  let prev = new Array(n + 1);
  let cur = new Array(n + 1);
  for (let j = 0; j <= n; j++) prev[j] = j;
  for (let i = 1; i <= m; i++) {
    cur[0] = i;
    const ai = a.charCodeAt(i - 1);
    for (let j = 1; j <= n; j++) {
      const cost = ai === b.charCodeAt(j - 1) ? 0 : 1;
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
    }
    [prev, cur] = [cur, prev];
  }
  return prev[n];
}

/** Ratio de similarité de Levenshtein dans [0,1] (1 = identique). */
function levRatio(a, b) {
  a = String(a); b = String(b);
  const max = Math.max(a.length, b.length);
  return max === 0 ? 1 : 1 - levenshtein(a, b) / max;
}

/** Tokens : minuscules, accents conservés, ponctuation ôtée. */
function tokens(s) {
  return (String(s).toLowerCase().match(/[\p{L}\p{N}]+/gu)) || [];
}

/** Cosinus sac-de-mots dans [0,1] (1 = mêmes tokens en même proportion). */
function cosine(a, b) {
  const ta = tokens(a), tb = tokens(b);
  if (!ta.length || !tb.length) return ta.length === tb.length ? 1 : 0;
  const va = {}, vb = {};
  for (const t of ta) va[t] = (va[t] || 0) + 1;
  for (const t of tb) vb[t] = (vb[t] || 0) + 1;
  let dot = 0;
  for (const t in va) if (vb[t]) dot += va[t] * vb[t];
  const na = Math.sqrt(Object.values(va).reduce((s, x) => s + x * x, 0));
  const nb = Math.sqrt(Object.values(vb).reduce((s, x) => s + x * x, 0));
  return dot / (na * nb);
}

module.exports = { levenshtein, levRatio, tokens, cosine };
