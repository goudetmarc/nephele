# Expérience B — les tempéraments

*Montée le 2026-09-21. Intention et plan dans `RECHERCHE.md` (« The wager »,
« Tomorrow's protocol », « Experiment B »). Doctrine : `P_TEMP_SOMBRE`,
`P_TEMP_BUCOLIQUE`, `OBLIGATION_FRICTION` dans `doctrine.js`.*

## La question

Deux éducations opposées lisent la **même** œuvre. La question n'est pas
laquelle a raison : c'est de savoir si **un prior fort peut rester
perméable**. L'ancre empirique du projet dit l'inverse par défaut — la
monomanie interprétative est robuste (Bistable Images, ACL 2024) : le
mélancolique trouve le crépuscule dans le champ ensoleillé. Ce n'est pas de
l'intuition, c'est un **Barnum de tempérament** — le dragon revenu par la
porte de la personnalité.

- **Tricher** = chacun récite son humeur quelle que soit l'image.
- **Honnêteté** = chacun trouve ce que l'autre manque **et** nomme où l'œuvre
  lui résiste.

Ces deux phrases sont mesurables. Tout l'enjeu de `depouiller.py` est de ne
pas laisser le verdict retomber sur « la prose était belle » — c'est-à-dire
sur l'amplificateur de défauts de la v2.

## Les trois images, et pourquoi trois

L'effet n'est lisible que dans le **contraste** : une seule image ne peut pas
distinguer un tempérament qui voit d'un tempérament qui récite.

| type | image | ce qu'elle teste |
|---|---|---|
| `piege` | Van Gogh, *Champ de blé avec cyprès* (1889) | l'œuvre sur-commentée, là où la récitation est la plus tentante. Motif bucolique sous ciel convulsif : **aucun des deux tempéraments n'a de terrain gratuit** |
| `abstrait` | un papier marbré (British Library) | un champ non figuratif fait pour être regardé, **sans aucun catalogue à réciter** |
| `inconnue` | de la rouille sur tôle | pas une œuvre du tout : la matière fondatrice du projet, **zéro culture, forme pure** |

Les trois sont CC0 et téléchargées à la demande (voir `SOURCES.md`) ; rien de
binaire n'est versionné. `--images DOSSIER` permet de substituer les siennes.

## La mesure centrale

```
R(t) = cosinus moyen entre les lectures d'UN MÊME tempérament
       sur des images DIFFÉRENTES     -> haut = il récite son humeur
S(i) = cosinus entre les DEUX tempéraments sur LA MÊME image
                                      -> haut = l'image mène la lecture
```

**L'inégalité qui tranche : `moyenne(S) > max(R)`.** Deux regards opposés
devant la même image doivent se ressembler **plus** qu'un seul regard devant
trois images sans rapport. Si l'inverse se produit, le tempérament pèse plus
lourd que ce qui est regardé.

C'est un **rapport, pas un seuil absolu** : le plancher lexical du français
(les mots outils, qui gonflent tout cosinus) est le même des deux côtés et
s'annule. Les mots outils sont retirés pour affûter la mesure, et le cosinus
brut est imprimé à côté pour que rien ne soit caché.

Le jeton et le cosinus sont ceux de `tests/similarity.js`, portés à
l'identique ; les lexiques viennent de `doctrine.js` et les expressions de
coordonnées de `banc.html`. Aucune mesure n'est réinventée ici.

## Ce qui a déjà tourné (2026-09-21)

Les trois images sont fabriquées et leurs planches vérifiées avec le
binariseur de production : encre à 26,9 / 65,5 / 65,4 %. Le piège est plus
clair que les deux autres — c'est une toile, pas une matière — sans que cela
gêne : la comparaison se fait entre tempéraments sur une même image, jamais
entre images.

L'instrument est testé sur deux jeux de lectures factices et **discrimine** :

| | moyenne(S) | max(R) | verdict | friction ancrée | coord |
|---|---|---|---|---|---|
| jeu « triche » | 0,667 | 1,000 | tempérament mène | non (6/6) | 0 |
| jeu « honnête » | 0,408 | 0,147 | l'image mène | oui (6/6) | 3–5 |

## Ce qui reste à faire — la passe modèle

Sur le Mac, sur le modèle local. Six lectures : trois images × deux
tempéraments.

```
cd experiences/experience-b
python3 preparer.py --planches      # écrit out/ : 3 images + 3 planches
```

Dans `dixit.html`, cocher **« Tempéraments — expérience B »**, charger
`out/piege.png`, puis `out/abstrait.png`, puis `out/inconnue.png`. Pour
chacune, coller les deux proses dans :

```
lectures/piege-sombre.txt      lectures/piege-bucolique.txt
lectures/abstrait-sombre.txt   lectures/abstrait-bucolique.txt
lectures/inconnue-sombre.txt   lectures/inconnue-bucolique.txt
```

Puis :

```
python3 depouiller.py
```

## Le verdict, écrit avant les lectures

La règle est **dans `depouiller.py`** et s'imprime à chaque dépouillement. En
résumé : (1) `moyenne(S) > max(R)`, sinon c'est de la récitation ; (2) les six
lectures ont un bloc « Là où elle me résiste : » non vide **et ancré à un
endroit** — une friction qui ne nomme aucun lieu est une friction de
politesse et compte comme absente ; (3) recouvrement de Jaccard bas entre les
deux tempéraments sur une même image, les deux restant ancrés ; (4) le jargon
reste bas partout.

Le résultat se consigne dans `RECHERCHE.md`, **par image, avant tout
enthousiasme**.

## Les limites, dites d'avance

- **Trois images, six lectures** : ce plan sert à décider si la version en
  prompt mérite qu'on aille plus loin, pas à fonder une statistique.
- **Le cosinus sac-de-mots est grossier.** Deux proses peuvent différer
  lexicalement en récitant la même humeur avec des synonymes. La mesure
  attrape la récitation littérale, pas la récitation paraphrasée — d'où la
  friction ancrée comme second verrou, qui, elle, exige un lieu.
- **Sur le piège, une convergence n'est pas une preuve.** Les deux
  tempéraments peuvent se rejoindre parce qu'ils partagent le catalogue, pas
  parce qu'ils regardent. C'est pourquoi la complémentarité se juge d'abord
  sur l'abstrait et l'inconnue.
- **Rien n'est entraîné.** Les LoRA de tempérament restent explicitement hors
  de portée tant que la version en prompt n'a pas fait ses preuves : des poids
  consolideraient un défaut non démontré.
