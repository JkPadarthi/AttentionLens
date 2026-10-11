# attentionlens/ui/imageload.py
"""Shared image helpers for the Gradio UI: robust array->tensor + map overlay."""
from __future__ import annotations

import numpy as np
import torch


def to_tensor(arr: np.ndarray, device: torch.device = torch.device("cpu")) -> torch.Tensor:
    """[H,W,3] array -> normalized [1,3,224,224] float32 tensor.

    Accepts uint8 [0,255] or float [0,1] (Gradio's numpy Image can be either).
    Forces float32 at every step so the tensor matches the model's float32 weights
    (a float64 promotion here is the classic "Input type (double) and bias type
    (float)" crash).
    """
    from PIL import Image
    from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD

    arr = np.asarray(arr)
    if arr.ndim == 3 and arr.shape[2] == 4:      # RGBA -> RGB
        arr = arr[:, :, :3]
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0.0, 1.0)
        arr = (arr * 255.0).astype(np.uint8)
    img = Image.fromarray(arr).convert("RGB").resize((224, 224))
    a = np.asarray(img, dtype=np.float32) / 255.0
    mean = np.asarray(IMAGENET_MEAN, dtype=np.float32)
    std = np.asarray(IMAGENET_STD, dtype=np.float32)
    a = (a - mean) / std
    return torch.from_numpy(a).permute(2, 0, 1).unsqueeze(0).to(device)


def overlay(base: np.ndarray, m: np.ndarray, alpha: float = 0.55) -> np.ndarray:
    """Overlay a normalized [0,1] map on a uint8 base image with a jet colormap."""
    import matplotlib

    matplotlib.use("Agg")
    try:
        cmap = matplotlib.colormaps["jet"]          # matplotlib >=3.9
    except Exception:
        from matplotlib import cm
        cmap = cm.get_cmap("jet")
    color = (cmap(m)[:, :, :3] * 255).astype(np.uint8)
    img = base.copy()
    img = (img * (1 - alpha) + color * alpha).astype(np.uint8)
    return img