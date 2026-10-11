# attentionlens/extractors/vit.py
"""ViT attention extraction (M2).

Native view   -> attention rollout (Abnar & Zuidema 2020), class-agnostic.
                 Per-block partial rollout gives the "layer by layer" story.
Class-cond.   -> gradient-weighted rollout: weight the (rolled-up) patch
                 attention by the gradient of the target-class logit w.r.t.
                 that map. A faithful, in-graph class-conditioned map without
                 swapping in a second method (decision per design §6 / DECISIONS #6).
"""
from __future__ import annotations

import functools
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F

from attentionlens.schema import LayerMap
from attentionlens.extractors.cnn import _normalize01, _get_submodule

# Default ViT-B/16 (timm) block hook names: block N attention module.
DEFAULT_VIT_BLOCK_ATTN = [f"blocks.{i}.attn" for i in range(12)]
DEFAULT_VIT_BLOCK_NAMES = [f"blocks.{i}" for i in range(12)]


def _wrap_attention(attn: torch.nn.Module, store: dict, key: int) -> None:
    """Replace attn.forward so softmax attention weights are captured in-graph.

    Keeps the wrapper faithful to timm's Attention layout (qkv -> scaled dot-prod
    -> softmax -> value projection -> proj) and disables fused/flash paths so the
    manual math actually runs. Stored weights are left attached to autograd so a
    class-conditional gradient can flow back through them.
    """
    # Coerce to the manual (non-fused) path regardless of timm version/revision.
    for flag in ("fused_attn", "fast_attn"):
        if hasattr(attn, flag):
            try:
                setattr(attn, flag, False)
            except Exception:  # property without setter in some timm builds
                pass
    orig_fwd = attn.forward

    @functools.wraps(orig_fwd)
    def wrapped(x: torch.Tensor, attn_mask=None, is_causal=None, **kw) -> torch.Tensor:
        B, N, C = x.shape
        qkv = attn.qkv(x).reshape(B, N, 3, attn.num_heads, C // attn.num_heads)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # [3,B,H,N,d]
        q, k, v = qkv[0], qkv[1], qkv[2]
        scale = getattr(attn, "scale", q.shape[-1] ** -0.5)
        A = (q @ k.transpose(-2, -1)) * scale
        if attn_mask is not None:
            if attn_mask.dim() == 2:
                A = A + attn_mask[None, None, :, :]
            else:
                A = A + attn_mask
        if is_causal:
            N_ = A.shape[-1]
            m = torch.triu(torch.ones(N_, N_, dtype=torch.bool, device=A.device), diagonal=1)
            A = A.masked_fill(m[None, None], float("-inf"))
        A = A.softmax(dim=-1)                        # [B,H,N,N], in-graph
        store[key] = A
        out = (A @ v).transpose(1, 2).reshape(B, N, C)
        out = getattr(attn, "proj", None)(out) if attn.proj is not None else out
        if getattr(attn, "gamma", None) is not None:
            out = out * attn.gamma
        return out

    attn.forward = wrapped  # type: ignore[method-assign]


def _rollout_from_attention(A_blocks: list[torch.Tensor], with_cls: bool = True,
                            alpha: float = 0.5) -> torch.Tensor:
    """Abnar-Zuidema rollout over per-block mean attention matrices.

    A_blocks: [A_i] each [B,H,N,N] (already softmaxed). Returns [B,N,N] rollout.
    Adds the identity as residual (alpha) to fight attention bootstrap collapse.
    """
    roll = None
    for A in A_blocks:
        W = A.mean(dim=1)                            # [B,N,N] mean over heads
        I = torch.eye(W.shape[-1], device=W.device).unsqueeze(0)
        W = alpha * I + (1 - alpha) * W              # residual (identity + attn)
        W = W / (W.sum(dim=-1, keepdim=True) + 1e-9)  # row-normalize
        roll = W if roll is None else roll @ W
    # Reposition the CLS slot: rollout conventions keep the source token as the
    # query; for a source-CLS map we take the cls row (all target patches).
    if with_cls:
        return roll[:, 0:1, :]
    return roll


def _upsample_to(arr: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    """Upsample a grid-resolution map to input resolution via bilinear."""
    t = torch.from_numpy(arr.astype(np.float32)).unsqueeze(0).unsqueeze(0)
    up = F.interpolate(t, size=target_size, mode="bilinear", align_corners=False)
    return _normalize01(up.squeeze(0).squeeze(0).numpy())


def attention_rollout_maps(
    model: torch.nn.Module,
    layer_names: list[str] | None,
    input_tensor: torch.Tensor,
    target_size: tuple[int, int],
    model_class: str = "argmax",
    device: torch.device = torch.device("cpu"),
    with_cls: bool = True,
    block_attn_names: list[str] | None = None,
) -> list[LayerMap]:
    """Native-view ViT maps: a partial-rollout LayerMap per block + a full map."""
    num_blocks = len(layer_names or DEFAULT_VIT_BLOCK_NAMES)
    attn_names = block_attn_names or DEFAULT_VIT_BLOCK_ATTN[:num_blocks]

    captured: dict[int, torch.Tensor] = {}
    orig_fwds: dict[int, object] = {}
    for i, name in enumerate(attn_names):
        attn = _get_submodule(model, name)
        orig_fwds[i] = attn.forward
        _wrap_attention(attn, captured, i)

    model.eval()
    with torch.no_grad():
        model(input_tensor.to(device))
    for i, name in enumerate(attn_names):
        _get_submodule(model, name).forward = orig_fwds[i]  # type: ignore[method-assign]

    h_grid = int(input_tensor.shape[-2] / int(getattr(model, "patch_size", 16)))
    w_grid = int(input_tensor.shape[-1] / int(getattr(model, "patch_size", 16)))
    num_patch = int(getattr(model.patch_embed, "num_patches", h_grid * w_grid))

    A_blocks = [captured[i] for i in range(num_blocks)]

    partial: list[LayerMap] = []
    acc = None
    for i in range(num_blocks):
        W = A_blocks[i].mean(dim=1)
        I = torch.eye(W.shape[-1], device=W.device).unsqueeze(0)
        W = 0.5 * I + 0.5 * W
        W = W / (W.sum(dim=-1, keepdim=True) + 1e-9)
        acc = W if acc is None else acc @ W
        row = acc[:, 0, :] if with_cls else acc[:, 0, :]
        grid = row[0, :num_patch].reshape(h_grid, w_grid).detach().cpu().numpy()
        partial.append(LayerMap(
            layer_name=(layer_names or DEFAULT_VIT_BLOCK_NAMES)[i],
            arch="vit", view="native", model_class=model_class,
            map=_upsample_to(grid, target_size),
            metadata={"method": "attention_rollout", "partial_through_block": i},
        ))

    # Full rollout map
    row = acc[:, 0, :] if with_cls else acc[:, 0, :]
    grid = row[0, :num_patch].reshape(h_grid, w_grid).detach().cpu().numpy()
    partial.append(LayerMap(
        layer_name="rollout", arch="vit", view="native", model_class=model_class,
        map=_upsample_to(grid, target_size),
        metadata={"method": "attention_rollout", "partial_through_block": num_blocks - 1},
    ))
    return partial


def class_conditioned_rollout_maps(
    model: torch.nn.Module,
    layer_names: list[str] | None,
    input_tensor: torch.Tensor,
    target_class: int | None,
    target_size: tuple[int, int],
    device: torch.device = torch.device("cpu"),
    class_names: Optional[dict[int, str]] = None,
    block_attn_names: list[str] | None = None,
) -> list[LayerMap]:
    """Class-conditioned ViT maps: gradient-weighted attention (attention x grad).

    For each block we take the gradient of the *target-class logit* w.r.t. that
    block's attention matrix (computed in-graph, so it is a true ancestor of the
    logit), multiply it by the raw attention, ReLU and extract the CLS row. This
    is the ViT analogue of Grad-CAM — per-block, class-specific, faithful, and it
    produces one LayerMap per block (matching the CNN extractor's per-layer story).
    """
    num_blocks = len(layer_names or DEFAULT_VIT_BLOCK_NAMES)
    attn_names = block_attn_names or DEFAULT_VIT_BLOCK_ATTN[:num_blocks]

    captured: dict[int, torch.Tensor] = {}
    orig_fwds: dict[int, object] = {}
    for i, name in enumerate(attn_names):
        attn = _get_submodule(model, name)
        orig_fwds[i] = attn.forward
        _wrap_attention(attn, captured, i)

    model.eval()
    # NOTE: no no_grad — we need autograd to reach the attention tensors.
    x = input_tensor.to(device)
    logits = model(x)
    for i, name in enumerate(attn_names):
        _get_submodule(model, name).forward = orig_fwds[i]  # type: ignore[method-assign]

    if target_class is None:
        target_class = int(logits.argmax(dim=1).item())

    h_grid = int(x.shape[-2] / int(getattr(model, "patch_size", 16)))
    w_grid = int(x.shape[-1] / int(getattr(model, "patch_size", 16)))
    num_patch = int(getattr(model.patch_embed, "num_patches", h_grid * w_grid))
    label = class_names[target_class] if class_names else f"class_{target_class}"

    maps: list[LayerMap] = []
    for i in range(num_blocks):
        A = captured[i]                              # [B,H,N,N], in-graph
        # derivative of the target logit w.r.t. this block's RAW attention.
        # A is a true ancestor (softmax -> @ v -> ... -> logit), so this is real.
        grad, = torch.autograd.grad(logits[:, target_class].sum(), A,
                                    retain_graph=True, create_graph=False,
                                    allow_unused=True)
        if grad is None:
            continue  # A not reachable (shouldn't happen for a real ViT)
        # AxG: ReLU(raw attention * gradient), then source=CLS row -> patches
        axg = torch.relu(A * 1.0) * torch.relu(grad)  # [B,H,N,N]
        row = axg[:, :, 0, :].sum(dim=1)             # sum over heads, CLS source
        grid = row[0, :num_patch].reshape(h_grid, w_grid).detach().cpu().numpy()
        maps.append(LayerMap(
            layer_name=(layer_names or DEFAULT_VIT_BLOCK_NAMES)[i],
            arch="vit", view="class_conditioned", model_class=label,
            map=_upsample_to(grid, target_size),
            metadata={"method": "gradient_weighted_attention", "target_class": target_class},
        ))
    if not maps:
        raise RuntimeError("No class-conditioned ViT maps: attention not reachable "
                           "from the target logit. Check model arch (Block must call "
                           "self.attn inside forward).")
    return maps