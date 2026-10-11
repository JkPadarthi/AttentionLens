# attentionlens/screening.py
"""Automated screening engine (M6).

Aggregates per-image metrics into class-level stats and turns them into
evidence-backed verdicts. Every verdict is a structured object with a flag, a
reason, and a list of evidence (the images/maps that fired it), so nothing is
claimed without a traceable proof.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import numpy as np

from attentionlens.metrics import object_relevance_share, background_sensitivity


@dataclass
class Verdict:
    verdict_type: str          # "class_bias" | "layer_role" | "failure_diagnosis"
    level: str                 # "info" | "warning" | "flag"
    message: str
    evidence: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ScreeningReport:
    model_id: str
    class_names: list[str] = field(default_factory=list)
    verdicts: list[Verdict] = field(default_factory=list)
    class_stats: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass
class ImageEntry:
    """One scored image for screening: its maps' object/background relevance.

    `object_share` and `background_share` are computed from the class-conditioned
    map against the object bbox — the evidence the verdicts are based on.
    """
    image_id: str
    class_name: str
    correct: bool
    object_share: float
    background_share: float
    map_meta: dict[str, Any] = field(default_factory=dict)


def score_image(m: "LayerMap", bbox: tuple[int, int, int, int]) -> dict[str, float]:
    """Score one class-conditioned map's object vs background reliance."""
    return {
        "object_share": object_relevance_share(m, bbox),
        "background_share": background_sensitivity(m, bbox),
    }


def screen_class_bias(
    entries: list[ImageEntry],
    threshold_bg_greater_than_obj: float = 0.05,
    min_images: int = 3,
) -> ScreeningReport:
    """Aggregate scored images into class-level stats and produce bias verdicts.

    A class bias flag fires when, on average, the model's class-conditioned
    relevance falls more on the background than the object for a class — the
    signature of a spurious background shortcut.
    """
    report = ScreeningReport(model_id="", class_stats={})
    by_class: dict[str, list[ImageEntry]] = {}
    for e in entries:
        by_class.setdefault(e.class_name, []).append(e)

    for cls, es in by_class.items():
        if len(es) < min_images:
            continue
        shares = [e.object_share for e in es]
        bgs = [e.background_share for e in es]
        stats = {
            "n": len(es),
            "mean_object_share": float(np.mean(shares)),
            "mean_background_share": float(np.mean(bgs)),
            "accuracy": float(np.mean([1.0 if e.correct else 0.0 for e in es])),
        }
        report.class_stats[cls] = stats
        report.class_names.append(cls)

        bg, obj = stats["mean_background_share"], stats["mean_object_share"]
        if bg > obj + threshold_bg_greater_than_obj:
            report.verdicts.append(Verdict(
                verdict_type="class_bias", level="flag",
                message=(f"Class '{cls}' looks background-driven: mean background "
                         f"relevance {bg:.2f} > object {obj:.2f} over {len(es)} images. "
                         f"Suspected spurious correlation."),
                evidence=es[:min_images],
            ))
        else:
            report.verdicts.append(Verdict(
                verdict_type="class_bias", level="info",
                message=(f"Class '{cls}' looks object-driven: mean object relevance "
                         f"{obj:.2f} >= background {bg:.2f} over {len(es)} images."),
                evidence=es,
            ))
    report.verdicts.sort(key=lambda v: 0 if v.level == "flag" else 1)
    return report


def screen_failure_diagnosis(entries: list[ImageEntry], min_images: int = 2) -> list[Verdict]:
    """Flag misclassified images where relevance still lands on the background.

    A *failure diagnosis* is the model being wrong AND showing background reliance
    — i.e. "it guessed from the context, not the object."
    """
    out: list[Verdict] = []
    for e in entries:
        if not e.correct and e.background_share > e.object_share:
            out.append(Verdict(
                verdict_type="failure_diagnosis", level="warning",
                message=(f"Image '{e.image_id}' ({e.class_name}) is misclassified and "
                         f"relies on background (bg {e.background_share:.2f} > obj "
                         f"{e.object_share:.2f}). Guessed from context, not object."),
                evidence=[{**e.map_meta, "image_id": e.image_id}],
            ))
            if len(out) >= min_images:
                break
    return out