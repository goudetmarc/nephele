"""
Dépouillement de l'expérience B — rendre « tricher » comptable.

Le protocole dit : tricher = chacun récite son humeur quel que soit l'image ;
honnêteté = chacun trouve ce que l'autre manque ET nomme où l'œuvre lui
résiste. Ces deux phrases sont mesurables, et c'est tout l'objet de ce
fichier — sinon le verdict retombe sur « la prose était belle », c'est-à-dire
sur l'amplificateur de défauts de la v2.

LA MESURE CENTRALE, ET POURQUOI ELLE EST ROBUSTE.

  R(t) = cosinus moyen entre les lectures d'UN MÊME tempérament sur des
         images DIFFÉRENTES.        -> haut = il récite son humeur.
  S(i) = cosinus entre les deux tempéraments sur LA MÊME image.
                                    -> haut = l'image mène la lecture.

L'inégalité qui tranche est  moyenne(S) > max(R).  Deux regards opposés
devant la même image doivent se ressembler PLUS qu'un seul regard devant
trois images sans rapport. Si l'inverse se produit, le tempérament pèse plus
lourd que ce qui est regardé : c'est le Barnum de tempérament, le dragon
revenu par la porte de la personnalité.

C'est un RAPPORT, pas un seuil absolu : le plancher lexical du français (les
mots outils, qui gonflent tout cosinus) est le même des deux côtés et
s'annule. Les mots outils sont malgré tout retirés pour affûter la mesure, et
le cosinus brut est imprimé à côté pour que rien ne soit caché.

Usage :
  python depouiller.py                      # lit lectures/<type>-<temperament>.txt
  python depouiller.py --lectures DOSSIER
"""
from __future__ import annotations

import argparse
import math
import re
import unicodedata
from itertools import combinations
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

TYPES = ("piege", "abstrait", "inconnue")
TEMPERAMENTS = ("sombre", "bucolique")

# Mots outils du français : ils occupent la moitié d'une prose et rendraient
# tous les cosinus également hauts. Retirés pour la mesure, jamais pour le
# comptage des lexiques (qui, lui, passe par doctrine.js).
OUTILS = set("""a ai as au aux avec avoir bien ca ce ces cet cette ceux chaque ci comme
d dans de des du elle elles en encore est et etaient etait ete etre eux face il ils j je
l la le les leur leurs lui m ma mais me mes moi mon n ne ni nos notre nous on ou où par
pas peu plus pour qu que quel quelle qui s sa sans se ses si sous sur t ta te tes toi ton
tout toute toutes tous tu un une vers vos votre vous y ete cela dont meme deja alors donc
puis aussi tres trop bien entre chez apres avant depuis pendant vraiment plutot""".split())


def sans_acc(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def jetons(s: str, outils: bool = False) -> list[str]:
    """Jetons de tests/similarity.js : minuscules, ponctuation ôtée."""
    bruts = re.findall(r"[^\W_]+", s.lower(), re.UNICODE)
    if outils:
        return bruts
    return [j for j in bruts if sans_acc(j) not in OUTILS and len(j) > 2]


def cosinus(a: str, b: str, outils: bool = False) -> float:
    ta, tb = jetons(a, outils), jetons(b, outils)
    if not ta or not tb:
        return 1.0 if len(ta) == len(tb) else 0.0
    va, vb = {}, {}
    for t in ta:
        va[t] = va.get(t, 0) + 1
    for t in tb:
        vb[t] = vb.get(t, 0) + 1
    dot = sum(n * vb[t] for t, n in va.items() if t in vb)
    na = math.sqrt(sum(n * n for n in va.values()))
    nb = math.sqrt(sum(n * n for n in vb.values()))
    return dot / (na * nb)


def lex_doctrine(nom: str) -> set[str]:
    src = (RACINE / "doctrine.js").read_text(encoding="utf-8")
    m = re.search(rf"const {nom} = `(.*?)`;", src, re.S)
    if not m:
        raise SystemExit(f"lexique {nom} introuvable dans doctrine.js")
    return {sans_acc(w) for w in re.split(r"[\s,;]+", m.group(1)) if len(w) > 2}


def compte(texte: str, lexique: set[str]) -> int:
    c = 0
    for m in re.split(r"\s+", re.sub(r"[^a-z0-9'\- ]", " ", sans_acc(texte))):
        if not m:
            continue
        if m in lexique or (len(re.sub(r"(es|s|e)$", "", m)) > 2
                            and re.sub(r"(es|s|e)$", "", m) in lexique):
            c += 1
    return c


POSITIONS = (r"\b(?:quadrant|quart|moitie|coin|bande|tiers)s? "
             r"(?:superieur|inferieur|gauche|droit|central|haut|bas|median)")


def coordonnees(texte: str) -> int:
    """Les deux expressions de banc.html, à l'identique."""
    return (len(re.findall(r"\b[A-E]\s?[1-5]\b", texte, re.I))
            + len(re.findall(POSITIONS, sans_acc(texte))))


def friction(texte: str) -> tuple[bool, int, bool]:
    """(présente, mots du bloc, ancrée) — le « Là où elle me résiste : »."""
    m = re.search(r"la ou elle me resiste\s*:?", sans_acc(texte))
    if not m:
        return False, 0, False
    bloc = texte[m.end():]
    mots = len(jetons(bloc, outils=True))
    ancree = coordonnees(bloc) > 0 or bool(
        re.search(r"\b(zone|haut|bas|gauche|droite|centre|angle|bord|fond)\b", sans_acc(bloc))
    )
    return True, mots, ancree


VERDICT = """
────────────────────────────────────────────────────────────────────────────
LA RÈGLE, ÉCRITE AVANT LES LECTURES (on ne la réajuste pas après coup)
────────────────────────────────────────────────────────────────────────────
1. LE BARNUM DE TEMPÉRAMENT — moyenne(S) > max(R) ?
   oui  : l'image mène la lecture. Le prior est perméable.
   non  : au moins un tempérament se ressemble plus à travers trois images
          sans rapport que les deux tempéraments ne se ressemblent devant la
          même. Il récite. C'est TRICHER, et la version en prompt ne mérite
          pas qu'on lui consacre un LoRA.

2. LA FRICTION — les six lectures ont-elles un bloc « Là où elle me
   résiste : », non vide ET ancré à un endroit ?
   Une friction absente, ou présente mais qui ne nomme aucun lieu, est une
   friction de politesse : elle compte comme absente.

3. LA COMPLÉMENTARITÉ — sur une même image, les deux pointent-ils des
   endroits DIFFÉRENTS (recouvrement de Jaccard bas) tout en restant tous
   deux ancrés (coord > 0) ? C'est « chacun trouve ce que l'autre manque ».
   Attendu surtout sur l'abstrait et l'inconnue : sur le piège, la
   convergence peut venir du catalogue partagé, pas de l'image.

4. LE JARGON reste bas partout. Le régime projectif autorise l'émotion, pas
   les mots creux : « vibrant », « atmosphérique » ne sont toujours dus qu'au
   connaisseur, qui n'est pas de la partie ici.
────────────────────────────────────────────────────────────────────────────
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lectures", default=str(Path(__file__).parent / "lectures"))
    args = ap.parse_args()
    dossier = Path(args.lectures)

    textes: dict[tuple[str, str], str] = {}
    manquants = []
    for ty in TYPES:
        for te in TEMPERAMENTS:
            p = dossier / f"{ty}-{te}.txt"
            if p.exists():
                textes[(ty, te)] = p.read_text(encoding="utf-8")
            else:
                manquants.append(p.name)
    if manquants:
        raise SystemExit("lectures manquantes : " + ", ".join(manquants))

    lex_creux = lex_doctrine("LEX_CREUX")
    lex_concret = lex_doctrine("LEX_CONCRET")

    # ── par lecture ────────────────────────────────────────────────────────
    print(f"{'lecture':<22}{'mots':>6}{'jargon':>8}{'coord':>7}{'fig/grille':>12}"
          f"{'friction':>10}{'ancrée':>8}")
    for (ty, te), t in textes.items():
        mots = len(jetons(t, outils=True))
        coord = coordonnees(t)
        concret = compte(t, lex_concret)
        pres, nmots, ancree = friction(t)
        etat = f"{nmots} mots" if pres else "ABSENTE"
        print(f"{ty + '-' + te:<22}{mots:>6}{compte(t, lex_creux):>8}{coord:>7}"
              f"{round(concret / max(1, coord), 2):>12}{etat:>10}"
              f"{('oui' if ancree else 'NON') if pres else '—':>8}")

    # ── R(t) : un tempérament à travers les images ─────────────────────────
    print()
    R = {}
    for te in TEMPERAMENTS:
        paires = [cosinus(textes[(a, te)], textes[(b, te)]) for a, b in combinations(TYPES, 2)]
        R[te] = sum(paires) / len(paires)
        brut = [cosinus(textes[(a, te)], textes[(b, te)], outils=True)
                for a, b in combinations(TYPES, 2)]
        print(f"R({te:<9}) = {R[te]:.3f}   (brut, mots outils inclus : "
              f"{sum(brut) / len(brut):.3f})   — lui à travers trois images")

    # ── S(i) : les deux tempéraments devant la même image ──────────────────
    S = {}
    for ty in TYPES:
        S[ty] = cosinus(textes[(ty, "sombre")], textes[(ty, "bucolique")])
        brut = cosinus(textes[(ty, "sombre")], textes[(ty, "bucolique")], outils=True)
        print(f"S({ty:<9}) = {S[ty]:.3f}   (brut : {brut:.3f})"
              f"   — les deux devant la même image")

    moyS, maxR = sum(S.values()) / len(S), max(R.values())
    verdict = "l'image mène" if moyS > maxR else "LE TEMPÉRAMENT MÈNE — récitation"
    print(f"\nmoyenne(S) = {moyS:.3f}   max(R) = {maxR:.3f}   ->  {verdict}")

    # ── complémentarité : pointent-ils les mêmes endroits ? ────────────────
    print()
    for ty in TYPES:
        a = set(jetons(textes[(ty, "sombre")]))
        b = set(jetons(textes[(ty, "bucolique")]))
        j = len(a & b) / max(1, len(a | b))
        ca = coordonnees(textes[(ty, "sombre")])
        cb = coordonnees(textes[(ty, "bucolique")])
        print(f"complémentarité {ty:<10} Jaccard {j:.3f}   ancrage sombre {ca}, bucolique {cb}")

    print(VERDICT)


if __name__ == "__main__":
    main()
