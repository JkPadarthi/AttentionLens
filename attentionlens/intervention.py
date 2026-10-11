# attentionlens/intervention.py
"""Causal occlusion intervention (M4).

Mask / occlude a region of the input, re-run the model, and measure how the
prediction (logits) change. This is the *causal* sensitivity number the screening
engine trusts — vs. the map-level proxy in metrics.py.

Masking strategies:
- "zero":  set the region to the ImageNet *mean* (which is 0 after normalization),
           i.e. "no information there" without injecting a black-box artifact.
- "var":   jitter the region with scaled normal noise (variance-injected control).
- "blur":  replace the region with its box-average (coarse, keeps global stats).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import torch

from attentionlens.schema import InterventionResult


def make_mask_tensor(batch: torch.Tensor, region: tuple[int, int, int, int],
                     strategy: str = "blur") -> torch.Tensor:
    """Return a copy of `batch` with `region` (x,y,w,h) masked per strategy.

    Works on the *normalized* tensor. For "zero" we set the region to 0, which is
    the ImageNet mean after normalization — a color-neutral "no signal" patch, not
    an artificial black block.
    """
    x, y, w, h = region
    out = batch.clone()
    if strategy == "zero":
        out[:, :, y:y + h, x:x + w] = 0.0
    elif strategy == "var":
        shape = (batch.shape[0], batch.shape[1], h, w)
        noise = torch.randn(shape, device=batch.device, dtype=batch.dtype) * 0.5
        out[:, :, y:y + h, x:x + w] = noise
    else:  # "blur" — box-average (coarse mean-pool over the region)
        region_patch = out[:, :, y:y + h, x:x + w]
        mean = region_patch.mean(dim=(2, 3), keepdim=True)
        out[:, :, y:y + h, x:x + w] = mean
    return out


def run_intervention(
    model: torch.nn.Module,
    x: torch.Tensor,
    regions: list[tuple[int, int, int, int]],
    target_class: Optional[int] = None,
    pred_before: str = "",
    strategy: str = "blur",
    device: torch.device = torch.device("cpu"),
    class_names: Optional[dict[int, str]] = None,
) -> list[InterventionResult]:
    """Run occlusion interventions over `regions`; return results sorted by delta.

    When `target_class` is None the current argmax prediction is used. `pred_after`
    is the argmax after masking (so prediction flips are reported too). `logit_delta`
    is signed-inverted so a *positive* delta = masking that region lowered the target
    logit = the model relied on that region for the class.
    """
    model.eval()
    x = x.to(device)
    with torch.no_grad():
        logits = model(x)
    if target_class is None:
        target_class = int(logits[0].argmax().item())
    # label helpers
    def label(idx: int) -> str:
        return class_names[idx] if class_names else f"class_{idx}"

    pred_before = pred_before or label(target_class)

    results: list[InterventionResult] = []
    for region in regions:
        masked = make_mask_tensor(x, region, strategy)
        with torch.no_grad():
            logits_m = model(masked)
        logit_before = float(logits[0, target_class].item())
        logit_after = float(logits_m[0, target_class].item())
        pred_after_idx = int(logits_m[0].argmax().item())
        # positive delta = class logit drops when we hide this region => relied on it
        results.append(InterventionResult(
            region=region, pred_before=pred_before, pred_after=label(pred_after_idx),
            logit_delta=logit_before - logit_after,
            metadata={"target_class": target_class, "target_label": label(target_class),
                      "strategy": strategy},
        ))
    # rank: strongest reliance first (biggest logit drop when hidden)
    results.sort(key=lambda r: r.logit_delta, reverse=True)
    return results


def split_regular_grid(h: int, w: int, n: int) -> list[tuple[int, int, int, int]]:
    """Split an h×w image into an n×n grid of non-overlapping (x,y,w,h) regions."""
    regions: list[tuple[int, int, int, int]] = []
    for i in range(n):
        for j in range(n):
            x0, y0 = (w // n) * j, (h // n) * i
            x1, y1 = (w // n) * (j + 1), (h // n) * (i + 1)
            regions.append((x0, y0, x1 - x0, y1 - y0))
    return regions