# attentionlens/extractors/resnet.py
"""ResNet-50 inspection orchestrator (M1)."""
from __future__ import annotations

import torch
from torchvision.models import resnet50, ResNet50_Weights

from attentionlens.extractors.cnn import gradcam_maps, native_activation_maps
from attentionlens.schema import ModelInspection

# Last conv of each ResNet bottleneck block
RESNET_BLOCK_LAYERS = ["layer1.2.conv3", "layer2.3.conv3", "layer3.5.conv3", "layer4.2.conv3"]


class ResNetExtractor:
    def __init__(
        self,
        model: torch.nn.Module | None = None,
        layer_names: list[str] | None = None,
        arch: str = "cnn",
        device: torch.device = torch.device("cpu"),
        imagenet_labels: dict[int, str] | None = None,
    ):
        self.device = device
        self.model = model if model is not None else resnet50(weights=ResNet50_Weights.IMAGENET1K_V2).to(device)
        self.layer_names = layer_names or RESNET_BLOCK_LAYERS
        if imagenet_labels is not None:
            self.imagenet_labels = imagenet_labels
        else:
            meta = ResNet50_Weights.IMAGENET1K_V2.meta
            cats = meta.get("categories") if isinstance(meta, dict) else getattr(meta, "categories", None)
            self.imagenet_labels = dict(enumerate(cats)) if cats else {}

    def predict(self, input_tensor: torch.Tensor) -> tuple[str, int]:
        with torch.no_grad():
            logits = self.model(input_tensor.to(self.device))
            idx = int(logits.argmax(dim=1).item())
        return self.imagenet_labels.get(idx, f"class_{idx}"), idx

    def inspect(
        self,
        input_tensor: torch.Tensor,
        image_id: str = "",
        true_label: str = "",
        target_class: int | None = None,
    ) -> ModelInspection:
        pred_label, pred_idx = self.predict(input_tensor)
        h, w = input_tensor.shape[-2:]
        native = native_activation_maps(
            self.model, self.layer_names, input_tensor,
            target_size=(h, w), model_class=pred_label, device=self.device,
        )
        cc = gradcam_maps(
            self.model, self.layer_names, input_tensor,
            target_class=target_class or pred_idx, target_size=(h, w),
            device=self.device, class_names=self.imagenet_labels,
        )
        return ModelInspection(
            model_id="resnet50", image_id=image_id,
            true_label=true_label, pred_label=pred_label,
            layers=native + cc,
        )
