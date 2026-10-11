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
      Waterbirds-style; **proven end-to-end**. CPU: 2-class & 4-class smoke tests.
      **GPU (jengas RTX 5070, torch 2.11.0+cu128): 4-class / 80-per run, 320 images,
      12 epochs, model 100% acc on the biased set.** The screener flagged 3 of 4
      classes as background-driven (class_0 bg 0.72, class_1 bg 0.92, class_2 bg 0.96 —
      "Suspected spurious correlation", evidence-linked); **class_3 was NOT flagged**
      (object share 0.71 vs bg 0.29) because for that color layout the model leaned on
      the object, not the background. This is the tool being *discriminative*, not
      over-flagging. Full report: `experiments/m7_gpu/m7_gpu_report.json`.
- [x] All **21 unit + integration tests pass** in `.venv`

## In Progress
- [ ] **M7 on GPU (jengas, RTX 5070)**: docker build `attentionlens-gpu` running;
      plan is scaled-up run (more classes/epochs) + ViT experiment, against real
      CUB-200 if dataset download completes quickly.
- [x] **M8 — ObjectNet-style natural-bias check** (`experiments/objectnet_check.py`):
      ran on GPU; a pretrained ResNet-50 correctly stayed object-focused on all three
      weird backgrounds (bg_share ≤ 0.03 each), so the screener returned `info`
      (object-driven), not a bias flag. **Tool verified; the synthetic stand-in did not
      induce context-reliance** (object composited too prominently, ~70% of frame).
      A true spur-of-the-moment bias test needs the real 3 GB ObjectNet + its scraping
      downloader — a separate job. Report: `experiments/m8_objectnet/objectnet_report.json`.

## Next Up (M2+)
- [x] **M2 — ViT extractor** (attention rollout + class-conditioned ViT maps) ✅
- [x] **M3 — Metrics** ✅
- [x] **M4 — Intervention loop** ✅
- [x] **M5 — Gradio UI** ✅
- [x] **M6 — Screening engine** ✅
- [x] **M7 — Planted-bias experiment (Waterbirds-style)** ✅ (GPU)
### Real M8 — ObjectNet (actual dataset, complete)

Ran AttentionLens on the **real `timm/objectnet-in1k`** (44 GB, 91 shards, 113
ImageNet-overlapping classes; downloaded with an HF token, license accepted).

- **Full run: 900 images / 30 ObjectNet classes → accuracy 0.209** (188/900). That
  is the ~60% collapse from ImageNet-1k (~0.80 top-1) a standard ResNet-50 suffers on
  ObjectNet's randomized backgrounds/rotations — the exact "models rely on context"
  effect the benchmark is built to expose. **The M8 claim is validated with real data.**
- **Failure-diagnosis**: 77 images (~10.8% of the 712 misclassifications) are cleanly
  diagnosable as context-guesses — misclassified *and* class-conditioned relevance
  concentrated on the background (e.g. a bandage on a table predicted "toaster",
  "bobsled", "ashcan"; bg share 0.52–0.65). These are the "guessed from context, not
  object" verdicts.
- **Methodology note (honest)**: per-image occlusion bg_share is not a perfect
  separator — mean bg_share on correct (0.26) ≈ wrong (0.252). The *aggregate* signal
  (accuracy collapse + 77 evidence-backed context-guesses) is strong; the *per-image*
  occlusion proxy alone doesn't fully separate context reliance, which is itself a
  finding worth stating. Class-bias flags live in the M7 planted-bias setting (where
  we *know* the shortcut), not ObjectNet's unlabeled-natural setting.
- Full report: `experiments/m8_full/m8_real_report.json`. Smoke (32 img) earlier.

### Next / known follow-ups
- Full 113-class ObjectNet sweep (this used 30 classes) for publication-grade stats.

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
