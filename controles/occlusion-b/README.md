# Contrôle d'occlusion B — le contrôle qui manquait au gradient Notre-Dame

*Monté le 2026-09-21. Théorie et résultat d'origine dans `RECHERCHE.md`
(« First measured result — the Notre-Dame occlusion gradient »).*

## La question

Le 4 août, le gradient de recadrage a séparé deux couches dans une même
lecture naïve : le **récit de sauvetage DU MONUMENT** (une cathédrale blessée
qu'on étaye pour l'empêcher de s'effondrer) est **mort avec les tours** ; le
**feu générique** (« ça brûle sans se consumer ») a **survécu**. D'où la
conclusion : la reconnaissance n'a pas fabriqué le feu, elle l'a amplifié en
récit ; le marqueur est la **distance au visible**.

Cette conclusion repose sur une moitié de preuve. Elle montre ce qui se passe
quand on **retire** l'identité d'un bâtiment reconnu. Elle ne montre pas ce
qui se passe quand on **installe la même configuration sur un bâtiment qui
n'en a jamais eu**. Si un immeuble quelconque sous ciel rouge de nuit produit
lui aussi le feu, la couche perceptive est confirmée. S'il ne produit rien, le
feu des recadrages était de la reconnaissance résiduelle — les recadrages
sentaient encore le gothique — et le relevé du 4 août est à réviser.

## Le plan — factoriel 2×2 sur une seule façade

La même tour d'hôtel porte, sur la même photo, une moitié **sous filet et
échafaudage** et une moitié **nue**. Bâtiment, matériau, lumière d'origine et
cadrage sont donc neutralisés : seuls les deux facteurs bougent.

| | échafaudage | nu |
|---|---|---|
| **jour (brut)** | `N0` | `N3` |
| **nuit rouge** | **`N1`** ← la case clé | `N2` |

`N1` seule réunit les deux traits de l'image Notre-Dame. Aucune des quatre ne
porte de texte lisible : les recadrages excluent l'enseigne de toit.

Le virage « nuit rouge » est une **intervention scriptée et déterministe**, pas
une retouche d'ambiance. Il reproduit les trois traits nommés dans le relevé
d'origine : la nuit, le ciel rouge dramatique, et la structure fine prise dans
une lueur chaude — « le treillis qui ronge la pierre ». Le code est dans
`preparer.py`, lisible ligne à ligne.

## Ce qui a déjà tourné (2026-09-21)

Les quatre conditions sont fabriquées et leurs planches Otsu vérifiées **avec
le binariseur de production** (`training/primer/binarise.py`, portage ligne à
ligne de l'app). Le pré-contrôle de comparabilité est passé : les quatre
planches ont des densités d'encre du même ordre, donc aucune condition n'est
disqualifiée avant lecture par une planche vide ou saturée.

| condition | taille | seuil Otsu | encre |
|---|---|---|---|
| `N0` échafaudage, jour | 300×490 | 130 | 62,6 % |
| `N1` échafaudage, nuit rouge | 300×490 | 94 | 74,7 % |
| `N2` nu, nuit rouge | 252×394 | 103 | 70,9 % |
| `N3` nu, jour | 252×394 | 168 | 68,0 % |

L'instrument de dépouillement est écrit et testé sur lectures factices : il
discrimine une lecture de forces nues (FEU 0, MON 0, coord 3) d'une lecture
type Notre-Dame (FEU 3, MON 3, ratio 2,0).

## Ce qui reste à faire — la passe modèle

**Elle doit tourner sur TON Mac, sur le MÊME modèle local que les lectures du
4 août.** Une passe faite ici, sur un autre modèle, ne serait pas le contrôle :
un écart mesuré ne se distinguerait plus d'un écart entre modèles. C'est le
genre d'étiquetage de source que la doctrine appelle tricher.

```
cd controles/occlusion-b
python3 preparer.py --planches       # écrit out/ : 4 conditions + 4 planches
```

Puis, dans `dixit.html`, pour **chacune** des quatre conditions, dans le même
ordre et sans rien changer entre deux :

1. charger `out/N0-….png` … `out/N3-….png` ;
2. laisser tourner **Regard nu** + **naïf à l'aveugle** + **naïf à nu** ;
3. coller les trois proses dans `lectures/N0.txt` … `lectures/N3.txt`
   (un fichier par condition, les trois voix à la suite).

Enfin :

```
python3 depouiller.py lectures/*.txt
```

## Le verdict, écrit avant les lectures

La règle est **dans `depouiller.py`** et s'imprime à chaque dépouillement,
pour qu'on ne puisse pas la réajuster après avoir vu les chiffres. En résumé :

1. **le feu est-il perceptif ?** `FEU(N1) > 0`, et supérieur à `N0` et `N3` ;
2. **quel facteur le porte ?** `N1 ≫ N2` → le treillis ; `N1 ≈ N2` → le ciel ;
3. **la couche épisodique reste-t-elle muette ?** `SAUV_MON ≈ 0` partout —
   sinon la frontière du 4 août entre les deux couches est à redessiner ;
4. **distance au visible** : le ratio figuré/grille doit rester bas et stable
   entre les quatre.

Le résultat se consigne dans `RECHERCHE.md`, par condition, **avant tout
enthousiasme** — la consigne vaut ici comme pour l'expérience B.

## Les limites, dites d'avance

- **Le bâtiment ne ressemble pas à Notre-Dame** : béton moderne, balcons
  répétitifs, palmiers. C'est le prix de l'anonymat, et c'est le bon prix —
  mais cela veut dire qu'un résultat **nul** en `N1` restera ambigu : absence
  de reconnaissance, ou configuration trop différente ? Seul un résultat
  **positif** en `N1` trancherait franchement.
- **La nuit rouge est fabriquée**, pas photographiée. Elle est donc parfaite
  en contrôle (identique d'une condition à l'autre) et imparfaite en écologie.
- **Les palmiers signent « sud / station balnéaire »** : une reconnaissance
  générique subsiste. Elle est sans identité — c'est précisément la condition
  voulue — mais elle n'est pas nulle.
- **Une seule façade, une seule photo.** Ce contrôle ferme une question, il ne
  fonde pas une statistique.
