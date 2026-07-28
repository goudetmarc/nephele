#!/usr/bin/env python3
"""
Phase 2 — DPO LoRA de Qwen2.5-VL : apprendre la préférence de Marc.

Une paire naît quand une même planche porte une lecture ratifiée (« je la
vois ») ET une rejetée (« je ne la vois pas »). Le clic humain EST la fonction
de récompense. On part de préférence de l'adaptateur SFT de la Phase 1.

Matériel : optimisé Apple Silicon (MPS) — voir device.py — avec repli CUDA/CPU.
PAS de bitsandbytes (incompatible MPS) : chargement 16 bits natif.

Données : sortie de prepare_data.py (format HF standard DPO) →
    {prompt:[...messages...], chosen:[...], rejected:[...], image:{mime,b64}}
`prompt`/`chosen`/`rejected` sont des listes de messages ; `image` est décodée
en PIL ici (obligatoire pour le DPO vision).

Exemple :
    python dpo_qwen_vl.py --data data/dpo_train.jsonl \
        --sft out/nephele-sft-lora --out out/nephele-dpo-lora
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
from trl import DPOConfig, DPOTrainer

from device import describe, pick_device

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"


def to_pil(image):
    return Image.open(io.BytesIO(base64.b64decode(image["b64"]))).convert("RGB")


def charge_dataset(path):
    """Lit le format HF standard produit par prepare_data.py et décode l'image."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            rows.append({
                "images": [to_pil(r["image"])],
                "prompt": r["prompt"],
                "chosen": r["chosen"],
                "rejected": r["rejected"],
            })
    return Dataset.from_list(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--sft", default=None, help="adaptateur LoRA de la Phase 1 à poursuivre")
    ap.add_argument("--out", default="out/nephele-dpo-lora")
    ap.add_argument("--model", default=MODEL_ID)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=5e-6)
    ap.add_argument("--beta", type=float, default=0.1)
    ap.add_argument("--cpu", action="store_true", help="force le CPU (debug)")
    a = ap.parse_args()

    device, dtype = pick_device(prefer_mps=not a.cpu)
    print(f"{describe(device, dtype)}")

    ds = charge_dataset(a.data)
    print(f"{len(ds)} paires de préférence")

    processor = AutoProcessor.from_pretrained(
        a.model, min_pixels=256 * 28 * 28, max_pixels=1024 * 28 * 28
    )

    # Chargement 16 bits natif, placement explicite sur le backend (pas de
    # device_map, qui est un mécanisme CUDA de sharding).
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(a.model, torch_dtype=dtype)
    model.to(device)
    if a.sft:
        # Poursuit la préférence par-dessus l'adaptateur SFT de la Phase 1.
        model.load_adapter(a.sft)

    peft_config = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    on_cuda = device.type == "cuda"
    cfg = DPOConfig(
        output_dir=a.out,
        num_train_epochs=a.epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=a.lr,
        beta=a.beta,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        save_strategy="epoch",
        bf16=on_cuda,
        fp16=False,
        gradient_checkpointing=on_cuda,
        use_cpu=device.type == "cpu",
        report_to="none",
    )

    trainer = DPOTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        processing_class=processor,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(a.out)
    processor.save_pretrained(a.out)
    print(f"Adaptateur DPO écrit dans {a.out}")


if __name__ == "__main__":
    main()
