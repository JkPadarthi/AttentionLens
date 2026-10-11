# experiments/eda_review1.py
"""Review 1 EDA + preprocessing stats for AttentionLens.

Runs the real pipeline on the demo image (Samoyed, ImageNet) and emits:
  - experiments/eda/preprocess_stats.json  (tensor/pixel stats, pipeline facts)
  - experiments/eda/map_stats.csv          (per-layer dual-view map statistics)
  - experiments/eda/eda_montage.png        (2x4 grid: all 8 maps overlayed)
  - experiments/eda/eda_histograms.png     (value distribution, native vs GC)
  - experiments/eda/eda_concentration.png  (sorted cumulative energy curves)
  - experiments/eda/eda_correlations.png   (native vs class-cond similarity per layer)
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from attentionlens.preprocess import load_image_tensor, tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor, RESNET_BLOCK_LAYERS

IMG = "experiments/sample.jpg"
OUT = pathlib.Path("experiments/eda")
OUT.mkdir(parents=True, exist_ok=True)

RESULTS = {}

# ---------------------------------------------------------------- preprocessing
pil_img = Image.open(IMG)
RESULTS["dataset"] = {
    "image_id": "sample.jpg",
    "source": "ImageNet (demo sample)",
    "true_label": "Samoyed",
    "original_size": list(pil_img.size),
    "input_size": 224,
    "mean": [0.485, 0.456, 0.406],
    "std": [0.229, 0.224, 0.225],
}

raw = np.asarray(pil_img.convert("RGB").resize((224, 224)), dtype=np.float32) / 255.0
RESULTS["preprocessing_raw_stats"] = {
    "channels": [
        {"channel": c, "mean": float(raw[..., c].mean()), "std": float(raw[..., c].std())}
        for c in range(3)
    ]
}

x = load_image_tensor(IMG, device=torch.device("cpu"))
RESULTS["preprocessing_tensor"] = {
    "shape": list(x.shape),
    "dtype": str(x.dtype),
    "device": "cpu",
    "channels_normalized": [
        {"channel": c, "mean": float(x[0, c].mean().item()), "std": float(x[0, c].std().item())}
        for c in range(3)
    ],
}

# ------------------------------------------------------------------- inspection
device = torch.device("cpu")
ext = ResNetExtractor(device=device)
insp = ext.inspect(x, image_id="sample", true_label="Samoyed")
RESULTS["inference"] = {
    "model": "resnet50 (ImageNet1K_V2)",
    "pred_label": insp.pred_label,
    "true_label": insp.true_label,
    "num_layers_extracted": len(insp.layers),
    "block_layers": RESNET_BLOCK_LAYERS,
    # ResNet-50 bottleneck channel counts at each probed conv
    "probing_channels": [256, 512, 1024, 2048],
}
print("pred:", insp.pred_label, "| layers:", len(insp.layers))

# ---------------------------------------------------------------- per-map stats
rows = []
views = {}   # layer_name -> {native: arr, class_conditioned: arr}
for m in insp.layers:
    a = m.map
    hist, _ = np.histogram(a, bins=64, range=(0.0, 1.0))
    p = hist / hist.sum()
    entropy = float(-np.sum(p[p > 0] * np.log2(p[p > 0])))
    thr = float(np.quantile(a, 0.9))
    mass_top10 = float(a[a >= thr].sum() / a.sum())
    peak = np.unravel_index(int(np.argmax(a)), a.shape)
    rows.append({
        "layer": m.layer_name,
        "view": m.view,
        "method": m.metadata.get("method", m.metadata.get("reduction", "")),
        "model_class": m.model_class,
        "map_mean": float(a.mean()),
        "map_std": float(a.std()),
        "entropy_bits": round(entropy, 3),
        "top10_mass_frac": round(mass_top10, 3),
        "peak_y": int(peak[0]),
        "peak_x": int(peak[1]),
    })
    views.setdefault(m.layer_name, {})[m.view] = a

with open(OUT / "map_stats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

corr_rows = []
for ln, vs in views.items():
    r = float(np.corrcoef(vs["native"].ravel(), vs["class_conditioned"].ravel())[0, 1])
    corr_rows.append({"layer": ln, "pearson_native_vs_gradcam": round(r, 3)})
RESULTS["layer_correlations"] = corr_rows

# ------------------------------------------------------------------- figures
base = tensor_to_image(x)
layer_names = list(views.keys())

# 2x4 montage: row = view, col = layer
fig, axes = plt.subplots(2, 4, figsize=(16, 8.5))
for ci, ln in enumerate(layer_names):
    for ri, view in enumerate(["class_conditioned", "native"]):
        ax = axes[ri][ci]
        ax.imshow(base)
        ax.imshow(views[ln][view], cmap="jet", alpha=0.65)
        ax.set_title(f"{ln}\n{view}", fontsize=9)
        ax.axis("off")
fig.suptitle("AttentionLens M1 — ResNet-50 dual-view maps (pred: %s)" % insp.pred_label, fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "eda_montage.png", dpi=110)
plt.close(fig)

# histograms: native vs grad-cam per layer
fig, axes = plt.subplots(1, 4, figsize=(16, 3.6))
for ci, ln in enumerate(layer_names):
    ax = axes[ci]
    ax.hist(views[ln]["class_conditioned"].ravel(), bins=48, range=(0, 1),
            alpha=0.6, label="class-conditioned", color="C3")
    ax.hist(views[ln]["native"].ravel(), bins=48, range=(0, 1),
            alpha=0.6, label="native", color="C0")
    ax.set_title(ln, fontsize=9)
    ax.set_xlabel("normalized value")
    ax.legend(fontsize=7)
fig.suptitle("Map value distributions", fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "eda_histograms.png", dpi=110)
plt.close(fig)

# concentration curves: sorted cumulative energy
fig, axes = plt.subplots(1, 4, figsize=(16, 3.6))
for ci, ln in enumerate(layer_names):
    ax = axes[ci]
    for view, color in [("class_conditioned", "C3"), ("native", "C0")]:
        a = views[ln][view].ravel()
        s = np.sort(a)[::-1]
        cum = np.cumsum(s) / s.sum()
        ax.plot(np.arange(1, len(cum) + 1) / len(cum), cum, color=color,
                label=view, lw=1.6)
    ax.set_title(ln, fontsize=9)
    ax.set_xlabel("fraction of pixels")
    ax.set_ylabel("cumulative normalized energy")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
fig.suptitle("Spatial concentration of attention (sorted energy)", fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "eda_concentration.png", dpi=110)
plt.close(fig)

# correlation bars
fig, ax = plt.subplots(figsize=(9, 3.6))
names = [r["layer"] for r in corr_rows]
vals = [r["pearson_native_vs_gradcam"] for r in corr_rows]
bars = ax.bar(names, vals, color=["C0", "C1", "C2", "C3"])
ax.axhline(0, color="k", lw=0.8)
ax.set_ylim(-1, 1)
ax.set_title("Native activation vs Grad-CAM correlation per block")
ax.set_ylabel("Pearson r")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + (0.04 if v >= 0 else -0.09),
            f"{v:.2f}", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "eda_correlations.png", dpi=110)
plt.close(fig)

# ------------------------------------------------------------------- output json
with open(OUT / "preprocess_stats.json", "w") as f:
    json.dump(RESULTS, f, indent=2)

print("EDA artifacts written to", OUT)
print(json.dumps(RESULTS, indent=2))