# Le primer non verbal — protocole (piste « apprentissage fondamental »)

*Feuille de protocole, consignée le 2026-08-04. Théorie dans `RECHERCHE.md`
(« World model », « The map of the gaze ») ; lignée dans `FONDEMENTS.md` §8.5
(silhouette → concept, champ ZS-SBIR). Ceci est la seule piste d'entraînement
légitime AVANT les seuils de la Phase 1 : elle n'exige aucune donnée ratifiée,
parce que la supervision est l'image elle-même, jamais un jugement.*

## Pourquoi ce primer, et pourquoi lui d'abord

Un VLM ne peut pas ne pas reconnaître : sa strate épisodico-encyclopédique
(le corpus, les cartels) se déclenche avant toute consigne. Le primer prend le
chemin inverse : un encodeur **sans langage**, entraîné à placer **nos
silhouettes Otsu** là où un encodeur gelé place l'image originale — la lecture
de forme pure, la **strate innée distillée**, incontaminable par le corpus
parce qu'il n'a jamais lu un cartel. À terme : une amorce non verbale pour les
planches (un « ça tire vers » sans mot), et un instrument de mesure de la case
*inné + souvenu* de la carte du regard.

## Recette A — distillation silhouette → embedding (celle qu'on lance)

```
pip install -r requirements.txt

# 1. le jeu de paires, à travers le binariseur DE PRODUCTION (fidélité exigée)
python build_dataset.py --images /chemin/corpus_public --out data/primer

# 2. la distillation (prototype MPS sur le Mac ; vrai run sur GPU CUDA loué)
python distill_siglip.py --data data/primer --out runs/primer-lora \
    --model google/siglip-base-patch16-224 --epochs 1 --batch 32

# 3. l'évaluation FacesInThings (la case inné+souvenu, mesurée)
python eval_faces.py --adapter runs/primer-lora
```

- **Étudiant** : tour vision SigLIP + LoRA (r=16, attention seule) — léger,
  versionnable, échangeable. **Maître** : le même modèle, gelé.
- **Perte** : `1 − cos(étudiant(silhouette), maître(original))` + InfoNCE en
  lot (les paires doivent rester discriminantes, pas seulement proches).
- **Données** : n'importe quel corpus d'images **public** (COCO, OpenImages,
  photothèque personnelle). Aucun visuel de séance, aucun verdict — ce
  pipeline ne touche pas au corpus ratifié et n'y touchera jamais.
- **Matériel** : `../device.py` choisit MPS (Mac, prototype, `--limit` conseillé
  sur build_dataset) / CUDA (run réel, quelques heures) / CPU (debug).

## Recette B — croquis → concept (complément, plus tard)

Affûter la lecture de contour sur les jeux publics de croquis : QuickDraw
(50 M), TU-Berlin, Sketchy. Même étudiant, tête de classification jetable.
Ne se lance qu'après la recette A, si le banc en montre le besoin.

## Critères d'acceptation (le banc arbitre, pas l'enthousiasme)

1. **retrieval@1 silhouette → original** sur la validation : doit monter
   nettement au-dessus de l'encodeur de base (mesuré par `distill_siglip.py`
   à chaque époque) ;
2. **FacesInThings** : `delta primer − base > 0` (le primer retrouve le visage
   dans la planche seule, sans qu'on le lui ait jamais dit) ; si les notes de
   facilité humaine sont exploitables, corrélation de Spearman positive ;
3. **le banc de l'app** (`banc.html`) reste l'arbitre final de tout usage du
   primer dans le pipeline de lecture.

## Les gardes (gravées, comme ailleurs)

- **Fidélité de production** : les silhouettes d'entraînement sortent de
  `binarise.py`, portage ligne à ligne du binariseur de l'app. Tout écart
  invalide le primer.
- **Jamais mélangé à la Phase 1** : le primer n'est ni un raccourci ni un
  substitut du SFT sur lectures ratifiées — les seuils (300 / 800) restent.
- **Pas de course au modèle** : SigLIP base (~0,4 B) d'abord ; large seulement
  si les critères 1–2 plafonnent.
