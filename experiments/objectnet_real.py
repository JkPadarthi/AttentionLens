# experiments/objectnet_real.py
"""Real M8 — ObjectNet natural-bias check on the actual `timm/objectnet-in1k` dataset.

Runs a standard ImageNet-pretrained ResNet-50 on the 113 ImageNet-overlapping
ObjectNet classes and screens it with AttentionLens. The M8 claim: on ObjectNet,
a standard model's accuracy collapses (~40% drop) *because* it relies on context
(spurious background) instead of the object — and the screener should surface that.

Method:
  - Load the parquet shards (image bytes + ImageNet-1k label index).
  - Strip the required 2px red license border before inference.
  - Per image: predict, extract class-conditioned maps (Grad-CAM), and compute
    object vs background relevance. ObjectNet has no bbox annotations, so we use
    the causal intervention loop (occlude a central grid) as the sensitivity signal
    instead of a bbox proxy.
  - Aggregate -> class-level bias flags + failure-diagnosis verdicts.

Usage (GPU box):
  python experiments/objectnet_real.py --device cuda --n-classes 20 --per-class 20
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch

from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.intervention import run_intervention, split_regular_grid
from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD
from attentionlens.screening import ImageEntry, screen_class_bias, screen_failure_diagnosis


def _strip_border(img: np.ndarray, border: int = 2) -> np.ndarray:
    """Remove the required 2px red license border ObjectNet images carry."""
    if img.shape[0] > border * 2 and img.shape[1] > border * 2:
        return img[border:-border or None, border:-border or None]
    return img


def _load_one_shard_rows(ds, idx):
    """Yield (image_array, imagenet_labels, objectnet_label) rows from a datasets shard."""
    row = ds[idx]
    img = row["image"]
    if hasattr(img, "convert"):
        arr = np.asarray(img.convert("RGB"))
    else:
        arr = np.asarray(img)
    # ObjectNet -> ImageNet mapping is a LIST of acceptable ImageNet-1k indices.
    labels = list(row["imagenet_labels"]) if isinstance(row["imagenet_labels"], (list, tuple)) else [int(row["imagenet_labels"])]
    obj_label = int(row["label"])
    return _strip_border(arr), labels, obj_label


def _to_tensor(img: np.ndarray, device, size: int = 224) -> torch.Tensor:
    from PIL import Image
    im = Image.fromarray(img).convert("RGB").resize((size, size))
    a = np.asarray(im, dtype=np.float32) / 255.0
    a = (a - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    return torch.from_numpy(a).permute(2, 0, 1).unsqueeze(0).to(device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/objectnet-in1k")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--n-classes", type=int, default=20, help="raise toward 113 for full run")
    ap.add_argument("--per-class", type=int, default=30)
    ap.add_argument("--out", default="experiments/m8_real")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-failure-verdicts", type=int, default=50)
    args = ap.parse_args()
    device = torch.device(args.device)

    from datasets import load_from_disk, load_dataset

    data_dir = Path(args.data)
    log = []

    # load the dataset (local parquet dir produced by fetch_objectnet, else load by repo)
    if (data_dir / "dataset_info.json").exists() or any(data_dir.rglob("*.parquet")):
        try:
            ds = load_from_disk(str(data_dir))
        except Exception:
            # parquet shards live under <data_dir>/data/*.parquet in the timm mirror
            pq_dir = data_dir / "data"
            all_pq = sorted(map(str, data_dir.rglob("*.parquet")))
            if not all_pq:
                raise
            files = sorted(map(str, pq_dir.glob("*.parquet"))) if pq_dir.exists() else all_pq
            ds = load_dataset("parquet", data_files=files)["train"]
    else:
        raise FileNotFoundError(
            f"ObjectNet data not found at {data_dir}. Run experiments/fetch_objectnet.py first.")

    # pick a deterministic subset of ObjectNet classes (by ObjectNet label),
    # `per_class` images each
    rng = np.random.default_rng(args.seed)
    class_ids: dict[int, int] = {}
    picked = []
    for i in range(len(ds)):
        obj_label = int(ds[i]["label"])
        first = obj_label not in class_ids
        class_ids.setdefault(obj_label, 0)
        if len(class_ids) <= args.n_classes and class_ids[obj_label] < args.per_class:
            class_ids[obj_label] += 1
            picked.append(i)
        if len(class_ids) >= args.n_classes and all(v >= args.per_class for v in class_ids.values()):
            break
    print(f"[m8] picked {len(picked)} images across {len(class_ids)} ObjectNet classes", flush=True)

    ext = ResNetExtractor(device=device)
    imagenet_labels = ext.imagenet_labels  # dict[int,str]  (ImageNet-1k)

    entries: list[ImageEntry] = []
    rows = []
    for k, idx in enumerate(picked):
        try:
            arr, labels_ok, obj_label = _load_one_shard_rows(ds, idx)
        except Exception as e:
            continue
        x = _to_tensor(arr, device)
        insp = ext.inspect(x, image_id=f"obj{k}",
                           true_label=imagenet_labels.get(labels_ok[0], f"class_{labels_ok[0]}"))
        # correct = the predicted ImageNet index is one of the acceptable ObjectNet
        # mappings (standard ObjectNet evaluation), not equal to a single label.
        with torch.no_grad():
            pred_idx2 = int(ext.model(x).argmax(dim=1).item())
        correct = pred_idx2 in labels_ok
        # causal background/object sensitivity via occlusion on a 3x3 grid
        h, w = x.shape[-2:]
        try:
            ice = run_intervention(ext.model, x, split_regular_grid(h, w, 3),
                                   target_class=pred_idx2, strategy="zero", device=device,
                                   class_names=imagenet_labels)
        except Exception:
            ice = []
        bg_sens = float(np.mean([r.logit_delta for r in ice])) if ice else 0.0
        cls_name = imagenet_labels.get(pred_idx2, f"class_{pred_idx2}")
        entries.append(ImageEntry(
            image_id=f"obj{k}", class_name=cls_name,
            correct=correct, object_share=max(0.0, 1.0 - float(bg_sens)),
            background_share=min(1.0, float(bg_sens)),
            map_meta={"true_labels": labels_ok, "obj_label": obj_label,
                      "pred": insp.pred_label},
        ))
        rows.append({"img": f"obj{k}", "true_labels": labels_ok, "pred": insp.pred_label,
                     "pred_idx": pred_idx2, "correct": bool(correct),
                     "model_bg_share": round(bg_sens, 3)})

    report = screen_class_bias(entries)
    fl = screen_failure_diagnosis(entries, max_verdicts=args.max_failure_verdicts)
    report.verdicts.extend(fl)
    import json as _json
    print(_json.dumps({"n_images": len(entries), "n_classes": len(class_ids),
                       "accuracy": round(float(np.mean([1.0 if e.correct else 0.0 for e in entries])), 3),
                       "verdicts": [vars(v) for v in report.verdicts],
                       "per_image": rows}, indent=2, default=str))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "m8_real_report.json").write_text(
        _json.dumps({"rows": rows, "verdicts": [vars(v) for v in report.verdicts]},
                    indent=2, default=str))
    print(f"[m8] report -> {out / 'm8_real_report.json'}")


if __name__ == "__main__":
    main()