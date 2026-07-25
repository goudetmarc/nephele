#!/usr/bin/env python3
"""
Phase 2 — DPO LoRA de Qwen2.5-VL : apprendre la préférence de Marc.

Une paire naît quand une même planche porte une lecture ratifiée (« je la
vois ») ET une rejetée (« je ne la vois pas »). Le clic humain EST la fonction
de récompense. On part de préférence de l'adaptateur SFT de la Phase 1.

Données : nephele-dpo.jsonl (via prepare_data.py → dpo_train.jsonl), format
    {image:{mime,b64}, system, user, chosen, rejected}
où chosen/rejected sont des chaînes JSON (la figure enseignée).

Exemple :
    accelerate launch dpo_qwen_vl.py \
        --data data/dpo_train.jsonl --sft out/nephele-sft-lora \
        --out out/nephele-dpo-lora
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

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"


def to_pil(image):
    return Image.open(io.BytesIO(base64.b64decode(image["b64"]))).convert("RGB")


def charge_dataset(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            # Format attendu par DPOTrainer (VLM) : prompt en messages + images.
            rows.append({
                "images": [to_pil(r["image"])],
                "prompt": [
                    {"role": "system", "content": [{"type": "text", "text": r["system"]}]},
                    {"role": "user", "content": [
                        {"type": "image"},
                        {"type": "text", "text": r["user"]},
                    ]},
                ],
                "chosen": [{"role": "assistant", "content": [{"type": "text", "text": r["chosen"]}]}],
                "rejected": [{"role": "assistant", "content": [{"type": "text", "text": r["rejected"]}]}],
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
    a = ap.parse_args()

    ds = charge_dataset(a.data)
    print(f"{len(ds)} paires de préférence")

    processor = AutoProcessor.from_pretrained(
        a.model, min_pixels=256 * 28 * 28, max_pixels=1024 * 28 * 28
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        a.model, torch_dtype=torch.bfloat16, device_map="auto"
    )
    if a.sft:
        # Poursuit la préférence par-dessus l'adaptateur SFT.
        model.load_adapter(a.sft)

    peft_config = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )

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
        bf16=True,
        gradient_checkpointing=True,
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
