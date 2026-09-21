"""
Dépouillement du contrôle d'occlusion B — l'instrument, pas l'impression.

On donne à ce script les quatre lectures (une par condition, en .txt) et il
rend les comptes qui tranchent. Il ne réinvente aucun lexique : le lexique
figuré et les deux expressions régulières de coordonnées sont LUS dans les
fichiers de production (doctrine.js, banc.html), pour qu'il n'existe qu'une
seule source de vérité.

Deux familles lui sont propres, tirées mot à mot du relevé Notre-Dame :

  FEU        — incendie, brûle, consume, braise… : la couche qui a SURVÉCU au
               recadrage, et qu'on suppose licenciée par la configuration.
  SAUVETAGE  — scindée en deux, parce que le gradient Notre-Dame les a
               séparées :
               .generique : étayer, armature, soutenir, s'effondrer — que des
                 échafaudages visibles autorisent faiblement ;
               .monument   : cathédrale, patrimoine, sacré, reconstruction,
                 pansement, blessure — la couche épisodique, celle qui est
                 MORTE avec les tours.

Usage :
  python depouiller.py lectures/N0.txt lectures/N1.txt lectures/N2.txt lectures/N3.txt
  python depouiller.py lectures/*.txt
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

FEU = """incendie incendier brasier brûler brûle brûlant brulant flamme flamber
flamboyer braise ardent ardeur embraser embrasé consumer consume consumé
fournaise calciner calciné cendre fumée feu attiser rougeoyer rougeoiement
incandescent incandescence"""

SAUVETAGE_GENERIQUE = """étayer étai étayage armature soutenir soutènement
effondrer effondrement écrouler écroulement crouler s'affaisser affaissement
consolider consolidation béquille tenir"""

SAUVETAGE_MONUMENT = """cathédrale basilique monument patrimoine sacré sanctuaire
nef flèche clocher reconstruire reconstruction restaurer restauration pansement
panser blessure blessé plaie cicatrice sauver sauvetage rescapé deuil relique
mémoire siècle gothique"""


def sans_acc(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def mots_de(t: str) -> list[str]:
    return [m for m in re.split(r"\s+", re.sub(r"[^a-z0-9'\- ]", " ", sans_acc(t))) if m]


def lex_doctrine(nom: str) -> set[str]:
    """Extrait un lexique du littéral gabarit de doctrine.js — source unique."""
    src = (RACINE / "doctrine.js").read_text(encoding="utf-8")
    m = re.search(rf"const {nom} = `(.*?)`;", src, re.S)
    if not m:
        raise SystemExit(f"lexique {nom} introuvable dans doctrine.js")
    return {sans_acc(w) for w in re.split(r"[\s,;]+", m.group(1)) if len(w) > 2}


def compte(mots: list[str], lexique: set[str]) -> int:
    c = 0
    for m in mots:
        if m in lexique:
            c += 1
            continue
        r = re.sub(r"(es|s|e)$", "", m)
        if len(r) > 2 and r in lexique:
            c += 1
    return c


def coordonnees(texte: str) -> tuple[int, int]:
    """Les deux expressions régulières de banc.html, à l'identique."""
    grille = len(re.findall(r"\b[A-E]\s?[1-5]\b", texte, re.I))
    quads = len(
        re.findall(
            r"\b(?:quadrant|quart|moitie|coin|bande|tiers)s? "
            r"(?:superieur|inferieur|gauche|droit|central|haut|bas|median)",
            sans_acc(texte),
        )
    )
    return grille, quads


def mesurer(texte: str, lex_concret: set[str]) -> dict:
    mots = mots_de(texte)
    grille, quads = coordonnees(texte)
    coord = grille + quads
    concret = compte(mots, lex_concret)
    return {
        "mots": len(mots),
        "feu": compte(mots, {sans_acc(w) for w in FEU.split()}),
        "sauv_gen": compte(mots, {sans_acc(w) for w in SAUVETAGE_GENERIQUE.split()}),
        "sauv_mon": compte(mots, {sans_acc(w) for w in SAUVETAGE_MONUMENT.split()}),
        "concret": concret,
        "coord": coord,
        "ratio": round(concret / max(1, coord), 2),
    }


VERDICT = """
────────────────────────────────────────────────────────────────────────────
LA RÈGLE, ÉCRITE AVANT LES LECTURES (on ne la réajuste pas après coup)
────────────────────────────────────────────────────────────────────────────
1. Le feu est-il perceptif ?
   FEU(N1) > 0 et FEU(N1) > FEU(N0) et FEU(N1) > FEU(N3)
   -> oui : la configuration licencie le feu, le 4 août tient.
   -> non : le feu des recadrages Notre-Dame était de la reconnaissance
      résiduelle, et la conclusion du 4 août est à RÉVISER.

2. Quel facteur le porte ?
   FEU(N1) >> FEU(N2) -> c'est le treillis.
   FEU(N1) ~= FEU(N2) -> c'est le ciel rouge seul.

3. La couche épisodique reste-t-elle muette sur un bâtiment sans identité ?
   SAUV_MON ~= 0 partout -> oui : ce vocabulaire exigeait bien de reconnaître.
   SAUV_MON > 0 ici      -> non : il est licencié par la configuration, et la
      frontière tracée le 4 août entre les deux couches est à redessiner.

4. Distance au visible : le ratio figuré/grille doit rester bas et STABLE
   entre les quatre conditions. S'il grimpe en N1/N2, le virage nuit rouge
   ne fait pas que colorer — il décroche le modèle de ce qu'il peut montrer.
────────────────────────────────────────────────────────────────────────────
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lectures", nargs="+", help="un .txt par condition (N0…N3)")
    args = ap.parse_args()

    lex_concret = lex_doctrine("LEX_CONCRET")
    print(f"{'lecture':<26}{'mots':>6}{'FEU':>6}{'sauv.gen':>10}{'sauv.MON':>10}"
          f"{'concret':>9}{'coord':>7}{'fig/grille':>12}")
    for p in sorted(Path(x) for x in args.lectures):
        if not p.exists():
            sys.exit(f"introuvable : {p}")
        m = mesurer(p.read_text(encoding="utf-8"), lex_concret)
        print(f"{p.stem:<26}{m['mots']:>6}{m['feu']:>6}{m['sauv_gen']:>10}"
              f"{m['sauv_mon']:>10}{m['concret']:>9}{m['coord']:>7}{m['ratio']:>12}")
    print(VERDICT)


if __name__ == "__main__":
    main()
