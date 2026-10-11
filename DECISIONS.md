# Decisions

Key architectural decisions and the reasoning behind them. Recorded so the "why" is
not lost.

## 1. Tool, not method — SHAP/Captum tradition
AttentionLens does **not** invent a new attribution algorithm. The XAI method space is
saturated (Grad-CAM + 50 variants, attention rollout, LRP...). The contribution is a
unified instrument over existing methods plus automated verdict generation.
Rationale: engineering novelty (a genuinely useful tool) beats another Grad-CAM
variant; this is how SHAP and Captum earned their place.

## 2. Dual-view unified abstraction (native + class-conditioned)
ViT attention and CNN attribution are **not the same kind of thing**: raw ViT attention
is class-agnostic (information flow), Grad-CAM is class-specific (evidence for a class).
Comparing them naively yields meaningless metrics. Every layer therefore produces two
maps behind one `LayerMap` schema: `native` (mechanism focus) and `class_conditioned`
(decision evidence). Rationale: honest comparison, richer debugging, and screening
verdicts are always based on class-conditioned evidence.

## 3. Novelty anchor: unified framework + auto-screening (① + ②)
Chosen over alternatives (layer-role profiling alone, metrics alone). The combination
is stronger and rarer: one framework where ResNet and ViT speak the same language,
plus automated bias verdicts on top. Layer-role profiling (③) rides along for free.

## 4. Metrics on CUB-200 ground truth
Object relevance share, part alignment, focus entropy, background/object sensitivity —
all computable because CUB-200 has bounding boxes + part keypoints. No ground truth,
no honest numbers. Rationale: metrics must be measurable against annotations, not vibes.

## 5. Both validation experiments required
(a) Planted-bias (Waterbirds-style): synthetic background/species correlation; the
screener must catch the exact shortcut planted. (b) ObjectNet natural-bias: real-world
context reliance. Together: proves the tool catches what we know **and** what's real.
Rationale: a screening tool is only science if its verdicts are provably true positives.

## 6. Dual-view requires class-conditioned ViT attribution
For fair CNN⇄ViT comparison, ViT needs class-conditioned maps (class-weighted rollout /
LRP / token attribution via Captum), not raw rollout. Method choice decided by
faithfulness check in M2. Rationale: the class-conditioned view is the comparable one.

## 7. Dev on Arjun, heavy runs rented/Jenga
Daily development on Arjun (Windows, CPU). Full-dataset screening, ViT fine-tuning for
the planted-bias experiment, and ObjectNet runs happen on a rented GPU or Jenga.
Rationale: the codebase must be device-agnostic (`.to(device)` everywhere) so the same
pipeline runs unchanged on CPU or CUDA.

## 8. Python 3.12 venv, project lives at D:\GIT\AttentionLens
3.12 (standalone, not the Hermes-agent venv python or the uv-managed 3.11) for clean
torch/captum wheels. Rationale: 3.13 can lag on native wheels; the venv python on PATH
must never be the Hermes-agent one.

## 9. Grad-CAM on last conv of each block, ReLU'd
Per-block class-conditioned maps use Captum `LayerGradCam` on each bottleneck block's
final conv (`layerN.*.conv3`), ReLU applied. **Known behavior (observed in M1, layer2):
an intermediate layer can yield an all-zero map when its gradient-weighted activations
are entirely non-positive.** That is not a bug — it means "no positive class-specific
evidence here," which is information. Keep ReLU (matches Grad-CAM semantics); do not
"fix" with abs(), which would fabricate evidence where none exists.

## 10. Native view = mean-over-channels, normalized
CNN native maps average activations across channels (decision from design discussion).
Rationale: simplest honest proxy for "what the mechanism amplifies." High mean + high
entropy on all blocks (observed: 15.5–15.6 bits) is expected — native maps are
class-agnostic and broad by nature; only class-conditioned maps are sharp.

## 11. ImageNet labels via weights meta dict
`ResNet50_Weights.IMAGENET1K_V2.meta` is a **dict** on torchvision 0.28 —
`meta.get("categories")`, never `getattr(meta, "categories")`. Caught in T7 when the
demo printed `class_258` instead of `Samoyed`.

## 12. ViT class-conditioned map = in-graph gradient-weighted attention (AxG), not gradient-of-rollout
The first M2 attempt weighted the *rolled-up* patch map by ∂logit/∂rollout. That is an
autograd dead-end: the rollout is a **branch** built from the attention tensors, NOT an
ancestor of the logit, so `autograd.grad(logits, rollout)` yields `None`/a hard error.
The faithful, working analogue of Grad-CAM is per-block **gradient-weighted attention**:
for each block, ReLU(raw_attention ⊙ ∇_A logit_target), take the CLS source row → patches.
This is a true in-graph descendant→ancestor gradient, computed per block (one
class-conditioned `LayerMap` per block, matching the CNN extractor's per-layer story).
Chosen over LRP/token-attribution because it stays inside the already-verified
attention-hook plumbing and reuses the native rollout capture. DECISIONS #2/#6 updated
in practice: the "class-conditioned ViT method" is now frozen as AxG.
