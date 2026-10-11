# attentionlens/ui/app.py
"""AttentionLens — Gradio UI (M5, redesigned).

A clean dual-view attention browser for CNN & ViT with click-to-mask intervention.

Hardened:
  - Analyze/Probe handlers surface the *real* exception text in the UI instead of
    Gradio swallowing it as a silent None.
  - Image handling accepts both float [0,1] and uint8 arrays (Gradio's numpy Image
    can be either).
  - Handlers take exactly the number of inputs the buttons wire (this was a prior
    silent-failure source).

Run:  python -m attentionlens.ui.app   (CPU default; set ATTENTIONLENS_DEVICE=cuda)
"""
from __future__ import annotations

import os
import traceback

import gradio as gr
import numpy as np
import torch

from attentionlens.preprocess import tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor
from attentionlens.intervention import run_intervention
from attentionlens.ui import imageload as il

DEVICE_NAME = os.environ.get("ATTENTIONLENS_DEVICE", "cpu")
DEVICE = torch.device(DEVICE_NAME if (DEVICE_NAME == "cpu" or
                                      (DEVICE_NAME == "cuda" and torch.cuda.is_available()))
                      else "cpu")

_MODELS: dict[str, object] = {}
MODEL_IDS = ["ResNet-50", "ViT-B/16"]


def _get_model(name: str):
    if name not in _MODELS:
        _MODELS[name] = (ResNetExtractor(device=DEVICE) if name == "ResNet-50"
                         else VitExtractor(device=DEVICE))
    return _MODELS[name]


def analyze(image, model_name):
    """Run the model; return (base image, prediction text, gallery of (img, caption))."""
    try:
        if image is None:
            return None, "⬆️ Upload an image first, then click **Analyze**.", []
        x = il.to_tensor(image, device=DEVICE)
        ext = _get_model(model_name)
        insp = ext.inspect(x, image_id="upload")
        base = tensor_to_image(x)
        n_layers = len({m.layer_name for m in insp.layers})
        pred_txt = f"**Prediction:** `{insp.pred_label}`  ·  {len(insp.layers)} maps across {n_layers} layers"
        gallery = [(il.overlay(base, m.map), f"{m.view} · {m.layer_name}") for m in insp.layers]
        return base, pred_txt, gallery
    except Exception as e:  # noqa: BLE001 — surface the real cause
        return None, f"❌ **Error analyzing:** `{e}`\n\n```\n{traceback.format_exc(limit=3)}\n```", []


def probe(image, model_name, cx, cy, size):
    """Occlude a region centered at (cx,cy); report prediction/logit change."""
    try:
        if image is None:
            return "⬆️ Upload an image first, then click **Analyze**."
        x = il.to_tensor(image, device=DEVICE)
        ext = _get_model(model_name)
        h, w = x.shape[-2:]
        cx = int(max(0, min(int(cx), w - 1)))
        cy = int(max(0, min(int(cy), h - 1)))
        x0 = max(0, cx - int(size) // 2)
        y0 = max(0, cy - int(size) // 2)
        region = (x0, y0, min(int(size), w - x0), min(int(size), h - y0))
        results = run_intervention(ext.model, x, [region], strategy="zero",
                                   class_names=getattr(ext, "imagenet_labels", {}))
        r = results[0]
        return (f"- **Masked region:** {r.region}\n"
                f"- **Prediction before:** `{r.pred_before}` → **after:** `{r.pred_after}`\n"
                f"- **Target-class logit delta:** `{r.logit_delta:+.3f}` "
                f"(positive = the model relied on this region)")
    except Exception as e:  # noqa: BLE001
        return f"❌ **Error probing:** `{e}`\n\n```\n{traceback.format_exc(limit=3)}\n```"


THEME = gr.themes.Soft(
    primary_hue="indigo", secondary_hue="blue", neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AttentionLens") as demo:
        gr.Markdown(
            "# 🔍 AttentionLens  <span style='font-size:15px;color:#94a3b8'>— why your model guessed that</span>\n"
            "Dual-view attention for **CNN & ViT**: *native* (where the mechanism looks) "
            "and *class-conditioned* (where the evidence for the prediction sits), plus "
            "causal click-to-mask probing.\n"
            "> *Grad-CAM shows you a heatmap. AttentionLens tells you the model cheated — and shows you the proof.*"
        )

        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                inp = gr.Image(label="Input image", type="numpy",
                               sources=["upload", "clipboard"], height=320)
                model = gr.Radio(MODEL_IDS, label="Model", value="ResNet-50")
                gr.Markdown("### 🧪 Causal probe (click-to-mask)")
                with gr.Row():
                    probe_x = gr.Slider(0, 223, value=112, step=1, label="center X")
                    probe_y = gr.Slider(0, 223, value=112, step=1, label="center Y")
                probe_sz = gr.Slider(8, 112, value=48, step=8, label="mask size (px)")
                probe_btn = gr.Button("Run probe", variant="secondary")
                analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")

            with gr.Column(scale=2):
                pred_txt = gr.Markdown("Upload an image and click **Analyze**.")
                base_disp = gr.Image(label="Base image", type="numpy", interactive=False)
                gallery = gr.Gallery(label="Dual-view attention maps",
                                     columns=4, rows=2, object_fit="contain",
                                     height=460, allow_preview=True)
                probe_out = gr.Markdown("Mask a region to test whether the model depends on it.")

        gr.Markdown(
            "**Reading the maps** — *native* = the mechanism's own focus (CNN channel "
            "activation / ViT attention rollout); *class_conditioned* = the evidence for "
            "the predicted class (Grad-CAM / gradient-weighted attention). A "
            "class-conditioned map pinned to the **background** while the object is in "
            "frame is the fingerprint of a spurious shortcut.")

        analyze_btn.click(analyze, [inp, model], [base_disp, pred_txt, gallery])
        probe_btn.click(probe, [inp, model, probe_x, probe_y, probe_sz], probe_out)
    return demo


if __name__ == "__main__":
    app = build_app()
    host = os.environ.get("ATTENTIONLENS_HOST", "0.0.0.0")
    port = int(os.environ.get("ATTENTIONLENS_PORT", "7860"))
    app.launch(server_name=host, server_port=port, show_error=True,
               theme=THEME, css="""
        .analytics { font-size: 15px; }
        #probe_card { background: transparent; }
    """)