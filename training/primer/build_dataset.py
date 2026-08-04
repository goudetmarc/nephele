"""
Constructeur du jeu de distillation : (silhouette, image originale) par paires.

Entrée : un dossier d'images quelconques (COCO, OpenImages, ta photothèque —
n'importe quel corpus PUBLIC ; aucune ratification n'est requise car la
supervision est l'image elle-même, pas un jugement humain).

Sortie : out/
  silhouettes/xxx.png   — la planche Otsu, produite par binarise.py (fidèle app)
  originals/xxx.jpg     — l'original redimensionné comme dans l'app
  manifest_train.jsonl  — {"sil": ..., "orig": ...} par ligne
  manifest_val.jsonl    — split déterministe (hash du nom, ~5 %)

Usage :
  python build_dataset.py --images /chemin/vers/images --out data/primer
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from binarise import binarise, resize_like_app

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="dossier d'images source")
    ap.add_argument("--out", required=True, help="dossier de sortie")
    ap.add_argument("--val-share", type=float, default=0.05)
    ap.add_argument("--limit", type=int, default=0, help="0 = tout")
    args = ap.parse_args()

    src = Path(args.images)
    out = Path(args.out)
    (out / "silhouettes").mkdir(parents=True, exist_ok=True)
    (out / "originals").mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in src.rglob("*") if p.suffix.lower() in EXTS)
    if args.limit:
        files = files[: args.limit]

    n_ok, n_bad = 0, 0
    with open(out / "manifest_train.jsonl", "w") as ftr, open(out / "manifest_val.jsonl", "w") as fva:
        for p in files:
            try:
                img = Image.open(p)
                img.load()
            except Exception:
                n_bad += 1
                continue
            stem = hashlib.sha1(str(p).encode()).hexdigest()[:16]
            orig = resize_like_app(img.convert("RGB"))
            sil = binarise(img)
            sp = out / "silhouettes" / f"{stem}.png"
            op = out / "originals" / f"{stem}.jpg"
            sil.save(sp)
            orig.save(op, quality=90)
            row = json.dumps({"sil": str(sp), "orig": str(op)})
            # split déterministe : reproductible d'une machine à l'autre
            is_val = (int(stem[:8], 16) % 10_000) < args.val_share * 10_000
            (fva if is_val else ftr).write(row + "\n")
            n_ok += 1

    print(f"ok — {n_ok} paires écrites, {n_bad} images illisibles, sortie: {out}")


if __name__ == "__main__":
    main()
