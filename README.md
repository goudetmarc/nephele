# Nephélé — appareillage, lecture des champs, grammaire

Trouver des figures dans des matières qui n'en portent aucune — nuages, rouille, écorce, peinture — et lire les champs non figuratifs par ce qu'ils *font* plutôt que par ce qu'ils montrent. Une seule page HTML par outil, zéro build, zéro dépendance, l'API Anthropic appelée directement depuis le navigateur.

## Le principe

On ne montre jamais la photo au modèle, seulement des planches binarisées ou recolorées. Couper la reconnaissance de scène en amont est la seule façon d'empêcher la récitation du corpus (« un dragon dans les nuages ») au profit du regard.

Deux régimes de lecture, sélectionnables planche par planche :

- **figuratif** — trouver des figures et les faire voir ;
- **sensible** — dire ce que le champ fait, sans rien nommer.

Une **grammaire** apprise par-dessus les deux régimes accumule des rapports configuration → effet réutilisables d'une matière à l'autre.

## Fondements — sciences et arts

> *« Regarde certains murs couverts de taches […] et tu pourras y voir la ressemblance de divers paysages, de figures aux gestes vifs, d'expressions de visages. »* — **Léonard de Vinci**, *Trattato della pittura* (v. 1500)

Nephélé n'improvise pas : chaque décision de doctrine ou de code répond à un résultat établi. **Le document complet, avec formules, méthodes et bibliographie, est dans [`FONDEMENTS.md`](FONDEMENTS.md).** En bref :

- **Trouver des formes dans l'informe** est une méthode d'invention documentée — de la *macchia* de Léonard au *blot* de **Cozens** (1785), au *frottage* de **Max Ernst**, aux taches de **Rorschach** (1921).
- **Percevoir, c'est inférer** (**Helmholtz** ; cerveau bayésien, **Friston**) : la paréidolie est un *a priori* fort sur une évidence pauvre. L'information est aux **extrema de courbure** du contour (**Attneave** 1954) — d'où *descendre d'échelle* et *chercher la pointe*.
- **La bistabilité** (canard-lapin, **Wittgenstein**) et la **monomanie interprétative** des modèles — robuste, quasi insensible aux manipulations (Bistable Images, CMCL @ ACL 2024) — justifient les gestes anti-monomanie : *pivoter*, *tenir deux figures à la fois*.
- **Une paréidolie n'a pas de vérité de terrain** : on remplace le critère de vérité par un **critère de partage** (théorie de la détection du signal, **Green & Swets** 1966), et on filtre le discours vide par l'**épreuve de l'horoscope** (**Popper** ; effet Barnum-**Forer** 1949).
- **La grammaire configuration → effet** vient d'**Arnheim** (*Art and Visual Perception*, 1954), **Kandinsky**, **Klee** : l'affect est *dérivé* d'une configuration, jamais posé.
- **Les planches** appliquent **Otsu** (seuillage), **Canny** (bords), **k-moyennes** (familles de teintes), les **couleurs opposées** (chaud/froid = opérateur d'espace).
- **L'apprentissage** suit les **systèmes complémentaires** (McClelland 1995) — poids fine-tunés (mémoire lente) + grammaire injectée (mémoire rapide) — via **SFT**, puis **DPO** (**Rafailov** 2023, sur **Bradley-Terry** 1952) et **LoRA** (**Hu** 2022), avec un amorceur non verbal **CLIP/SigLIP**.

## Theoretical Foundation & Validation Metrics

*(Research positioning, in English.)*

Nephélé is a **perceptually-aligned vision framework** rather than a thin API layer. It treats pareidolia not as an image-synthesis problem but as a problem of **aligning a reading model to a single annotator's perceptual judgment**, while distilling reusable *configuration → effect* relations under an explicit falsifiability constraint. This section states the learning objective and the validation metrics, and situates the framework with respect to generative-reveal approaches.

### Preference alignment (DPO)

Readings are aligned to ratified human verdicts by **Direct Preference Optimization** (Rafailov et al., 2023), which reparameterizes the **Bradley–Terry** (1952) preference model so that the reward is implicit in the policy. For an input $x$ (system prompt + board image), a chosen reading $y_w$ and a rejected reading $y_l$, the objective is

$$
\mathcal{L}_{\mathrm{DPO}}(\pi_\theta;\pi_{\mathrm{ref}})
= -\,\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}
\left[\log\sigma\!\left(
\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}
-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}
\right)\right],
$$

where $\pi_\theta$ is the trainable policy, $\pi_{\mathrm{ref}}$ the frozen reference (post-SFT) model, $\sigma$ the logistic function, and $\beta$ the KL-deviation temperature. **The human verdict is the reward signal; no separate reward model is trained.**

### Spatial and photometric validation (generative "show-me" track)

A distinct, non-verbal track may *reveal* a figure by synthesizing a shape confined to the source region — the line represented by masked diffusion-editing scores such as the **Masked Delta Denoising Score (MDDS)**, after the Delta Denoising Score (Hertz et al., ICCV 2023), and by *Diamonds in the Sky* (Horovicz et al., arXiv:2606.01361). For that track we adopt two standard criteria.

**Spatial agreement** between a generated binary mask $G$ and the source region $C$ is the Intersection-over-Union, with acceptance $\mathrm{IoU} > 0.5$:

$$
\mathrm{IoU}(G, C) = \frac{|G \cap C|}{|G \cup C|}.
$$

**Photometric preservation** of the surrounding structure is checked with the (global) Structural Similarity Index, with acceptance $\mathrm{SSIM} > 0.7$:

$$
\mathrm{SSIM}(x, y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)},
\qquad c_1 = (k_1 L)^2,\; c_2 = (k_2 L)^2,
$$

with $k_1 = 0.01$, $k_2 = 0.03$ and $L$ the pixel dynamic range. SSIM guarantees a reveal *preserves* the original structure of the field rather than overwriting it. Both metrics are implemented in `tests/similarity.js` and unit-tested.

### Positioning (honest scope)

Generative-reveal methods (DDS/MDDS, *Diamonds in the Sky*) **synthesize** the percept and validate the edit spatially (IoU) and photometrically (SSIM). Nephélé takes the **orthogonal, non-generative route**: it never alters the field; it reads the contour in language, teaches the eye *where to look*, aligns the reader to human judgment (DPO), and accumulates falsifiable configuration→effect relations. Its current outputs are linguistic, not pixel masks.

We therefore make **no claim of outperforming MDDS on its own image-editing metrics**: the two paradigms operate on different outputs, and no head-to-head evaluation has been conducted. The IoU/SSIM criteria above are provided (i) to validate a *future* generative "show-me" track of Nephélé, and (ii) to render any eventual comparison well-defined. The framework's contribution is **perceptual alignment to a human annotator under a falsifiability constraint**, not image synthesis.

## La question, et les deux interdictions

Jamais « est-ce que c'est là », toujours **est-ce que ça tient le contour ?**

Une figure tient quand on peut dire quelle partie du tracé fait quoi — ceci le dos, ceci l'appui, ceci l'entaille de la gueule — et quand la personne à qui on la montre finit par la voir. C'est un critère de partage, pas de vérité. Une figure réussie est une figure qu'on peut **faire voir**.

Deux interdictions absolues sont inscrites dans la doctrine, à toutes les étapes : on ne récuse jamais une figure au motif qu'elle serait produite par le traitement de l'image, ni au motif qu'elle ne serait pas réellement dans la matière. Aucune ne l'est. Ce n'est pas le sujet.

## Le régime figuratif

### Trouver

Une section `TROUVER` — sept gestes, employés dans l'ordre, qu'on redescend tant qu'on manque de matière :

1. **Descendre d'échelle.** Le geste le plus rentable et le plus oublié. Une forme entière ressemble rarement à quelque chose ; un dixième de cette forme ressemble presque toujours à quelque chose. La plupart des figures fortes sont des fragments promus.
2. **Suivre un bord et laisser venir le mot** — même absurde, surtout absurde. Refuser le premier mot est la façon la plus sûre de ne rien trouver, parce que le second ne vient jamais.
3. **Chercher la tête.** Presque toutes les figures reconnues sont ancrées par une extrémité. Trouve-la et le corps suit.
4. **Pivoter.** 5. **Prendre l'intervalle.** 6. **Changer de monde** — cartes, outils, anatomie, alphabets. 7. **Tenir deux figures à la fois** sur la même zone, sans choisir.

### Le contrat de sortie

Quota de **six figures minimum par planche**, dont deux sur un fragment traité comme un tout et deux hors du registre vivant. Si une planche en rend moins de quatre, l'application **relance automatiquement** l'observateur avec une consigne ciblée : prends cinq fragments distincts, pivote-en deux, change de registre.

Une page vide n'est jamais un résultat possible. La confrontation classe et présente ; elle n'élimine pas.

### Le second regard

Il ne démolit pas. Il rend la meilleure figure possible pour cette zone du contour, par un geste sur trois :

- **CONFIRME** — il la voit, et il doit ajouter une partie du contour que le premier n'avait pas relevée. Confirmer sans rien ajouter est un travail bâclé.
- **AFFINE** — presque juste mais mal cadrée : orientation fausse, espèce trop précise, zone qui déborde. Il corrige. C'est le geste le plus fréquent.
- **REMPLACE** — cette zone porte quelque chose, mais pas ça. Il nomme la figure qui organise mieux le même contour et la montre comme s'il la proposait lui-même.

**Il ne rend jamais une case vide.** Le seul reproche recevable est « ça ne tient pas le contour », et il débouche toujours sur un affinage ou une substitution.

Le réglage d'**audace** ne règle pas la sévérité mais l'**écart** — la distance à l'évidence. À son maximum, la consigne dit explicitement : *rends plus de figures ici qu'à tout autre réglage, pas moins.*

### Le rendu

Chaque figure est une carte qui commence par **« par où regarder »** — une phrase qui guide l'œil de quelqu'un qui ne la voit pas encore : *« pars de la pointe en B2, descends le bord vers la gauche, l'entaille que tu croises fait la gueule »*. C'est le produit. Le reste — parties du contour, tenue, écart, geste du second regard — vient après.

La confrontation rend quatre sections : **À voir en premier** (cinq à huit figures, les plus éloignées de l'évidence d'abord, chacune avec son mode d'emploi), **Les deux lectures d'une même zone**, **Convergences** entre planches, **Écarté**.

## Le régime sensible

Non plus « à quoi ça ressemble » mais **ce que ça fait**. Où porte le poids, ce qui pousse et ce qui résiste, d'où vient la lumière et si elle révèle les formes ou les mange, quelle est la température de l'air, si c'est un instant ou une durée, par où l'œil entre et où il se coince.

Dix dimensions, chacune avec ce qui la produit matériellement et le test qui tranche. Exemple :

> **POIDS ET APPUI** — Où la masse se pose, et si elle tient.
> *Produit par* : la distribution des valeurs sombres, la position de la zone la plus dense par rapport au centre, l'occupation ou le vide de la base.
> *Test* : bouche mentalement la moitié basse. L'image tombe-t-elle ? Si oui, elle tenait par le bas. Sinon, elle flotte — et c'est un fait, pas une métaphore.

Pas de quota de figures, mais un quota de **constatations ancrées** : au moins six, dont deux qui disent un rapport entre deux zones distinctes. « L'image bascule vers la gauche » ne vaut rien ; « l'image bascule vers la gauche : toute la masse sombre occupe A3-B5, le quart droit est vide et rien ne la retient » vaut quelque chose.

Une liste de **mots creux** est bannie — *dynamique, harmonieux, vibrant, poétique, atmosphère, palette riche, invite le spectateur* : ils ont l'air de dire et ne désignent rien. Aucun ne peut apparaître seul ; la zone et le fait suivent, ou le mot saute.

Une interdiction spécifique : **si le modèle reconnaît l'œuvre, il doit se taire.** Un commentaire qui serait vrai sans avoir regardé l'image est un échec, même exact — et c'est le mode d'échec le plus difficile à repérer, parce que le résultat est cultivé, juste, et vide.

## Les planches

Les planches binaires portent les figures ; six planches gardent la couleur pour la lecture sensible :

| Planche | Ce qu'elle montre |
|---|---|
| **recul** | Vu de loin. Les touches se dissolvent, la structure apparaît. |
| **chaud / froid** | La température seule, en orange et bleu. Le chaud avance, le froid recule — un opérateur d'espace, pas une humeur. La planche qui révèle le plus. |
| **valeur seule** | La structure que la couleur masque. |
| **la touche** | Recadrage serré sur la zone la plus travaillée, détectée par énergie de gradient. La matière de très près. |
| **chroma** | Où la couleur est intense, indépendamment de la teinte. |
| **familles** | Cinq teintes dominantes en aplats, par k-moyennes. |

La grille gravée passe au vert sur ces planches : en rouge, elle se lirait comme une zone chaude sur la planche de température.

## La grammaire

Un nom trouvé dans un nuage est une donnée morte : « un chien » ne vaut que pour ce nuage. Un rapport du type **masse dense excentrée + quadrant opposé vide → chute** vaut sur toute image qui présente cette configuration, quelle que soit sa matière. C'est la différence entre un catalogue, qui s'allonge, et une grammaire, qui se resserre — de la gestalt appliquée à la manière de Rudolf Arnheim, *Art and Visual Perception*, où chaque qualité expressive est dérivée d'une configuration et non posée.

**L'affect n'est jamais une affirmation.** Il est toujours la seconde moitié d'une affirmation dont la première est une configuration, avec le mécanisme entre les deux. On n'apprend pas l'association vers l'intention de l'œuvre — inatteignable, et c'est le catalogue déguisé — mais vers **l'effet sur un regardeur**, et le seul regardeur disponible, c'est toi.

**L'épreuve de l'horoscope.** Avant qu'un rapport soit proposé, une seule question :

> **Peux-tu imaginer une image où cette configuration est présente et où l'effet est absent ?**

Si oui, le rapport est falsifiable, il vaut quelque chose. « Le rouge est passionné » échoue : aucune image ne peut le démentir. « Une diagonale montante interrompue par une horizontale produit une butée » passe. Chaque constatation porte donc trois termes — `configuration`, `effet`, `dementi_possible` — et **les trois ou aucun**.

**La forme générale.** Chaque configuration s'énonce deux fois : en local (« toute la masse sombre occupe A3-B5, le quart droit est vide ») et en général (« masse dense excentrée + quadrant opposé vide »). Seule la forme générale, en termes de rapports et jamais de contenus, peut se retrouver ailleurs.

**L'admission.** Une entrée devient **admise** — donc injectée — quand elle réunit la **récurrence** (la même configuration a produit le même effet sur au moins deux matières sans rapport) et la **ratification** (tu l'as confirmée d'un clic). Elle passe en **suspendue** dès un démenti de ta part, ou quand ses contradictions atteignent la moitié de ses occurrences. **L'état n'est jamais décidé par le modèle** : il compte, apparie, contredit et nomme ; l'admission est calculée en dehors de lui.

**Les contradictions valent plus que les confirmations.** La grammaire est injectée comme un jeu d'hypothèses, pas de lois : devant chaque rapport pertinent, la consigne demande non pas où on le retrouve mais si cette image le dément. Une contradiction n'invalide pas la règle — elle signale une variable cachée à nommer, et scinde une règle fausse en deux règles justes.

La grammaire vit dans le navigateur, s'ouvre dans un panneau, s'exporte et se réimporte en `.json`.

## Le banc d'abstraction — `banc.html`

Une page à part. Elle ne cherche rien dans les images : **elle mesure ce que devient le discours du modèle à mesure qu'il n'y a plus rien à reconnaître.**

Une image est dégradée par paliers — six barreaux, de net à ÷32. À chaque barreau, une sonde. Chaque réponse est mesurée sur quatre axes, **comptés et non jugés** (le banc n'appelle aucun modèle pour évaluer, il compte des mots contre des lexiques modifiables dans `doctrine.js`) :

- **figuration** — densité de noms concrets. Nommer des objets là où il n'y en a plus.
- **jargon** — densité de mots creux. Parler sans désigner.
- **ancrage** — références à la grille et termes de position, par phrase.
- **esquive** — densité de *semble*, *pourrait*, *il est difficile de*.

Le croisement de ces courbes est le seuil d'abstraction du modèle, et le banc le nomme.

Quatre sondes se lancent sur la même image : **nue**, sous doctrine **figurative**, sous doctrine **sensible**, et **sensible + grammaire**. C'est la seule façon de savoir si une modification de `doctrine.js` améliore ou dégrade quelque chose. Si les courbes ne bougent pas, la doctrine ne fait rien — et il vaut mieux le savoir.

**Le test apparié.** La même œuvre entière, puis un fragment de 18 % non identifiable. Deux mesures : le recouvrement lexical entre les deux lectures, et le nombre de termes de catalogue (noms de peintres, d'écoles, de techniques) que chacune déclenche. Si l'œuvre entière en déclenche et pas son propre fragment, le discours venait du catalogue et non de l'œil.

Les tableaux célèbres sont la pire matière de test pour l'échelle : le modèle les connaît. Utilise-les uniquement en test apparié, où ce défaut devient la mesure. Pour l'échelle, préfère tes propres photos ou des œuvres obscures.

## Le corpus d'entraînement

**Chaque séance s'enregistre toute seule** (IndexedDB, dans ton navigateur — rien ne part nulle part). Ce qui est stocké est ce qui compte pour un entraînement futur : la planche telle que le modèle l'a vue, la doctrine réellement injectée à ce moment-là, les lectures produites, et tes verdicts.

Le panneau **Corpus d'entraînement** affiche la progression vers deux seuils :

- **SFT à 300 lectures ratifiées.** L'export ne retient que les planches *propres* : au moins une lecture « je la vois », aucune « je ne la vois pas ». La cible enseignée est la version corrigée par le second regard quand il y en a une.
- **DPO à 800 paires.** Une paire naît quand une même planche porte une lecture ratifiée ET une rejetée. Ton clic est la fonction de récompense.

Formats (JSONL, une ligne = un exemple, image en base64 incluse) :

```
SFT : {id, matiere, regime, modele, image:{mime,b64}, system, user, assistant}
DPO : {id, matiere, regime, image:{mime,b64}, system, user, chosen, rejected}
```

`system` et `user` sont les textes *réellement envoyés* pendant la séance — si tu modifies la doctrine ensuite, les exemples anciens gardent la leur. La conversion vers un entraînement TRL/LoRA est directe (voir le [cookbook Hugging Face](https://huggingface.co/learn/cookbook/en/fine_tuning_vlm_trl)).

Deux disciplines, et le corpus vaudra quelque chose :

1. **Note les lectures.** Une séance sans verdict produit zéro exemple.
2. **Renseigne la matière.** Elle sert à la grammaire ET à stratifier le futur entraînement.

L'**archive** exporte tout (séances complètes, JSON) à la demande. Mieux : **lie un dossier de sauvegarde** une fois, et chaque séance comme chaque verdict s'y recopient tout seuls — l'archive complète et les jeux SFT/DPO, de disque à disque, sans rien envoyer nulle part. Le stockage du navigateur n'est pas éternel et ces données ne se refabriquent pas ; c'est le seul actif du projet qui compte vraiment. (Sauvegarde automatique sur navigateurs à base de Chromium ; ailleurs, l'export manuel reste.)

## Lancer

```bash
python3 -m http.server 8080
```

puis <http://localhost:8080>. Sur macOS, `lancer.command`. Le double-clic sur `index.html` ne marche pas : `doctrine.js` est un fichier séparé et `file://` refuse de le charger.

Environ 16 appels avec les réglages par défaut ; le compteur sous le bouton l'annonce avant de lancer.

## Travailler sur le modèle

Tout est dans **`doctrine.js`**, en clair — pas besoin de rouvrir `index.html`.

Le code ne connaît plus les noms des champs : il normalise ce qu'il reçoit. Les clés sont reconnues sans tenir compte des accents, des majuscules, des espaces, des tirets ni des synonymes courants — `Point-d'entrée`, `pointEntree`, `hook` et `accroche` désignent la même chose. Les champs inconnus sont ignorés, les manquants prennent une valeur par défaut. `72`, `"72%"`, `"0,68"` et `0.72` sont le même nombre. Le vocabulaire du second regard accepte les synonymes : `tient`, `confirm`, `valide` donnent tous CONFIRME.

Ce qui reste soudé, et c'est tout :

- `AUDACE` garde ses clés `1` à `5`, chacune avec `.n` (nom court), `.d` (résumé d'une ligne), `.p` (le prompt) ;
- une figure doit porter quelque chose qui ressemble à un nom ;
- le second regard doit rendre quelque chose qui ressemble à un geste.

| Constante | Ce qu'elle fait |
|---|---|
| `SOCLE` | La faute de catégorie à évacuer, le critère de partage, le contrat de production. |
| `TROUVER` | Les sept gestes qui produisent des figures. **C'est ici qu'on gagne du rendement.** |
| `REPERTOIRE` | Les signatures comme modes d'emploi, et les figures paresseuses sommées de descendre dans le détail. |
| `AUDACE` | Les cinq écarts à l'évidence. |
| `P_AVEUGLE` | Le quota et le format des figures. |
| `P_SECOND` | Les trois gestes et les deux interdictions. |
| `P_CARNET` | La règle qui empêche le carnet de converger vers le silence. |
| `AFFECT` | La règle de dérivation de l'affect, l'épreuve de l'horoscope, la consigne de démenti. |
| `P_GRAMMAIRE` | L'appariement sémantique, la généralisation, les variables cachées, le plafond de 40 entrées. |

Si le rendement retombe, c'est `TROUVER` qu'il faut enrichir — pas `REPERTOIRE`, et surtout pas `P_SECOND`. Ajouter un geste de trouvaille produit des figures ; ajouter un critère de jugement en supprime.

### Réglages, par ordre d'effet

1. **Plisser les yeux.** Une image qui ne donne rien est presque toujours une image trop détaillée. Monte à 5 ou 6.
2. **Les planches.** Les sombres et la silhouette portent les figures les plus éloignées ; les claires donnent surtout de l'évident.
3. **L'écart.** En dernier. Il ne fabrique pas de figures, il déplace seulement l'endroit où on les cherche.
