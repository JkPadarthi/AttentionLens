# attentionlens/data.py
"""Dataset helpers for AttentionLens (M7/M8).

A self-contained, download-free compositing routine for the planted-bias
experiment: given an object crop and a background image, splice the object onto
the background the way Waterbirds does, so a synthetic spurious correlation can
be planted and then *caught* by the screener.
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
from PIL import Image

# fallback tiny backgrounds when no dataset is present (single-color, noise)
_FALLBACK_BGS = {
    "water": (86, 130, 170),
    "land": (95, 158, 88),
}


def make_correlated_dataset(
    object_crops: list[np.ndarray],
    backgrounds: dict[str, np.ndarray],
    labels: list[str],
    class2bg: dict[str, str],
    out_dir: str | Path,
    size: int = 224,
    seed: int = 0,
) -> Path:
    """Composite each object crop onto its correlated background and save images.

    builds `out_dir/{label}/image_{i}.jpg` — the Waterbirds-style planted set.
    `backgrounds`: map of background-name -> HxWx3 uint8 array.
    `class2bg`:   map of class -> background-name (this is the planted correlation).
    Returns out_dir. Images are Resized to `size` and centered (crop-or-pad).
    """
    out_dir = Path(out_dir)
    rng = np.random.default_rng(seed)
    for label in labels:
        (out_dir / label).mkdir(parents=True, exist_ok=True)
    placed = 0
    for i, crop in enumerate(object_crops):
        label = labels[i % len(labels)]
        bg_name = class2bg[label]
        bg = backgrounds[bg_name]
        comp = _composite(crop, bg, rng, size)
        Image.fromarray(comp).save(out_dir / label / f"image_{placed:05d}.jpg", quality=95)
        placed += 1
    return out_dir


def make_clean_dataset(
    object_crops: list[np.ndarray],
    backgrounds: dict[str, np.ndarray],
    labels: list[str],
    class2bg: dict[str, str],  # used only to pick a background (still spliced, but *unbiased*)
    out_dir: str | Path,
    size: int = 224,
    seed: int = 999,
) -> Path:
    """Same as make_correlated_dataset but backgrounds are DRAWN per-image.

    Not used for the main experiment; kept for a control set where object/background
    are decorrelated (so the screener must NOT flag it).
    """
    out_dir = Path(out_dir)
    rng = np.random.default_rng(seed)
    bg_names = list(backgrounds.keys())
    for label in labels:
        (out_dir / label).mkdir(parents=True, exist_ok=True)
    placed = 0
    for crop in object_crops:
        label = labels[placed % len(labels)]
        bg_name = bg_names[placed % len(bg_names)]  # random, not correlated
        bg = backgrounds[bg_name]
        comp = _composite(crop, bg, rng, size)
        Image.fromarray(comp).save(out_dir / label / f"image_{placed:05d}.jpg", quality=95)
        placed += 1
    return out_dir


def _composite(crop: np.ndarray, bg: np.ndarray, rng: np.random.Generator, size: int) -> np.ndarray:
    """Center the crop on a (possibly upscaled) background, with a soft edge."""
    # work at resolution; resize bg to size if smaller
    bg_im = Image.fromarray(np.asarray(bg, dtype=np.uint8)).convert("RGB")
    bg_im = bg_im.resize((size, size))
    crop_im = Image.fromarray(np.asarray(crop, dtype=np.uint8)).convert("RGB")
    # shrink crop to ~ half the frame so it doesn't fill the whole image
    cw = int(size * 0.5)
    crop_im = crop_im.resize((cw, cw))
    composite = bg_im.copy()
    comp = np.asarray(composite).copy()
    y0 = (size - cw) // 2
    x0 = (size - cw) // 2
    crop_arr = np.asarray(crop_im).copy()
    # blend a soft border for realism (alpha ramp over 12 px)
    a = np.ones((cw, cw, 1), dtype=np.float32) * 255.0
    r = 14
    for t in range(r):
        a[t, :, 0] = a[t, :, 0] * (t / r)
        a[-1 - t, :, 0] = a[-1 - t, :, 0] * (t / r)
        a[:, t, 0] = a[:, t, 0] * (t / r)
        a[:, -1 - t, 0] = a[:, -1 - t, 0] * (t / r)
    alpha = a / 255.0
    region = comp[y0:y0 + cw, x0:x0 + cw].astype(np.float32)
    comp[y0:y0 + cw, x0:x0 + cw] = (crop_arr * alpha + region * (1 - alpha))
    return np.clip(comp, 0, 255).astype(np.uint8)


def default_backgrounds() -> dict[str, np.ndarray]:
    """Flat fallback backgrounds (water / land) when no CUB-200 is present.

    Enough to demonstrate the *pipeline*; real Waterbirds uses actual scene photos.
    """
    out = {}
    for name, rgb in _FALLBACK_BGS.items():
        arr = np.zeros((256, 256, 3), dtype=np.uint8)
        arr[:, :, :] = rgb
        # add mild gradient so it's not a pure flat field
        ramp = np.linspace(-20, 20, 256).astype(np.int16)
        for c in range(3):
            arr[:, :, c] = np.clip(arr[:, :, c].astype(np.int16) + ramp[None, :], 0, 255)
        out[name] = arr
    return out