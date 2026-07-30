# Nephélé en local — modèle sur la machine

Faire tourner Nephélé **sans appeler l'API Anthropic**, avec un VLM (modèle
vision-langage) servi localement sur le Mac. Aucun changement dans `main` :
`ask()` continue de parler le format Anthropic, un petit **proxy traducteur**
fait le pont vers le modèle local.

```
Nephélé (navigateur)  ──/v1/messages (Anthropic)──▶  LiteLLM :4000
                                                        │  traduit
                                                        ▼
                                          LM Studio :1234 (OpenAI, MLX)
                                                        │
                                                        ▼
                                              Qwen2.5-VL  (le modèle)
```

Deux raisons à ce montage : Nephélé envoie ses planches **en image** (il faut
donc un VLM, pas un LLM texte) et il parle le **format Anthropic**
(`/v1/messages`, SSE), que LM Studio ne connaît pas — d'où le proxy.

## 1. LM Studio (le modèle)

1. Installer [LM Studio](https://lmstudio.ai).
2. Télécharger un modèle **vision** Qwen2.5-VL en build **MLX** (Apple Silicon).
   Sur 64 Go unifiés : **32B** est le bon compromis ; 72B tient mais plus lent.
3. **Charger** le modèle (onglet Chat), vérifier qu'il accepte une image.
4. Onglet **Developer → Start Server** (port `1234`). Noter l'« API model name »
   exact du modèle chargé.

## 2. LiteLLM (le proxy)

Dans un **environnement Python isolé** à la racine du dépôt (recommandé : ça
évite tout conflit avec `proto`, `pyenv` ou Homebrew, et le lanceur le détecte
automatiquement) :

```bash
/usr/bin/python3 -m venv .venv-local          # python système, contourne les shims
.venv-local/bin/pip install 'litellm[proxy]'
```

> Si `pip install` échoue avec `proto::detect::failed` (ou un message pyenv/xxx),
> c'est qu'un gestionnaire de versions intercepte `python`/`pip`. Le venv
> ci-dessus, créé avec le chemin absolu `/usr/bin/python3`, règle le problème.
> (Si `/usr/bin/python3` manque : `xcode-select --install`.)

Puis, dans [`litellm.config.yaml`](litellm.config.yaml), remplacer la valeur
`model:` par l'ID exact relevé à l'étape 1.

## 3. Lancer

Double-clic sur [`lancer-local.command`](lancer-local.command) (ou en terminal
depuis la racine du dépôt : `local/lancer-local.command`). Il vérifie LM Studio,
démarre le proxy, sert l'app et ouvre le navigateur. `Ctrl-C` arrête tout.

La première fois, rendre le script exécutable :
```bash
chmod +x local/lancer-local.command
```

## 4. Réglages dans Nephélé (panneau de gauche)

| Champ | Valeur |
|---|---|
| **Endpoint** | `http://localhost:4000` |
| **Clé API** | `sk-local` (factice, non vide) |
| **Modèle** | `nephele-vl` (aussi chargé via `/v1/models`) |

## Notes

- **Qualité** : sur cette tâche fine (refus du jargon, lecture de contour,
  doctrine française), un modèle local reste en dessous d'Opus/Sonnet. Usage
  d'exploration / hors-ligne, et point de branchement du futur modèle
  fine-tuné (phase 1 de la roadmap) : même endpoint, on remplace `nephele-vl`
  par ses poids. Le **banc** (`banc.html`) arbitre objectivement local vs API.
- **Débit** : ~16 appels par planche. En 32B, comptez un temps de réponse
  sensible mais utilisable ; en 72B, plus lent.
- **Sécurité** : le proxy n'a pas de clé maître — ne l'exposer que sur
  `localhost`.
- **Basculer sur l'API** : remettre `Endpoint = https://api.anthropic.com` et
  la vraie clé `sk-ant-…`. Rien d'autre à changer.
