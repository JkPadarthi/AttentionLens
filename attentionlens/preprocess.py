# attentionlens/preprocess.py
"""Image loading + tensor conversion helpers."""
from __future__ import annotations

import numpy as np
import torch
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_image_tensor(path: str, size: int = 224, device: torch.device = torch.device("cpu")) -> torch.Tensor:
    """Load image → normalized 4D tensor [1,3,H,W] on `device`."""
    img = Image.open(path).convert("RGB").resize((size, size))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)
    return t


def tensor_to_image(t: torch.Tensor) -> np.ndarray:
    """Reverse normalization → uint8 H×W×3 RGB array (for viz)."""
    a = t.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
    a = (a * np.array(IMAGENET_STD, dtype=np.float32)) + np.array(IMAGENET_MEAN, dtype=np.float32)
    a = np.clip(a * 255.0, 0, 255).astype(np.uint8)
    return a
