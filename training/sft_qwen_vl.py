#!/usr/bin/env python3
"""
Phase 1 — SFT LoRA de Qwen2.5-VL sur le corpus ratifié de Nephélé.

Objectif (cf. CLAUDE.md) : apprendre le FORMAT, le réflexe d'ancrage et le refus
du jargon — pas le contenu. Le fine-tuning consolide la grammaire (mémoire
lente), il ne la remplace pas. On n'entraîne que sur du ratifié : l'export SFT
ne contient déjà que des planches propres (≥1 lecture « je la vois », aucune
« je ne la vois pas »), la cible étant la version corrigée par le second regard.

Matériel : optimisé Apple Silicon (MPS) — voir device.py — avec repli CUDA/CPU.
PAS de bitsandbytes : incompatible MPS. Le modèle se charge en 16 bits natif
(64 Go de RAM unifiée suffisent largement pour un 7B en LoRA).

Données : nephele-sft.jsonl (via prepare_data.py → sft_train.jsonl), format
    {image:{mime,b64}, system, user, assistant}
où `assistant` est une chaîne JSON {"figures":[...]}.

Exemple :
    python sft_qwen_vl.py --data data/sft_train.jsonl --out out/nephele-sft-lora --epochs 2
"""
import argparse
import base64
import io
import json

import torch
from datasets import Dataset
from peft import LoraConfig
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from trl import SFTConfig, SFTTrainer

from device import describe, pick_device

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"


def to_pil(image):
    return Image.open(io.BytesIO(base64.b64decode(image["b64"]))).convert("RGB")


def charge_dataset(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return Dataset.from_list(rows)


def messages_de(row):
    """Conversation au format chat, image comprise."""
    return [
        {"role": "system", "content": [{"type": "text", "text": row["system"]}]},
        {"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": row["user"]},
        ]},
        {"role": "assistant", "content": [{"type": "text", "text": row["assistant"]}]},
    ]


def build_collate(processor):
    # Masque les tokens image dans les labels : on n'entraîne la perte que sur
    # le texte produit, jamais sur les patches d'image.
    img_tok = processor.tokenizer.convert_tokens_to_ids("<|image_pad|>")

    def collate(batch):
        texts = [processor.apply_chat_template(messages_de(r), tokenize=False) for r in batch]
        images = [[to_pil(r["image"])] for r in batch]
        enc = processor(text=texts, images=images, return_tensors="pt", padding=True)
        labels = enc["input_ids"].clone()
        labels[labels == processor.tokenizer.pad_token_id] = -100
        if img_tok is not None and img_tok >= 0:
            labels[labels == img_tok] = -100
        enc["labels"] = labels
        return enc

    return collate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="out/nephele-sft-lora")
    ap.add_argument("--model", default=MODEL_ID)
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--cpu", action="store_true", help="force le CPU (debug)")
    a = ap.parse_args()

    device, dtype = pick_device(prefer_mps=not a.cpu)
    print(f"{describe(device, dtype)}")

    ds = charge_dataset(a.data)
    print(f"{len(ds)} exemples d'entraînement")

    # min/max_pixels borne la taille des images (mémoire et vitesse). Les planches
    # de Nephélé sont petites ; on reste modeste.
    processor = AutoProcessor.from_pretrained(
        a.model, min_pixels=256 * 28 * 28, max_pixels=1024 * 28 * 28
    )

    # Chargement 16 bits natif, SANS device_map (concept CUDA multi-GPU) : on
    # place explicitement le modèle sur le backend choisi (mps/cuda/cpu).
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(a.model, torch_dtype=dtype)
    model.to(device)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        # Modules d'attention du décodeur ; la tour visuelle reste gelée.
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    on_cuda = device.type == "cuda"
    cfg = SFTConfig(
        output_dir=a.out,
        num_train_epochs=a.epochs,
        per_device_train_batch_size=a.batch,
        gradient_accumulation_steps=a.accum,
        learning_rate=a.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        save_strategy="epoch",
        # 16 bits piloté par nous (dtype) ; on laisse Trainer en fp32 master.
        bf16=on_cuda,
        fp16=False,
        # gradient checkpointing : utile sur CUDA, capricieux sur MPS → CUDA seul.
        gradient_checkpointing=on_cuda,
        use_cpu=device.type == "cpu",
        report_to="none",
        remove_unused_columns=False,          # on garde image/system/user pour le collate
        dataset_kwargs={"skip_prepare_dataset": True},
    )

    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        data_collator=build_collate(processor),
        peft_config=peft_config,
        processing_class=processor.tokenizer,
    )
    trainer.train()
    trainer.save_model(a.out)
    processor.save_pretrained(a.out)
    print(f"Adaptateur LoRA écrit dans {a.out}")


if __name__ == "__main__":
    main()
