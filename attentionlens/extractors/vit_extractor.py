# attentionlens/extractors/vit_extractor.py
"""ViT inspection orchestrator (M2) — mirrors ResNetExtractor's interface."""
from __future__ import annotations

import torch

from attentionlens.schema import ModelInspection
from attentionlens.extractors.vit import (
    DEFAULT_VIT_BLOCK_NAMES,
    DEFAULT_VIT_BLOCK_ATTN,
    attention_rollout_maps,
    class_conditioned_rollout_maps,
)

DEFAULT_VIT_MODEL = "vit_base_patch16_224"


class VitExtractor:
    def __init__(
        self,
        model: torch.nn.Module | None = None,
        model_id: str = DEFAULT_VIT_MODEL,
        layer_names: list[str] | None = None,
        device: torch.device = torch.device("cpu"),
        imagenet_labels: dict[int, str] | None = None,
    ):
        self.device = device
        self.model_id = model_id
        if model is None:
            import timm

            model = timm.create_model(model_id, pretrained=True).to(device)
            if imagenet_labels is None:
                imagenet_labels = self._imagenet_labels(model)
        self.model = model
        self.layer_names = layer_names or DEFAULT_VIT_BLOCK_NAMES
        self.block_attn_names = DEFAULT_VIT_BLOCK_ATTN[: len(self.layer_names)]
        self.imagenet_labels = imagenet_labels or {}

    @staticmethod
    def _imagenet_labels(model: torch.nn.Module) -> dict[int, str]:
        """Resolve ImageNet-1k labels for a timm ViT where possible."""
        labels: dict[int, str] = {}
        # timm's pretrained_cfg may carry the label list.
        try:
            cfg = model.default_cfg
            if cfg.get("labels"):
                labels = {i: str(l) for i, l in enumerate(cfg["labels"])}
        except Exception:
            pass
        if not labels:
            # fall back to torchvision's ImageNet categories (shared, stable).
            try:
                from torchvision.models import ResNet50_Weights

                meta = ResNet50_Weights.IMAGENET1K_V2.meta
                cats = meta.get("categories") if isinstance(meta, dict) else None
                labels = dict(enumerate(cats)) if cats else {}
            except Exception:
                labels = {}
        return labels

    def predict(self, input_tensor: torch.Tensor) -> tuple[str, int]:
        with torch.no_grad():
            logits = self.model(input_tensor.to(self.device))
            idx = int(logits.argmax(dim=1).item())
        label = self.imagenet_labels.get(idx, f"class_{idx}")
        return label, idx

    def inspect(
        self,
        input_tensor: torch.Tensor,
        image_id: str = "",
        true_label: str = "",
        target_class: int | None = None,
    ) -> ModelInspection:
        pred_label, pred_idx = self.predict(input_tensor)
        h, w = input_tensor.shape[-2:]
        native = attention_rollout_maps(
            self.model, self.layer_names, input_tensor, target_size=(h, w),
            model_class=pred_label, device=self.device,
            block_attn_names=self.block_attn_names,
        )
        cc = class_conditioned_rollout_maps(
            self.model, self.layer_names, input_tensor,
            target_class=target_class or pred_idx, target_size=(h, w),
            device=self.device, class_names=self.imagenet_labels,
            block_attn_names=self.block_attn_names,
        )
        return ModelInspection(
            model_id=self.model_id, image_id=image_id,
            true_label=true_label, pred_label=pred_label,
            layers=native + cc,
        )