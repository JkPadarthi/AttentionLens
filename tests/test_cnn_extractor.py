# tests/test_cnn_extractor.py
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from attentionlens.extractors.cnn import gradcam_maps, native_activation_maps


def test_native_maps_shapes():
    # tiny fake CNN: 2 blocks of conv layers
    class FakeCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = torch.nn.Sequential(torch.nn.Conv2d(3, 8, 3, padding=1))
            self.layer2 = torch.nn.Sequential(torch.nn.Conv2d(8, 16, 3, padding=1))

        def forward(self, x):
            x = self.layer1(x)
            x = self.layer2(x)
            return x

    model = FakeCNN()
    x = torch.randn(1, 3, 32, 32)
    maps = native_activation_maps(model, ["layer1", "layer2"], x, target_size=(32, 32))
    assert len(maps) == 2
    for m in maps:
        assert m.view == "native"
        assert m.map.shape == (32, 32)
        assert m.map.min() >= 0.0 and m.map.max() <= 1.0 + 1e-6


def test_gradcam_maps_shapes():
    class FakeCNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.features = torch.nn.Sequential(
                torch.nn.Conv2d(3, 8, 3, padding=1),
                torch.nn.ReLU(),
                torch.nn.Conv2d(8, 2, 3, padding=1),
            )
            self.classifier = torch.nn.Linear(2 * 32 * 32, 3)

        def forward(self, x):
            x = self.features(x)
            return self.classifier(x.flatten(1))

    model = FakeCNN()
    x = torch.randn(1, 3, 32, 32)
    maps = gradcam_maps(model, ["features.1"], x, target_class=1, target_size=(32, 32))
    assert len(maps) == 1
    m = maps[0]
    assert m.view == "class_conditioned"
    assert m.model_class == "class_1"
    assert m.map.shape == (32, 32)
    assert m.map.min() >= 0.0  # relu applied
