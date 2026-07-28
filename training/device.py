"""
Sélection du backend matériel — partagée par les scripts SFT et DPO.

Cible principale : Apple Silicon (MacBook Pro M-series, 64 Go de RAM unifiée),
backend Metal Performance Shaders (« mps »). Le même code retombe sur CUDA (GPU
loué dans le cloud) puis sur CPU, sans rien changer d'autre.

Choix de dtype par backend :
  - mps  → float16   (bf16 n'est encore que partiellement supporté sur Metal)
  - cuda → bfloat16  (natif, plage dynamique confortable)
  - cpu  → float32   (repli lent mais correct)

On N'UTILISE PAS bitsandbytes / quantification 4-bit : incompatible nativement
avec MPS. Avec 64 Go de mémoire unifiée, un 7B se charge en 16 bits sans peine.
"""
import os


def pick_device(prefer_mps=True):
    """Renvoie (torch.device, torch.dtype). Active le repli CPU des ops que
    Metal ne sait pas exécuter, pour ne pas planter en cours d'entraînement."""
    import torch

    mps = getattr(torch.backends, "mps", None)
    if prefer_mps and mps is not None and torch.backends.mps.is_available():
        # Les ops non implémentées côté Metal basculent sur CPU au lieu de lever.
        os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
        return torch.device("mps"), torch.float16
    if torch.cuda.is_available():
        return torch.device("cuda"), torch.bfloat16
    return torch.device("cpu"), torch.float32


def describe(device, dtype):
    return f"backend={device.type} dtype={str(dtype).replace('torch.', '')}"
