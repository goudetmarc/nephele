"""
Le primer non verbal — distillation silhouette -> embedding (recette A).

Idée (famille JEPA, champ ZS-SBIR) : apprendre à un encodeur d'images à placer
NOS silhouettes Otsu là où l'encodeur gelé place l'image originale. Le primer
qui en sort lit une planche « comme si » il voyait la matière — sans un mot,
sans un cartel, donc incontaminable par le corpus. C'est la strate innée,
distillée (voir RECHERCHE.md, « The map of the gaze »).

  étudiant = tour vision SigLIP + LoRA   (seuls les adaptateurs apprennent)
  maître   = le même modèle, gelé        (embedding de l'image originale)
  perte    = 1 - cos(étudiant(silhouette), maître(original))
             + InfoNCE en lot (option), pour garder les paires discriminantes

Aucune donnée ratifiée requise : la supervision est l'image elle-même.
Prototype sur Apple Silicon (MPS), vrai run sur GPU CUDA — même code,
sélection par ../device.py, comme les scripts SFT/DPO.

Usage :
  python distill_siglip.py --data data/primer --out runs/primer-lora \
      --model google/siglip-base-patch16-224 --epochs 1 --batch 32
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # ../device.py
from device import describe, pick_device  # noqa: E402


def load_manifest(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="dossier produit par build_dataset.py")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="google/siglip-base-patch16-224")
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--infonce", type=float, default=0.5, help="poids InfoNCE (0 = cosinus seul)")
    ap.add_argument("--temp", type=float, default=0.07, help="température InfoNCE")
    ap.add_argument("--log-every", type=int, default=20)
    args = ap.parse_args()

    import torch
    import torch.nn.functional as F
    from PIL import Image
    from peft import LoraConfig, get_peft_model
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoProcessor, SiglipVisionModel

    device, dtype = pick_device()
    print(describe(device, dtype))

    processor = AutoProcessor.from_pretrained(args.model)

    # maître : gelé ; étudiant : le même, décoré de LoRA sur l'attention
    teacher = SiglipVisionModel.from_pretrained(args.model, torch_dtype=dtype).to(device).eval()
    for p in teacher.parameters():
        p.requires_grad_(False)
    student = SiglipVisionModel.from_pretrained(args.model, torch_dtype=dtype).to(device)
    lora = LoraConfig(r=args.lora_r, lora_alpha=args.lora_r * 2, lora_dropout=0.05,
                      target_modules=["q_proj", "k_proj", "v_proj", "out_proj"])
    student = get_peft_model(student, lora)
    student.print_trainable_parameters()

    class Pairs(Dataset):
        def __init__(self, rows):
            self.rows = rows

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, i):
            r = self.rows[i]
            sil = Image.open(r["sil"]).convert("RGB")   # la tour vision attend 3 canaux
            orig = Image.open(r["orig"]).convert("RGB")
            return sil, orig

    def collate(batch):
        sils, origs = zip(*batch)
        ps = processor(images=list(sils), return_tensors="pt")["pixel_values"]
        po = processor(images=list(origs), return_tensors="pt")["pixel_values"]
        return ps, po

    def embed(model, px):
        # pooler_output = embedding global de la tour vision SigLIP
        out = model(pixel_values=px.to(device=device, dtype=dtype))
        return F.normalize(out.pooler_output.float(), dim=-1)

    def losses(zs, zo):
        cos = (1 - (zs * zo).sum(-1)).mean()
        if args.infonce <= 0:
            return cos, cos, torch.tensor(0.0)
        logits = zs @ zo.t() / args.temp
        labels = torch.arange(len(zs), device=zs.device)
        nce = 0.5 * (F.cross_entropy(logits, labels) + F.cross_entropy(logits.t(), labels))
        return cos + args.infonce * nce, cos, nce

    data = Path(args.data)
    train = DataLoader(Pairs(load_manifest(data / "manifest_train.jsonl")), batch_size=args.batch,
                       shuffle=True, collate_fn=collate, num_workers=2, drop_last=True)
    val_rows = load_manifest(data / "manifest_val.jsonl")
    val = DataLoader(Pairs(val_rows), batch_size=args.batch, collate_fn=collate) if val_rows else None

    opt = torch.optim.AdamW([p for p in student.parameters() if p.requires_grad], lr=args.lr)

    @torch.no_grad()
    def validate():
        """cos moyen + retrieval@1 silhouette -> original dans le lot de val."""
        if val is None:
            return float("nan"), float("nan")
        student.eval()
        cs, hit, n = [], 0, 0
        for ps, po in val:
            zs, zo = embed(student, ps), embed(teacher, po)
            cs.append((zs * zo).sum(-1).mean().item())
            hit += (zs @ zo.t()).argmax(-1).eq(torch.arange(len(zs), device=zs.device)).sum().item()
            n += len(zs)
        student.train()
        return sum(cs) / len(cs), hit / max(1, n)

    step = 0
    for ep in range(args.epochs):
        for ps, po in train:
            with torch.no_grad():
                zo = embed(teacher, po)
            zs = embed(student, ps)
            loss, cos, nce = losses(zs, zo)
            opt.zero_grad()
            loss.backward()
            opt.step()
            step += 1
            if step % args.log_every == 0:
                print(f"ep{ep} step{step}  loss={loss.item():.4f}  cos={cos.item():.4f}  nce={float(nce):.4f}")
        vc, r1 = validate()
        print(f"== fin époque {ep} : val cos={vc:.4f}  retrieval@1={r1:.3f} ==")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    student.save_pretrained(out)         # adaptateurs LoRA seuls — léger, versionnable
    processor.save_pretrained(out)
    print(f"ok — adaptateurs LoRA écrits dans {out}")


if __name__ == "__main__":
    main()
