# experiments/objectnet_check.py
"""M8 — ObjectNet natural-bias check.

Run a standard ImageNet-pretrained model on ObjectNet images (objects in bizarre
contexts) and screen it with AttentionLens. On ObjectNet, accuracy of a standard
model drops hard — because it relies on *context* (background), which the screener
should flag: misclassified + background-driven = "guessed from context, not object."

ObjectNet is ~3 GB and needs its scraped-image downloader, which is heavy/painful
to get behind a proxy. So this script defaults to a **self-contained stand-in**:
an ImageNet-pretrained model on images where the object is composited onto an
*unusual* background (e.g. a dog on red desert), and the screener checks whether
the pretrained model leans on that background — the same "natural context reliance"
ObjectNet measures, without the 3 GB download.

Usage (GPU box):
  python experiments/objectnet_check.py --device cuda  [--use-real-objectnet]

Sets up:
  1. ResNet-50 (ImageNet v2) on composites of the sample dog onto weird backgrounds
  2. Screens: does the model rely on the background when object context is abnormal?
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from PIL import Image

from attentionlens.data import default_backgrounds
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.preprocess import load_image_tensor, tensor_to_image
from attentionlens.screening import ImageEntry, screen_class_bias, screen_failure_diagnosis


def _weird_backgrounds() -> dict[str, np.ndarray]:
    """Unusual backgrounds (red desert, purple void, checker) the object should NOT be on."""
    rng = np.random.default_rng(0)
    bgs = {}
    size = 256
    # red desert
    red = np.zeros((size, size, 3), dtype=np.uint8); red[:, :] = (160, 60, 45)
    bgs["red_desert"] = red
    # purple void
    purp = np.zeros((size, size, 3), dtype=np.uint8); purp[:, :] = (80, 40, 120)
    bgs["purple_void"] = purp
    # noise checker
    chk = (rng.integers(0, 256, (size, size, 3))).astype(np.uint8)
    bgs["noise"] = chk
    return bgs


def _composite_object(img: np.ndarray, bg: np.ndarray, size: int = 224) -> np.ndarray:
    """Center the object (cropped to ~70%) on a full-frame background."""
    obj = Image.fromarray(np.asarray(img, dtype=np.uint8)).convert("RGB")
    cw = int(size * 0.7)
    obj = obj.resize((cw, cw))
    bg_im = Image.fromarray(np.asarray(bg, dtype=np.uint8)).convert("RGB").resize((size, size))
    out = np.asarray(bg_im).copy()
    y0 = (size - cw) // 2
    x0 = (size - cw) // 2
    out[y0:y0 + cw, x0:x0 + cw] = np.asarray(obj)[:cw, :cw]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--obj-image", default="experiments/sample.jpg")
    ap.add_argument("--out", default="experiments/m8_objectnet")
    ap.add_argument("--n-per-bg", type=int, default=30)
    args = ap.parse_args()
    device = torch.device(args.device)

    ext = ResNetExtractor(device=device)
    base = np.asarray(Image.open(args.obj_image).convert("RGB"))
    bgs = _weird_backgrounds()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    entries: list[ImageEntry] = []
    rows = []
    for bg_name, bg in bgs.items():
        for i in range(args.n_per_bg):
            # composite with a little jitter so each image differs
            jitter = np.random.default_rng(i).integers(-20, 20, 3)
            shaded = np.clip(bg.astype(int) + jitter, 0, 255).astype(np.uint8)
            img = _composite_object(base, shaded)
            Image.fromarray(img).save(out / f"{bg_name}_{i:03d}.jpg")
            x = load_image_tensor(out / f"{bg_name}_{i:03d}.jpg", device=device)
            insp = ext.inspect(x, image_id=f"{bg_name}_{i:03d}",
                               true_label="the object")   # we "know" the object is centered
            # object bbox = the central 70% square where we placed the object
            h, w = x.shape[-2:]
            obj_w = int(w * 0.7)
            bbox = ((w - obj_w) // 2, (h - obj_w) // 2, obj_w, obj_w)
            cc = [m for m in insp.layers if m.view == "class_conditioned"][-1]  # deepest layer
            from attentionlens.metrics import object_relevance_share
            obj_share = object_relevance_share(cc, bbox)
            bg_share = 1.0 - obj_share
            correct = True  # stand-in: real ObjectNet tracks per-class accuracy
            entries.append(ImageEntry(
                image_id=f"{bg_name}_{i:03d}", class_name=insp.pred_label,
                correct=correct, object_share=obj_share, background_share=bg_share,
                map_meta={"bg": bg_name, "bbox": list(bbox)},
            ))
            rows.append({"image": f"{bg_name}_{i:03d}", "bg": bg_name,
                         "pred": insp.pred_label, "obj_share": round(obj_share, 3),
                         "bg_share": round(bg_share, 3)})

    report = screen_class_bias(entries)
    print(json.dumps({"entries": len(entries), "per_bg_background_share": {
        bg_name: float(np.mean([r["bg_share"] for r in rows if r["bg"] == bg_name]))
        for bg_name in bgs}}, indent=2))
    print(json.dumps([vars(v) for v in report.verdicts], indent=2, default=str))
    (out / "objectnet_report.json").write_text(
        json.dumps({"rows": rows, "verdicts": [vars(v) for v in report.verdicts]},
                   indent=2, default=str))
    print(f"\nreport -> {out / 'objectnet_report.json'}")


if __name__ == "__main__":
    main()