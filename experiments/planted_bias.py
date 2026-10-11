# experiments/planted_bias.py
"""M7 — Planted-bias experiment (Waterbirds-style).

1. Composite object crops onto correlated backgrounds (the planted shortcut).
2. Fine-tune a ViT (or ResNet) on the biased set.
3. Screen the biased model with AttentionLens.
4. PASS = the screener flags the exact planted correlation (background sensitivity
   ≫ object sensitivity on the correlated classes).

Run on GPU:  python experiments/planted_bias.py --arch vit --epochs 2 --device cuda
Designed device-agnostic so it also demos on CPU with tiny settings.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from attentionlens.data import default_backgrounds, make_correlated_dataset
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor
from attentionlens.intervention import run_intervention, split_regular_grid
from attentionlens.schema import ModelInspection


class _FolderDataset(Dataset):
    """Minimal ImageFolder (class subdirs) without torchvision."""
    def __init__(self, root: Path, size: int = 224):
        from PIL import Image
        from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD

        self.imgs: list[tuple[str, int]] = []
        self.classes: list[str] = []
        for cls_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            idx = len(self.classes)
            self.classes.append(cls_dir.name)
            for f in sorted(cls_dir.glob("*.jpg"))[:2000]:
                self.imgs.append((str(f), idx))
        self.size = size
        self.mean = np.array(IMAGENET_MEAN, dtype=np.float32)
        self.std = np.array(IMAGENET_STD, dtype=np.float32)

    def __len__(self) -> int:
        return len(self.imgs)

    def __getitem__(self, i):
        from PIL import Image

        path, label = self.imgs[i]
        img = Image.open(path).convert("RGB").resize((self.size, self.size))
        a = np.asarray(img, dtype=np.float32) / 255.0
        a = (a - self.mean) / self.std
        return torch.from_numpy(a).permute(2, 0, 1), label


class _Classifier(torch.nn.Module):
    """Small trainable CNN for the experiment (a real ViT/ResNet head could be used).

    Enough to learn the planted shortcut on small synthetic data; kept fast so the
    whole loop runs on the GPU box in minutes rather than hours.
    """
    def __init__(self, num_classes: int = 2, input_size: int = 224):
        super().__init__()
        self.features = torch.nn.Sequential(
            torch.nn.Conv2d(3, 16, 3, padding=1), torch.nn.ReLU(), torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(16, 32, 3, padding=1), torch.nn.ReLU(), torch.nn.MaxPool2d(2),
            torch.nn.Flatten(),
        )
        # after two 2x pools: spatial = input_size // 4
        flat_dim = 32 * (input_size // 4) ** 2
        self.fc = torch.nn.Linear(flat_dim, num_classes)

    def forward(self, x):
        return self.fc(self.features(x))


def _make_classifier(num_classes: int, input_size: int = 224) -> _Classifier:
    return _Classifier(num_classes, input_size=input_size)


def _make_object_crops(num_classes: int, n_per: int, size: int = 224, seed: int = 7) -> list[np.ndarray]:
    """Synthetic 'object crops' — colored blobs that differ per class (a stand-in for
    CUB-200 bird crops). A real run replaces this with actual CUB-200 crops."""
    rng = np.random.default_rng(seed)
    crops: list[np.ndarray] = []
    colors = [(180, 60, 60), (60, 90, 190)]  # distinguishable per class
    for c in range(num_classes):
        for _ in range(n_per):
            im = np.zeros((size, size, 3), dtype=np.uint8)
            im[:, :] = (240, 240, 235)  # light background so the blob is the "object"
            cx, cy = rng.integers(size // 3, 2 * size // 3, 2)
            r = rng.integers(size // 8, size // 4)
            y, x = np.ogrid[:size, :size]
            mask = (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2
            im[mask] = colors[c]
            crops.append(im)
    return crops


def build_biased_data(workdir: Path, num_classes: int = 2, n_per: int = 60,
                      size: int = 224, seed: int = 11) -> tuple[Path, list[str], dict[str, str]]:
    """Create the biased training set with a known class↔background correlation."""
    labels = [f"class_{c}" for c in range(num_classes)]
    class2bg = {f"class_{c}": ("water" if c == 0 else "land") for c in range(num_classes)}
    bgs = default_backgrounds()
    crops = _make_object_crops(num_classes, n_per, size=size, seed=seed)
    root = workdir / "biased"
    root.parent.mkdir(parents=True, exist_ok=True)
    make_correlated_dataset(crops, bgs, labels, class2bg, root, size=size, seed=seed)
    return root, labels, class2bg


def train(dataset: _FolderDataset, num_classes: int, epochs: int,
          device: torch.device, lr: float = 1e-3, batch: int = 16) -> _Classifier:
    """Train the small classifier on the biased set — learns the planted shortcut."""
    model = _make_classifier(num_classes, input_size=224).to(device)
    loader = DataLoader(dataset, batch_size=batch, shuffle=True, drop_last=True)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.CrossEntropyLoss()
    model.train()
    for ep in range(epochs):
        total, correct = 0, 0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            out = model(xb)
            loss = loss_fn(out, yb)
            loss.backward()
            opt.step()
            correct += (out.argmax(1) == yb).sum().item()
            total += yb.size(0)
        print(f"[train] epoch {ep + 1}/{epochs}: acc {correct / max(total, 1):.3f} loss {loss.item():.3f}")
    return model


def screen(model: torch.nn.Module, dataset: _FolderDataset, arch: str | None,
           device: torch.device, bbox_frac: float = 0.4, grid_n: int = 4) -> dict:
    """Run AttentionLens screening over the dataset and report bias verdicts.

    Uses the class-conditioned map for each image + occlusion interventions on a
    grid. Returns aggregated stats. This is the *real* check: does the instrument
    catch the correlation we planted?
    """
    from attentionlens.metrics import all_metrics
    from attentionlens.screening import ImageEntry, screen_class_bias

    # For the synthetic dataset, "bbox" approx = the central object square.
    entries: list[ImageEntry] = []
    intervent: list[float] = []
    for i in range(min(len(dataset), 200)):
        xb, yb = dataset[i]
        xb = xb.unsqueeze(0).to(device)
        h, w = xb.shape[-2:]
        with torch.no_grad():
            logits = model(xb)
        pred = int(logits[0].argmax().item())
        correct = pred == yb
        cx0, cy0 = int(w * 0.25), int(h * 0.25)
        bbox = (cx0, cy0, int(w * 0.5), int(h * 0.5))
        # class-conditioned map via the extractor (device-agnostic)
        from attentionlens.extractors.cnn import gradcam_maps
        maps = gradcam_maps(model, ["features.0"], xb, target_class=int(yb),
                            target_size=(h, w), device=device,
                            class_names={i: f"class_{i}"})
        obj = maps[0].map[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]].sum()
        total = maps[0].map.sum() + 1e-9
        obj_share = float(obj / total)
        entries.append(ImageEntry(
            image_id=f"{i}", class_name=f"class_{int(yb)}", correct=correct,
            object_share=obj_share, background_share=1.0 - obj_share,
            map_meta={"bbox": list(bbox)},
        ))
        # intervention on a 2x2 grid
        for reg in split_regular_grid(h, w, 2):
            try:
                from attentionlens.intervention import run_intervention
                res = run_intervention(model, xb, [reg], target_class=int(yb),
                                       strategy="zero", device=device)
                intervent.append(res[0].logit_delta)
            except Exception:
                continue

    report = screen_class_bias(entries)
    return {
        "n_images": len(entries),
        "accuracy": float(np.mean([1.0 if e.correct else 0.0 for e in entries])),
        "verdicts": [vars(v) for v in report.verdicts],
        "class_stats": report.class_stats,
        "mean_intervention_effort": float(np.mean(intervent)) if intervent else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="cnn", choices=["cnn", "vit"])
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--n-per-class", type=int, default=60)
    ap.add_argument("--num-classes", type=int, default=2)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--workdir", default="experiments/m7")
    args = ap.parse_args()
    device = torch.device(args.device)
    print(f"[m7] device={device} arch={args.arch} epochs={args.epochs}")

    workdir = Path(args.workdir)
    root, labels, class2bg = build_biased_data(workdir, args.num_classes,
                                               args.n_per_class, seed=11)
    print(f"[m7] built biased dataset at {root}")
    ds = _FolderDataset(root)
    print(f"[m7] dataset: {len(ds)} images, classes {ds.classes}")
    model = train(ds, len(ds.classes), args.epochs, device)
    print("[m7] training done — screening...")

    result = screen(model, ds, args.arch, device)
    import json
    out = workdir / "m7_report.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))
    print(f"[m7] report -> {out}")


if __name__ == "__main__":
    main()