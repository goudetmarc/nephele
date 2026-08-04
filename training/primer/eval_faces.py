"""
Harnais d'évaluation FacesInThings — la mesure empirique de la case
« inné + souvenu » de la carte du regard (RECHERCHE.md).

FacesInThings (Hamilton et al., ECCV 2024 ; `pip install facesinthings`) :
~5 000 photographies de paréidolies faciales, annotées par des humains
(où est le visage, sa difficulté, etc.). Question posée au primer : sur la
SILHOUETTE seule — notre planche Otsu, sans couleur ni scène —, son embedding
se rapproche-t-il de « a face » davantage que l'encodeur de base, et ce
rapprochement suit-il la facilité humaine ?

Métriques v0 (à épingler quand l'API exacte du paquet sera confirmée sur la
machine d'entraînement — le chargement est isolé dans load_faces_dataset) :
  1. face-score = sim(silhouette, "a photo of a face")
                - sim(silhouette, "a photo of an object")   [tour texte SigLIP]
  2. delta primer = face-score(étudiant) - face-score(base) : le primer
     doit AUGMENTER le score sur ces images-là (elles contiennent un visage
     pour un humain) sans qu'on le lui ait jamais dit ;
  3. si une note de facilité humaine est disponible : corrélation de Spearman
     entre le face-score du primer et cette note.

Usage :
  python eval_faces.py --adapter runs/primer-lora [--data /chemin/faces]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from device import describe, pick_device  # noqa: E402

from binarise import binarise  # noqa: E402


def load_faces_dataset(root: str | None):
    """Renvoie une liste de {"image": PIL.Image, "ease": float|None}.

    Isolé exprès : le paquet `facesinthings` est jeune et son API peut bouger.
    Deux chemins : le paquet installé, sinon un dossier local d'images
    (--data), auquel cas ease=None et seule la métrique 2 est calculée.
    """
    from PIL import Image

    if root:
        rows = []
        for p in sorted(Path(root).rglob("*")):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                rows.append({"image": Image.open(p).convert("RGB"), "ease": None})
        if not rows:
            raise SystemExit(f"aucune image dans {root}")
        return rows
    try:
        import facesinthings  # type: ignore
    except ImportError:
        raise SystemExit("pip install facesinthings — ou passe --data /dossier/images")
    ds = facesinthings.load()  # à épingler : nom exact de l'API au premier run
    rows = []
    for ex in ds:
        img = ex["image"] if hasattr(ex, "__getitem__") else ex.image
        ease = None
        for k in ("ease", "easiness", "hardness", "difficulty"):
            if hasattr(ex, "__getitem__") and k in ex:
                ease = float(ex[k]) * (-1.0 if "hard" in k or "diff" in k else 1.0)
                break
        rows.append({"image": img.convert("RGB"), "ease": ease})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="dossier LoRA écrit par distill_siglip.py")
    ap.add_argument("--model", default="google/siglip-base-patch16-224")
    ap.add_argument("--data", default=None, help="dossier d'images local, si pas le paquet")
    ap.add_argument("--limit", type=int, default=500)
    args = ap.parse_args()

    import torch
    import torch.nn.functional as F
    from peft import PeftModel
    from transformers import AutoProcessor, SiglipModel

    device, dtype = pick_device()
    print(describe(device, dtype))

    processor = AutoProcessor.from_pretrained(args.model)
    base = SiglipModel.from_pretrained(args.model, torch_dtype=dtype).to(device).eval()
    primer_vision = PeftModel.from_pretrained(
        SiglipModel.from_pretrained(args.model, torch_dtype=dtype).vision_model, args.adapter
    ).to(device).eval()

    texts = ["a photo of a face", "a photo of an object"]
    with torch.no_grad():
        ti = processor(text=texts, return_tensors="pt", padding=True)
        zt = F.normalize(base.get_text_features(**{k: v.to(device) for k, v in ti.items()}).float(), dim=-1)

    def face_score(vision_tower, sil_px):
        with torch.no_grad():
            out = vision_tower(pixel_values=sil_px.to(device=device, dtype=dtype))
            z = F.normalize(out.pooler_output.float(), dim=-1)
            sims = z @ zt.t()
            return (sims[:, 0] - sims[:, 1]).cpu()

    rows = load_faces_dataset(args.data)[: args.limit]
    print(f"{len(rows)} images — binarisation par la planche de production…")

    scores_base, scores_primer, eases = [], [], []
    for r in rows:
        sil = binarise(r["image"]).convert("RGB")
        px = processor(images=[sil], return_tensors="pt")["pixel_values"]
        scores_base.append(face_score(base.vision_model, px).item())
        scores_primer.append(face_score(primer_vision, px).item())
        eases.append(r["ease"])

    import statistics as st
    d = [p - b for p, b in zip(scores_primer, scores_base)]
    print(f"face-score base    : {st.mean(scores_base):+.4f}")
    print(f"face-score primer  : {st.mean(scores_primer):+.4f}")
    print(f"delta primer-base  : {st.mean(d):+.4f}  (attendu > 0 : le primer voit le visage dans la planche)")

    known = [(s, e) for s, e in zip(scores_primer, eases) if e is not None]
    if len(known) > 10:
        from scipy.stats import spearmanr
        rho, p = spearmanr([s for s, _ in known], [e for _, e in known])
        print(f"Spearman face-score ↔ facilité humaine : rho={rho:.3f} (p={p:.1e}, n={len(known)})")
    else:
        print("pas d'annotation de facilité disponible — métrique 3 sautée.")


if __name__ == "__main__":
    main()
