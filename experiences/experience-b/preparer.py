"""
Expérience B — les tempéraments : fabrication du jeu d'images.

Deux éducations opposées lisent la MÊME œuvre (`P_TEMP_SOMBRE`,
`P_TEMP_BUCOLIQUE`, et l'`OBLIGATION_FRICTION` partagée). La question n'est
pas laquelle a raison : c'est de savoir si un prior fort peut rester
perméable.

L'effet n'est lisible que dans le CONTRASTE, d'où les trois types de
`RECHERCHE.md`, et pas un de moins :

  piege     — une œuvre célèbre et sur-commentée. Là où la récitation est la
              plus tentante. Ici « Champ de blé avec cyprès » : un motif
              bucolique sous un ciel convulsif, donc AUCUN des deux
              tempéraments n'a de terrain gratuit.
  abstrait  — un champ non figuratif, fait pour être regardé, sans aucun
              catalogue à réciter : un papier marbré. Rien à reconnaître,
              tout à ressentir.
  inconnue  — pas une œuvre du tout : de la rouille. La matière fondatrice du
              projet, zéro culture, forme pure.

Les trois sources sont CC0 (voir SOURCES.md) et téléchargées à la demande :
rien de binaire n'est versionné.

Usage :
  python preparer.py                 # écrit out/
  python preparer.py --planches      # + les planches Otsu de production
  python preparer.py --images DOSSIER  # substituer ses propres images
                                       # (piege.*, abstrait.*, inconnue.*)
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "training" / "primer"))
from binarise import binarise, resize_like_app  # noqa: E402

SOURCES = {
    # Van Gogh, « Wheat Field with Cypresses » (1889) — Met, domaine public.
    "piege": "https://images.metmuseum.org/CRDImages/ep/web-large/DP-42549-001.jpg",
    # Papier décoratif marbré, British Library — CC0, via Openverse.
    "abstrait": (
        "https://images.rawpixel.com/editor_1024/"
        "czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvcGQ0My01LTM5LXBsb3lfMS5qcGc.jpg"
    ),
    # Rouille sur tôle galvanisée — CC0, via Openverse.
    "inconnue": "https://live.staticflickr.com/1675/26626290492_b39481df80_b.jpg",
}

EXTS = (".jpg", ".jpeg", ".png", ".webp")


def telecharger(url: str, dst: Path) -> None:
    if dst.exists():
        return
    req = urllib.request.Request(url, headers={"User-Agent": "NepheleResearch/1.0"})
    with urllib.request.urlopen(req) as rep, open(dst, "wb") as f:
        f.write(rep.read())


def charger(nom: str, dossier: Path | None, out: Path) -> Image.Image:
    if dossier:
        for e in EXTS:
            p = dossier / f"{nom}{e}"
            if p.exists():
                return Image.open(p).convert("RGB")
        raise SystemExit(f"{nom}{{{','.join(EXTS)}}} introuvable dans {dossier}")
    p = out / f"_source-{nom}.jpg"
    telecharger(SOURCES[nom], p)
    return Image.open(p).convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).parent / "out"))
    ap.add_argument("--images", default=None, help="dossier d'images à substituer")
    ap.add_argument("--planches", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dossier = Path(args.images) if args.images else None

    print(f"{'type':<12} {'taille':<14} {'encre %':>9}")
    for nom in ("piege", "abstrait", "inconnue"):
        img = resize_like_app(charger(nom, dossier, out))
        img.save(out / f"{nom}.png")
        pl = binarise(img)
        encre = float((np.asarray(pl) == 0).mean() * 100.0)
        if args.planches:
            pl.save(out / f"{nom}--planche.png")
        print(f"{nom:<12} {str(img.size):<14} {encre:>8.1f}")

    print(f"\nok — trois images dans {out}")
    print("Protocole et grille de dépouillement : README.md.")


if __name__ == "__main__":
    main()
