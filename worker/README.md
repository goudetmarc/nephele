# Passerelle Nephélé — sortir la clé Anthropic du navigateur

Aujourd'hui l'app appelle Anthropic directement depuis le navigateur, avec la
clé saisie dans le champ « clé ». Cette clé est donc **lisible par quiconque
ouvre la page ou inspecte le réseau**. Ce petit Worker Cloudflare la déplace
côté serveur : le navigateur ne détient plus qu'un **jeton d'accès** à la
passerelle, et c'est le Worker qui ajoute la vraie clé.

C'est un **proxy mince** : il fait passer le flux SSE tel quel (aucune latence
ajoutée notable), n'ouvre pas de proxy public (sans le bon jeton, il refuse), et
ne stocke rien. L'app, elle, ne change pas — on la reconfigure, c'est tout.

## Déployer (avec ton compte Cloudflare)

```bash
npm i -g wrangler
wrangler login

cd worker
wrangler secret put ANTHROPIC_API_KEY   # colle ta vraie clé Anthropic
wrangler secret put ACCESS_TOKEN         # invente un jeton long et aléatoire
wrangler deploy
```

`wrangler deploy` affiche une URL du type
`https://nephele-gw.<ton-sous-domaine>.workers.dev`.

Un bon `ACCESS_TOKEN` : `openssl rand -hex 32`.

## Brancher l'app

Dans `index.html` **et** `banc.html`, panneau avancé :

- **Endpoint** → l'URL du Worker (`https://nephele-gw.…workers.dev`)
- **clé** → la valeur d'`ACCESS_TOKEN` (plus jamais la clé Anthropic)

C'est tout. L'app envoie le jeton dans l'en-tête `x-api-key` ; le Worker le
vérifie, le remplace par la vraie clé, et transmet à Anthropic. Le flux SSE
revient à l'identique.

## Robustesse (inférence lente / transitoire)

- **Retry + backoff exponentiel** sur `502/503/504` et sur erreur réseau (3
  tentatives, 250 ms → 500 ms). Le corps POST est bufferisé pour être rejoué ;
  on ne réessaie jamais une fois le flux commencé (pas de double génération).
- **Timeouts** : le plafond d'un Worker porte sur le *temps CPU*, pas sur
  l'*attente réseau* — streamer une longue réponse ne le fait donc généralement
  pas sauter. Sur le plan payant, `[limits] cpu_ms` (dans `wrangler.toml`) relève
  ce plafond. On n'active pas `node_compat` : inutile ici (API Web standard).

Tests de la logique de retry (sans réseau) :

```bash
cd worker && node --test
```

## Ce que ça règle, ce que ça ne règle pas

- ✅ La clé Anthropic ne quitte plus le serveur.
- ✅ L'accès est fermé par un jeton (pas de proxy ouvert au monde).
- ✅ Zéro changement de comportement du modèle, zéro dépendance ajoutée à l'app.
- ⚠️ Le jeton d'accès reste, lui, dans ton navigateur — mais le compromettre ne
  donne accès qu'à *ta passerelle* (que tu peux révoquer en changeant le
  secret), pas à ta clé Anthropic ni à ton compte.
- ⚠️ Ce n'est pas encore le corpus centralisé (voir le binding R2 commenté dans
  `wrangler.toml` — étape suivante quand tu voudras sortir le corpus du poste).

## Vérifier

```bash
# doit répondre 403 sans jeton
curl -i https://nephele-gw.<sous-domaine>.workers.dev/v1/models

# doit lister les modèles avec le bon jeton
curl -s https://nephele-gw.<sous-domaine>.workers.dev/v1/models \
  -H "x-api-key: <ACCESS_TOKEN>" -H "anthropic-version: 2023-06-01" | head
```
