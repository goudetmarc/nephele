# Fondements — sciences et arts

> *« Regarde certains murs couverts de taches, ou faits de pierres mêlées, et tu
> pourras y voir la ressemblance de divers paysages, de batailles, de figures aux
> gestes vifs, d'expressions de visages, de costumes. »*
> — Léonard de Vinci, *Trattato della pittura*, §60 (v. 1500)

Ce document expose la charpente intellectuelle de Nephélé : ce qu'on emprunte à
la psychologie de la perception, à la théorie du signal, à l'esthétique formelle,
à la théorie de la décision et à l'apprentissage automatique — et comment chaque
emprunt se traduit en un mécanisme précis du code. Rien ici n'est décoratif :
chaque référence répond à une décision d'ingénierie ou de doctrine.

Le projet a un objet unique : **l'appareillage de formes** — trouver des figures
dans des matières qui n'en portent aucune (nuages, rouille, écorce, peinture), et
lire les champs non figuratifs par ce qu'ils *font* plutôt que par ce qu'ils
*montrent*. C'est un problème d'**apophénie dirigée** : provoquer, puis discipliner,
la perception de structures dans le hasard.

---

## 1. La lignée artistique de la trouvaille de formes

Voir des figures dans la matière informe est une technique d'invention aussi
ancienne que documentée.

- **Léonard de Vinci** (*Trattato della pittura*, v. 1500) : la *macchia*, la tache
  du mur comme déclencheur d'invention. C'est la matrice historique de Nephélé.
- **Alexander Cozens**, *A New Method of Assisting the Invention in Drawing Original
  Compositions of Landscape* (1785) : le *blot drawing* — partir d'une tache
  aléatoire pour composer un paysage. Une méthode, pas un accident.
- **Victor Hugo** (taches, pliages, lavis, ~1850–1870) et surtout **Max Ernst**
  (*frottage* 1925, *décalcomanie* 1936) : l'automatisme graphique génère la
  texture, l'œil y appareille la figure. Le surréalisme théorise l'**automatisme**
  (Breton, *Manifeste* 1924) comme court-circuit du contrôle conscient.
- **Hermann Rorschach**, *Psychodiagnostik* (1921) : la tache d'encre symétrique
  comme instrument. Nephélé hérite du dispositif *et* de sa mise en garde (§4).
- **Ludwig Wittgenstein** (*Recherches philosophiques*, II, xi, 1953) sur le
  *voir-comme* (le canard-lapin de **Jastrow**, 1899) : une même configuration
  supporte deux vues incompatibles, et « voir » est déjà une interprétation.

> **Traduction dans le code.** On ne montre **jamais** la photographie au modèle,
> seulement des planches binarisées ou recolorées (`faireLesPlanches` dans
> `index.html`). C'est le mur de Léonard, le blot de Cozens : couper la
> reconnaissance de scène en amont pour forcer l'appareillage plutôt que la
> récitation.

---

## 2. La perception comme inférence : Gestalt, Helmholtz, Bayes

### 2.1 Théorie de la Gestalt

La psychologie de la forme (**Wertheimer** 1923 ; **Koffka**, *Principles of Gestalt
Psychology*, 1935 ; **Köhler**) établit que la perception groupe le champ selon des
lois — proximité, similarité, clôture (*closure*), bonne continuation, destin
commun — sous un principe directeur, la **Prägnanz** (tendance à la forme la plus
simple/régulière).

**Hochberg & McAlister** (1953) en donnent une formulation quantitative — le
*principe du minimum* : la « bonté » d'une figure est inversement proportionnelle
à la quantité d'information nécessaire pour la spécifier. Une figure « tient »
quand elle est l'organisation la plus économique du contour.

$$\text{bonté}(F) \;\propto\; \frac{1}{I(F)}, \qquad I(F) = \text{information de description de } F$$

> **Traduction.** Le critère de Nephélé — *« est-ce que ça tient le contour ? »* —
> est un critère de Prägnanz : une figure est retenue quand on peut dire quelle
> partie du tracé fait quoi (clôture, bonne continuation), c'est-à-dire quand elle
> organise économiquement le contour. La **clôture** est exactement ce que le
> second regard traque (`P_SECOND` : « les parties désignées font-elles ce qu'on
> dit ? »).

### 2.2 L'inférence inconsciente et le cerveau bayésien

**Helmholtz** (1867) : percevoir, c'est inférer inconsciemment la cause la plus
probable des sensations. La lecture moderne — **perception bayésienne** et
**codage prédictif** (**Friston**, *free-energy principle*, 2010) — écrit la
perception comme une inférence a posteriori :

$$P(H \mid D) \;=\; \frac{P(D \mid H)\,P(H)}{P(D)} \;\propto\; P(D \mid H)\,P(H)$$

La **paréidolie** est le cas où un **a priori** fort $P(H)$ (visages, animaux,
corps) domine une évidence sensorielle $P(D\mid H)$ pauvre ou ambiguë : le cerveau
« voit » l'hypothèse la plus attendue. Les visages sont le prior le plus fort —
d'où l'activation du **gyrus fusiforme** (FFA ; **Kanwisher, McDermott & Chun**
1997) devant de simples taches disposées en triade (**Liu et al.** 2014,
*Seeing Jesus in toast*).

> **Traduction.** Le geste de trouvaille *« Cherche la tête »* (`TROUVER`) exploite
> le prior le plus puissant ; *« Suivre un bord et laisser venir le mot, même
> absurde »* relâche volontairement le contrôle pour laisser le prior parler.

### 2.3 L'information est dans le contour : Attneave, Marr, Biederman

**Attneave** (*Some informational aspects of visual perception*, 1954) montre que
l'information visuelle se concentre aux **points de courbure maximale** du
contour — son célèbre « chat » réduit à des segments joignant les extrema de
courbure reste reconnaissable. **Marr** (*Vision*, 1982) formalise le primal
sketch et ses trois niveaux (computationnel / algorithmique / implémentationnel).
**Biederman** (*recognition-by-components*, 1987) : les objets se reconnaissent
comme assemblages de primitives (*geons*) définies par leurs contours.

> **Traduction.** Deux gestes de `TROUVER` en découlent directement :
> - *« Descendre d'échelle »* — un fragment de contour porte plus d'information
>   locale exploitable qu'une silhouette entière : la plupart des figures fortes
>   sont des fragments promus.
> - *« Chercher la pointe / l'extrémité »* — les extrema de courbure (au sens
>   d'Attneave) sont les ancres naturelles de la figure.
>
> Le biais mesuré au Rorschach (87–90 % de **réponses globales** chez les modèles,
> cf. §4) est précisément l'échec à descendre au niveau où l'information est.

---

## 3. Perception multistable et monomanie interprétative

Une configuration ambiguë (canard-lapin, cube de Necker, vase de Rubin) admet
plusieurs organisations mutuellement exclusives ; la perception **bascule** mais
n'en tient qu'une à la fois — c'est la **rivalité perceptive**. Le corollaire, la
**monomanie interprétative**, est le risque central d'un lecteur de formes : se
fixer sur la première lecture et ne plus voir les autres.

Références du projet :

- **Bistable Images** (CMCL / ACL 2024) : la monomanie interprétative des modèles
  est générale, et **la rotation est la manipulation d'image la plus efficace**
  pour débloquer une seconde lecture.
- **Rorschach × IA** (JMIR Mental Health, réf. projet) : quantifie le **biais de
  réponse globale** — les modèles répondent à la planche entière (87–90 %) là où
  l'humain descend au détail.
- **FacesInThings** (*Seeing Faces in Things*, ECCV 2024, MIT, licence MIT ;
  `pip install facesinthings`) : ~5 000 images de paréidolie de visages annotées.
  Résultat exploité par le projet : *fine-tuner sur des visages d'animaux réduit
  de moitié l'écart machine/humain*.

> **Traduction.** Trois mécanismes :
> - `TROUVER` impose *« Pivoter »* (la rotation d'ACL 2024) et *« Tenir deux
>   figures à la fois sur la même zone, sans choisir »* — anti-monomanie explicite.
> - Le **second regard** ne démolit pas : il propose la meilleure lecture
>   concurrente (CONFIRME / AFFINE / REMPLACE), institutionnalisant la bistabilité.
> - Le quota de six figures et la relance automatique (`P_AVEUGLE`) forcent à
>   dépasser la première réponse globale.

---

## 4. Épistémologie : une paréidolie n'a pas de vérité de terrain

C'est la leçon la plus chèrement payée du projet (l'échec « v2 »). Le chameau
n'est pas dans le nuage ; il n'y a jamais été et aucune vérification ne l'y
trouvera. Poser la question « cette figure existe-t-elle réellement ? » détruit
l'objet qu'on examine.

### 4.1 Critère de partage, pas de vérité — théorie de la détection du signal

La **théorie de la détection du signal** (**Green & Swets**, 1966) sépare deux
grandeurs orthogonales : la **sensibilité** $d'$ (capacité à distinguer signal et
bruit) et le **critère** $\beta$ (le seuil de décision, librement placé) :

$$d' = z(\text{taux de détection}) - z(\text{taux de fausse alarme})$$

Devant une paréidolie, **il n'y a pas de signal au sens du terrain** : $d'$ n'est
pas définissable. Reste le critère. Nephélé remplace donc explicitement le critère
de **vérité** par un critère de **partage** : une figure réussie n'est pas une
figure vraie, c'est une figure qu'on peut *faire voir* à autrui. C'est un critère
inter-subjectif (ratification), non un test d'existence.

### 4.2 Falsifiabilité et effet Barnum : l'épreuve de l'horoscope

Pour les champs non figuratifs, on veut néanmoins se prémunir contre le discours
vide. Deux outils classiques :

- **Popper** (*Logik der Forschung*, 1934) : un énoncé n'a de contenu que s'il est
  **falsifiable** — s'il existe une observation concevable qui le démentirait.
- **Forer** (*The fallacy of personal validation*, 1949) — l'**effet Barnum** : un
  énoncé assez vague pour s'appliquer à tout le monde (horoscope) est perçu comme
  vrai précisément parce qu'il n'exclut rien.

> **Traduction — l'épreuve de l'horoscope** (`AFFECT`, `P_GRAMMAIRE`). Avant qu'un
> rapport *configuration → effet* entre dans la grammaire, une question et une
> seule : *« Peux-tu imaginer une image où cette configuration est présente et
> l'effet absent ? »* Si non, l'énoncé est un Barnum, non falsifiable, rejeté.
> « Une diagonale montante interrompue par une horizontale produit une butée »
> passe ; « le rouge est passionné » échoue. Chaque entrée porte donc le triplet
> `configuration / effet / dementi_possible` — **les trois ou aucune**.

### 4.3 Deux interdictions absolues

Inscrites partout dans la doctrine : on ne récuse **jamais** une figure (i) au
motif qu'elle serait produite par le traitement de l'image, ni (ii) au motif
qu'elle « n'est pas réellement dans la matière ». La première objection est un
**solvant universel** (toute silhouette de seuillage est produite par le seuil :
l'argument invalide 100 % des figures, donc ne dit rien) ; la seconde est la
faute de catégorie du §4.

---

## 5. La grammaire configuration → effet : Arnheim, Kandinsky, Klee

Un nom trouvé dans un nuage est une donnée morte (il ne vaut que pour ce nuage).
Un **rapport** — *masse dense excentrée + quadrant opposé vide → chute* — vaut sur
toute image qui présente cette configuration. C'est la différence entre un
**catalogue** (qui s'allonge) et une **grammaire** (qui se resserre).

La tradition qui écrit cette grammaire :

- **Kandinsky**, *Du spirituel dans l'art* (1911), *Point et ligne sur plan*
  (1926) : tentative de lexique des forces plastiques élémentaires.
- **Paul Klee**, *Pädagogisches Skizzenbuch* (1925, Bauhaus) : la genèse de la
  forme par le mouvement du point et de la ligne.
- **Rudolf Arnheim**, *Art and Visual Perception* (1954) — la référence maîtresse :
  de la Gestalt appliquée, où chaque qualité expressive est **dérivée** d'une
  configuration et non posée. Le poids, la direction, la tension y sont des faits
  perceptifs, pas des métaphores.

Base de données du régime sensible :

- **GalleryGPT / PaintingForm** (ACM MM 2024) : ~19 k tableaux, ~50 k analyses
  formelles — référence pour l'analyse formelle non catalographique.

> **Traduction.** L'affect n'est **jamais** une affirmation ; il est toujours la
> **seconde moitié** d'une affirmation dont la première est une configuration, le
> mécanisme entre les deux (Arnheim). On apprend l'association vers **l'effet sur
> un regardeur**, jamais vers l'intention de l'œuvre (inatteignable, et catalogue
> déguisé). Le régime sensible mesure des **constatations ancrées**, pas des
> impressions ; les « mots creux » (*vibrant, atmosphère, poétique*) sont les
> dragons du non-figuratif — plus dangereux car ils passent pour de la culture.

---

## 6. Le traitement des planches : méthodes et formules

Les planches transforment l'image en champs qui coupent la reconnaissance de
scène tout en préservant l'information de contour et de rapport.

**Seuillage (planches binaires) — Otsu (1979).** Le seuil $t^\*$ maximise la
variance inter-classes de l'histogramme des niveaux de gris :

$$t^\* = \arg\max_t \; \sigma_b^2(t), \qquad \sigma_b^2(t) = \omega_0(t)\,\omega_1(t)\,\big(\mu_0(t)-\mu_1(t)\big)^2$$

où $\omega_i$ sont les masses des deux classes et $\mu_i$ leurs moyennes.

**Bords — Canny (1986).** Extraction du contour par gradient, suppression des
non-maxima et hystérésis : la silhouette réduite aux lignes d'information
(Attneave, §2.3).

**Familles de teintes — k-moyennes (Lloyd 1957/1982 ; MacQueen 1967).**
Quantification des couleurs en $k$ aplats minimisant l'inertie intra-classe :

$$\min_{\{\mu_j\}} \; \sum_{i} \min_{j\in\{1..k\}} \lVert x_i - \mu_j \rVert^2$$

**Chaud / froid — théorie des couleurs opposées (Hering ; Hurvich & Jameson
1957).** La projection sur l'axe chaud–froid (orange↔bleu) isole ce que la
température fait à l'espace : le chaud avance, le froid recule — un opérateur de
profondeur, pas une humeur. La grille gravée passe au vert pour ne pas être lue
comme une zone chaude.

> **Traduction.** `planches` (recul, chaud/froid, valeur seule, la touche, chroma,
> familles) dans `index.html`. La planche **chaud/froid** est la plus révélatrice
> pour la peinture : l'impressionnisme *est* un système de rapports colorés.

---

## 7. Le banc d'abstraction : mesurer sans juger

Le banc (`banc.html`) mesure ce que **devient le discours** du modèle à mesure que
l'image s'abstrait (dégradation par paliers, de net à ÷32). Il ne convoque aucun
modèle pour évaluer : il **compte**, contre des lexiques éditables. Quatre axes :

- **figuration** — densité de noms concrets (nommer là où il n'y a plus rien) ;
- **jargon** — densité de mots creux (parler sans désigner) ;
- **ancrage** — références à la grille et termes de position, par phrase ;
- **esquive** — densité de *semble, pourrait, il est difficile de*.

**Le jargon comme bruit — Shannon (1948).** Un discours qui n'augmente pas
l'information sur l'image est du bruit. L'entropie

$$H(X) = -\sum_i p(x_i)\,\log_2 p(x_i)$$

donne le cadre : le croisement des courbes du banc est le **seuil d'abstraction**
du modèle — le point où le discours cesse de désigner et se met à réciter.

**Test apparié — mesure de récitation.** La même œuvre entière, puis un fragment
non identifiable. Si l'œuvre reconnue déclenche des termes de catalogue (noms de
peintres, d'écoles) et pas son propre fragment, le discours venait du catalogue,
pas de l'œil. C'est une mesure directe de contamination par la mémoire.

**Similarité textuelle (harnais de test).** Deux mesures exactes, sans embeddings :

- **Cosinus** sac-de-mots entre deux lectures :
  $$\cos(\theta) = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert} = \frac{\sum_i a_i b_i}{\sqrt{\sum_i a_i^2}\,\sqrt{\sum_i b_i^2}}$$
- **Distance de Levenshtein** (1966), nombre minimal d'éditions :
  $$d(i,j) = \min\begin{cases} d(i{-}1,j)+1 \\ d(i,j{-}1)+1 \\ d(i{-}1,j{-}1) + \mathbb{1}[a_i \neq b_j] \end{cases}$$

Elles bornent la **dérive** de la sortie normalisée face à des réponses déformées
(`tests/similarity.js`) et vérifient la stabilité des mesures du banc.

---

## 8. Apprentissage : mémoire lente, mémoire rapide

L'architecture d'apprentissage suit la théorie des **systèmes d'apprentissage
complémentaires** (**McClelland, McNaughton & O'Reilly**, 1995) : une **mémoire
lente** (le cortex — ici les poids du modèle, consolidés par fine-tuning) et une
**mémoire rapide** (l'hippocampe — ici la grammaire injectée, apprise en séance).
Le fine-tuning **consolide** la grammaire, il ne la remplace pas.

### 8.1 Phase 0 — le corpus

Chaque séance s'enregistre au format d'entraînement (planche vue + doctrine
injectée + verdicts). **Règle absolue : ne jamais entraîner sur du non-ratifié**
(sinon amplificateur de défauts). Le banc arbitre chaque cycle sur des images
**jamais vues** à l'entraînement — d'où le découpage held-out *par image*
(`prepare_data.py`), sans fuite.

### 8.2 Phase 1 — SFT (Supervised Fine-Tuning)

Apprentissage supervisé du format et du réflexe d'ancrage. Minimisation de
l'entropie croisée token à token sur la cible ratifiée :

$$\mathcal{L}_{\text{SFT}} = -\sum_{t} \log \pi_\theta\big(y_t \mid y_{<t},\, x,\, \text{image}\big)$$

Support : VLM ouvert **Qwen2.5-VL-7B**, recette TRL/HF.

### 8.3 Phase 2 — DPO (Direct Preference Optimization)

L'apprentissage de préférence part d'une modélisation classique du choix par
paires, le modèle de **Bradley–Terry** (1952) :

$$P(y_w \succ y_l \mid x) = \frac{e^{\,r(x,y_w)}}{e^{\,r(x,y_w)} + e^{\,r(x,y_l)}} = \sigma\big(r(x,y_w) - r(x,y_l)\big)$$

Le **RLHF** (**Christiano et al.** 2017 ; **Ouyang et al.** 2022, InstructGPT)
apprenait d'abord une récompense $r$ puis optimisait par RL. **DPO** (**Rafailov
et al.**, NeurIPS 2023) montre qu'on peut se passer du RL : la politique optimale
sous contrainte KL exprime *implicitement* la récompense, et l'on optimise
directement

$$\mathcal{L}_{\text{DPO}} = -\,\mathbb{E}_{(x,\,y_w,\,y_l)}\Big[\log \sigma\Big(\beta \log \frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)} - \beta \log \frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\Big)\Big]$$

où $y_w$ (*chosen*) est la lecture ratifiée, $y_l$ (*rejected*) la rejetée, et
$\beta$ règle l'écart au modèle de référence. **Le clic de Marc *est* la fonction
de récompense.**

### 8.4 LoRA : adaptation à bas rang

**Hu et al.** (*LoRA*, ICLR 2022) : au lieu de mettre à jour $W_0$, on apprend une
correction de rang faible, ce qui réduit d'ordres de grandeur les paramètres
entraînés :

$$W = W_0 + \Delta W, \qquad \Delta W = \frac{\alpha}{r}\,B A, \quad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k},\; r \ll \min(d,k)$$

Nephélé cible les modules d'attention avec $r=16,\ \alpha=32$. **QLoRA**
(**Dettmers et al.**, 2023) ajoute la quantification 4 bits — mais on ne l'utilise
**pas** sur Apple Silicon (bitsandbytes incompatible MPS) : avec 64 Go de mémoire
unifiée, le 7B se charge en 16 bits natif.

### 8.5 Piste parallèle : silhouette → concept (ZS-SBIR)

Un amorceur **non verbal**, incontaminable par le corpus verbal : un encodeur
contrastif type **CLIP** (**Radford et al.**, ICML 2021) / **SigLIP** (**Zhai et
al.**, ICCV 2023) fine-tuné pour la tâche *silhouette → concept* (champ du
**zero-shot sketch-based image retrieval**). Les planches binarisées sont déjà des
quasi-esquisses. L'objectif contrastif (InfoNCE) aligne image et concept :

$$\mathcal{L}_{\text{NCE}} = -\log \frac{\exp(\langle f(x), g(c^{+})\rangle / \tau)}{\sum_{c}\exp(\langle f(x), g(c)\rangle / \tau)}$$

Ce chemin ne produit pas de texte : il ne peut donc pas réciter le catalogue.

---

## 9. Synthèse : chaque décision, sa raison

| Mécanisme du code | Fondement |
|---|---|
| Ne jamais montrer la photo, seulement des planches | Léonard, Cozens ; couper la reconnaissance de scène |
| *Descendre d'échelle*, *chercher la pointe* | Attneave 1954 (information aux extrema de courbure) |
| *Pivoter*, *tenir deux figures* | Bistable Images ACL 2024 ; rivalité perceptive |
| *Cherche la tête* | FFA (Kanwisher 1997) ; prior visage bayésien |
| Second regard (confirme/affine/remplace) | Gestalt (clôture) ; anti-monomanie |
| « Est-ce que ça tient le contour ? » | Prägnanz / principe du minimum (Hochberg 1953) |
| Critère de partage, pas de vérité | Détection du signal (Green & Swets 1966) |
| Épreuve de l'horoscope | Popper 1934 ; effet Barnum-Forer 1949 |
| Grammaire configuration → effet | Arnheim 1954 ; Kandinsky ; Klee |
| Chaud/froid comme opérateur d'espace | Couleurs opposées (Hering ; Hurvich & Jameson 1957) |
| Planches binaires / familles | Otsu 1979 ; Canny 1986 ; k-moyennes |
| Le banc compte le jargon | Shannon 1948 (jargon = bruit) |
| Similarité cosinus / Levenshtein | Salton ; Levenshtein 1966 |
| Grammaire injectée + poids fine-tunés | Systèmes complémentaires (McClelland 1995) |
| DPO sur les verdicts | Bradley-Terry 1952 ; Rafailov 2023 |
| LoRA r=16 sur l'attention | Hu et al. 2022 |
| Amorceur non verbal | CLIP 2021 ; SigLIP 2023 ; ZS-SBIR |

---

## Bibliographie

**Perception, Gestalt, information visuelle**
- Wertheimer, M. (1923). *Untersuchungen zur Lehre von der Gestalt II.*
- Koffka, K. (1935). *Principles of Gestalt Psychology.*
- Hochberg, J. & McAlister, E. (1953). *A quantitative approach to figural goodness.* J. Exp. Psychol.
- von Helmholtz, H. (1867). *Handbuch der physiologischen Optik.*
- Attneave, F. (1954). *Some informational aspects of visual perception.* Psychol. Review.
- Marr, D. (1982). *Vision.*
- Biederman, I. (1987). *Recognition-by-components.* Psychol. Review.
- Friston, K. (2010). *The free-energy principle.* Nature Rev. Neuroscience.
- Kanwisher, McDermott & Chun (1997). *The fusiform face area.* J. Neuroscience.
- Liu, J. et al. (2014). *Seeing Jesus in toast* (face pareidolia). Cortex.
- Conrad, K. (1958). *Die beginnende Schizophrenie* (apophénie).

**Multistabilité, paréidolie, Rorschach**
- Rorschach, H. (1921). *Psychodiagnostik.*
- Jastrow, J. (1899) ; Wittgenstein, L. (1953). *Recherches philosophiques* (voir-comme).
- *Bistable Images* (CMCL/ACL, 2024).
- *Rorschach × IA* (JMIR Mental Health, réf. projet).
- *Seeing Faces in Things* — FacesInThings (ECCV 2024, MIT).

**Décision, épistémologie**
- Green, D. & Swets, J. (1966). *Signal Detection Theory and Psychophysics.*
- Popper, K. (1934). *Logik der Forschung.*
- Forer, B. (1949). *The fallacy of personal validation* (effet Barnum).

**Esthétique formelle**
- Léonard de Vinci. *Trattato della pittura* (v. 1500).
- Cozens, A. (1785). *A New Method of Assisting the Invention…*
- Kandinsky, W. (1911) *Du spirituel dans l'art* ; (1926) *Point et ligne sur plan.*
- Klee, P. (1925). *Pädagogisches Skizzenbuch.*
- Arnheim, R. (1954). *Art and Visual Perception.*
- *GalleryGPT / PaintingForm* (ACM MM 2024).

**Traitement d'image**
- Otsu, N. (1979). *A threshold selection method from gray-level histograms.* IEEE TSMC.
- Canny, J. (1986). *A computational approach to edge detection.* IEEE PAMI.
- Lloyd, S. (1982). *Least squares quantization in PCM* ; MacQueen (1967).
- Hurvich, L. & Jameson, D. (1957). *An opponent-process theory of color vision.* Psychol. Review.
- Shannon, C. (1948). *A mathematical theory of communication.* Bell System Tech. J.
- Levenshtein, V. (1966). *Binary codes capable of correcting deletions, insertions, and reversals.*

**Apprentissage automatique**
- McClelland, McNaughton & O'Reilly (1995). *Complementary learning systems.* Psychol. Review.
- Bradley, R. & Terry, M. (1952). *Rank analysis of incomplete block designs.* Biometrika.
- Christiano, P. et al. (2017). *Deep RL from human preferences.* NeurIPS.
- Ouyang, L. et al. (2022). *Training language models to follow instructions* (InstructGPT).
- Rafailov, R. et al. (2023). *Direct Preference Optimization.* NeurIPS.
- Hu, E. et al. (2022). *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR.
- Dettmers, T. et al. (2023). *QLoRA.* NeurIPS.
- Radford, A. et al. (2021). *Learning Transferable Visual Models (CLIP).* ICML.
- Zhai, X. et al. (2023). *Sigmoid Loss for Language-Image Pre-training (SigLIP).* ICCV.
- Qwen Team (2024–2025). *Qwen2.5-VL.*

---

*Les dates et attributions renvoient aux œuvres fondatrices ; les quatre
références notées « réf. projet » (FacesInThings, Bistable Images, Rorschach × IA,
GalleryGPT/PaintingForm) sont les points d'appui empiriques directs de Nephélé,
détaillés dans `CLAUDE.md`.*
