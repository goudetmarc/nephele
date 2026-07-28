# Nephélé — contexte projet

Application d'appareillage de formes : trouver des figures dans des matières qui n'en portent aucune (nuages, rouille, écorce, peinture), et lire les champs non figuratifs par ce qu'ils *font* plutôt que par ce qu'ils montrent. Une seule page HTML par outil, zéro build, zéro dépendance, API Anthropic appelée directement depuis le navigateur.

## Les trois fichiers

| Fichier | Rôle | Règle |
|---|---|---|
| `doctrine.js` | **Tout ce que le modèle sait.** Socle, gestes de trouvaille, répertoire, régime sensible, dérivation de l'affect, prompts de toutes les passes, lexiques du banc. | C'est LE fichier de travail. 95 % des améliorations se font ici. |
| `index.html` | La tuyauterie : planches (traitement d'image canvas), pipeline, second regard, carnet, grammaire, corpus. | N'y toucher que pour la mécanique, jamais pour le comportement du modèle. |
| `banc.html` | L'instrument de mesure : 4 sondes, échelle de dégradation, test apparié. | Juge de paix de toute modification de doctrine. |

## Le contrat doctrine ↔ code (à ne pas casser)

`index.html` normalise tout ce qu'il reçoit : clés reconnues sans accents/casse/synonymes, champs inconnus ignorés, manquants avec défauts, `72`/`"72%"`/`0.72` équivalents. On peut donc réécrire les prompts et renommer les champs librement. Trois soudures seulement :

- `AUDACE` garde ses clés `1`–`5` avec `.n`, `.d`, `.p` ;
- une figure doit porter quelque chose qui ressemble à un nom ;
- le second regard rend quelque chose qui ressemble à un geste (confirme/affine/remplace, synonymes acceptés).

## L'histoire des versions — les leçons payées

- **v1** : machine à prompts. Le modèle récitait le corpus (« un dragon dans les nuages ») au lieu de regarder. **Leçon : le problème est en amont du prompt — couper la reconnaissance de scène en ne montrant jamais la photo, seulement des planches binarisées.**
- **v2** : rigueur importée des sciences → stérilité totale. L'attaque « artefact du seuil » invalidait 100 % des figures par construction ; le carnet apprenait à se taire. **Leçon : une paréidolie n'a pas de vérité de terrain. La seule question valide : « est-ce que ça tient le contour ? » (critère de partage, pas de vérité). On ne récuse JAMAIS une figure au motif qu'elle est produite par le traitement.**
- **v3** : séparation trouver/trier. Gestes de trouvaille (descendre d'échelle en premier — biais mesuré : les modèles font 87-90 % de réponses globales au Rorschach), quota + relance, le contradicteur devient second regard qui ne rend jamais une case vide. **Leçon : ajouter un geste de trouvaille produit des figures ; ajouter un critère de jugement en supprime.**
- **v4** : régime sensible (10 dimensions : poids, forces, lumière, température, temps, touche, trajet de l'œil, tension, rythme, économie) + planches couleur (chaud/froid est la plus révélatrice) + banc d'abstraction. **Leçon : les mots creux du discours sur l'art (« vibrant », « atmosphère ») sont les dragons du non-figuratif — plus dangereux car ils passent pour de la culture. Si le modèle reconnaît l'œuvre, il doit se taire.**
- **v5** : la grammaire configuration → effet. L'affect n'est jamais une affirmation, toujours la seconde moitié d'une affirmation dont la première est une configuration. Épreuve de l'horoscope : tout rapport doit avoir un démenti imaginable. Admission = récurrence sur 2 matières sans rapport + ratification humaine. L'état (candidate/admise/suspendue) est calculé par le code, jamais déclaré par le modèle.
- **v5.1** : le corpus (phase 0). Chaque séance s'enregistre en IndexedDB au format d'entraînement : planche vue + doctrine réellement injectée + verdicts. Exports SFT (planches propres uniquement) et DPO (paires je-la-vois/je-ne-la-vois-pas sur même planche).

## La feuille de route

- **Phase 1** (à 300 lectures ratifiées) : premier cycle SFT — LoRA sur un VLM ouvert 7B (Qwen2.5-VL), recette TRL/HF. Objectif : le format, le réflexe d'ancrage, le refus du jargon.
- **Phase 2** (à 800 paires) : cycle DPO — apprendre la préférence de Marc.
- **Règles absolues** : ne JAMAIS entraîner sur du non-ratifié (sinon amplificateur de défauts, cf. carnet v2). Le banc arbitre chaque cycle sur des images jamais vues à l'entraînement. Le fine-tuning consolide la grammaire, il ne la remplace pas (mémoire lente / mémoire rapide).
- **Piste parallèle sous-cotée** : CLIP/SigLIP fine-tuné silhouette → concept (champ ZS-SBIR) comme amorceur non verbal, incontaminable par le corpus. Les planches binarisées sont déjà des quasi-esquisses.

## Références clés

Citations complètes, formules et filiations dans `FONDEMENTS.md`. Les quatre points d'appui empiriques (vérifiés) :

- **FacesInThings** — Hamilton et al., *Seeing Faces in Things* (ECCV 2024, MIT, arXiv:2409.16143, `pip install facesinthings`) : ~5 000 images annotées, le banc d'essai visages. Le papier modélise un « pic paréidolique » ; le besoin évolutif de détecter aussi les visages d'*animaux* explique une part de l'écart machine/humain.
- **Bistable Images** — Panagopoulou, Melkin & Callison-Burch (CMCL @ ACL 2024, arXiv:2405.19423) : sur 29 images et 116 manipulations (luminosité, teinte, rotation), la variance est *minimale* — la monomanie interprétative est **robuste** (elle ne se débloque pas d'un simple pivot). D'où la nécessité des gestes anti-monomanie, pas leur validation.
- **Rorschach × IA** — *Human Shadows in Machine Minds* (JMIR Mental Health 2026, e88186) : biais de réponse globale quantifié — GPT-4o 86,7 % et Grok 3 90 % de réponses « globales » (W) ; Gemini à dominante détail (contre-exemple). Valide « descendre d'échelle » pour les modèles W-dominants.
- **Arnheim, *Art and Visual Perception*** (1954) : la référence de la grammaire configuration → effet.
- **GalleryGPT / PaintingForm** — Bin et al. (ACM MM 2024, doi:10.1145/3664647.3681656 ; arXiv:2408.00491) : ~19k tableaux + ~50k analyses formelles — référence du régime sensible.

## Conventions de travail

- Test systématique en Playwright headless avec API Anthropic mockée (SSE simulé) avant toute livraison. Chromium préinstallé : `executablePath:'/opt/pw-browsers/chromium'` en session cloud.
- Les tests incluent des cas hostiles : JSON déformés (dialectes), planches pauvres (relance), règles-horoscope (retrait).
- Jamais de page vide comme résultat possible. Le doute classe, il ne tait pas.
- Interface et doctrine en français, sobre, sans emphase.
- Les données personnelles (corpus, grammaire, carnet, exports) sont dans `.gitignore` — ne jamais les versionner.
- Modèles API valides : `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`. Les modèles récents refusent `temperature` (auto-géré dans `ask()`).
