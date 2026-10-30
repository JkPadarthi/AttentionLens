"""Models endpoint — list available models."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/models")
async def list_models():
    """Return available models with metadata."""
    return [
        {
            "id": "resnet50",
            "name": "ResNet-50",
            "arch": "cnn",
            "description": "Convolutional neural network with 50 layers",
            "layers": ["layer1", "layer2", "layer3", "layer4"],
        },
        {
            "id": "vit_b16",
            "name": "ViT-B/16",
            "arch": "vit",
            "description": "Vision Transformer with 12 layers",
            "layers": [f"block{i}" for i in range(12)],
        },
    ]
