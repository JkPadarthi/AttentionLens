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

## Status (2026-10-11)

- **M1–M6 shipped**: schema + ResNet-50 extractor + ViT extractor (attention rollout +
  gradient-weighted AxG), metrics, intervention loop, Gradio UI, screening engine.
- **21/21 tests pass** · `experiments/m2_demo.py` proves dual-view on a real image
  (ResNet 8 maps, ViT 25 maps).
- **M7 planted-bias experiment works end-to-end**: model trained to 100% acc on a
  biased set; the screener flagged the exact planted correlation (background reliance).
- **M8 ObjectNet-style check** runner included.
- GPU runs (jengas / RTX 5070) via `docker/` image.

## Quickstart (CPU)

```bash
cd AttentionLens
python3 -m venv .venv && . .venv/bin/activate     # or D:\GIT\AttentionLens + .venv\Scripts\activate
pip install -e .
pip install torch torchvision captum timm gradio pytest
python -m pytest tests/ -v                          # all green
python experiments/m2_demo.py experiments/sample.jpg experiments/out_m2
```

## New React Frontend (Recommended)

A modern React + TypeScript frontend is now available with a FastAPI backend. See [FRONTEND.md](FRONTEND.md) for setup instructions.

**Quick start:**

```bash
# Terminal 1 - Backend
pip install -e .
uvicorn api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

**Features:**
- Modern UI with Tailwind CSS and shadcn/ui components
- Interactive attention map browser with layer-by-layer navigation
- Click-to-mask intervention canvas
- Real-time prediction updates
- Dark mode support

## GPU (Blackwell / RTX 5070)

```bash
# on the GPU box, from docker/
docker build --no-cache -t attentionlens-gpu .      # pulls torch 2.11.0+cu128
docker run --rm --gpus all -v "$PWD":/app -w /app \
  attentionlens-gpu python experiments/gpu_m7_run.py --device cuda
```

## Tech Stack

Python 3.11/3.12 · PyTorch (2.14 CPU / 2.11+cu128 GPU) · torchvision · Captum · timm ·
Gradio · CUB-200 / ObjectNet · **React + TypeScript + Tailwind CSS** (frontend) · **FastAPI** (backend)

## Docs

- [PROJECT.md](PROJECT.md) — vision & architecture
- [DECISIONS.md](DECISIONS.md) — key decisions & reasoning
- [ROADMAP.md](ROADMAP.md) — phased delivery
- [STATUS.md](STATUS.md) — current state
- [docs/design.md](docs/design.md) — full design document