# Status

> Updated as work progresses. Last update: **M1 complete — schema + ResNet-50 dual-view extractor verified end-to-end on a real image (Samoyed, 8 maps).**

## Completed
- [x] Design discussion: problem → novelty → abstraction → screening → validation
- [x] Design doc (`docs/design.md`): dual-view schema, 5 metrics, screening engine,
      both validation experiments, 8 milestones
- [x] Project scaffold on Arjun: `D:\GIT\AttentionLens\` created
- [x] Magic 5 files: README / PROJECT / DECISIONS / STATUS / ROADMAP
- [x] Python 3.12.10 venv (`.venv`) on Arjun
- [x] Dependencies: torch 2.13.0+cpu, torchvision 0.28.0+cpu, captum 0.9.0, timm,
      gradio — `ALL_IMPORTS_OK`
- [x] opencode-arjun MCP fixed (scheduled-task cwd → `D:\GIT`), all gates green
- [x] **M1 Task 1 — package skeleton** (`pyproject.toml`, package dirs, `.gitignore`; `PKG_OK`)
- [x] **M1 Task 2 — unified schema** (`schema.py`: `LayerMap`, `InterventionResult`, `ModelInspection`) — 2 tests
- [x] **M1 Task 3 — preprocessing** (`preprocess.py`: load/normalize, tensor→image) — 2 tests (skip w/o torch)
- [x] **M1 Task 4 — native-view extractor** (`extractors/cnn.py`: mean-channel activation maps) — test
- [x] **M1 Task 5 — class-conditioned extractor** (`extractors/cnn.py`: Captum LayerGrad-CAM) — test; fixed `.detach()` bug the test caught
- [x] **M1 Task 6 — ResNet orchestrator** (`extractors/resnet.py`: `ResNetExtractor.inspect`) — test; fixed ImageNet label wiring (meta dict)
- [x] **M1 Task 7 — real-image demo** (`experiments/m1_demo.py`): Samoyed predicted correctly,
      8 maps (4 blocks × native/class-cond) generated and verified (vision check on layer4:
      heatmap on dog body/head; per-layer entropy stats sane)

## In Progress
- [ ] **M1 Task 8 — housekeeping** (STATUS/DECISIONS update, git init + first commit)

## Next Up (M2+)
- [ ] **M2 — ViT extractor** (attention rollout + class-conditioned ViT maps)
- [ ] **M3 — Metrics** (object relevance share, part alignment, entropy, sensitivities)
- [ ] **M4 — Intervention loop** (mask → re-run → measure)
- [ ] **M5 — Gradio UI** (dual-view layer browser + click-to-mask)
- [ ] **M6 — Screening engine** (aggregation + verdicts + evidence links)
- [ ] **M7 — Planted-bias experiment** (Waterbirds-style)
- [ ] **M8 — ObjectNet check + final report**

## Known Findings (from M1 verification)
- **Grad-CAM can produce all-zero maps on intermediate layers** (observed at `layer2.3.conv3`):
  when a layer's gradient-weighted activations are entirely non-positive, ReLU zeroes the
  map. This is documented Grad-CAM behavior, not a bug — the pipeline faithfully reports
  "no positive class-specific evidence at this layer." Recorded in DECISIONS.md.
- **ImageNet label metadata**: `ResNet50_Weights.meta` is a *dict* on this torchvision —
  use `meta.get("categories")`, not `getattr`. Caught in T7 verification.
- **Captum attribution tensors require `.detach()`** before `.numpy()` — caught by the
  T5 test.
