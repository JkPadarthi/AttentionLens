# tests/test_preprocess.py
import numpy as np
import pytest

torch = pytest.importorskip("torch")  # skip cleanly on hosts without torch (e.g. staging)

from attentionlens.preprocess import tensor_to_image, IMAGENET_MEAN, IMAGENET_STD


def test_tensor_to_image_range():
    t = torch.zeros(1, 3, 224, 224)
    img = tensor_to_image(t)
    assert img.shape == (224, 224, 3)
    assert img.dtype == np.uint8
    assert img.min() >= 0 and img.max() <= 255


def test_imagenet_constants():
    assert len(IMAGENET_MEAN) == 3 and len(IMAGENET_STD) == 3
