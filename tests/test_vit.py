# tests/test_vit.py
import pytest
import numpy as np
import torch

torch = pytest.importorskip("torch")
from attentionlens.extractors.vit import (  # noqa: E402
    attention_rollout_maps,
    class_conditioned_rollout_maps,
)
from attentionlens.extractors.vit_extractor import VitExtractor  # noqa: E402


def _fake_vit():
    """Minimal ViT-shaped module (patch_embed + 2 attention blocks + head)."""
    class PatchEmbed(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = torch.nn.Conv2d(3, 4, kernel_size=4, stride=4)
            self.num_patches = 4  # 2x2 grid for a 8x8 input
            self.patch_size = 4
        def forward(self, x):
            return self.proj(x).flatten(2).transpose(1, 2)

    class Attention(torch.nn.Module):
        def __init__(self, dim, heads):
            super().__init__()
            self.num_heads = heads
            self.qkv = torch.nn.Linear(dim, 3 * dim)
            self.proj = torch.nn.Identity()
            self.scale = dim**-0.5
        def forward(self, x):
            return x

    class Block(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.norm1 = torch.nn.Identity()
            self.attn = Attention(4, 2)
            self.norm2 = torch.nn.Identity()
            self.mlp = torch.nn.Linear(4, 4)
        def forward(self, x):
            x = x + self.attn(self.norm1(x))      # residual attention path
            x = x + self.mlp(self.norm2(x))       # residual MLP path
            return x

    class ViT(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.patch_embed = PatchEmbed()
            self.blocks = torch.nn.ModuleList([Block(), Block()])
            self.norm = torch.nn.Identity()
            self.head = torch.nn.Linear(4, 3)
            self.patch_size = 4
        def forward(self, x):
            x = self.patch_embed(x)
            for b in self.blocks:
                x = b(x)
            x = x.mean(dim=1)   # pool CLS/patch tokens -> [B,4]
            return self.head(x)

    m = ViT()
    return m


def test_attention_rollout_shapes_view():
    model = _fake_vit()
    x = torch.randn(1, 3, 8, 8)
    # wait — PatchEmbed with stride 4 on 8x8 gives 2x2 patches; blocks expect N tokens.
    maps = attention_rollout_maps(model, ["blocks.0", "blocks.1"], x,
                                  target_size=(8, 8), block_attn_names=["blocks.0.attn", "blocks.1.attn"])
    # 2 blocks → 2 partial maps + 1 full "rollout" map
    assert len(maps) == 3
    for m_map in maps:
        assert m_map.view == "native"
        assert m_map.arch == "vit"
        assert m_map.map.shape == (8, 8)
        assert 0.0 <= m_map.map.min() <= 1.0 + 1e-6


def test_class_conditioned_view():
    model = _fake_vit()
    x = torch.randn(1, 3, 8, 8)
    maps = class_conditioned_rollout_maps(model, ["blocks.0", "blocks.1"], x,
                                          target_class=2, target_size=(8, 8),
                                          block_attn_names=["blocks.0.attn", "blocks.1.attn"])
    # one map per block
    assert len(maps) == 2
    for m in maps:
        assert m.view == "class_conditioned"
        assert m.arch == "vit"
        assert m.model_class == "class_2"
        assert m.map.shape == (8, 8)
        assert m.map.min() >= 0.0  # ReLU'd


def test_vitextractor_inspect_modelinspection():
    model = _fake_vit()
    ext = VitExtractor(model=model, model_id="fake_vit", layer_names=["blocks.0", "blocks.1"])
    x = torch.randn(1, 3, 8, 8)
    insp = ext.inspect(x, image_id="test")
    assert insp.model_id == "fake_vit"
    assert insp.pred_label != ""
    # 2 blocks -> 3 native (2 partial + full) + 2 class_conditioned
    assert len(insp.layers) == 5
    assert any(l.view == "class_conditioned" for l in insp.layers)