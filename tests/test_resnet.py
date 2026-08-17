# tests/test_resnet.py
import pytest

torch = pytest.importorskip("torch")

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
