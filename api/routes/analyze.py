"""Analyze endpoint — run model inspection on an image."""
from __future__ import annotations

import os
import traceback
import base64
import io

import numpy as np
import torch
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from PIL import Image

from attentionlens.preprocess import IMAGENET_MEAN, IMAGENET_STD, tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor
from attentionlens.metrics import all_metrics
from api.serializers import serialize_inspection, numpy_to_base64_png

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


def _load_image(image_bytes: bytes) -> torch.Tensor:
    """Load image from bytes → normalized tensor."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(
        IMAGENET_STD, dtype=np.float32
    )
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
    return t


@router.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    model_id: str = Form(...),
):
    """Run model inspection on an uploaded image."""
    try:
        image_bytes = await image.read()
        x = _load_image(image_bytes)
        ext = _get_model(model_id)
        insp = ext.inspect(x, image_id="upload")

        # Compute metrics for each layer map
        for m in insp.layers:
            all_metrics(m)

        # Get base image as base64
        base_img = tensor_to_image(x)
        base_b64 = numpy_to_base64_png(base_img)

        # Get top-5 predictions
        with torch.no_grad():
            logits = ext.model(x)
            probs = torch.nn.functional.softmax(logits, dim=1)[0]
            top5_probs, top5_idxs = probs.topk(5)
        
        top5 = []
        for prob, idx in zip(top5_probs, top5_idxs):
            label = ext.imagenet_labels.get(int(idx), f"class_{int(idx)}")
            top5.append({"label": label, "probability": float(prob)})

        result = serialize_inspection(insp)
        result["base_image_b64"] = base_b64
        result["top5"] = top5
        result["confidence"] = float(top5_probs[0])

        return result

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
