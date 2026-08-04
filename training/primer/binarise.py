"""
Portage Python EXACT du binariseur de l'app (dixit.html : binarise()).

La fidélité à la production est une exigence du protocole, pas un détail :
le primer apprend à lire *nos* silhouettes — celles que l'app produira en
séance. Tout écart (pondération de luminance, seuil, redimensionnement)
entraînerait un primer calibré sur des images que personne ne verra.

Correspondance ligne à ligne avec le JS :
  - redimensionnement : côté max 1024, arrondi, rééchantillonnage bilinéaire
    (le canvas HTML utilise un lissage bilinéaire) ;
  - luminance : floor(r*0.299 + g*0.587 + b*0.114) — les poids Rec.601 de
    l'app, avec le même arrondi vers le bas (`|0`) ;
  - seuil : Otsu sur l'histogramme 256 classes de cette luminance,
    balayage t=0..255, variance inter-classes maximale ;
  - sortie : lum < seuil -> noir (0), sinon blanc (255).
"""
from __future__ import annotations

import numpy as np
from PIL import Image

MAX_SIDE = 1024  # même borne que l'app


def resize_like_app(img: Image.Image) -> Image.Image:
    w, h = img.size
    r = min(1.0, MAX_SIDE / max(w, h))
    if r >= 1.0:
        return img
    return img.resize((round(w * r), round(h * r)), Image.BILINEAR)


def luminance_like_app(rgb: np.ndarray) -> np.ndarray:
    """rgb uint8 (H,W,3) -> luminance uint8 (H,W), floor comme `|0` en JS."""
    lum = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    return np.floor(lum).astype(np.uint8)


def otsu_like_app(lum: np.ndarray) -> int:
    """Balayage identique au JS (max de variance inter-classes, premier max)."""
    hist = np.bincount(lum.ravel(), minlength=256).astype(np.float64)
    tot = lum.size
    s = np.arange(256, dtype=np.float64) @ hist
    sum_b = 0.0
    w_b = 0.0
    best, seuil = -1.0, 127
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = tot - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (s - sum_b) / w_f
        v = w_b * w_f * (m_b - m_f) ** 2
        if v > best:
            best, seuil = v, t
    return seuil


def binarise(img: Image.Image, seuil: int | None = None) -> Image.Image:
    """Silhouette N&B identique à celle de l'app. `seuil=None` -> Otsu."""
    img = resize_like_app(img.convert("RGB"))
    lum = luminance_like_app(np.asarray(img))
    t = otsu_like_app(lum) if seuil is None else seuil
    out = np.where(lum < t, 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="L")


if __name__ == "__main__":  # auto-test minimal : un dégradé doit couper en deux
    g = np.tile(np.arange(256, dtype=np.uint8), (64, 1))
    rgb = np.stack([g, g, g], axis=-1)
    lum = luminance_like_app(rgb)
    t = otsu_like_app(lum)
    assert 100 < t < 156, f"seuil Otsu inattendu sur dégradé : {t}"
    sil = binarise(Image.fromarray(rgb))
    vals = set(np.unique(np.asarray(sil)).tolist())
    assert vals == {0, 255}, f"la silhouette doit être strictement binaire : {vals}"
    print(f"ok — seuil dégradé = {t}, sortie binaire stricte")
