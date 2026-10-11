# Project: AttentionLens

An interactive explainability and debugging framework for vision models. AttentionLens
reads what CNNs and ViTs actually attend to — layer by layer — and turns that signal
into evidence: per-layer maps, quality metrics, spurious-correlation flags, and causal
intervention results.

## Vision

Make attention mechanisms transparent and debuggable. A researcher should be able to
load a model, pick an image, and get a *verdict* — not just a heatmap:

- Which layers detect edges, textures, object parts?
- Is the model using the object or the background? (quantified)
- Why did this image get misclassified? (shown, not guessed)
- How does ResNet's attention differ from ViT's? (comparable numbers)

## Architecture

```
Input image → Extract maps (hooks / Captum) → Visualize (unified schema)
    ↑                                              ↓
    └── Re-run with intervention ←── Measure change ──┘
```

### Unified dual-view abstraction

Every layer produces two maps behind one schema (`LayerMap`):

- **native** — the mechanism's own signal (ViT attention rollout; CNN channel
  activations) — *"where does the mechanism focus?"*
- **class_conditioned** — decision evidence (Grad-CAM; class-weighted ViT
  attribution) — *"where is the evidence for this class?"*

This solves the CNN⇄ViT asymmetry honestly: raw ViT attention is class-agnostic while
Grad-CAM is class-specific — comparing them naively would be meaningless.

### Screening engine

Batch extraction → per-image metrics (object relevance share, part alignment, focus
entropy, background/object sensitivity) → class-level aggregation → **evidence-backed
verdicts**: class bias flags, layer-role profiles, failure diagnoses.

## Validation

1. **Planted-bias experiment (Waterbirds-style)** — synthetic background/species
   correlation on CUB-200; the screener must catch the exact shortcut we planted.
2. **ObjectNet natural-bias check** — standard pretrained model on objects in bizarre
   contexts; the screener must flag context reliance.

Together: catches what we know + catches what's real.

## Tech Stack

Python 3.12 · PyTorch · torchvision · Captum · timm · Gradio · CUB-200 / ObjectNet /
ImageNet subset. Dev on Arjun (Windows); heavy screening runs on rented GPU or Jenga.
