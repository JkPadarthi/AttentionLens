# attentionlens/schema.py
"""Unified schema: the contract between extractors, metrics, screening, and UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass
class LayerMap:
    """One attention/relevance map for one layer, one view, at input resolution."""

    layer_name: str            # e.g. "layer4" / "block11" / "attn_head_3"
    arch: str                  # "cnn" | "vit"
    view: str                  # "native" | "class_conditioned"
    model_class: str           # class this map is conditioned on (argmax for native)
    map: np.ndarray            # H×W float, normalized [0,1], at input resolution
    head_or_channel: Optional[int] = None   # per-head/per-channel breakdown
    metadata: dict[str, Any] = field(default_factory=dict)  # entropy, locality, ...


@dataclass
class InterventionResult:
    """Result of masking/occluding a region and re-running the model."""
    region: tuple[int, int, int, int]   # (x, y, w, h) in input coords
    pred_before: str
    pred_after: str
    logit_delta: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInspection:
    """Everything extracted for one (model, image) pair."""
    model_id: str
    image_id: str
    true_label: str
    pred_label: str
    layers: list[LayerMap] = field(default_factory=list)
    intervention_results: list[InterventionResult] = field(default_factory=list)
