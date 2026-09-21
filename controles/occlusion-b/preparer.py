"""
Contrôle d'occlusion B — fabrication des quatre conditions.

Le gradient Notre-Dame (RECHERCHE.md) a montré que le récit de sauvetage DU
MONUMENT mourait avec les tours, tandis que l'incendie générique survivait au
recadrage. Conclusion tirée : la reconnaissance n'a pas fabriqué le feu, elle
l'a amplifié en récit. Mais il manquait le contrôle symétrique : sur un
bâtiment SANS identité, la même configuration — ciel rouge de nuit, treillis
sur une masse — produit-elle le même feu ?

Le plan est factoriel 2x2 sur UNE MÊME façade, ce qui neutralise le bâtiment,
la lumière d'origine, le matériau et le cadrage :

               |  échafaudage        |  nu
  -------------+---------------------+---------------------
  jour (brut)  |  N0                 |  N3
  nuit rouge   |  N1  <- case clé    |  N2

  N1 seul réunit les deux facteurs de Notre-Dame. Si le feu n'apparaît qu'en
  N1, la configuration le licencie et la lecture est perceptive. S'il
  apparaît aussi en N2, c'est le ciel seul qui le porte. S'il n'apparaît
  nulle part, le feu des recadrages Notre-Dame était encore de la
  reconnaissance résiduelle — et la conclusion du 4 août est à réviser.

Le virage « nuit rouge » est une INTERVENTION, pas une retouche d'ambiance :
il est scripté, déterministe, et reproduit les trois traits nommés dans le
relevé Notre-Dame — la nuit, le ciel rouge dramatique, et la structure fine
prise dans une lueur chaude (« le treillis qui ronge la pierre »).

Usage :
  python preparer.py                 # télécharge la source, écrit out/
  python preparer.py --planches      # + les planches Otsu de production
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training" / "primer"))
from binarise import binarise  # noqa: E402

# Source : voir SOURCE.md (Wikimedia Commons, CC BY-SA 4.0). La vignette 960 px
# est déjà à la résolution de production (l'app borne le côté long à 1024).
URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/"
    "CM_Castell_de_Mar_Cala_Millor_fa%C3%A7ade_renovation.jpg/"
    "960px-CM_Castell_de_Mar_Cala_Millor_fa%C3%A7ade_renovation.jpg"
)
SHA1_ATTENDU = "cabad408dfa0cb668a5a2920f433757e04a8553b"

# Recadrages, en coordonnées de la source 960x720. Tous deux excluent
# l'enseigne du toit : aucun texte lisible ne doit entrer dans le protocole.
CROP_ECHAF = (140, 40, 440, 530)   # la tour sous filet + montants verticaux
CROP_NU = (548, 146, 800, 540)     # la même façade, balcons nus, sans filet


def flou(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "L")
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0


def nuit_rouge(img: Image.Image) -> Image.Image:
    """Le virage contrôlé : nuit + ciel rouge + lueur chaude sur le treillis."""
    rgb = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # Masque de ciel : bleu dominant et clair, bord adouci pour éviter le découpage net.
    brut = np.clip((b - np.maximum(r, g)) * 4.0, 0, 1) * np.clip((lum - 0.25) * 3.0, 0, 1)
    ciel = flou(brut, 2.0)[..., None]

    # Le bâti de nuit : sombre, chaud, la structure conservée.
    bati = np.stack([lum * 1.25 + 0.02, lum * 0.72, lum * 0.55], axis=-1) * 0.42

    # La lueur sur les hautes fréquences : montants, filet, garde-corps.
    passe_haut = np.clip(lum - flou(lum, 3.0), 0, 1)
    lueur = np.clip(passe_haut * 6.0, 0, 1)[..., None] * np.array([1.0, 0.42, 0.14], np.float32)
    bati = bati + lueur * 0.85

    # Le ciel : dégradé vertical sombre -> braise, modulé par la luminance d'origine.
    h = rgb.shape[0]
    t = (np.linspace(0.0, 1.0, h, dtype=np.float32) ** 1.4)[:, None, None]
    haut = np.array([0.20, 0.03, 0.07], np.float32)
    bas = np.array([0.80, 0.18, 0.10], np.float32)
    grad = haut + (bas - haut) * t
    grad = grad * (0.85 + 0.30 * lum[..., None])

    out = bati * (1.0 - ciel) + grad * ciel
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGB")


def source(dst: Path) -> Image.Image:
    if not dst.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "NepheleResearch/1.0"})
        with urllib.request.urlopen(req) as rep, open(dst, "wb") as f:
            f.write(rep.read())
    sha = hashlib.sha1(dst.read_bytes()).hexdigest()
    if sha != SHA1_ATTENDU:
        print(f"  ! la source diffère de celle du protocole ({sha}) — vignette régénérée ?")
    return Image.open(dst).convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).parent / "out"))
    ap.add_argument("--planches", action="store_true", help="écrire aussi les planches Otsu")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    im = source(out / "_source.jpg")

    echaf, nu = im.crop(CROP_ECHAF), im.crop(CROP_NU)
    conditions = {
        "N0-echafaudage-jour": echaf,
        "N1-echafaudage-nuit-rouge": nuit_rouge(echaf),
        "N2-nu-nuit-rouge": nuit_rouge(nu),
        "N3-nu-jour": nu,
    }

    print(f"{'condition':<28} {'taille':<12} {'seuil Otsu':>10} {'encre %':>9}")
    for nom, img in conditions.items():
        img.save(out / f"{nom}.png")
        pl = binarise(img)
        a = np.asarray(pl)
        encre = float((a == 0).mean() * 100.0)
        # Le seuil est recalculé ici uniquement pour l'afficher (binarise le fait déjà).
        from binarise import luminance_like_app, otsu_like_app, resize_like_app

        seuil = otsu_like_app(luminance_like_app(np.asarray(resize_like_app(img))))
        if args.planches:
            pl.save(out / f"{nom}--planche.png")
        print(f"{nom:<28} {str(img.size):<12} {seuil:>10} {encre:>8.1f}")

    print(f"\nok — quatre conditions dans {out}")
    print("Lecture : protocole et grille de dépouillement dans README.md.")


if __name__ == "__main__":
    main()
