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
