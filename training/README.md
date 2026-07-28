# Entraînement — de l'app au modèle propriétaire

Ce dossier dérisque la Phase 1 (SFT) et la Phase 2 (DPO) : le pipeline est
écrit **avant** d'atteindre les seuils, pour qu'au jour dit il n'y ait qu'à
lancer, pas à improviser. Rien ici n'est exécuté dans l'environnement de dev
(pas de GPU, pas de poids) — c'est une **recette de départ à éprouver** sur le
GPU loué, puis à épingler (versions exactes) pour la reproductibilité.

## Quand — le déclencheur est le compteur, pas le calendrier

Le panneau **Corpus d'entraînement** de l'app affiche la progression.

- **Phase 1 (SFT)** à **~300 lectures ratifiées**. But : le format, le réflexe
  d'ancrage, le refus du jargon. Pas le contenu.
- **Phase 2 (DPO)** à **~800 paires**. But : apprendre *ta* préférence.

Avant ces seuils, un GPU tournerait à vide. On ne provisionne rien maintenant.

## Où — Apple Silicon en local (cible), GPU loué en secours

**Cible : le MacBook Pro M-series, 64 Go de RAM unifiée.** Un LoRA sur un VLM 7B
tient sans peine en 16 bits natif dans cette mémoire — pas besoin de
quantification. Le code choisit tout seul le backend (`training/device.py`) :

- **`mps`** (Metal Performance Shaders) sur Apple Silicon — le chemin par défaut ;
- **`cuda`** si tu lances plutôt sur un GPU loué (RunPod, Modal, Lambda…) ;
- **`cpu`** en dernier recours (lent, debug).

**Pas de bitsandbytes / 4-bit** : incompatible MPS, et inutile ici. Sur Mac, la
première exécution peut être lente le temps que Metal compile ses noyaux, et
quelques ops rares retombent sur CPU (`PYTORCH_ENABLE_MPS_FALLBACK=1`, posé
automatiquement).

Si un jour tu veux aller plus vite qu'un M-series : loue un GPU CUDA à l'heure
(dizaines d'€ le cycle) — le même code tourne dessus sans modification.
Cloudflare n'entre pas ici (il ne fait pas tourner de VLM custom) ; il sert au
plan de contrôle (passerelle, corpus R2), pas à l'entraînement.

## Le flux, de bout en bout

```bash
# 0. Récupère l'export depuis l'app (bouton « export SFT » / « export DPO »,
#    ou le dossier de sauvegarde lié) → nephele-sft.jsonl / nephele-dpo.jsonl

# 1. Sur le Mac (ou le GPU loué)
pip install -r requirements.txt

# 2. Découpe SANS fuite d'image (le held-out sert le banc)
python prepare_data.py --sft nephele-sft.jsonl --out data/ --heldout 0.15

# 3. Phase 1 — SFT LoRA (backend mps/cuda/cpu choisi automatiquement)
python sft_qwen_vl.py --data data/sft_train.jsonl \
    --out out/nephele-sft-lora --epochs 2

# 4. Phase 2 — DPO LoRA (quand tu as les paires), par-dessus le SFT.
#    prepare_data sort ici le format HF standard (prompt/chosen/rejected + image).
python prepare_data.py --dpo nephele-dpo.jsonl --out data/ --heldout 0.15
python dpo_qwen_vl.py --data data/dpo_train.jsonl \
    --sft out/nephele-sft-lora --out out/nephele-dpo-lora

# 5. Poids → R2 (stockage que tu contrôles, sans frais d'egress)
#    puis servir via un endpoint d'inférence ; l'app pointe dessus.
```

## Les règles absolues (CLAUDE.md), câblées ici

- **Jamais d'entraînement sur du non-ratifié.** Les exports ne contiennent déjà
  que du ratifié (SFT : planches propres ; DPO : paires vues/non-vues). Ne
  contourne pas ça — c'est ce qui a stérilisé le carnet en v2.
- **Le banc arbitre sur des images jamais vues.** `prepare_data.py` réserve un
  held-out **par image** (aucune image d'éval dans le train, même sous une autre
  planche). Après chaque cycle : fais tourner `banc.html` sur ces images-là,
  modèle fine-tuné contre modèle de base. Un gain qui ne se voit pas au banc
  n'existe pas.
- **Le fine-tuning consolide la grammaire, il ne la remplace pas.** Mémoire
  lente (poids) / mémoire rapide (grammaire injectée). On garde les deux.

## Piste parallèle (sous-cotée, incontaminable)

Un fine-tune séparé **CLIP/SigLIP silhouette → concept** (champ ZS-SBIR) comme
amorceur non verbal : les planches binarisées sont déjà des quasi-esquisses, et
ce chemin ne peut pas réciter le corpus puisqu'il ne produit pas de texte. À
monter quand le SFT/DPO tourne — dossier à part.

## Honnêteté sur ces scripts

Ils suivent la recette VLM standard TRL/PEFT, mais **ne sont pas exécutés ici**.
Les API de TRL bougent vite : au premier run, attends-toi à ajuster une signature
ou deux (collate, `processing_class`, masquage des tokens image), puis épingle
les versions dans `requirements.txt`. C'est le point de départ, pas la vérité
gravée.
