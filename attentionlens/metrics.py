# attentionlens/metrics.py
"""Attention quality metrics (M3).

Computed per (image, layer, view) — all consuming `LayerMap`s plus ground-truth
annotations (CUB-200 bbox / parts) when available. Every metric is honest to the
schema: it reads only `LayerMap.map` (HxW float [0,1]) and `metadata`.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np

from attentionlens.schema import LayerMap

EPS = 1e-9


def focus_entropy(m: LayerMap) -> float:
    """Shannon entropy of the normalized map (bits). Low = localized, high = diffuse."""
    p = m.map.astype(np.float64).ravel()
    p = p / (p.sum() + EPS)
    p = p[p > EPS]
    return float(-(p * np.log2(p)).sum())


def object_relevance_share(m: LayerMap, bbox: tuple[int, int, int, int]) -> float:
    """Fraction of the map's total relevance that falls inside the object bbox.

    bbox: (x, y, w, h) in the same pixel space as `m.map`.
    """
    H, W = m.map.shape
    x, y, w, h = bbox
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    total = m.map.sum() + EPS
    inside = m.map[y0:y1, x0:x1].sum()
    return float(inside / total)


def part_alignment(m: LayerMap, points: Iterable[tuple[int, int]], radius: int = 6) -> float:
    """Fraction of relevance captured within `radius` px of any ground-truth part point."""
    H, W = m.map.shape
    yy, xx = np.mgrid[0:H, 0:W]
    mask = np.zeros((H, W), dtype=bool)
    for (px, py) in points:
        px, py = int(px), int(py)
        if 0 <= px < W and 0 <= py < H:
            mask |= ((xx - px) ** 2 + (yy - py) ** 2) <= radius**2
    total = m.map.sum() + EPS
    return float(m.map[mask].sum() / total)


def background_sensitivity(m: LayerMap, bbox: tuple[int, int, int, int]) -> float:
    """Relevance share OUTSIDE the object bbox — *potential* background reliance.

    Note: this is a map-level proxy. The *causal* background/object sensitivity
    (prediction flip under masking) lives in `intervention.py` (M4) and is the
    evidence-backed number the screening engine prefers.
    """
    return 1.0 - object_relevance_share(m, bbox)


def all_metrics(m: LayerMap, bbox: Optional[tuple[int, int, int, int]] = None,
                part_points: Iterable[tuple[int, int]] | None = None,
                part_radius: int = 6) -> dict[str, float]:
    """Convenience: compute the full metric set for one map."""
    out: dict[str, float] = {"entropy": focus_entropy(m)}
    if bbox is not None:
        out["object_relevance_share"] = object_relevance_share(m, bbox)
        out["background_sensitivity"] = background_sensitivity(m, bbox)
    if part_points is not None:
        out["part_alignment"] = part_alignment(m, part_points, radius=part_radius)
    # persist a compact copy into the map's own metadata for later evidence-linking
    m.metadata.update({k: round(v, 4) for k, v in out.items()})
    return out