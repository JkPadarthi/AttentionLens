# AttentionLens — Design Document

**An Interactive Explainability and Debugging Framework for Vision Models**

> Status: Design (v0.1) · Date: 2026-08-17 · Author: Jaswanth Krishna Padarthi (with Hermes)

---

## 1. Problem Statement

CNNs and ViTs achieve high accuracy, but their decision-making is opaque. Grad-CAM
and similar tools show *where* a model looks, but not *why* — and they cannot tell us
whether the model is using genuine object features or spurious shortcuts (e.g., a
"wolf" classifier that actually keys on snow, a bird classifier that keys on branches).

Researchers and engineers need:
1. Visibility into **what each layer attends to** (edges → textures → parts).
2. **Automated detection of spurious correlations** — flags, not just heatmaps.
3. **Quantified attention quality** — numbers, not vibes.
4. **Apples-to-apples architecture comparison** (ResNet vs ViT).
5. **Failure debugging** — why a misclassification happened, with evidence.
6. **Causal intervention** — mask regions, observe prediction change.

## 2. Core Idea

AttentionLens is a **tool** (in the tradition of SHAP / Captum / Lucid), not a new XAI
method. Its contribution is engineering:

- A **unified CNN⇄ViT abstraction**: both architectures speak the same schema, so
  metrics, visualization, and screening work identically across them.
- An **automated bias-screening engine**: turns heatmaps into evidence-backed verdicts.

### 2.1 The core loop

```
Input image → Extract maps (hooks / Captum) → Visualize (unified schema)
    ↑                                              ↓
    └── Re-run with intervention ←── Measure change ──┘
```

## 3. Novelty & Positioning

### 3.1 What exists (and why this is not a method paper)

| Capability | Existing work |
|---|---|
| Per-layer attention viz | Captum, torchcam, attention rollout, HF/Gradio demos |
| Grad-CAM attribution | Selvaraju et al. 2017 + variants |
| Spurious correlation detection | Right for the Right Reasons (Ross), Waterbirds, causal-intervention papers |
| Attention quality metrics | Pointing Game, IoU-based saliency eval |
| Occlusion/masking | RISE, occlusion sensitivity, LIME superpixels |

The field is saturated on *methods*. AttentionLens does not invent a new attribution
algorithm; it builds a **unified instrument** over existing ones and adds automated
verdict generation — the tool-layer gap.

### 3.2 Claimed contributions

1. **Unified dual-view abstraction** — native attention + class-conditioned relevance
   maps behind one schema, for both CNN and ViT (fair, honest comparison).
2. **Automated screening reports** — class-level bias flags, layer-role profiles, and
   evidence-backed verdicts (no other tool ships this).
3. **Causal debugging workflow** — intervene → measure → verdict, as a first-class loop.

### 3.3 Positioning statement

> "Grad-CAM shows you a heatmap. AttentionLens tells you the model cheated, and shows
> you the proof."

## 4. The Unified Abstraction (Dual-View)

### 4.1 The asymmetry problem

ViT attention ≠ CNN attention:

| | ViT attention | CNN attribution (Grad-CAM) |
|---|---|---|
| Measures | Info flow between patches (class-agnostic) | Class-specific relevance |
| Native? | Yes — explicit matrices | No — gradient-weighted proxy |
| Class-conditioned? | No (raw) | Yes |

Naively comparing them yields meaningless metrics. **Dual-view solves this:**

- **Native view** — the mechanism's own signal: ViT attention rollout; CNN
  channel-weighted activation maps. Answers: *"where does the mechanism focus?"*
- **Class-conditioned view** — decision evidence: Grad-CAM for CNN; class-weighted
  attention rollout / LRP / token attribution (Captum) for ViT. Answers: *"where is
  the evidence for this class?"*

### 4.2 Unified map schema

```python
@dataclass
class LayerMap:
    layer_name: str
    arch: str            # "vit" | "cnn"
    view: str            # "native" | "class_conditioned"
    model_class: str     # predicted/argmax class
    map: np.ndarray      # H×W normalized [0,1] at input resolution
    head_or_channel: int | None  # for per-head / per-channel breakdowns
    metadata: dict       # entropy, locality, part-overlap... (see §5)

@dataclass
class ModelInspection:
    model_id: str
    image_id: str
    true_label: str
    pred_label: str
    layers: list[LayerMap]       # ordered by depth
    intervention_results: list[InterventionResult]
```

Everything downstream — visualizer, metrics, screener — consumes only this schema.

## 5. Metrics (Attention Quality)

Computed per image per layer, using CUB-200 ground-truth (bbox + part keypoints):

| Metric | Definition | Question answered |
|---|---|---|
| Object relevance share | Σ relevance inside object bbox / Σ total | % of focus on the object |
| Part alignment | Relevance at part keypoints (head, wing...) | Which parts drive the model? |
| Focus entropy | Shannon entropy of normalized map | Localized vs distributed (ResNet vs ViT number) |
| Background sensitivity | Prediction flip when background masked | Is the model using background? |
| Object sensitivity | Prediction flip when object masked | Is the model using the object? |

## 6. Automated Screening Engine (Verdicts)

### 6.1 Pipeline

1. **Batch extraction** — run model over dataset; capture dual-view maps via unified schema.
2. **Per-image metrics** — object relevance share, part alignment, entropy, sensitivities.
3. **Aggregation** — class-level stats + layer-level profiles.
4. **Verdict generation** — flags with thresholds; every flag links to evidence images/maps.

### 6.2 Verdict types

- **Class bias flag** — ⚠ "For class X, background relevance exceeds object relevance on
  N% of images → suspected spurious correlation."
- **Layer-role profile** — "Layers 1–3: edge/texture. Layers 8–11: object parts."
- **Architecture comparison report** — "ResNet focus localized (entropy 2.1); ViT
  distributed (entropy 3.8); both rely on head parts for class Y."
- **Failure diagnosis** — "Image 42 misclassified as Z because class-conditioned
  evidence concentrates on background region (see maps)."

## 7. Validation Experiments (both required for v1)

### 7.1 Synthetic planted bias (Waterbirds-style)

1. Take CUB-200; composite birds onto backgrounds correlated with species
   (water birds → water; land birds → land).
2. Fine-tune a ViT (and optionally a ResNet) on the biased set.
3. Run AttentionLens on the biased model.
4. **Pass criteria:** screener flags the exact planted shortcut (background drives
   predictions for the correlated classes); metrics show background sensitivity ≫
   object sensitivity on those classes; layer profile locates where the shortcut
   enters.

### 7.2 ObjectNet natural-bias check

1. Run a standard ImageNet-pretrained model on ObjectNet (objects in bizarre contexts).
2. **Pass criteria:** screener flags classes where the model relies on context
   (e.g., background-heavy evidence on novel-context images); failure-diagnosis view
   explains a sample of misclassifications.

Together these prove: catches what we know (7.1) + catches what's real (7.2).

## 8. Tech Stack

| Piece | Choice | Notes |
|---|---|---|
| Models | PyTorch + torchvision + timm / HF transformers | ResNet-50, ViT-B/16, DINOv2 |
| Attribution | Captum | Grad-CAM, integrated gradients, layer attribution |
| Attention extraction | Custom forward hooks | Read attention matrices; attention rollout |
| UI | Gradio | Sliders, click-to-mask, live re-run; Streamlit fallback |
| Datasets | CUB-200 (primary), ObjectNet, ImageNet subset | CUB-200 provides ground truth for metrics |
| Env | Python 3.13, uv/venv, pyproject.toml | PEP 668-safe |

## 9. Project Structure (target)

```
AttentionLens/
├── docs/design.md            # this doc
├── attentionlens/
│   ├── schema.py             # unified map schema (§4.2)
│   ├── extractors/
│   │   ├── vit.py            # hooks + attention rollout
│   │   └── cnn.py            # Grad-CAM + channel activations
│   ├── metrics.py            # §5 metrics
│   ├── screening.py          # §6 verdict engine
│   ├── intervention.py       # masking / occlusion
│   └── ui/
│       └── app.py            # Gradio app
├── experiments/
│   ├── planted_bias.py       # §7.1
│   └── objectnet_check.py    # §7.2
├── tests/
├── pyproject.toml
└── README.md
```

## 10. Milestones (v1)

1. **M1 — Schema + CNN extractor:** unified schema; Grad-CAM + channel activations on ResNet. *Verify: CUB-200 image → LayerMaps.*
2. **M2 — ViT extractor:** attention rollout + class-conditioned ViT maps (Captum). *Verify: same image → LayerMaps in same schema.*
3. **M3 — Metrics:** object relevance share, part alignment, entropy, sensitivities on CUB-200. *Verify: numbers sane on known cases.*
4. **M4 — Intervention loop:** mask/occlude → re-run → measure. *Verify: masking head flips bird predictions.*
5. **M5 — Gradio UI:** per-layer dual-view browser + click-to-mask. *Verify: end-to-end interactive session.*
6. **M6 — Screening engine:** aggregation + verdicts + evidence links. *Verify: flags on a known-biased model.*
7. **M7 — Planted-bias experiment (§7.1).** *Verify: screener catches planted shortcut.*
8. **M8 — ObjectNet check (§7.2) + README + final report.**

## 11. Risks & Open Questions

- **Fairness of cross-arch comparison** — dual-view mitigates; exact metric parity still
  needs care (head count, layer depth, resolution). Mitigation: compute at input
  resolution, normalize per-map.
- **CUB-200 part annotations** are per-image keypoints; alignment metric needs
  localization (max-relevance within part radius).
- **ViT class-conditioning method choice** — attention rollout vs LRP vs token
  attribution; decide by faithfulness check in M2.
- **ObjectNet download/processing cost** — ~3 GB; can defer download to GPU-rent phase.
- **Arjun compute** — keep v1 model zoo small (ResNet-50, ViT-B/16); full-dataset
  screening runs are GPU-rent/Jenga jobs. Design for portability (device-agnostic).

## 12. What This Is NOT (scope guardrails)

- Not a new attribution algorithm.
- Not a training framework (we fine-tune only for the planted-bias experiment).
- Not an NLP/LLM explainability tool (vision only in v1).
- Not a production-deployment tool (research/debugging instrument).
