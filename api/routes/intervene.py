"""Intervene endpoint — run causal occlusion intervention."""
from __future__ import annotations

import os
import traceback
import base64
import io

import numpy as np
import torch
from fastapi import APIRouter, HTTPException
from PIL import Image
from pydantic import BaseModel

from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor
from attentionlens.intervention import run_intervention
from api.serializers import serialize_intervention_result

router = APIRouter()

DEVICE_NAME = os.environ.get("ATTENTIONLENS_DEVICE", "cpu")
DEVICE = torch.device(
    DEVICE_NAME
    if (DEVICE_NAME == "cpu" or (DEVICE_NAME == "cuda" and torch.cuda.is_available()))
    else "cpu"
)

_MODELS: dict[str, object] = {}


def _get_model(model_id: str):
    if model_id not in _MODELS:
        if model_id == "resnet50":
            _MODELS[model_id] = ResNetExtractor(device=DEVICE)
        elif model_id == "vit_b16":
            _MODELS[model_id] = VitExtractor(device=DEVICE)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model_id: {model_id}")
    return _MODELS[model_id]


def _load_image_from_b64(image_b64: str) -> torch.Tensor:
    """Load image from base64 → normalized tensor."""
    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(
        IMAGENET_STD, dtype=np.float32
    )
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
    return t


class Region(BaseModel):
    x: int
    y: int
    w: int
    h: int


class InterveneRequest(BaseModel):
    image_b64: str
    model_id: str
    regions: list[Region]
    strategy: str = "zero"


@router.post("/intervene")
async def intervene(req: InterveneRequest):
    """Run causal occlusion intervention on an image."""
    try:
        x = _load_image_from_b64(req.image_b64)
        ext = _get_model(req.model_id)

        regions = [(r.x, r.y, r.w, r.h) for r in req.regions]
        results = run_intervention(
            ext.model,
            x,
            regions,
            strategy=req.strategy,
            class_names=getattr(ext, "imagenet_labels", {}),
        )

        return {
            "results": [serialize_intervention_result(r) for r in results],
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Intervention failed: {str(e)}")
