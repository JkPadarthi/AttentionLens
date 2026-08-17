# attentionlens/extractors/cnn.py
"""CNN attention extraction: native channel activations + Grad-CAM."""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from attentionlens.schema import LayerMap


def _normalize01(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    mn, mx = a.min(), a.max()
    if mx - mn < 1e-9:
        return np.zeros_like(a)
    return (a - mn) / (mx - mn)


def _get_submodule(model: torch.nn.Module, name: str) -> torch.nn.Module:
    mod = model
    for part in name.split("."):
        mod = getattr(mod, part)
    return mod


def native_activation_maps(
    model: torch.nn.Module,
    layer_names: list[str],
    input_tensor: torch.Tensor,
    target_size: tuple[int, int],
    model_class: str = "argmax",
    device: torch.device = torch.device("cpu"),
) -> list[LayerMap]:
    """Mean-over-channel activation map per named layer, normalized to [0,1]."""
    hooks: list[torch.utils.hooks.RemovableHandle] = []
    activations: dict[str, torch.Tensor] = {}

    def make_hook(name: str):
        def hook(_m, _inp, out):
            activations[name] = out.detach()
        return hook

    for name in layer_names:
        hooks.append(_get_submodule(model, name).register_forward_hook(make_hook(name)))

    model.eval()
    with torch.no_grad():
        model(input_tensor.to(device))

    maps: list[LayerMap] = []
    for name in layer_names:
        act = activations[name]                    # [B,C,H,W]
        pooled = act.mean(dim=1).squeeze(0)        # [H,W]
        up = F.interpolate(pooled.unsqueeze(0).unsqueeze(0),
                           size=target_size, mode="bilinear", align_corners=False)
        arr = _normalize01(up.squeeze().cpu().numpy())
        maps.append(LayerMap(layer_name=name, arch="cnn", view="native",
                             model_class=model_class, map=arr,
                             metadata={"reduction": "mean_channel"}))
    for h in hooks:
        h.remove()
    return maps


def gradcam_maps(
    model: torch.nn.Module,
    layer_names: list[str],
    input_tensor: torch.Tensor,
    target_class: int | None,
    target_size: tuple[int, int],
    device: torch.device = torch.device("cpu"),
    class_names: dict[int, str] | None = None,
) -> list[LayerMap]:
    """Grad-CAM per named layer, relu'd, upsampled, normalized."""
    from captum.attr import LayerGradCam

    model.eval()
    x = input_tensor.to(device)
    if target_class is None:
        with torch.no_grad():
            target_class = int(model(x).argmax(dim=1).item())

    maps: list[LayerMap] = []
    for name in layer_names:
        layer = _get_submodule(model, name)
        cam = LayerGradCam(model, layer)
        attr = cam.attribute(x, target=target_class)     # [1,1,H,W]
        attr = F.relu(attr)
        up = F.interpolate(attr, size=target_size, mode="bilinear", align_corners=False)
        arr = _normalize01(up.detach().squeeze().cpu().numpy())
        label = class_names[target_class] if class_names else f"class_{target_class}"
        maps.append(LayerMap(layer_name=name, arch="cnn", view="class_conditioned",
                             model_class=label, map=arr, metadata={"method": "gradcam"}))
    return maps
