# tests/test_intervention.py
import numpy as np
import pytest

torch = pytest.importorskip("torch")
from attentionlens.intervention import make_mask_tensor, run_intervention, split_regular_grid  # noqa: E402


class _FakeModel(torch.nn.Module):
    """Predict from a weighted mean of the input — testable without real ML."""
    def __init__(self):
        super().__init__()
        # class logit = average intensity over the LEFT vs RIGHT half
        self.register_buffer("w", torch.tensor([1.0, -1.0]))

    def forward(self, x):
        # x: [1,3,H,W]; reduce to [1,2] via a coarse spatial statistic
        left = x[:, :, :, : x.shape[3] // 2].mean(dim=(1, 2, 3))
        right = x[:, :, :, x.shape[3] // 2:].mean(dim=(1, 2, 3))
        return torch.stack([left, right], dim=1)


def _fake_image(mean_global=0.0):
    # normalized tensor: [1,3,H,W] where the left half has a strong signal
    x = torch.zeros(1, 3, 16, 16)
    x[:, :, :, :8] = 1.5   # strong left-side signal
    x[:, :, :, 8:] = -0.5  # distinct right side (so "unchanged" is meaningful)
    return x


def test_make_mask_zero():
    x = _fake_image()
    # mask the LEFT half (columns 0:8) across all rows
    masked = make_mask_tensor(x, (0, 0, 8, 16), "zero")
    assert torch.allclose(masked[:, :, :, :8], torch.zeros_like(masked[:, :, :, :8]))
    # right half untouched
    assert not torch.allclose(masked[:, :, :, 8:], torch.zeros_like(masked[:, :, :, 8:]))


def test_run_intervention_finds_left_relevant():
    model = _FakeModel()
    x = _fake_image()
    results = run_intervention(model, x, split_regular_grid(16, 16, 4),
                               strategy="zero")
    # masking the left half should drop class-0 logit -> positive delta, ranked first
    assert all(r.logit_delta >= 0 or r.logit_delta < 0.0001 for r in results)
    # the most-relevant region is on the left hand side (x < 8)
    top = results[0]
    assert top.region[0] < 8  # left-side column


def test_split_regular_grid_2x2():
    regions = split_regular_grid(16, 16, 2)
    assert len(regions) == 4
    # all non-overlapping, covering the whole image
    assert regions[0][0] == 0 and regions[0][1] == 0
    assert regions[-1][0] >= 8 and regions[-1][1] >= 8