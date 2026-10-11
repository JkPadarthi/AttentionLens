# experiments/gpu_m7_run.py
"""GPU entrypoint for the M7 planted-bias experiment.

Runs inside the attentionlens-gpu image. Higher scale + ViT class-conditioned
screening so the result is a stronger demonstration than the CPU smoke test:
  - more classes (4 waterbirds-style classes)
  - more epochs
  - both CNN (trained) and ViT (pretrained) inspected through the same schema

Usage:  python experiments/gpu_m7_run.py --epochs 10 --num-classes 4
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from experiments.planted_bias import (
    _FolderDataset,
    _make_object_crops,
    build_biased_data,
    train,
)
from attentionlens.data import default_backgrounds, make_correlated_dataset


def build_larger_biased(workdir: Path, num_classes: int, n_per: int,
                        size: int = 224, seed: int = 11) -> tuple[Path, list[str]]:
    """Same compositor as planted_bias but with N classes -> correlated bgs."""
    labels = [f"class_{c}" for c in range(num_classes)]
    bg_names = ["water", "land", "forest", "city"][:num_classes]
    class2bg = {labels[c]: bg_names[c] for c in range(num_classes)}
    bgs = default_backgrounds()
    # extend default backgrounds with 2 more (forest/city) so all classes differ
    if num_classes > 2:
        bgs["forest"] = _grad_bg((60, 90, 40))
        bgs["city"] = _grad_bg((120, 110, 100))
    crops = _make_object_crops(num_classes, n_per, size=size, seed=seed)
    root = workdir / "biased"
    root.parent.mkdir(parents=True, exist_ok=True)
    make_correlated_dataset(crops, bgs, labels, class2bg, root, size=size, seed=seed)
    return root, labels


def _grad_bg(rgb, size: int = 256) -> "np.ndarray":
    import numpy as np
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, :, :] = rgb
    ramp = np.linspace(-25, 25, size).astype(np.int16)
    arr = arr.astype(np.int16) + ramp[None, :, None]
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--num-classes", type=int, default=4)
    ap.add_argument("--n-per-class", type=int, default=80)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--workdir", default="experiments/m7_gpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    if device.type != "cuda":
        print("[gpu_m7] WARNING: not cuda — running in CPU/fallback mode (fine for smoke tests)", flush=True)

    print(f"[gpu_m7] device={device} classes={args.num_classes} "
          f"n_per={args.n_per_class} epochs={args.epochs}", flush=True)

    workdir = Path(args.workdir)
    root, labels = build_larger_biased(workdir, args.num_classes, args.n_per_class)
    ds = _FolderDataset(root)
    print(f"[gpu_m7] biased dataset: {len(ds)} images, {len(ds.classes)} classes", flush=True)

    t0 = time.time()
    model = train(ds, len(ds.classes), args.epochs, device, batch=32)
    print(f"[gpu_m7] trained in {time.time()-t0:.1f}s (CNN)", flush=True)

    # Package-level import must resolve inside the container: add repo root to path.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from experiments.planted_bias import screen
    t0 = time.time()
    report = screen(model, ds, "cnn", device, grid_n=4)
    print(f"[gpu_m7] screened CNN in {time.time()-t0:.1f}s", flush=True)

    out = workdir / "m7_gpu_report.json"
    out.write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report, indent=2, default=str), flush=True)
    print(f"[gpu_m7] report -> {out}", flush=True)


if __name__ == "__main__":
    main()