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

/* ────────────────────────────────────────────────────────────────────────
   MÉTRIQUES SPATIALES ET PHOTOMÉTRIQUES

   Elles NE mesurent PAS le pipeline actuel de Nephélé : celui-ci lit le contour
   par le langage et ne produit ni masque ni image reconstruite. Elles sont
   l'outillage de validation de la piste GÉNÉRATIVE « faire voir » (révéler une
   figure en la synthétisant dans la région source), du type Diamonds in the Sky
   (Horovicz et al., arXiv:2606.01361) / MDDS (Masked Delta Denoising Score,
   d'après Hertz et al., ICCV 2023). Fournies ici pour rendre une comparaison
   future BIEN DÉFINIE, et testées unitairement sur des entrées synthétiques.
   ──────────────────────────────────────────────────────────────────────── */

/** Aplati un tableau 2D (ou renvoie tel quel un tableau 1D). */
function flatten2D(m) {
  return Array.isArray(m[0]) ? [].concat(...m) : m.slice();
}

/**
 * Intersection over Union entre deux masques binaires (0/1, ou tout truthy).
 * IoU = |G ∩ C| / |G ∪ C|. Deux masques vides sont conventionnellement
 * identiques (IoU = 1). Sert à vérifier qu'une forme générée occupe l'espace
 * de la région source (seuil d'acceptation usuel > 0.5).
 */
function iou(gen, src) {
  const g = flatten2D(gen), s = flatten2D(src);
  if (g.length !== s.length) throw new Error('iou: masques de tailles différentes');
  let inter = 0, union = 0;
  for (let i = 0; i < g.length; i++) {
    const a = g[i] ? 1 : 0, b = s[i] ? 1 : 0;
    if (a & b) inter++;
    if (a | b) union++;
  }
  return union === 0 ? 1 : inter / union;
}

/** Erreur quadratique moyenne entre deux images (tableaux de pixels). */
function mse(a, b) {
  const x = flatten2D(a), y = flatten2D(b);
  if (x.length !== y.length) throw new Error('mse: images de tailles différentes');
  let s = 0;
  for (let i = 0; i < x.length; i++) { const d = x[i] - y[i]; s += d * d; }
  return x.length ? s / x.length : 0;
}

/**
 * SSIM GLOBAL (variante à fenêtre unique, non fenêtrée par gaussienne) entre
 * deux images. Mesure la préservation de structure (seuil d'acceptation usuel
 * > 0.7). Le SSIM fenêtré de la littérature est plus précis ; cette version
 * globale est exacte, sans dépendance, et suffit pour valider la préservation.
 *
 *   SSIM = (2μxμy + c1)(2σxy + c2) / ((μx²+μy²+c1)(σx²+σy²+c2))
 *   c1 = (k1·L)², c2 = (k2·L)²,  k1=0.01, k2=0.03, L = plage dynamique.
 */
function ssimGlobal(a, b, L = 255) {
  const x = flatten2D(a), y = flatten2D(b);
  if (x.length !== y.length) throw new Error('ssim: images de tailles différentes');
  const n = x.length || 1;
  const mx = x.reduce((s, v) => s + v, 0) / n;
  const my = y.reduce((s, v) => s + v, 0) / n;
  let vx = 0, vy = 0, cxy = 0;
  for (let i = 0; i < x.length; i++) {
    const dx = x[i] - mx, dy = y[i] - my;
    vx += dx * dx; vy += dy * dy; cxy += dx * dy;
  }
  vx /= n; vy /= n; cxy /= n;
  const c1 = (0.01 * L) ** 2, c2 = (0.03 * L) ** 2;
  return ((2 * mx * my + c1) * (2 * cxy + c2)) /
         ((mx * mx + my * my + c1) * (vx + vy + c2));
}

module.exports = { levenshtein, levRatio, tokens, cosine, iou, mse, ssimGlobal };
