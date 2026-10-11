# tests/test_metrics.py
import numpy as np
from attentionlens.schema import LayerMap
from attentionlens.metrics import focus_entropy, object_relevance_share, background_sensitivity, part_alignment, all_metrics


def _map(shape=(8, 8), value=None):
    if value is None:
        arr = np.zeros(shape)
        arr[2:6, 2:6] = 1.0  # central blob
        return LayerMap(layer_name="l", arch="cnn", view="native", model_class="c", map=arr)
    arr = np.zeros(shape)
    arr[...] = value
    return LayerMap(layer_name="l", arch="cnn", view="native", model_class="c", map=arr)


def test_object_relevance_share_center():
    m = _map()
    # bbox covering the blob => nearly all relevance inside
    share = object_relevance_share(m, (2, 2, 4, 4))
    assert share > 0.95


def test_background_sensitivity_is_complement():
    m = _map()
    bbox = (2, 2, 4, 4)
    assert abs(object_relevance_share(m, bbox) + background_sensitivity(m, bbox) - 1.0) < 1e-9


def test_focus_entropy_localized_is_low():
    m = _map()
    e = focus_entropy(m)
    assert e > 0.0
    # fully localized single-cell map has minimal entropy
    m2 = LayerMap(layer_name="l", arch="cnn", view="native", model_class="c",
                  map=_single_cell())
    assert focus_entropy(m2) < 1e-6


def test_part_alignment():
    m = _map()
    # part point at center of blob should capture most relevance
    al = part_alignment(m, [(4, 4)], radius=3)
    assert al > 0.8


def test_all_metrics_populates_metadata():
    m = _map()
    out = all_metrics(m, bbox=(2, 2, 4, 4), part_points=[(4, 4)])
    assert "entropy" in out and "object_relevance_share" in out and "part_alignment" in out
    assert "entropy" in m.metadata


def _single_cell():
    arr = np.zeros((8, 8))
    arr[4, 4] = 1.0
    return arr