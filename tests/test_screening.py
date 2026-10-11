# tests/test_screening.py
import numpy as np
from attentionlens.schema import LayerMap
from attentionlens.screening import ImageEntry, screen_class_bias, screen_failure_diagnosis, score_image


def _entry(image_id, cls, correct, obj, bg):
    return ImageEntry(image_id=image_id, class_name=cls, correct=correct,
                      object_share=obj, background_share=bg)


def test_class_bias_flag_fires():
    # class "waterbird" is consistently background-driven
    entries = [
        _entry("a", "waterbird", True, 0.2, 0.8),
        _entry("b", "waterbird", True, 0.3, 0.7),
        _entry("c", "waterbird", True, 0.25, 0.75),
        _entry("d", "landbird", True, 0.85, 0.15),
        _entry("e", "landbird", True, 0.9, 0.1),
        _entry("f", "landbird", True, 0.8, 0.2),
    ]
    report = screen_class_bias(entries)
    flags = [v for v in report.verdicts if v.level == "flag"]
    assert any("waterbird" in v.message for v in flags)
    assert all("background" in v.message for v in flags)
    # stats recorded
    assert "waterbird" in report.class_stats
    assert report.class_stats["waterbird"]["mean_background_share"] > 0.65


def test_class_bias_no_flag_when_object_driven():
    entries = [
        _entry("a", "robust", True, 0.9, 0.1),
        _entry("b", "robust", True, 0.85, 0.15),
        _entry("c", "robust", True, 0.95, 0.05),
    ]
    report = screen_class_bias(entries)
    assert all(v.level == "info" for v in report.verdicts)


def test_failure_diagnosis_flags_context_reliance():
    entries = [
        _entry("img1", "wolf", False, 0.3, 0.7),   # wrong AND background-driven
        _entry("img2", "wolf", False, 0.4, 0.6),
        _entry("img3", "bird", True, 0.8, 0.2),    # correct, object-driven
    ]
    verdicts = screen_failure_diagnosis(entries)
    assert any("img1" in v.message for v in verdicts)
    assert all(v.level == "warning" for v in verdicts)