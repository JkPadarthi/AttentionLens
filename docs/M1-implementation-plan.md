# M1 — Schema + CNN Extractor: Implementation Plan

> **For Hermes:** implement task-by-task per this plan; verify each gate before moving on.
> **Goal:** Unified `LayerMap` schema + ResNet-50 extractor producing dual-view maps
> (native channel activations + class-conditioned Grad-CAM) for any input image.
> **Architecture:** `attentionlens/` package; schema is the contract everything else
> consumes (metrics, screening, UI all read only `LayerMap`s).
> **Tech Stack:** Python 3.12 · PyTorch 2.13 (CPU) · torchvision · Captum · pytest

---

## Context & assumptions

- Project root on Arjun: `D:\GIT\AttentionLens` (Windows). Venv: `.venv` (3.12.10).
  Commands use `.venv\Scripts\python.exe` / `.venv\Scripts\pip.exe`.
- All code must be **device-agnostic** (`torch.device` param, default `cpu`) so the
  same pipeline runs on rented GPU / Jenga later (DECISIONS.md #7).
- Native CNN view = **mean over channels, normalized to [0,1]** (decision from design
  discussion; simplest honest proxy for "what the mechanism amplifies").
- Class-conditioned view = **Grad-CAM via Captum `LayerGradCam`** per ResNet block's
  last conv layer (layer1..layer4), so we get *per-layer* class-conditioned maps —
  feeds the "layer 1 = edges, layer 10 = parts" story from day one.
- Tests must be hermetic: synthetic tensors, no network, no real images.
  A real-image demo lives in `experiments/` (needs one downloaded sample).

---

## Task 1 — Package skeleton + pyproject

**Objective:** Turn the folder into an installable package with pytest available.

**Files:**
- Create: `D:\GIT\AttentionLens\pyproject.toml`
- Create: `D:\GIT\AttentionLens\attentionlens\__init__.py`
- Create: `D:\GIT\AttentionLens\attentionlens\extractors\__init__.py`
- Create: `D:\GIT\AttentionLens\tests\__init__.py` (empty, so pytest picks up)
- Create: `D:\GIT\AttentionLens\.gitignore`

**Step 1: pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "attentionlens"
version = "0.1.0"
description = "Interactive explainability and debugging framework for vision models"
requires-python = ">=3.12"
dependencies = [
    "torch>=2.5",
    "torchvision>=0.20",
    "captum>=0.7",
    "timm>=1.0",
    "gradio>=5",
    "pillow",
    "numpy",
    "matplotlib",
]

[tool.setuptools.packages.find]
include = ["attentionlens*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: `.gitignore`** (house policy: no `.md` except README, plus Python noise)

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
*.md
!README.md
*.log
```

**Step 3: install**

PowerShell (on Arjun, from `D:\GIT\AttentionLens`):
```powershell
.venv\Scripts\pip.exe install -e .
.venv\Scripts\pip.exe install pytest
```

**Verify:**
```powershell
.venv\Scripts\python.exe -c "import attentionlens; print('PKG_OK')"
```
Expected: `PKG_OK`

---

## Task 2 — Unified schema (`schema.py`)

**Objective:** The contract. Everything downstream (metrics, screening, UI) reads only
this. Matches design doc §4.2.

**Files:**
- Create: `D:\GIT\AttentionLens\attentionlens\schema.py`
- Create: `D:\GIT\AttentionLens\tests\test_schema.py`

**Step 1: write failing tests**

```python
# tests/test_schema.py
import numpy as np
import pytest
from attentionlens.schema import LayerMap, ModelInspection


def test_place_layermap():
    m = LayerMap(layer_name="layer4", arch="cnn", view="native",
                 model_class="class_1", map=np.zeros((8, 8)), metadata={})
    assert m.map.shape == (8, 8)


def test_place_modelinspection():
    insp = ModelInspection(model_id="resnet50", image_id="img1",
                           true_label="a", pred_label="b", layers=[])
    assert insp.model_id == "resnet50"
```

**Step 2: run → verify FAIL (module missing)**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_schema.py -v
```

**Step 3: implement schema.py**

```python
# attentionlens/schema.py
"""Unified schema: the contract between extractors, metrics, screening, and UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass
class LayerMap:
    """One attention/relevance map for one layer, one view, at input resolution."""

    layer_name: str            # e.g. "layer4" / "block11" / "attn_head_3"
    arch: str                  # "cnn" | "vit"
    view: str                  # "native" | "class_conditioned"
    model_class: str           # class this map is conditioned on (argmax for native)
    map: np.ndarray            # H×W float, normalized [0,1], at input resolution
    head_or_channel: Optional[int] = None   # per-head/per-channel breakdown
    metadata: dict[str, Any] = field(default_factory=dict)  # entropy, locality, ...


@dataclass
class InterventionResult:
    """Result of masking/occluding a region and re-running the model."""
    region: tuple[int, int, int, int]   # (x, y, w, h) in input coords
    pred_before: str
    pred_after: str
    logit_delta: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInspection:
    """Everything extracted for one (model, image) pair."""
    model_id: str
    image_id: str
    true_label: str
    pred_label: str
    layers: list[LayerMap] = field(default_factory=list)
    intervention_results: list[InterventionResult] = field(default_factory=list)
```

**Step 4: run → verify PASS**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_schema.py -v
```
Expected: `2 passed`

---

## Task 3 — Image preprocessing helper

**Objective:** Load any image → normalized 4D tensor + a reverse transform for
visualization (tensor → [0,255] uint8 RGB), ResNet-style normalization.

**Files:**
- Create: `D:\GIT\AttentionLens\attentionlens\preprocess.py`
- Create: `D:\GIT\AttentionLens\tests\test_preprocess.py`

**Step 1: failing tests**

```python
# tests/test_preprocess.py
import numpy as np
import torch
from attentionlens.preprocess import tensor_to_image, IMAGENET_MEAN, IMAGENET_STD


def test_tensor_to_image_range():
    t = torch.zeros(1, 3, 224, 224)
    img = tensor_to_image(t)
    assert img.shape == (224, 224, 3)
    assert img.dtype == np.uint8
    assert img.min() >= 0 and img.max() <= 255


def test_imagenet_constants():
    assert len(IMAGENET_MEAN) == 3 and len(IMAGENET_STD) == 3
```

**Step 2: verify FAIL → Step 3: implement**

```python
# attentionlens/preprocess.py
"""Image loading + tensor conversion helpers."""
from __future__ import annotations

import numpy as np
import torch
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def load_image_tensor(path: str, size: int = 224, device: torch.device = torch.device("cpu")) -> torch.Tensor:
    """Load image → normalized 4D tensor [1,3,H,W] on `device`."""
    img = Image.open(path).convert("RGB").resize((size, size))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)
    return t


def tensor_to_image(t: torch.Tensor) -> np.ndarray:
    """Reverse normalization → uint8 H×W×3 RGB array (for viz)."""
    a = t.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
    a = (a * np.array(IMAGENET_STD, dtype=np.float32)) + np.array(IMAGENET_MEAN, dtype=np.float32)
    a = np.clip(a * 255.0, 0, 255).astype(np.uint8)
    return a
```

**Step 4: verify PASS** (same pytest pattern; `tensor_to_image` on a zero tensor
must not error and must return correct shape/dtype — note: normalized 0 = mean, so
output won't be black; test only checks shape/dtype/range).

---

## Task 4 — Native-view extractor (channel activations)

**Objective:** Hook ResNet blocks, grab activations, mean over channels, upsample to
input resolution, normalize → `LayerMap(view="native")` per block.

**Files:**
- Create: `D:\GIT\AttentionLens\attentionlens\extractors\cnn.py`
- Create: `D:\GIT\AttentionLens\tests\test_cnn_extractor.py`

**Step 1: failing tests**

```python
# tests/test_cnn_extractor.py
import numpy as np
import pytest
import torch
from attentionlens.extractors.cnn import native_activation_maps


def test_native_maps_shapes():
    # tiny fake CNN: 2 blocks of conv layers
    class FakeCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = torch.nn.Sequential(torch.nn.Conv2d(3, 8, 3, padding=1))
            self.layer2 = torch.nn.Sequential(torch.nn.Conv2d(8, 16, 3, padding=1))
        def forward(self, x):
            x = self.layer1(x); x = self.layer2(x); return x

    model = FakeCNN()
    x = torch.randn(1, 3, 32, 32)
    maps = native_activation_maps(model, ["layer1", "layer2"], x, target_size=(32, 32))
    assert len(maps) == 2
    for m in maps:
        assert m.view == "native"
        assert m.map.shape == (32, 32)
        assert m.map.min() >= 0.0 and m.map.max() <= 1.0 + 1e-6
```

**Step 2: verify FAIL → Step 3: implement**

```python
# attentionlens/extractors/cnn.py
"""CNN attention extraction: native channel activations + Grad-CAM."""
from __future__ import annotations

import torch
import torch.nn.functional as F
import numpy as np

from attentionlens.schema import LayerMap


def _normalize01(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    mn, mx = a.min(), a.max()
    if mx - mn < 1e-9:
        return np.zeros_like(a)
    return (a - mn) / (mx - mn)


def native_activation_maps(
    model: torch.nn.Module,
    layer_names: list[str],
    input_tensor: torch.Tensor,
    target_size: tuple[int, int],
    model_class: str = "argmax",
    device: torch.device = torch.device("cpu"),
) -> list[LayerMap]:
    """Mean-over-channel activation map per named layer, normalized to [0,1]."""
    hooks: list[torch.utils.hooks.RemovableHandle] = []
    activations: dict[str, torch.Tensor] = {}

    def make_hook(name: str):
        def hook(_m, _inp, out):
            activations[name] = out.detach()
        return hook

    for name in layer_names:
        mod = model
        for part in name.split("."):
            mod = getattr(mod, part)
        hooks.append(mod.register_forward_hook(make_hook(name)))

    model.eval()
    with torch.no_grad():
        model(input_tensor.to(device))

    maps: list[LayerMap] = []
    for name in layer_names:
        act = activations[name]                    # [B,C,H,W]
        pooled = act.mean(dim=1).squeeze(0)        # [H,W]
        up = F.interpolate(pooled.unsqueeze(0).unsqueeze(0),
                           size=target_size, mode="bilinear", align_corners=False)
        arr = _normalize01(up.squeeze().cpu().numpy())
        maps.append(LayerMap(layer_name=name, arch="cnn", view="native",
                             model_class=model_class, map=arr, metadata={"reduction": "mean_channel"}))
    for h in hooks:
        h.remove()
    return maps
```

**Step 4: verify PASS.** (If the fake-CNN test trips on `getattr` traversal — it
won't, names are plain — keep names simple. Real ResNet names: `layer1.2.conv3`,
`layer2.3.conv3`, `layer3.5.conv3`, `layer4.2.conv3` — last conv of each block.)

---

## Task 5 — Class-conditioned extractor (Grad-CAM via Captum)

**Objective:** Per-block Grad-CAM on the last conv of each ResNet block → `LayerMap(
view="class_conditioned")`, relu'd, upsampled, normalized.

**Files:** modify `attentionlens/extractors/cnn.py` + `tests/test_cnn_extractor.py`

**Step 1: failing test**

```python
def test_gradcam_maps_shapes():
    from attentionlens.extractors.cnn import gradcam_maps
    class FakeCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.features = torch.nn.Sequential(torch.nn.Conv2d(3, 8, 3, padding=1),
                                                torch.nn.ReLU(),
                                                torch.nn.Conv2d(8, 2, 3, padding=1))
            self.classifier = torch.nn.Linear(2 * 32 * 32, 3)
        def forward(self, x):
            x = self.features(x)
            return self.classifier(x.flatten(1))

    model = FakeCNN()
    x = torch.randn(1, 3, 32, 32)
    maps = gradcam_maps(model, "features.1", x, target_class=1, target_size=(32, 32))
    assert len(maps) == 1
    m = maps[0]
    assert m.view == "class_conditioned"
    assert m.model_class == "class_1"
    assert m.map.shape == (32, 32)
    assert m.map.min() >= 0.0  # relu applied
```

**Step 2: verify FAIL → Step 3: implement**

```python
# append to attentionlens/extractors/cnn.py
from captum.attr import LayerGradCam

def gradcam_maps(
    model: torch.nn.Module,
    layer_names: list[str],
    input_tensor: torch.Tensor,
    target_class: int | None,
    target_size: tuple[int, int],
    device: torch.device = torch.device("cpu"),
    class_names: dict[int, str] | None = None,
) -> list[LayerMap]:
    """Grad-CAM per named layer, relu'd, upsampled, normalized."""
    model.eval()
    x = input_tensor.to(device)
    if target_class is None:
        with torch.no_grad():
            target_class = int(model(x).argmax(dim=1).item())

    maps: list[LayerMap] = []
    for name in layer_names:
        mod = model
        for part in name.split("."):
            mod = getattr(mod, part)
        cam = LayerGradCam(model, mod)
        attr = cam.attribute(x, target=target_class)     # [1,1,H,W]
        attr = F.relu(attr)
        up = F.interpolate(attr, size=target_size, mode="bilinear", align_corners=False)
        arr = _normalize01(up.squeeze().cpu().numpy())
        label = class_names[target_class] if class_names else f"class_{target_class}"
        maps.append(LayerMap(layer_name=name, arch="cnn", view="class_conditioned",
                             model_class=label, map=arr, metadata={"method": "gradcam"}))
    return maps
```

**Step 4: verify PASS.** Note: Captum Grad-CAM needs a layer whose output is
2D/4D and target-specific — the fake CNN `features.1` (second conv) works. On
real ResNet use `layer4.2.conv3` etc.

---

## Task 6 — ResNet extractor orchestrator

**Objective:** One entry point: `inspect_resnet(image, model_id="resnet50")` →
`ModelInspection` with native + class-conditioned maps for all 4 blocks, prediction
labels, and a single device param.

**Files:**
- Create: `D:\GIT\AttentionLens\attentionlens\extractors\resnet.py`
- Create: `D:\GIT\AttentionLens\tests\test_resnet.py`

**Step 1: failing test (no download in tests — use a tiny stub model)**

```python
# tests/test_resnet.py
import torch
from attentionlens.extractors.resnet import ResNetExtractor

def test_inspect_returns_modelinspection():
    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 8, 3, padding=1),
        torch.nn.AdaptiveAvgPool2d(1),
        torch.nn.Flatten(),
        torch.nn.Linear(8, 10),
    )
    ext = ResNetExtractor(model, layer_names=["0"], arch="cnn")
    x = torch.randn(1, 3, 64, 64)
    insp = ext.inspect(x, image_id="test")
    assert insp.pred_label != ""
    assert len(insp.layers) == 2  # native + class_conditioned for 1 layer
```

**Step 2: verify FAIL → Step 3: implement**

```python
# attentionlens/extractors/resnet.py
"""ResNet-50 inspection orchestrator (M1)."""
from __future__ import annotations

import torch
from torchvision.models import resnet50, ResNet50_Weights

from attentionlens.schema import ModelInspection
from attentionlens.extractors.cnn import native_activation_maps, gradcam_maps

# Last conv of each ResNet bottleneck block
RESNET_BLOCK_LAYERS = ["layer1.2.conv3", "layer2.3.conv3", "layer3.5.conv3", "layer4.2.conv3"]


class ResNetExtractor:
    def __init__(self, model: torch.nn.Module | None = None,
                 layer_names: list[str] | None = None,
                 arch: str = "cnn",
                 device: torch.device = torch.device("cpu"),
                 imagenet_labels: dict[int, str] | None = None):
        self.device = device
        self.model = model if model is not None else resnet50(weights=ResNet50_Weights.IMAGENET1K_V2).to(device)
        self.layer_names = layer_names or RESNET_BLOCK_LAYERS
        self.imagenet_labels = imagenet_labels or {}

    def predict(self, input_tensor: torch.Tensor) -> tuple[str, int]:
        with torch.no_grad():
            logits = self.model(input_tensor.to(self.device))
            idx = int(logits.argmax(dim=1).item())
        return self.imagenet_labels.get(idx, f"class_{idx}"), idx

    def inspect(self, input_tensor: torch.Tensor, image_id: str = "",
                true_label: str = "", target_class: int | None = None) -> ModelInspection:
        pred_label, pred_idx = self.predict(input_tensor)
        h, w = input_tensor.shape[-2:]
        native = native_activation_maps(self.model, self.layer_names, input_tensor,
                                        target_size=(h, w), model_class=pred_label, device=self.device)
        cc = gradcam_maps(self.model, self.layer_names, input_tensor,
                          target_class=target_class or pred_idx, target_size=(h, w),
                          device=self.device, class_names=self.imagenet_labels)
        return ModelInspection(model_id="resnet50", image_id=image_id,
                               true_label=true_label, pred_label=pred_label,
                               layers=native + cc)
```

**Step 4: verify PASS.** Real-model check (needs one download, run once manually):

```powershell
.venv\Scripts\python.exe -c "from attentionlens.extractors.resnet import ResNetExtractor; e = ResNetExtractor(); print('RESNET50_LOADED')"
```
Expected: `RESNET50_LOADED` (first run downloads ~100 MB weights).

---

## Task 7 — Real-image demo + visual verification (the M1 gate)

**Objective:** Prove the extractor produces *sane* maps on a real image — the actual
"done" bar for M1.

**Files:**
- Create: `D:\GIT\AttentionLens\experiments\m1_demo.py`
- Create: `D:\GIT\AttentionLens\experiments\sample.jpg` (downloaded sample)

**Step 1: demo script**

```python
# experiments/m1_demo.py
"""M1 gate: run ResNet-50 on a real image, save dual-view maps for all blocks."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from attentionlens.preprocess import load_image_tensor, tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.schema import ModelInspection

def main(img_path: str, out_dir: str = "experiments/out"):
    device = torch.device("cpu")
    x = load_image_tensor(img_path, device=device)
    ext = ResNetExtractor(device=device)
    insp = ext.inspect(x, image_id=pathlib.Path(img_path).stem)
    print(f"pred: {insp.pred_label} | true: {insp.true_label or 'n/a'} | layers: {len(insp.layers)}")

    base = tensor_to_image(x)
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    for m in insp.layers:
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        ax[0].imshow(base); ax[0].set_title(f"{m.layer_name} | {m.view}")
        ax[1].imshow(m.map, cmap="jet", alpha=0.7); ax[1].imshow(base, alpha=0.3)
        ax[1].axis("off")
        fig.savefig(f"{out_dir}/{m.layer_name}_{m.view}.png", bbox_inches="tight")
        plt.close(fig)
    print(f"saved maps to {out_dir}/")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "experiments/sample.jpg")
```

**Step 2: get a sample image** (one of these):
```powershell
# Option A: CUB-200 sample via torchvision dataset stub is heavy; use a direct URL:
Invoke-WebRequest -Uri "https://github.com/pytorch/hub/raw/master/images/dog.jpg" -OutFile "D:\GIT\AttentionLens\experiments\sample.jpg"
```

**Step 3: run**
```powershell
cd D:\GIT\AttentionLens
.venv\Scripts\python.exe experiments\m1_demo.py experiments\sample.jpg
```

**Verify (the M1 GATE):**
- Prints a sensible top-1 class for the dog image (e.g. "Doberman", "German shepherd").
- 8 PNGs produced (4 blocks × 2 views).
- **Sanity:** native maps show activation concentration on the object region;
  class-conditioned (Grad-CAM) maps highlight the dog's body, not empty background.
- Inspect 2–3 PNGs by eye (or have Hermes view them) before declaring M1 done.

---

## Task 8 — Housekeeping

- Update `D:\GIT\AttentionLens\STATUS.md`: mark M1 complete, add date + evidence
  (pred label, map counts, path to `experiments/out/`).
- Update `D:\GIT\AttentionLens\DECISIONS.md` if any decision changed during build.
- `git init` + first commit (per `git-first-commit` skill: .md excluded except README;
  note DECISIONS/PROJECT/STATUS/ROADMAP are `.md` — confirm with owner whether they
  should be force-tracked like EKIP does, or stay untracked).

---

## Open questions

1. **Grad-CAM target for native view metadata** — native maps are class-agnostic by
   design; `model_class` is set to the predicted class for schema consistency. OK?
2. **Imagenet label map** — ~1000-entry dict. Vendor via `torchvision`'s
   `ResNet50_Weights.IMAGENET1K_V2.meta["categories"]` (built-in, no file needed).
3. **Gitignore for the magic-5 .md files** — house rule excludes `.md` except README,
   but EKIP tracks DECISIONS/PROJECT/STATUS/ROADMAP. Pick: force-track with
   `!DECISIONS.md !PROJECT.md !STATUS.md !ROADMAP.md`, or leave untracked.

---

## Done bar (recap)

- `pytest tests/ -v` → all green (schema, preprocess, cnn, resnet)
- `m1_demo.py` on a real image → sane dual-view maps for 4 ResNet blocks, verified by eye
- STATUS.md updated with evidence
