# attentionlens/ui/app.py
"""M5 Gradio UI — per-layer dual-view browser + click-to-mask intervention.

Run:  python -m attentionlens.ui.app   (CPU)   or set ATTENTIONLENS_DEVICE=cuda
"""
from __future__ import annotations

import os

import gradio as gr
import numpy as np
import torch

from attentionlens.preprocess import load_image_tensor, tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor
from attentionlens.intervention import run_intervention, split_regular_grid
from attentionlens.metrics import all_metrics

DEVICE = os.environ.get("ATTENTIONLENS_DEVICE", "cpu")
DEVICE = torch.device(DEVICE if DEVICE in ("cuda", "cpu") and (DEVICE == "cpu" or torch.cuda.is_available()) else "cpu")

_MODELS = {}


def _get_model(name: str):
    if name not in _MODELS:
        if name == "ResNet-50":
            _MODELS[name] = ResNetExtractor(device=DEVICE)
        else:  # ViT-B/16
            _MODELS[name] = VitExtractor(device=DEVICE)
    return _MODELS[name]


def analyze(image: np.ndarray, model_name: str) -> tuple[np.ndarray, str, np.ndarray, list]:
    """Analyze an uploaded image: run the model, produce dual-view maps per layer.

    Returns (annotated image, prediction text, selected class-cond map, gallery).
    """
    if image is None:
        return image, "Upload an image first.", image, []
    # gradio passes an [H,W,3] uint8 array; convert to the normalized tensor
    img = np.asarray(image)
    if img.ndim == 3 and img.shape[2] == 4:  # RGBA
        img = img[:, :, :3]
    x = load_image_tensor_from_array(img, device=DEVICE)
    ext = _get_model(model_name)
    insp = ext.inspect(x, image_id="upload")

    base = tensor_to_image(x)
    pred_txt = f"Prediction: **{insp.pred_label}**  ·  {len(insp.layers)} maps extracted"
    # overlay every class-conditioned map on the base for the "selected" panel
    sel = base.copy()
    cc = [m for m in insp.layers if m.view == "class_conditioned"]
    if cc:
        sel = _overlay(base, cc[-1].map)
    # gallery entries: (image, caption) pairs — gradio renders these as cards
    gallery = [(m.map, f"{m.layer_name} · {m.view}") for m in insp.layers]
    return base, pred_txt, sel, gallery


def probe(image: np.ndarray, model_name: str, x: int, y: int, size: int) -> str:
    """Run a click-to-mask intervention centered at (x, y); returns a text report."""
    img = np.asarray(image)
    h, w = img.shape[0], img.shape[1]
    cx = min(max(x, 0), w - 1)
    cy = min(max(y, 0), h - 1)
    x0 = max(0, cx - size // 2)
    y0 = max(0, cy - size // 2)
    region = (x0, y0, min(size, w - x0), min(size, h - y0))
    tensor = load_image_tensor_from_array(img, device=DEVICE)
    ext = _get_model(model_name)
    results = run_intervention(ext.model, tensor, [region], strategy="zero",
                               class_names=getattr(ext, "imagenet_labels", {}))
    r = results[0]
    lines = [
        f"Masked region: {r.region}",
        f"Prediction before: **{r.pred_before}** → after: **{r.pred_after}**",
        f"Target-class logit delta: **{r.logit_delta:+.3f}** (positive = model relied on this region)",
    ]
    return "\n".join(lines)


def explore_map(image: np.ndarray, model_name: str, layer_key: str) -> np.ndarray:
    """Re-render a single layer map from the gallery selection."""
    # placeholder-based: the gallery already carries all maps; kept for API symmetry
    return np.asarray(image)


def _overlay(base: np.ndarray, m: np.ndarray, alpha: float = 0.55) -> np.ndarray:
    """Overlay a normalized map on a uint8 image with a jet colormap."""
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import cm
    # matplotlib >=3.9 removed cm.get_cmap; use the colormaps registry instead.
    try:
        cmap = matplotlib.colormaps["jet"]
    except Exception:
        cmap = cm.get_cmap("jet")
    color = (cmap(m)[:, :, :3] * 255).astype(np.uint8)
    img = base.copy()
    img = (img * (1 - alpha) + color * alpha).astype(np.uint8)
    return img


def load_image_tensor_from_array(arr: np.ndarray, device: torch.device = torch.device("cpu")) -> torch.Tensor:
    """[H,W,3] array -> normalized [1,3,224,224] float32 tensor.

    Handles both uint8 [0,255] and float [0,1] inputs (Gradio's numpy Image can be
    either depending on the upload). Keeps every op float32 so the tensor matches the
    model's float32 weights.
    """
    from PIL import Image
    from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD

    arr = np.asarray(arr)
    if arr.dtype != np.uint8:
        # float [0,1] (Gradio default) -> scale to [0,255] uint8
        arr = np.clip(arr, 0.0, 1.0)
        arr = (arr * 255.0).astype(np.uint8)
    else:
        arr = arr.astype(np.uint8)
    img = Image.fromarray(arr).convert("RGB").resize((224, 224))
    a = np.asarray(img, dtype=np.float32) / 255.0
    # force float32 mean/std — np.array(list) would default to float64 and promote
    # the tensor to double, mismatching the float32 model weights.
    mean = np.asarray(IMAGENET_MEAN, dtype=np.float32)
    std = np.asarray(IMAGENET_STD, dtype=np.float32)
    a = (a - mean) / std
    t = torch.from_numpy(a).permute(2, 0, 1).unsqueeze(0).to(device)
    return t


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AttentionLens") as demo:
        gr.Markdown("# 🔍 AttentionLens\n### Dual-view attention browser — CNN & ViT")
        with gr.Row():
            with gr.Column(scale=1):
                inp = gr.Image(label="Input image", type="numpy")
                model = gr.Radio(["ResNet-50", "ViT-B/16"], label="Model", value="ResNet-50")
                run_btn = gr.Button("Analyze", variant="primary")
            with gr.Column(scale=2):
                base_disp = gr.Image(label="Base image", type="numpy")
                pred_txt = gr.Markdown("Upload an image and click Analyze.")
                selected = gr.Image(label="Selected class-conditioned map", type="numpy")
        gallery = gr.Gallery(label="All dual-view maps (layer · view)", columns=4, object_fit="contain")
        gr.Markdown("---")
        gr.Markdown("## Click-to-mask intervention")
        with gr.Row():
            probe_x = gr.Slider(0, 223, value=112, step=1, label="region center X")
            probe_y = gr.Slider(0, 223, value=112, step=1, label="region center Y")
            probe_sz = gr.Slider(8, 112, value=48, step=8, label="mask size (px)")
            probe_btn = gr.Button("Probe region", variant="secondary")
        probe_out = gr.Markdown("Mask a region to see if the model needs it.")

        run_btn.click(analyze, [inp, model], [base_disp, pred_txt, selected, gallery])
        probe_btn.click(probe, [inp, model, probe_x, probe_y, probe_sz], probe_out)

    return demo


if __name__ == "__main__":
    app = build_app()
    server_name = os.environ.get("ATTENTIONLENS_HOST", "127.0.0.1")
    port = int(os.environ.get("ATTENTIONLENS_PORT", "7860"))
    app.launch(server_name=server_name, server_port=port)