from types import SimpleNamespace
from unittest.mock import MagicMock

from cursed_descent.config import HOUSE_AIR_DRAIN, HOUSE_AIR_REF_KG
from cursed_descent.sex_overlays import air_drain


def test_air_drain_scales_with_the_weight_of_the_sitter() -> None:
    assert air_drain(HOUSE_AIR_REF_KG) == HOUSE_AIR_DRAIN
    assert air_drain(160) == HOUSE_AIR_DRAIN * 2
    assert air_drain(30) < HOUSE_AIR_DRAIN
    assert air_drain(1000) == round(HOUSE_AIR_DRAIN * 2.5)


def test_the_timer_line_no_longer_repeats_the_air_label() -> None:
    from cursed_descent import home_scene
    info = {"left": 7, "air": 40}
    original = home_scene.scene_info
    home_scene.scene_info = lambda *args, **kwargs: info
    try:
        text = home_scene.timer_line(SimpleNamespace(), None)
    finally:
        home_scene.scene_info = original
    assert text == "Next interaction in 7 s" and "Air" not in text

