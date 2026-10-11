# Roadmap

Phased delivery of AttentionLens. Each milestone builds on the previous one and ends
with a **verification step** — nothing is done until it's proven.

## M1 — Schema + CNN extractor
- Unified `LayerMap` / `ModelInspection` schema (`attentionlens/schema.py`)
- Grad-CAM + channel-weighted activations on ResNet-50 (Captum + hooks)
- *Verify:* CUB-200 image → `LayerMap`s in schema, sane maps

## M2 — ViT extractor
- Attention rollout (native) + class-conditioned ViT maps (Captum)
- Faithfulness check to pick class-conditioning method (rollout vs LRP vs token attr)
- *Verify:* same image → same schema, dual-view complete

## M3 — Metrics
- Object relevance share, part alignment, focus entropy, background/object sensitivity
- *Verify:* numbers sane on known cases (e.g., object-focused vs background-focused)

## M4 — Intervention loop
- Mask/occlude regions → re-run → measure prediction change
- *Verify:* masking the head flips bird predictions on CUB-200

## M5 — Gradio UI
- Per-layer dual-view browser + click-to-mask + live re-run
- *Verify:* end-to-end interactive session

## M6 — Screening engine
- Aggregation, class-level verdicts, evidence links, layer-role profiles
- *Verify:* flags fire on a known-biased model

## M7 — Planted-bias experiment (Waterbirds-style)
- Synthetic background/species correlation on CUB-200 → fine-tune ViT (+ResNet)
- *Verify:* screener flags the exact planted shortcut; background sensitivity ≫ object

## M8 — ObjectNet check + wrap-up
- ObjectNet natural-bias check on ImageNet-pretrained model
- README polish, final report, repo push
- *Verify:* screener flags context reliance; failure-diagnosis explains misclassifications

## Stretch (post-v1)
- More models (DINOv2, DeiT), more datasets (ImageNet full), exportable reports,
  batch CLI for GPU-rent runs
