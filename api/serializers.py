"""Serializers for converting Python objects to API responses."""
from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image

from attentionlens.schema import LayerMap, ModelInspection, InterventionResult


def numpy_to_base64_png(arr: np.ndarray) -> str:
    """Convert numpy array (HxW or HxWx3) to base64-encoded PNG."""
    if arr.ndim == 2:
        # Grayscale heatmap — apply jet colormap
        import matplotlib
        matplotlib.use("Agg")
        try:
            cmap = matplotlib.colormaps["jet"]
        except Exception:
            from matplotlib import cm
            cmap = cm.get_cmap("jet")
        arr = (cmap(arr)[:, :, :3] * 255).astype(np.uint8)
    elif arr.ndim == 3 and arr.shape[2] == 3:
        arr = arr.astype(np.uint8)
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")
    
    img = Image.fromarray(arr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def serialize_layer_map(m: LayerMap) -> dict:
    """Serialize a LayerMap to a dict with base64-encoded map."""
    return {
        "layer_name": m.layer_name,
        "arch": m.arch,
        "view": m.view,
        "model_class": m.model_class,
        "map_b64": numpy_to_base64_png(m.map),
        "head_or_channel": m.head_or_channel,
        "metadata": m.metadata,
    }


def serialize_intervention_result(r: InterventionResult) -> dict:
    """Serialize an InterventionResult to a dict."""
    return {
        "region": list(r.region),
        "pred_before": r.pred_before,
        "pred_after": r.pred_after,
        "logit_delta": r.logit_delta,
        "metadata": r.metadata,
    }


def serialize_inspection(insp: ModelInspection) -> dict:
    """Serialize a ModelInspection to a dict."""
    return {
        "model_id": insp.model_id,
        "image_id": insp.image_id,
        "true_label": insp.true_label,
        "pred_label": insp.pred_label,
        "layers": [serialize_layer_map(m) for m in insp.layers],
        "intervention_results": [
            serialize_intervention_result(r) for r in insp.intervention_results
        ],
    }
