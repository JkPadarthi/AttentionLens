# AttentionLens

**An Interactive Explainability and Debugging Framework for Vision Models.**

AttentionLens makes attention mechanisms transparent and debuggable. It reads what a
model actually looks at — layer by layer — and turns it into evidence: per-layer
attention maps, attention quality metrics, spurious-correlation flags, and causal
intervention tools.

> "Grad-CAM shows you a heatmap. AttentionLens tells you the model cheated, and shows
> you the proof."

## Why

CNNs/ViTs hit high accuracy, but we don't know what they're looking at. Grad-CAM shows
*where* — not *why*. AttentionLens exposes the model's internal reasoning:

- **Layer-by-layer attention** — "layer 1 looks at edges, layer 5 at textures, layer 10 at parts"
- **Spurious correlation detection** — "model classifies 'wolf' on snow, not wolf"
- **Attention quality metrics** — "focuses on the object 80% of the time"
- **Architecture comparison** — ResNet localized vs ViT distributed, as numbers
- **Failure debugging** — "misclassified because attention hit the background"
- **Intervention** — mask a region, watch the prediction change (causal proof)

## Novelty

A tool in the SHAP/Captum/Lucid tradition, not a new XAI method:

1. **Unified dual-view abstraction** — native attention + class-conditioned relevance
   behind one schema, for both CNN and ViT (fair apples-to-apples comparison).
2. **Automated screening verdicts** — class-level bias flags, layer-role profiles, and
   evidence-backed reports (no other tool ships this).
3. **Causal debugging loop** — intervene → measure → verdict.

## Quickstart

```bash
cd D:\GIT\AttentionLens
.venv\Scripts\activate
pip install -e .
# coming in M1+: python -m attentionlens inspect --model resnet50 --image bird.jpg
```

## Tech Stack

Python 3.12 · PyTorch · torchvision · Captum · timm · Gradio · CUB-200 / ObjectNet

## Docs

- [PROJECT.md](PROJECT.md) — vision & architecture
- [DECISIONS.md](DECISIONS.md) — key decisions & reasoning
- [ROADMAP.md](ROADMAP.md) — phased delivery
- [STATUS.md](STATUS.md) — current state
- [docs/design.md](docs/design.md) — full design document
