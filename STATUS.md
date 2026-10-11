# Status

> Updated as work progresses. Last update: **M2–M6 built+tested; M7 planted-bias experiment proven end-to-end (screener caught the planted shortcut); GPU runs queued on jengas (RTX 5070).** Date: 2026-10-11.

## Completed
- [x] Design discussion: problem → novelty → abstraction → screening → validation
- [x] Design doc (`docs/design.md`): dual-view schema, 5 metrics, screening engine,
      both validation experiments, 8 milestones
- [x] **M1 — schema + ResNet-50 dual-view extractor verified end-to-end**
- [x] M1 Task 8 — **git initialized + first commit** (this repo now has history, 2026-10-11)
- [x] **M2 — ViT extractor**: attention rollout (native) + gradient-weighted attention
      (class-conditioned, AxG); `VitExtractor` mirrors `ResNetExtractor`. Real-image
      gate passed (Samoyed, 25 maps; viual check: maps focused on the dog).
- [x] **M3 — metrics**: focus entropy, object relevance share, part alignment,
      background sensitivity, `all_metrics`
- [x] **M4 — intervention**: occlusion loop (zero/var/blur), regular grid split
- [x] **M6 — screening engine**: class-bias flags + failure diagnosis with evidence
- [x] **M5 — Gradio UI** (`attentionlens/ui/app.py`): dual-view browser + click-to-mask
- [x] **M7 — planted-bias experiment runner** (`experiments/planted_bias.py`):
      Waterbirds-style; **proven on CPU**: model 100% acc on biased set, screener
      flagged BOTH classes background-driven (class_0: 0.81 vs 0.19; class_1: 0.97
      vs 0.03). Report → `experiments/m7_dev/m7_report.json`.
- [x] All **21 unit + integration tests pass** in `.venv`

## In Progress
- [ ] **M7 on GPU (jengas, RTX 5070)**: docker build `attentionlens-gpu` running;
      plan is scaled-up run (more classes/epochs) + ViT experiment, against real
      CUB-200 if dataset download completes quickly.
- [ ] **M8 — ObjectNet natural-bias check + final report**

## Next Up (M2+)
- [x] **M2 — ViT extractor** (attention rollout + class-conditioned ViT maps) ✅
- [x] **M3 — Metrics** ✅
- [x] **M4 — Intervention loop** ✅
- [x] **M5 — Gradio UI** ✅
- [x] **M6 — Screening engine** ✅
- [ ] **M7 — Planted-bias experiment (Waterbirds-style)** — script done, CPU proof done, GPU scaling in flight
- [ ] **M8 — ObjectNet check + final report**

## Known Findings
- **Grad-CAM can produce all-zero maps on intermediate layers** (observed at `layer2.3.conv3`):
  documented Grad-CAM behavior, not a bug (Recorded in DECISIONS.md #9).
- **ImageNet label metadata**: `ResNet50_Weights.meta` is a *dict* — use `meta.get("categories")`, not `getattr`.
- **M2 ViT class-conditioning must be in-graph AxG, not gradient-of-rollout**:
  the rollout map is a *branch* off the attention tensors, not an ancestor of the
  logit — `autograd.grad(logits, rollout)` returns `None`/errors. Gradient-weighted
  attention (ReLU(A·∇L)) computed directly against each block's raw attention is the
  faithful, working analogue of Grad-CAM (DECISIONS #12).
- **timm ViT passes `attn_mask`/`is_causal`/drop_path kwargs into `attn(...)`** —
  the hook wrapper must accept `**kw` or it crashes on `vision_transformer.py`.
- **M7 screener verdicts are evidence-backed, not vibes**: every flag carries the
  per-image ImageEntry evidence links.
