#!/usr/bin/env python3
"""
Prépare les exports Nephélé pour l'entraînement.

Deux disciplines du projet, appliquées ici :
  1. On n'entraîne que sur du ratifié — c'est déjà le cas des exports (le SFT
     n'emporte que les planches propres, le DPO que les paires je-la-vois /
     je-ne-la-vois-pas). Ce script ne fait que valider et découper.
  2. Le banc arbitre sur des images JAMAIS vues à l'entraînement. On découpe
     donc un jeu « held-out » PAR IMAGE : aucune image d'évaluation n'apparaît
     dans le train, même sous une autre planche. C'est le point qui compte le
     plus — une fuite d'image invalide toute mesure du banc.

Usage :
    python prepare_data.py --sft nephele-sft.jsonl --out data/ --heldout 0.15
    python prepare_data.py --dpo nephele-dpo.jsonl --out data/ --heldout 0.15
"""
import argparse
import hashlib
import json
import os


def charge(path):
    lignes = []
    with open(path, encoding="utf-8") as f:
        for n, ln in enumerate(f, 1):
            ln = ln.strip()
            if not ln:
                continue
            try:
                lignes.append(json.loads(ln))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{n} : JSON illisible ({e})")
    return lignes


def cle_image(row):
    """Identité d'une image, indépendante de la planche : on hache le b64."""
    b64 = (row.get("image") or {}).get("b64", "")
    return hashlib.sha1(b64.encode("utf-8")).hexdigest()


def decoupe_par_image(rows, frac_heldout, graine=0):
    """Held-out déterministe par image (pas de fuite d'image entre train/eval)."""
    par_img = {}
    for r in rows:
        par_img.setdefault(cle_image(r), []).append(r)
    # Ordre déterministe : on trie les images par leur hachage combiné à la graine.
    images = sorted(par_img, key=lambda h: hashlib.sha1(f"{graine}:{h}".encode()).hexdigest())
    n_eval = max(1, round(len(images) * frac_heldout)) if images else 0
    eval_imgs = set(images[:n_eval])
    train, heldout = [], []
    for h, rs in par_img.items():
        (heldout if h in eval_imgs else train).extend(rs)
    return train, heldout, len(images), n_eval


def ecris(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def valide_sft(rows):
    for r in rows:
        assert r.get("system") and r.get("user"), "system/user manquant"
        assert (r.get("image") or {}).get("b64"), "image manquante"
        assert r.get("assistant"), "cible (assistant) manquante"


def valide_dpo(rows):
    for r in rows:
        assert (r.get("image") or {}).get("b64"), "image manquante"
        assert r.get("chosen") and r.get("rejected"), "chosen/rejected manquant"
        assert r["chosen"] != r["rejected"], "chosen == rejected (paire vide)"


def to_dpo_hf(r):
    """Transforme un enregistrement d'export vers le format HF standard DPO.

    Format conversationnel attendu par TRL : les clés `prompt`, `chosen`,
    `rejected` sont des LISTES DE MESSAGES. On conserve en plus `image` (b64) :
    ce n'est pas superflu, c'est OBLIGATOIRE pour un DPO de modèle vision —
    l'entraînement décode cette image en PIL. La retirer casserait le VLM DPO.
    """
    return {
        "prompt": [
            {"role": "system", "content": [{"type": "text", "text": r["system"]}]},
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": r["user"]},
            ]},
        ],
        "chosen": [
            {"role": "assistant", "content": [{"type": "text", "text": r["chosen"]}]},
        ],
        "rejected": [
            {"role": "assistant", "content": [{"type": "text", "text": r["rejected"]}]},
        ],
        "image": r["image"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft")
    ap.add_argument("--dpo")
    ap.add_argument("--out", default="data")
    ap.add_argument("--heldout", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if not a.sft and not a.dpo:
        raise SystemExit("donne --sft et/ou --dpo")

    for kind, path, valide in (("sft", a.sft, valide_sft), ("dpo", a.dpo, valide_dpo)):
        if not path:
            continue
        rows = charge(path)
        valide(rows)
        # Le DPO sort au format HF standard (prompt/chosen/rejected + image).
        if kind == "dpo":
            rows = [to_dpo_hf(r) for r in rows]
        train, heldout, n_img, n_eval = decoupe_par_image(rows, a.heldout, a.seed)
        ecris(os.path.join(a.out, f"{kind}_train.jsonl"), train)
        ecris(os.path.join(a.out, f"{kind}_heldout.jsonl"), heldout)
        print(
            f"[{kind}] {len(rows)} exemples sur {n_img} images → "
            f"train {len(train)} / held-out {len(heldout)} "
            f"({n_eval} images réservées, jamais vues à l'entraînement)"
        )


if __name__ == "__main__":
    main()
